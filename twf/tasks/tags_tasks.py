"""This module contains the Celery tasks for extracting tags from the parsed data of the pages."""
import copy
import logging
from collections import defaultdict
from celery import shared_task
from django.utils import timezone

from twf.models import Page, PageTag, Document, DocumentSyncHistory
from twf.tasks.task_base import BaseTWFTask
from twf.utils.tags_utils import assign_tag, extract_tags_from_parsed_data, SmartTagMatcher

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTWFTask)
def create_page_tags(self, project_id, user_id, **kwargs):

    try:
        # Get the projects to save the documents to
        pages = (Page.objects.filter(document__project=self.project)
                 .order_by('document__document_id', 'tk_page_number'))
        self.set_total_items(pages.count())

        assigned_tags = 0
        total_tags = 0

        for page in pages:
            PageTag.objects.filter(page=page).delete()
            parsed_data = page.parsed_data

            # Extract tags from parsed data and save them
            num_tags = 0
            for element in parsed_data["elements"]:
                num_tags += len(element["element_data"]["custom_list_structure"])
                for tag in element["element_data"]["custom_list_structure"]:
                    if not "text" in tag:
                        print("NO TEXT?", tag)  # TODO Fix me
                    else:
                        text = tag["text"].strip()
                        copy_of_tag = copy.deepcopy(tag)
                        copy_of_tag.pop("text")
                        tag = PageTag(page=page, variation=text, variation_type=tag["type"],
                                      additional_information=copy_of_tag)
                        is_assigned = assign_tag(tag, self.user)
                        if is_assigned:
                            assigned_tags += 1
                        total_tags += 1
                        tag.save(current_user=self.user)

            page.num_tags = num_tags

            page.parsed_data = parsed_data
            page.last_parsed_at = timezone.now()
            if "page_relevance" in parsed_data["file"] and parsed_data["file"]["page_relevance"] == "no":
                page.is_ignored = True
            page.save()

            self.advance_task()

        self.end_task()

    except Exception as e:
        self.end_task(status="FAILURE")


def smart_sync_tags(project, user, celery_task):
    """
    Smart synchronization of tags, preserving user work.

    This function intelligently matches old tags to new tags from Transkribus,
    preserving dictionary assignments, parked status, and other user modifications
    even when transcription text changes or tag positions shift.

    Args:
        project: Project object
        user: User performing the sync
        celery_task: BaseTWFTask instance for progress tracking

    Returns:
        dict: Statistics about the sync operation:
        {
            'added': int,           # New tags created
            'updated': int,         # Existing tags updated
            'deleted': int,         # Tags removed
            'preserved_assignments': int,  # Tags that kept their dictionary_entry
            'preserved_parked': int,       # Tags that kept their is_parked status
            'auto_assigned': int,          # New tags auto-assigned via Variation
            'warnings': [str]              # Any issues encountered
        }
    """
    pages = Page.objects.filter(document__project=project).order_by('document__document_id', 'tk_page_number')
    total_pages = pages.count()
    celery_task.set_total_items(total_pages)

    matcher = SmartTagMatcher()
    stats = {
        'added': 0,
        'updated': 0,
        'deleted': 0,
        'preserved_assignments': 0,
        'preserved_parked': 0,
        'auto_assigned': 0,
        'warnings': []
    }

    # Track changes per document for DocumentSyncHistory
    doc_changes = defaultdict(lambda: {
        'tags': {
            'added': 0,
            'updated': 0,
            'deleted': 0,
            'preserved_assignments': 0,
            'preserved_parked': 0,
            'auto_assigned': 0,
            'offset_shifts': []
        },
        'transcription_changes': False,
        'warnings': []
    })

    for page in pages:
        # Get existing tags
        old_tags = list(PageTag.objects.filter(page=page))

        # Extract new tags from parsed_data
        new_tags_data = extract_tags_from_parsed_data(page.parsed_data)

        # Match old → new
        matches, unmatched_old, unmatched_new = matcher.match_tags(old_tags, new_tags_data, page)

        # Clear previous ambiguous matches
        matcher.clear_ambiguous_matches()

        # Process matches (UPDATE)
        for old_tag, new_tag_data, score in matches:
            preserved_assignment = old_tag.dictionary_entry is not None
            preserved_parked = old_tag.is_parked

            # Check if offset changed (transcription edit)
            old_offset = old_tag.additional_information.get('offset', 0)
            new_offset = new_tag_data['offset']
            if old_offset != new_offset:
                doc_changes[page.document.id]['transcription_changes'] = True
                doc_changes[page.document.id]['tags']['offset_shifts'].append({
                    'line': new_tag_data['line_id'],
                    'tag': new_tag_data['variation'],
                    'old_offset': old_offset,
                    'new_offset': new_offset
                })

            # Update tag with new data while preserving user modifications
            old_tag.variation = new_tag_data['variation']
            old_tag.additional_information = {
                'offset': new_tag_data['offset'],
                'length': new_tag_data['length'],
                'continued': new_tag_data['continued'],
                'line_id': new_tag_data['line_id'],
                'line_text': new_tag_data['line_text']
            }
            # PRESERVE: dictionary_entry, date_variation_entry, is_parked
            old_tag.save(current_user=user)

            stats['updated'] += 1
            doc_changes[page.document.id]['tags']['updated'] += 1

            if preserved_assignment:
                stats['preserved_assignments'] += 1
                doc_changes[page.document.id]['tags']['preserved_assignments'] += 1
            if preserved_parked:
                stats['preserved_parked'] += 1
                doc_changes[page.document.id]['tags']['preserved_parked'] += 1

            if celery_task.twf_task:
                celery_task.twf_task.text += (f"  ✓ Matched tag '{old_tag.variation}' on page {page.tk_page_number} "
                                             f"(score: {score})\n")

        # Process unmatched old (DELETE)
        for old_tag in unmatched_old:
            if celery_task.twf_task:
                celery_task.twf_task.text += f"  - Deleted tag '{old_tag.variation}' from page {page.tk_page_number} (removed from TK)\n"
            old_tag.delete()
            stats['deleted'] += 1
            doc_changes[page.document.id]['tags']['deleted'] += 1

        # Process unmatched new (CREATE)
        for new_tag_data in unmatched_new:
            new_tag = PageTag(
                page=page,
                variation=new_tag_data['variation'],
                variation_type=new_tag_data['type'],
                additional_information={
                    'offset': new_tag_data['offset'],
                    'length': new_tag_data['length'],
                    'continued': new_tag_data['continued'],
                    'line_id': new_tag_data['line_id'],
                    'line_text': new_tag_data['line_text']
                }
            )

            # Try auto-assign via Variation
            was_assigned = assign_tag(new_tag, user)
            new_tag.save(current_user=user)

            stats['added'] += 1
            doc_changes[page.document.id]['tags']['added'] += 1

            if was_assigned:
                stats['auto_assigned'] += 1
                doc_changes[page.document.id]['tags']['auto_assigned'] += 1
                if celery_task.twf_task:
                    celery_task.twf_task.text += f"  + Created & auto-assigned tag '{new_tag.variation}' on page {page.tk_page_number}\n"
            else:
                if celery_task.twf_task:
                    celery_task.twf_task.text += f"  + Created new tag '{new_tag.variation}' on page {page.tk_page_number} (unassigned)\n"

        # Log ambiguous matches
        ambiguous = matcher.get_ambiguous_matches()
        if ambiguous:
            for amb in ambiguous:
                warning = (f"Page {amb['page']}, line {amb['line']}: "
                          f"Ambiguous match for '{amb['old_text']}' → '{amb['new_text']}' (score: {amb['score']})")
                stats['warnings'].append(warning)
                doc_changes[page.document.id]['warnings'].append(warning)
                if celery_task.twf_task:
                    celery_task.twf_task.text += f"  ⚠ {warning}\n"

        # Update page metadata
        page.num_tags = len(old_tags) - len(unmatched_old) + len(unmatched_new)
        page.save(current_user=user)

        # Advance progress
        celery_task.advance_task(
            text=f"Synced tags for page {page.tk_page_number}",
            status="success"
        )

    # Create DocumentSyncHistory records
    if celery_task.twf_task:
        celery_task.twf_task.text += f"\n=== Creating sync history records ===\n"

    for doc_id, changes in doc_changes.items():
        document = Document.objects.get(id=doc_id)

        # Determine sync type
        any_changes = any(changes['tags'].values())
        sync_type = 'updated' if any_changes else 'unchanged'

        DocumentSyncHistory.objects.create(
            document=document,
            task=celery_task.twf_task,
            project=project,
            user=user,
            sync_type=sync_type,
            changes=changes,
            created_by=user,
            modified_by=user
        )

        if celery_task.twf_task:
            celery_task.twf_task.text += f"  Created sync history for document {document.document_id}\n"

    return stats

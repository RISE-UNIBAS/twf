"""This module contains the functions for the AJAX requests related to the tags."""
from asgiref.sync import sync_to_async
from django.http import JsonResponse, StreamingHttpResponse
from django.utils import timezone

from twf.models import Page, Project, PageTag
from twf.views.views_ajax_base import add_details, set_details, calculate_and_set_progress, set_progress, \
    base_event_stream, base_detail_event_stream

PROGRESS_JOB_NAME = "extract-tags-progress"
DETAIL_JOB_NAME = "extract-tags-progress-detail"


async def start_tag_extraction(request, project_id):
    """This function starts the extraction of tags from the parsed data of the pages."""

    set_progress(0, project_id, PROGRESS_JOB_NAME)
    create_page_tags_async = sync_to_async(create_page_tags, thread_sensitive=True)
    await create_page_tags_async(project_id, request.user)
    return JsonResponse({'status': 'success'}, status=200)


def create_page_tags(project_id, extracting_user):
    """This function extracts tags from the parsed data of the pages."""

    try:
        # Get the projects to save the documents to
        project = Project.objects.get(pk=project_id)
        pages = Page.objects.filter(document__project=project).order_by('document__document_id', 'tk_page_number')

        total_pages = len(pages)
        processed_pages = 0
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
                        print("NO TEXT?", tag)  # TODO
                    else:
                        text = tag["text"].strip()
                        del tag["text"]
                        tag = PageTag(page=page, variation=text, variation_type=tag["type"],
                                      additional_information=tag)
                        is_assigned = tag.assign_tag()
                        if is_assigned:
                            assigned_tags += 1
                        total_tags += 1
                        tag.save()

            page.num_tags = num_tags

            page.parsed_data = parsed_data
            page.last_parsed_at = timezone.now()
            if "page_relevance" in parsed_data["file"] and parsed_data["file"]["page_relevance"] == "no":
                page.is_ignored = True
            page.save()

            processed_pages += 1
            calculate_and_set_progress(processed_pages, total_pages, project_id, PROGRESS_JOB_NAME)
            add_details(f"Extracted Tags for page {page.tk_page_id}.", project_id, DETAIL_JOB_NAME)

        set_progress(100, project_id, PROGRESS_JOB_NAME)
        set_details("Finished extracting tags.", project_id, DETAIL_JOB_NAME)

    except Project.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Project not found.'}, status=404)


def stream_tag_extraction_progress(request, project_id):
    """This function streams the progress of a process to the client."""
    set_progress(0, project_id, PROGRESS_JOB_NAME)

    return StreamingHttpResponse(base_event_stream(project_id, PROGRESS_JOB_NAME),
                                 content_type='text/event-stream')


def stream_tag_extraction_progress_detail(request, project_id):
    """This function streams the progress of a process to the client."""
    add_details("Processing files", project_id, DETAIL_JOB_NAME)

    return StreamingHttpResponse(base_detail_event_stream(project_id, DETAIL_JOB_NAME),
                                 content_type='text/event-stream')



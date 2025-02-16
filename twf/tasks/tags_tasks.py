"""This module contains the Celery tasks for extracting tags from the parsed data of the pages."""
import copy
from celery import shared_task
from django.utils import timezone

from twf.models import Page, PageTag
from twf.tasks.task_base import BaseTWFTask
from twf.utils.tags_utils import assign_tag


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

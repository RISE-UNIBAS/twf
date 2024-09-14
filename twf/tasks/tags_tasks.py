from celery import shared_task
from django.utils import timezone

from twf.models import Project, Page, PageTag, User


@shared_task(bind=True)
def create_page_tags(self, project_id, user_id):
    """This function extracts tags from the parsed data of the pages."""
    print("create_page_tags called with project_id", project_id, "and user_id", user_id)
    percentage_complete = 0
    self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                              'text': 'Starting Page Tag Extraction...'})

    try:
        # Get the projects to save the documents to
        project = Project.objects.get(pk=project_id)
        extracting_user = User.objects.get(pk=user_id)
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
                        is_assigned = tag.assign_tag(extracting_user)
                        if is_assigned:
                            assigned_tags += 1
                        total_tags += 1
                        tag.save(current_user=extracting_user)

            page.num_tags = num_tags

            page.parsed_data = parsed_data
            page.last_parsed_at = timezone.now()
            if "page_relevance" in parsed_data["file"] and parsed_data["file"]["page_relevance"] == "no":
                page.is_ignored = True
            page.save()

            processed_pages += 1
            percentage_complete = (processed_pages / total_pages) * 100
            self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                      'text': f'Extracing {total_tags} tags from {processed_pages} pages.'})

        self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'text': 'Finished.'})

    except Project.DoesNotExist:
        error_message = f'Project {project_id} does not exist.'
        self.update_state(state='FAILURE', meta={'error': error_message})
        raise ValueError(error_message)
    except User.DoesNotExist:
        error_message = f'User {user_id} does not exist.'
        self.update_state(state='FAILURE', meta={'error': error_message})
        raise ValueError(error_message)

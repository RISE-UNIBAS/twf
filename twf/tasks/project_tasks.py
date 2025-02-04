""" Celery tasks for duplicating a project and its related objects. """
from celery import shared_task
from django.db import transaction
import copy

from twf.models import Project, User, UserProfile
from twf.tasks.task_base import start_task, end_task, update_task_percentage, fail_task


@shared_task(bind=True)
def copy_project(self, original_project_id, user_id, new_title=None):
    """
    Create a deep copy of a project, including dictionaries, members, documents, pages, page tags,
    collections, collection items, tasks, prompts, and workflows.

    Args:
        self: The Celery task instance.
        original_project_id (int): The ID of the project to copy.
        user_id (int): The ID of the user performing the copy operation.
        new_title (str, optional): The title of the new project. Defaults to None.

    Returns:
        Project: The newly created project.
    """

    try:
        original_project = Project.objects.get(pk=original_project_id)
    except Project.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': f'Project with ID {original_project_id} not found.'})
        raise ValueError(f'Project with ID {original_project_id} not found.') from e

    task, percentage_complete = start_task(self, original_project, user_id, "Copy Project",
                                           text="Starting to copy project...")

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist as e:
        fail_task(self, task, f'User with ID {user_id} not found.', e)
        raise ValueError(f'User with ID {user_id} not found.') from e

    try:
        with transaction.atomic():
            update_task_percentage(self, task, 'Starting transaction...', 5)
            # Generate a new title if not provided
            new_title = new_title or f"Copy of {original_project.title}"

            # Create a copy of the original project
            new_project = copy.deepcopy(original_project)
            new_project.pk = None  # Reset primary key to create a new entry
            new_project.title = new_title
            new_project.status = 'open'  # Ensure new project starts as 'open'
            new_project.created_by = user
            new_project.modified_by = user
            new_project.save()

            # Copy selected dictionaries (referencing the same ones)
            new_project.selected_dictionaries.set(original_project.selected_dictionaries.all())

            # Copy members and their permissions
            update_task_percentage(self, task, 'Copying members...', 10)
            for member in original_project.members.all():
                new_project.members.add(member)

            # Copy user permissions
            update_task_percentage(self, task, 'Copying user permissions...', 20)
            user_profiles = UserProfile.objects.filter(user__in=new_project.members.all())
            for profile in user_profiles:
                if str(original_project.id) in profile.permissions:
                    profile.permissions[str(new_project.id)] = profile.permissions[str(original_project.id)]
                    profile.save()

            # Copy collections and their items
            update_task_percentage(self, task, 'Copying collections...', 30)
            collection_mapping = {}  # Store mapping of old -> new collections
            for collection in original_project.collections.all():
                new_collection = copy.deepcopy(collection)
                new_collection.pk = None
                new_collection.project = new_project
                new_collection.save()
                collection_mapping[collection.id] = new_collection

                # Copy CollectionItems
                for item in collection.items.all():
                    new_item = copy.deepcopy(item)
                    new_item.pk = None
                    new_item.collection = new_collection  # Assign to the new collection
                    new_item.save()

            # Copy documents and their pages/tags
            update_task_percentage(self, task, 'Copying documents...', 60)
            document_mapping = {}  # Store old -> new document mapping
            for document in original_project.documents.all():
                new_document = copy.deepcopy(document)
                new_document.pk = None
                new_document.project = new_project
                new_document.save()
                document_mapping[document.id] = new_document

                # Copy pages for each document
                page_mapping = {}
                for page in document.pages.all():
                    new_page = copy.deepcopy(page)
                    new_page.pk = None
                    new_page.document = new_document
                    new_page.save()
                    page_mapping[page.id] = new_page

                    # Copy PageTags for each page
                    for page_tag in page.tags.all():
                        new_page_tag = copy.deepcopy(page_tag)
                        new_page_tag.pk = None
                        new_page_tag.page = new_page
                        new_page_tag.save()

            # Copy tasks
            update_task_percentage(self, task, 'Copying tasks...', 70)
            for task_obj in original_project.tasks.all():
                new_task = copy.deepcopy(task_obj)
                new_task.pk = None
                new_task.project = new_project
                new_task.save()

            # Copy prompts
            update_task_percentage(self, task, 'Copying prompts...', 80)
            for prompt in original_project.prompts.all():
                new_prompt = copy.deepcopy(prompt)
                new_prompt.pk = None
                new_prompt.project = new_project

                # Map documents in prompt context to the copied documents
                new_prompt.document_context.set(
                    [document_mapping[doc.id] for doc in prompt.document_context.all() if doc.id in document_mapping]
                )
                new_prompt.page_context.set(
                    [page_mapping[page.id] for page in prompt.page_context.all() if page.id in page_mapping]
                )
                new_prompt.collection_context.set(
                    [collection_mapping[coll.id] for coll in prompt.collection_context.all() if coll.id in collection_mapping]
                )

                new_prompt.save()

            # Copy workflows
            update_task_percentage(self, task, 'Copying workflows...', 90)
            for workflow in original_project.workflow_set.all():
                new_workflow = copy.deepcopy(workflow)
                new_workflow.pk = None
                new_workflow.project = new_project
                new_workflow.save()

                # Reassign documents, dictionary entries, and collections
                new_workflow.assigned_document_items.set(
                    [document_mapping[doc.id] for doc in workflow.assigned_document_items.all() if doc.id in document_mapping]
                )
                new_workflow.assigned_dictionary_entries.set(workflow.assigned_dictionary_entries.all())  # Dictionaries remain the same
                new_workflow.assigned_collection_items.set(
                    [collection_mapping[coll.id] for coll in workflow.assigned_collection_items.all() if coll.id in collection_mapping]
                )
                new_workflow.save()

        end_task(self, task, 'Project duplicated',
                 description=f'Project duplicated for project {original_project.title}')

    except Exception as e:
        # Handle exceptions and end the task with failure
        fail_task(self, task, f"Project duplication failed.", e)
        raise

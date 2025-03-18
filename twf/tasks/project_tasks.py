""" Celery tasks for duplicating a project and its related objects. """
from celery import shared_task
from django.db import transaction
import copy

from twf.models import UserProfile
from twf.tasks.task_base import BaseTWFTask


@shared_task(bind=True, base=BaseTWFTask)
def copy_project(self, project_id, user_id, **kwargs):
    """Copy a project and its related objects."""
    self.validate_task_parameters(kwargs, ['new_title'])

    new_title = kwargs.get('new_title')

    try:
        with transaction.atomic():
            self.update_progress(5)
            # Generate a new title if not provided
            new_title = new_title or f"Copy of {self.project.title}"

            # Create a copy of the original project
            new_project = copy.deepcopy(self.project)
            new_project.pk = None  # Reset primary key to create a new entry
            new_project.title = new_title
            new_project.status = 'open'  # Ensure new project starts as 'open'
            new_project.created_by = self.user
            new_project.modified_by = self.user
            new_project.save()

            # Copy selected dictionaries (referencing the same ones)
            new_project.selected_dictionaries.set(self.project.selected_dictionaries.all())

            # Copy members and their permissions
            self.update_progress(10)
            for member in self.project.members.all():
                new_project.members.add(member)

            # Copy user permissions
            self.update_progress(20)
            user_profiles = UserProfile.objects.filter(user__in=new_project.members.all())
            for profile in user_profiles:
                if str(self.project.id) in profile.permissions:
                    profile.permissions[str(new_project.id)] = profile.permissions[str(self.project.id)]
                    profile.save()

            # Copy collections and their items
            self.update_progress(30)
            collection_mapping = {}  # Store mapping of old -> new collections
            for collection in self.project.collections.all():
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
            self.update_progress(60)
            document_mapping = {}  # Store old -> new document mapping
            for document in self.project.documents.all():
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
            self.update_progress(70)
            for task_obj in self.project.tasks.all():
                new_task = copy.deepcopy(task_obj)
                new_task.pk = None
                new_task.project = new_project
                new_task.save()

            # Copy prompts
            self.update_progress(80)
            for prompt in self.project.prompts.all():
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
            self.update_progress(90)
            for workflow in self.project.workflow_set.all():
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

        self.end_task()

    except Exception as e:
        # Handle exceptions and end the task with failure
        self.end_task(status="FAILURE")



@shared_task(bind=True, base=BaseTWFTask)
def query_project_openai(self, project_id, user_id, **kwargs):
    """Query a project and its related objects."""
    self.validate_task_parameters(kwargs, ['prompt', 'role_description', 'documents'])

    doc_ids = kwargs.pop('documents')
    documents = self.project.documents.filter(pk__in=doc_ids)

    self.process_single_ai_request(documents, 'openai',
                                   kwargs['prompt'], kwargs['role_description'], 'openai')


@shared_task(bind=True, base=BaseTWFTask)
def query_project_gemini(self, project_id, user_id, **kwargs):
    """Query a project and its related objects."""
    self.validate_task_parameters(kwargs, ['prompt', 'role_description', 'documents'])

    doc_ids = kwargs.pop('documents')
    documents = self.project.documents.filter(pk__in=doc_ids)

    self.process_single_ai_request(documents, 'genai',
                                   kwargs['prompt'], kwargs['role_description'], 'gemini')


@shared_task(bind=True, base=BaseTWFTask)
def query_project_claude(self, project_id, user_id, **kwargs):
    """Query a project and its related objects."""
    self.validate_task_parameters(kwargs, ['prompt', 'role_description', 'documents'])

    doc_ids = kwargs.pop('documents')
    documents = self.project.documents.filter(pk__in=doc_ids)

    self.process_single_ai_request(documents, 'anthropic',
                                   kwargs['prompt'], kwargs['role_description'], 'claude')


@shared_task(bind=True, base=BaseTWFTask)
def query_project_mistral(self, project_id, user_id, **kwargs):
    """Query a project and its related objects."""
    self.validate_task_parameters(kwargs, ['prompt', 'role_description', 'documents'])

    doc_ids = kwargs.pop('documents')
    documents = self.project.documents.filter(pk__in=doc_ids)

    self.process_single_ai_request(documents, 'mistral',
                                   kwargs['prompt'], kwargs['role_description'], 'mistral')
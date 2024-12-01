""" Celery tasks for duplicating a project and its related objects. """
from celery import shared_task
from django.db import transaction

from twf.models import Project, Document, Page, Collection, CollectionItem, User
from twf.tasks.task_base import start_task, end_task, update_task_percentage


@shared_task(bind=True)
def duplicate_project(self, original_project, user_id):
    """ Create a duplicate of a project and its related objects. """
    task, percentage_complete = start_task(self, original_project, user_id, text="Starting Project Duplication...",
                                           title="Duplicate Project")
    user = User.objects.get(id=user_id)

    options = {
        'new_title': "Some New TItle",
        'new_owner': 'original_owner',  # or 'current_user'
        'copy_collections': True,
        'attach_dictionaries': True,
    }
    new_owner = user if options['new_owner'] == 'current_user' else original_project.owner

    update_task_percentage(self, task, 'Duplicating project...', 5)

    try:
        with transaction.atomic():

            # Step 1: Duplicate the project itself
            duplicated_project = Project.objects.create(
                title=f"{original_project.title} (Copy)",
                collection_id=original_project.collection_id,
                description=original_project.description,
                status='open',
                owner=new_owner,
                created_by=user,
                modified_by=user
            )
            update_task_percentage(self, task, 'Project duplicated...', 10)

            # Step 2: Duplicate related Documents, Pages, etc.
            number_of_documents = original_project.documents.count()
            for doc in original_project.documents.all():
                duplicated_document = Document.objects.create(
                    project=duplicated_project,
                    title=doc.title,
                    document_id=doc.document_id,
                    metadata=doc.metadata,
                    created_by=user,
                    modified_by=user
                )

                # Copy Pages within each Document
                for page in doc.pages.all():
                    Page.objects.create(
                        document=duplicated_document,
                        metadata=page.metadata,
                        xml_file=page.xml_file,  # You may need to copy the file path or handle file duplicates
                        tk_page_id=page.tk_page_id,
                        tk_page_number=page.tk_page_number,
                        parsed_data=page.parsed_data,
                        num_tags=page.num_tags,
                        is_ignored=page.is_ignored,
                        created_by=user,
                        modified_by=user
                    )

                # Update task progress
                percentage_complete += 70 / number_of_documents
                update_task_percentage(self, task, 'Duplicating documents...', percentage_complete)

            update_task_percentage(self, task, 'Documents duplicated...', 80)

            # Step 3: Duplicate Collections and CollectionItems
            for collection in original_project.collections.all():
                duplicated_collection = Collection.objects.create(
                    project=duplicated_project,
                    title=f"{collection.title} (Copy)",
                    description=collection.description,
                    created_by=user,
                    modified_by=user
                )

                for item in collection.items.all():
                    CollectionItem.objects.create(
                        collection=duplicated_collection,
                        document=duplicated_document,  # Link to duplicated document
                        title=item.title,
                        status=item.status,
                        review_notes=item.review_notes,
                        document_configuration=item.document_configuration,
                        created_by=user,
                        modified_by=user
                    )

            end_task(self, task, 'Project duplicated',
                     description=f'Project duplicated for project {original_project.name}')

    except Exception as e:
        # Handle exceptions and end the task with failure
        end_task(self, task, 'Project duplication failed', description=str(e))
        raise

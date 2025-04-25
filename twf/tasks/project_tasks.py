""" Celery tasks for duplicating a project and its related objects. """
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
import traceback

from twf.models import Project, Note, Workflow
from twf.tasks.task_base import BaseTWFTask

User = get_user_model()


@shared_task(bind=True, base=BaseTWFTask, serializer='pickle')
def copy_project(self, project_id, user_id, **kwargs):
    """
    Create a copy of a project with all its essential components.
    
    This task creates a new project by copying the source project's structure and data:
    - Project basic data (title, description, configurations)
    - Selected dictionaries (references to same dictionaries)
    - Project members and their permissions
    - Collections and collection items
    - Documents, pages, and tags
    - Prompts with their context references
    - Workflows (in ended state)
    
    Some elements are not copied by design:
    - Tasks (to avoid duplicate task IDs and unnecessary history)
    - Active workflow states (all copied workflows are set to 'ended')
    - Reservation statuses (all items have is_reserved=False)
    
    Returns:
        Project: The newly created project object
    """
    self.validate_task_parameters(kwargs, ['new_project_name'])
    new_title = kwargs.get('new_project_name')

    try:
        with transaction.atomic():
            self.update_progress(5)
            # Generate a new title if not provided
            new_title = new_title or f"Copy of {self.project.title}"
            self.twf_task.text += f"Creating new project: {new_title}\n"

            # Create the new project with only essential attributes
            new_project = Project(
                title=new_title,
                status='open',
                created_by=self.user,
                modified_by=self.user,
                owner=self.project.owner,
                # Copy essential fields
                collection_id=self.project.collection_id,
                description=self.project.description,
                conf_credentials=self.project.conf_credentials,
                conf_tasks=self.project.conf_tasks,
                conf_export=self.project.conf_export,
                keywords=self.project.keywords,
                license=self.project.license,
                version=self.project.version,
                workflow_description=self.project.workflow_description,
                project_doi=self.project.project_doi
            )
            new_project.save()
            self.twf_task.text += f"Created new project with ID: {new_project.id}\n"

            # Copy selected dictionaries (referencing the same ones)
            self.update_progress(10)
            self.twf_task.text += "Copying dictionary references...\n"
            if self.project.selected_dictionaries.exists():
                new_project.selected_dictionaries.set(self.project.selected_dictionaries.all())

            # Copy members and their permissions
            self.update_progress(15)
            self.twf_task.text += "Copying project members...\n"
            if self.project.members.exists():
                new_project.members.set(self.project.members.all())

            # Copy user permissions
            self.update_progress(20)
            self.twf_task.text += "Copying user permissions...\n" 
            # Get a fresh queryset of users to ensure we have the latest data
            # Get all users who are members of the new project
            user_ids = new_project.members.values_list('user_id', flat=True)
            users = User.objects.filter(id__in=user_ids)
            
            for user in users:
                if hasattr(user, 'profile'):
                    profile = user.profile
                    if str(self.project.id) in profile.permissions:
                        profile.permissions[str(new_project.id)] = profile.permissions[str(self.project.id)]
                        profile.save()

            # Create mappings to track relationships between original and copied objects
            collection_mapping = {}      # old_id -> new_collection
            collection_item_mapping = {} # old_id -> new_collection_item
            document_mapping = {}        # old_id -> new_document
            page_mapping = {}            # old_id -> new_page

            # Copy collections and their items
            self.update_progress(30)
            self.twf_task.text += "Copying collections...\n"
            collection_count = 0
            collection_item_count = 0
            
            for collection in self.project.collections.all():
                new_collection = collection.__class__(
                    project=new_project,
                    title=collection.title,
                    description=collection.description,
                    created_by=self.user,
                    modified_by=self.user
                )
                new_collection.save()
                collection_mapping[collection.id] = new_collection
                collection_count += 1

                for item in collection.items.all():
                    new_item = item.__class__(
                        collection=new_collection,
                        title=item.title,
                        status=item.status,
                        document=item.document,  # Same document reference
                        document_configuration=item.document_configuration,
                        metadata=item.metadata,
                        review_notes=item.review_notes,
                        is_reserved=False,  # Reset reservation status
                        created_by=self.user,
                        modified_by=self.user
                    )
                    new_item.save()
                    collection_item_mapping[item.id] = new_item
                    collection_item_count += 1
            
            self.twf_task.text += f"Copied {collection_count} collections with {collection_item_count} items\n"

            # Copy documents and their pages/tags
            self.update_progress(50)
            self.twf_task.text += "Copying documents and pages...\n"
            document_count = 0
            page_count = 0
            tag_count = 0
            
            for document in self.project.documents.all():
                new_document = document.__class__(
                    project=new_project,
                    title=document.title,
                    document_id=document.document_id,
                    metadata=document.metadata,
                    last_parsed_at=document.last_parsed_at,
                    is_parked=document.is_parked,
                    workflow_remarks=document.workflow_remarks,
                    is_reserved=False,  # Reset reservation
                    status=document.status,
                    created_by=self.user,
                    modified_by=self.user
                )
                new_document.save()
                document_mapping[document.id] = new_document
                document_count += 1
                
                for page in document.pages.all():
                    new_page = page.__class__(
                        document=new_document,
                        metadata=page.metadata,
                        xml_file=page.xml_file,
                        tk_page_id=page.tk_page_id,
                        tk_page_number=page.tk_page_number,
                        parsed_data=page.parsed_data,
                        num_tags=page.num_tags,
                        is_ignored=page.is_ignored,
                        created_by=self.user,
                        modified_by=self.user
                    )
                    new_page.save()
                    page_mapping[page.id] = new_page
                    page_count += 1

                    for page_tag in page.tags.all():
                        new_page_tag = page_tag.__class__(
                            page=new_page,
                            variation=page_tag.variation,
                            variation_type=page_tag.variation_type,
                            dictionary_entry=page_tag.dictionary_entry,
                            additional_information=page_tag.additional_information,
                            date_variation_entry=page_tag.date_variation_entry,
                            is_parked=page_tag.is_parked,
                            created_by=self.user,
                            modified_by=self.user
                        )
                        new_page_tag.save()
                        tag_count += 1
            
            self.twf_task.text += f"Copied {document_count} documents with {page_count} pages and {tag_count} tags\n"

            # Copy prompts
            self.update_progress(80)
            self.twf_task.text += "Copying prompts...\n"
            prompt_count = 0
            
            for prompt in self.project.prompts.all():
                new_prompt = prompt.__class__(
                    project=new_project,
                    system_role=prompt.system_role,
                    prompt=prompt.prompt,
                    created_by=self.user,
                    modified_by=self.user
                )
                new_prompt.save()
                prompt_count += 1

                # Handle many-to-many relationships with proper mappings
                # Document context
                if prompt.document_context.exists():
                    docs_to_add = []
                    for doc in prompt.document_context.all():
                        if doc.id in document_mapping:
                            docs_to_add.append(document_mapping[doc.id])
                    if docs_to_add:
                        new_prompt.document_context.set(docs_to_add)
                
                # Page context
                if prompt.page_context.exists():
                    pages_to_add = []
                    for page in prompt.page_context.all():
                        if page.id in page_mapping:
                            pages_to_add.append(page_mapping[page.id])
                    if pages_to_add:
                        new_prompt.page_context.set(pages_to_add)
                
                # Collection item context
                if prompt.collection_context.exists():
                    items_to_add = []
                    for item in prompt.collection_context.all():
                        if item.id in collection_item_mapping:
                            items_to_add.append(collection_item_mapping[item.id])
                    if items_to_add:
                        new_prompt.collection_context.set(items_to_add)
            
            self.twf_task.text += f"Copied {prompt_count} prompts\n"

            # Copy workflows
            self.update_progress(90)
            self.twf_task.text += "Copying workflows...\n"
            workflow_count = 0
            
            # Use the Workflow class to properly access its fields
            
            for workflow in self.project.workflow_set.all():
                # Create a new workflow with basic attributes
                new_workflow = Workflow(
                    project=new_project,
                    user=workflow.user,
                    workflow_type=workflow.workflow_type,
                    status='ended',  # Set as ended to avoid issues
                    item_count=workflow.item_count,
                    current_item_index=0,  # Reset index
                    created_at=workflow.created_at,
                    updated_at=workflow.updated_at
                )
                
                # Set foreign key relationships if they exist and were copied
                if workflow.dictionary:
                    new_workflow.dictionary = workflow.dictionary  # Reference the same dictionary
                    
                if workflow.collection and workflow.collection.id in collection_mapping:
                    new_workflow.collection = collection_mapping[workflow.collection.id]
                
                # Do not copy the related_task to avoid task duplication issues
                new_workflow.related_task = None
                
                new_workflow.save()
                workflow_count += 1

                # Handle many-to-many relationships with proper error handling
                # Document items
                if hasattr(workflow, 'assigned_document_items') and workflow.assigned_document_items.exists():
                    try:
                        docs_to_assign = []
                        for doc in workflow.assigned_document_items.all():
                            if doc.id in document_mapping:
                                docs_to_assign.append(document_mapping[doc.id])
                        if docs_to_assign:
                            new_workflow.assigned_document_items.set(docs_to_assign)
                    except Exception as e:
                        self.twf_task.text += f"Warning: Could not copy document items relation: {e}\n"
                
                # Dictionary entries
                if hasattr(workflow, 'assigned_dictionary_entries') and workflow.assigned_dictionary_entries.exists():
                    try:
                        # Dictionary entries are referenced, not copied
                        new_workflow.assigned_dictionary_entries.set(workflow.assigned_dictionary_entries.all())
                    except Exception as e:
                        self.twf_task.text += f"Warning: Could not copy dictionary entries relation: {e}\n"
                
                # Collection items
                if hasattr(workflow, 'assigned_collection_items') and workflow.assigned_collection_items.exists():
                    try:
                        items_to_assign = []
                        for item in workflow.assigned_collection_items.all():
                            if item.id in collection_item_mapping:
                                items_to_assign.append(collection_item_mapping[item.id])
                        if items_to_assign:
                            new_workflow.assigned_collection_items.set(items_to_assign)
                    except Exception as e:
                        self.twf_task.text += f"Warning: Could not copy collection items relation: {e}\n"
            
            self.twf_task.text += f"Copied {workflow_count} workflows\n"

            # Create a note about the copy
            Note.objects.create(
                project=new_project,
                title="Project Copy Information",
                note=f"This project was copied from '{self.project.title}' on {timezone.now().strftime('%Y-%m-%d at %H:%M')}.\n\n"
                     f"Copy includes:\n"
                     f"- {document_count} documents\n"
                     f"- {page_count} pages\n"
                     f"- {tag_count} tags\n"
                     f"- {collection_count} collections\n"
                     f"- {collection_item_count} collection items\n"
                     f"- {prompt_count} prompts\n"
                     f"- {workflow_count} workflows\n\n"
                     f"Copied by: {self.user.username}",
                created_by=self.user,
                modified_by=self.user
            )

        # Record completion in the database task
        if self.twf_task:
            self.twf_task.text += f"Project copy completed successfully!\n"
            self.twf_task.status = "SUCCESS"
            self.twf_task.end_time = timezone.now()
            duration = (self.twf_task.end_time - self.start_datetime).total_seconds()
            
            # Create summary
            summary = f"\n---- TASK SUMMARY ----\n"
            summary += f"Status: SUCCESS\n"
            summary += f"Duration: {duration:.2f} seconds"
            
            if duration > 60:
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                summary += f" ({minutes}m {seconds}s)"
            summary += "\n"
            
            summary += f"Project copied: {self.project.title} → {new_project.title}\n"
            summary += f"Collections: {collection_count}\n"
            summary += f"Collection items: {collection_item_count}\n"
            summary += f"Documents: {document_count}\n"
            summary += f"Pages: {page_count}\n"
            summary += f"Tags: {tag_count}\n"
            summary += f"Prompts: {prompt_count}\n"
            summary += f"Workflows: {workflow_count}\n"
            summary += "----------------------\n"
            
            self.twf_task.text += summary
            
            # Set meta information in the database task
            self.twf_task.meta = {
                'status': 'SUCCESS',
                'duration': duration,
                'collections': collection_count,
                'collection_items': collection_item_count,
                'documents': document_count,
                'pages': page_count,
                'tags': tag_count,
                'prompts': prompt_count,
                'workflows': workflow_count,
                'new_project_id': new_project.id,
                'celery_task_id': self.task_id  # Store the Celery task ID for status lookup
            }
            
            self.twf_task.save()
            
        # Return the result in the format expected by task_status_view and celery_task_monitor.js
        result = {
            'new_project_id': new_project.id,
            'collections': collection_count,
            'collection_items': collection_item_count,
            'documents': document_count,
            'pages': page_count,
            'tags': tag_count,
            'prompts': prompt_count,
            'workflows': workflow_count,
            'task_id': self.task_id,
            'db_task_id': self.twf_task.id if self.twf_task else None
        }
            
        return result

    except Exception as e:
        # Log the error with detailed information
        error_msg = f"{type(e).__name__}: {str(e)}"
        stack_trace = traceback.format_exc()
        
        # Record failure in the database task
        if self.twf_task:
            self.twf_task.text += f"Error during project copy: {error_msg}\n"
            self.twf_task.text += f"Stack trace:\n{stack_trace}\n"
            self.twf_task.status = "FAILURE"
            self.twf_task.end_time = timezone.now()
            self.twf_task.title = f"Failed: {error_msg[:50]}..." if len(error_msg) > 50 else f"Failed: {error_msg}"
            
            # Add summary to task text
            duration = (self.twf_task.end_time - self.start_datetime).total_seconds()
            summary = f"\n---- TASK SUMMARY ----\n"
            summary += f"Status: FAILURE\n"
            summary += f"Duration: {duration:.2f} seconds\n"
            summary += f"Error: {error_msg}\n"
            summary += "----------------------\n"
            self.twf_task.text += summary
            
            self.twf_task.save()
        
        # Re-raise the exception to let Celery handle it
        raise


@shared_task(bind=True, base=BaseTWFTask)
def query_project_openai(self, project_id, user_id, **kwargs):
    """
    Query an OpenAI model with documents from the project.
    
    This task processes a query to OpenAI models (like GPT-4, GPT-4 Vision) using selected 
    documents from the project. It supports multimodal prompts with both text and images.
    
    The task will:
    1. Retrieve the specified documents from the project
    2. Process the query according to the specified prompt mode
    3. For image modes, automatically select up to 5 images per document
    4. Send the content to OpenAI and capture the response
    
    Args:
        project_id (int): ID of the project
        user_id (int): ID of the user running the task
        **kwargs: Additional keyword arguments
            - prompt (str): The text prompt to send to the model
            - role_description (str): System role description for the AI
            - documents (list): List of document IDs to include
            - prompt_mode (str): One of "text_only", "images_only", or "text_and_images"
                                Defaults to "text_only" if not specified
    """
    self.validate_task_parameters(kwargs, ['prompt', 'role_description', 'documents'])

    doc_ids = kwargs.pop('documents')
    documents = self.project.documents.filter(pk__in=doc_ids)
    
    # Get the prompt mode (defaults to text_only if not provided)
    prompt_mode = kwargs.pop('prompt_mode', 'text_only')

    # Let the process_single_ai_request function handle exceptions
    # The error will be logged in our DB and the exception will be raised for Celery
    return self.process_single_ai_request(
        documents, 
        'openai',
        kwargs['prompt'], 
        kwargs['role_description'], 
        'openai',
        prompt_mode=prompt_mode
    )


@shared_task(bind=True, base=BaseTWFTask)
def query_project_gemini(self, project_id, user_id, **kwargs):
    """
    Query a Google Gemini model with documents from the project.
    
    This task processes a query to Google Gemini models using selected documents 
    from the project. Gemini models have strong multimodal capabilities and can
    effectively process both text and images together.
    
    The task will:
    1. Retrieve the specified documents from the project
    2. Process the query according to the specified prompt mode
    3. For image modes, automatically select up to 5 images per document
    4. Send the content to Gemini and capture the response
    
    Args:
        project_id (int): ID of the project
        user_id (int): ID of the user running the task
        **kwargs: Additional keyword arguments
            - prompt (str): The text prompt to send to the model
            - role_description (str): System role description for the AI
            - documents (list): List of document IDs to include
            - prompt_mode (str): One of "text_only", "images_only", or "text_and_images"
                                Defaults to "text_only" if not specified
    """
    self.validate_task_parameters(kwargs, ['prompt', 'role_description', 'documents'])

    doc_ids = kwargs.pop('documents')
    documents = self.project.documents.filter(pk__in=doc_ids)
    
    # Get the prompt mode (defaults to text_only if not provided)
    prompt_mode = kwargs.pop('prompt_mode', 'text_only')

    # Let the process_single_ai_request function handle exceptions
    # The error will be logged in our DB and the exception will be raised for Celery
    return self.process_single_ai_request(
        documents, 
        'genai',
        kwargs['prompt'], 
        kwargs['role_description'], 
        'gemini',
        prompt_mode=prompt_mode
    )


@shared_task(bind=True, base=BaseTWFTask)
def query_project_claude(self, project_id, user_id, **kwargs):
    """
    Query an Anthropic Claude model with documents from the project.
    
    This task processes a query to Anthropic Claude models using selected documents
    from the project. In the current implementation, Claude is limited to text-only
    processing, regardless of the selected prompt_mode. When image modes are requested,
    the task automatically falls back to text-only mode with a notification.
    
    The task will:
    1. Retrieve the specified documents from the project
    2. Process the query using text-only mode (ignoring any image mode requests)
    3. Send the content to Claude and capture the response
    
    Args:
        project_id (int): ID of the project
        user_id (int): ID of the user running the task
        **kwargs: Additional keyword arguments
            - prompt (str): The text prompt to send to the model
            - role_description (str): System role description for the AI
            - documents (list): List of document IDs to include
            - prompt_mode (str): While this parameter is accepted, Claude currently
                                only supports "text_only" mode
    
    Note:
        Although Claude models do support image inputs in their native API,
        this implementation currently forces text-only mode for all Claude requests.
    """
    self.validate_task_parameters(kwargs, ['prompt', 'role_description', 'documents'])

    doc_ids = kwargs.pop('documents')
    documents = self.project.documents.filter(pk__in=doc_ids)
    
    # Get the prompt mode (defaults to text_only if not provided)
    prompt_mode = kwargs.pop('prompt_mode', 'text_only')
    
    # Note about Claude's image support (currently not supported)
    if prompt_mode in ['images_only', 'text_and_images']:
        self.twf_task.text += "Note: Claude support for images has been disabled in this version.\n"
    
    # Force text-only mode for Claude
    prompt_mode = 'text_only'

    # Let the process_single_ai_request function handle exceptions
    # The error will be logged in our DB and the exception will be raised for Celery
    return self.process_single_ai_request(
        documents, 
        'anthropic',
        kwargs['prompt'], 
        kwargs['role_description'], 
        'claude',
        prompt_mode=prompt_mode
    )


@shared_task(bind=True, base=BaseTWFTask)
def query_project_mistral(self, project_id, user_id, **kwargs):
    """
    Query a Mistral model with documents from the project.
    
    This task processes a query to Mistral AI models using selected documents
    from the project. Currently, Mistral models support only text inputs, so
    regardless of the selected prompt_mode, the task will operate in text-only mode.
    When image modes are requested, the task automatically falls back to text-only
    mode with a notification.
    
    The task will:
    1. Retrieve the specified documents from the project
    2. Process the query using text-only mode (ignoring any image mode requests)
    3. Send the content to Mistral and capture the response
    
    Args:
        project_id (int): ID of the project
        user_id (int): ID of the user running the task
        **kwargs: Additional keyword arguments
            - prompt (str): The text prompt to send to the model
            - role_description (str): System role description for the AI
            - documents (list): List of document IDs to include
            - prompt_mode (str): While this parameter is accepted, Mistral currently
                                only supports "text_only" mode
    
    Note:
        Mistral's API does not currently support image inputs. This implementation
        forces text-only mode for all Mistral requests, regardless of the selected
        prompt_mode.
    """
    self.validate_task_parameters(kwargs, ['prompt', 'role_description', 'documents'])

    doc_ids = kwargs.pop('documents')
    documents = self.project.documents.filter(pk__in=doc_ids)
    
    # Get the prompt mode (defaults to text_only if not provided)
    prompt_mode = kwargs.pop('prompt_mode', 'text_only')
    
    # Note about Mistral's image support (currently not supported)
    if prompt_mode in ['images_only', 'text_and_images']:
        self.twf_task.text += "Note: Mistral does not currently support image inputs. Using text-only mode.\n"
    
    # Force text-only mode for Mistral
    prompt_mode = 'text_only'

    # Let the process_single_ai_request function handle exceptions
    # The error will be logged in our DB and the exception will be raised for Celery
    return self.process_single_ai_request(
        documents, 
        'mistral',
        kwargs['prompt'], 
        kwargs['role_description'], 
        'mistral',
        prompt_mode=prompt_mode
    )


@shared_task(bind=True, base=BaseTWFTask)
def query_project_deepseek(self, project_id, user_id, **kwargs):
    self.validate_task_parameters(kwargs, ['prompt', 'role_description', 'documents'])

    doc_ids = kwargs.pop('documents')
    documents = self.project.documents.filter(pk__in=doc_ids)
    prompt_mode = 'text_only'

    # Let the process_single_ai_request function handle exceptions
    # The error will be logged in our DB and the exception will be raised for Celery
    return self.process_single_ai_request(
        documents,
        'deepseek',
        kwargs['prompt'],
        kwargs['role_description'],
        'deepseek',
        prompt_mode=prompt_mode
    )


@shared_task(bind=True, base=BaseTWFTask)
def query_project_qwen(self, project_id, user_id, **kwargs):
    self.validate_task_parameters(kwargs, ['prompt', 'role_description', 'documents'])

    doc_ids = kwargs.pop('documents')
    documents = self.project.documents.filter(pk__in=doc_ids)
    prompt_mode = 'text_only'

    # Let the process_single_ai_request function handle exceptions
    # The error will be logged in our DB and the exception will be raised for Celery
    return self.process_single_ai_request(
        documents,
        'qwen',
        kwargs['prompt'],
        kwargs['role_description'],
        'qwen',
        prompt_mode=prompt_mode
    )
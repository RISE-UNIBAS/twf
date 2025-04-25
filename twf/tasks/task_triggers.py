"""
This module contains the functions for triggering Celery tasks in the TWF application.

The functions in this module handle the extraction of parameters from HTTP requests,
the validation of those parameters, and the triggering of appropriate Celery tasks.
They serve as the bridge between the web interface and the background task processing system.

Key features:
- Standardized task triggering through the trigger_task helper function
- Support for various AI operations (OpenAI, Gemini, Claude, Mistral)
- Specialized handlers for multimodal content (text + images) in project queries
- Comprehensive support for dictionary, document, collection, and export tasks
"""
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse

from twf.tasks.collection_tasks import search_openai_for_collection, search_gemini_for_collection, \
    search_claude_for_collection, search_openai_for_collection_item, search_gemini_for_collection_item, \
    search_claude_for_collection_item, search_mistral_for_collection_item
from twf.tasks.document_tasks import search_openai_for_docs, search_gemini_for_docs, search_claude_for_docs, \
    search_openai_for_pages, search_gemini_for_pages, search_claude_for_pages, search_mistral_for_docs, \
    search_mistral_for_pages
from twf.tasks.structure_tasks import extract_zip_export_task
from twf.tasks.dictionary_tasks import search_gnd_entries, search_geonames_entries, search_wikidata_entries, \
    search_openai_entries, search_gnd_entry, search_geonames_entry, search_wikidata_entry, search_openai_entry, \
    search_claude_entries, search_gemini_entries, search_claude_entry, search_gemini_entry, search_mistral_entries, \
    search_mistral_entry
from twf.tasks.metadata_tasks import load_sheets_metadata, load_json_metadata
from twf.tasks.tags_tasks import create_page_tags
from twf.tasks.project_tasks import copy_project, query_project_openai, query_project_gemini, query_project_claude, \
    query_project_mistral
from twf.tasks.export_tasks import export_documents_task, export_collections_task, export_project_task, \
    export_to_zenodo_task
from twf.views.views_base import TWFView

def trigger_task(request, task_function, *args, **kwargs):
    """
    Trigger a Celery task and return a JSON response with the task ID.
    
    This is a helper function used by all task trigger handlers to standardize
    the process of starting a background task. It extracts the current project
    and user from the request, passes them to the task along with any additional
    arguments, and returns a standardized JSON response for AJAX handling.
    
    Args:
        request (HttpRequest): The HTTP request object
        task_function (function): The Celery task function to call
        *args, **kwargs: Additional positional and keyword arguments to pass to the task
        
    Returns:
        JsonResponse: A JSON response containing the task ID for client-side tracking
    """
    project = TWFView.s_get_project(request)
    user_id = request.user.id

    task = task_function.delay(project.id, user_id, *args, **kwargs)
    return JsonResponse({'status': 'success', 'task_id': task.id})

##############################
## PROJECT TASKS
def start_extraction(request):
    """Start Transkribus export zip extraction and page parsing process.
    No additional parameters are required."""
    return trigger_task(request, extract_zip_export_task)


def start_test_export_task(request):
    """Start the test export task."""
    return JsonResponse({'status': 'error', 'message': 'Not implemented'}, status=400)


##############################
## TAGS TASKS
def start_tags_creation(request):
    """Start the page tags creation process.
    No additional parameters are required."""
    return trigger_task(request, create_page_tags)


##############################
## DICTIONARY TASKS
def start_dict_gnd_batch(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.POST.get('dictionary')
    earliest_birth_year = request.POST.get('earliest_birth_year', None)
    latest_birth_year = request.POST.get('latest_birth_year', None)
    show_empty = request.POST.get('show_empty', False)
    if show_empty == 'on':
        show_empty = True
    if earliest_birth_year != '':
        earliest_birth_year = int(earliest_birth_year)
    if latest_birth_year != '':
        latest_birth_year = int(latest_birth_year)

    return trigger_task(request, search_gnd_entries,
                        dictionary_id=dictionary_id,
                        earliest_birth_year=earliest_birth_year,
                        latest_birth_year=latest_birth_year,
                        show_empty=show_empty)


def start_dict_geonames_batch(request):
    """Start the GeoNames requests as a Celery task."""

    dictionary_id = request.POST.get('dictionary')
    country_restriction = request.POST.get('only_search_in')
    similarity_threshold = request.POST.get('similarity_threshold')

    return trigger_task(request, search_geonames_entries,
                        dictionary_id=dictionary_id,
                        country_restriction=country_restriction,
                        similarity_threshold=similarity_threshold)


def start_dict_wikidata_batch(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.POST.get('dictionary')
    entity_type = request.POST.get('entity_type')
    language = request.POST.get('language')

    return trigger_task(request, search_wikidata_entries,
                        dictionary_id=dictionary_id,
                        entity_type=entity_type,
                        language=language)


def start_dict_openai_batch(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.POST.get('dictionary')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_openai_entries,
                        dictionary_id=dictionary_id,
                        prompt=prompt,
                        role_description=role_description)


def start_dict_claude_batch(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.POST.get('dictionary')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_claude_entries,
                        dictionary_id=dictionary_id,
                        prompt=prompt,
                        role_description=role_description)


def start_dict_gemini_batch(request):
    """Start the Gemini requests as a Celery task."""
    dictionary_id = request.POST.get('dictionary')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_gemini_entries,
                        dictionary_id=dictionary_id,
                        prompt=prompt,
                        role_description=role_description)


def start_dict_mistral_batch(request):
    """Start the Gemini requests as a Celery task."""
    dictionary_id = request.POST.get('dictionary')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_mistral_entries,
                        dictionary_id=dictionary_id,
                        prompt=prompt,
                        role_description=role_description)


def start_dict_gnd_request(request):
    dictionary_id = request.GET.get('dictionary_id')
    earliest_birth_year = request.POST.get('earliest_birth_year', None)
    latest_birth_year = request.POST.get('latest_birth_year', None)
    show_empty = request.POST.get('show_empty', False)
    if show_empty == 'on':
        show_empty = True
    if earliest_birth_year != '':
        earliest_birth_year = int(earliest_birth_year)
    if latest_birth_year != '':
        latest_birth_year = int(latest_birth_year)

    return trigger_task(request, search_gnd_entry,
                        dictionary_id=dictionary_id,
                        earliest_birth_year=earliest_birth_year,
                        latest_birth_year=latest_birth_year,
                        show_empty=show_empty)


def start_dict_geonames_request(request):
    dictionary_id = request.GET.get('dictionary_id')
    country_restriction = request.POST.get('only_search_in')
    similarity_threshold = request.POST.get('similarity_threshold')
    return trigger_task(request, search_geonames_entry,
                        dictionary_id=dictionary_id,
                        country_restriction=country_restriction,
                        similarity_threshold=similarity_threshold)


def start_dict_wikidata_request(request):
    dictionary_id = request.GET.get('dictionary_id')
    entity_type = request.POST.get('entity_type')
    language = request.POST.get('language')
    return trigger_task(request, search_wikidata_entry,
                        dictionary_id=dictionary_id,
                        entity_type=entity_type,
                        language=language)


def start_dict_openai_request(request):
    dictionary_id = request.GET.get('dictionary_id')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')
    return trigger_task(request, search_openai_entry,
                        dictionary_id=dictionary_id,
                        prompt=prompt,
                        role_description=role_description)


def start_dict_claude_request(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.GET.get('dictionary_id')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')
    return trigger_task(request, search_claude_entry,
                        dictionary_id=dictionary_id,
                        prompt=prompt,
                        role_description=role_description)


def start_dict_gemini_request(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.GET.get('dictionary_id')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')
    return trigger_task(request, search_gemini_entry,
                        dictionary_id=dictionary_id,
                        prompt=prompt,
                        role_description=role_description)


def start_dict_mistral_request(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.GET.get('dictionary_id')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')
    return trigger_task(request, search_mistral_entry,
                        dictionary_id=dictionary_id,
                        prompt=prompt,
                        role_description=role_description)


##############################
## DOCUMENT TASKS
def start_openai_doc_batch(request):
    """ Start the OpenAI requests as a Celery task."""
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')
    prompt_mode = request.POST.get('prompt_mode')

    return trigger_task(request, search_openai_for_docs,
                        prompt=prompt,
                        role_description=role_description,
                        prompt_mode=prompt_mode)


def start_gemini_doc_batch(request):
    """ Start the Gemini requests as a Celery task."""
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')
    prompt_mode = request.POST.get('prompt_mode')

    return trigger_task(request, search_gemini_for_docs,
                        prompt=prompt,
                        role_description=role_description,
                        prompt_mode=prompt_mode)


def start_claude_doc_batch(request):
    """ Start the Claude requests as a Celery task."""
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_claude_for_docs,
                        prompt=prompt,
                        role_description=role_description)


def start_mistral_doc_batch(request):
    """ Start the Mistral requests as a Celery task."""
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_mistral_for_docs,
                        prompt=prompt,
                        role_description=role_description)


def start_openai_page_batch(request):
    """ Start the OpenAI requests as a Celery task."""
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_openai_for_pages,
                        prompt=prompt,
                        role_description=role_description)


def start_gemini_page_batch(request):
    """ Start the Gemini requests as a Celery task."""
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_gemini_for_pages,
                        prompt=prompt,
                        role_description=role_description)


def start_claude_page_batch(request):
    """ Start the Claude requests as a Celery task."""
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_claude_for_pages,
                        prompt=prompt,
                        role_description=role_description)


def start_mistral_page_batch(request):
    """ Start the Claude requests as a Celery task."""
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_mistral_for_pages,
                        prompt=prompt,
                        role_description=role_description)


##############################
## METADATA TASKS
def start_json_metadata(request):
    """Start the metadata loading from JSON as a Celery task."""

    data_target_type = request.POST.get('data_target_type')
    json_data_key = request.POST.get('json_data_key')
    match_to_field = request.POST.get('match_to_field')

    data_file = request.FILES.get('data_file')

    if data_file:
        # Generate a unique filename
        file_name = f"metadata_upload_{uuid.uuid4().hex}.json"
        file_path = Path(settings.MEDIA_ROOT) / "temp" / file_name

        # Ensure the temp directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the file
        with default_storage.open(file_path, 'wb') as destination:
            for chunk in data_file.chunks():
                destination.write(chunk)

    else:
        return JsonResponse({'status': 'error', 'message': 'No file uploaded'}, status=400)

    return trigger_task(request, load_json_metadata,
                        data_file_path=file_path,
                        data_target_type=data_target_type,
                        json_data_key=json_data_key,
                        match_to_field=match_to_field)


def start_sheet_metadata(request):
    """Start the metadata loading from Google Sheets as a Celery task."""
    return trigger_task(request, load_sheets_metadata)


##############################
## COLLECTION TASKS
def start_openai_collection_batch(request):
    collection_id = request.POST.get('collection')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_openai_for_collection,
                        collection_id=collection_id,
                        prompt=prompt,
                        role_description=role_description)

def start_gemini_collection_batch(request):
    collection_id = request.POST.get('collection')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_gemini_for_collection,
                        collection_id=collection_id,
                        prompt=prompt,
                        role_description=role_description)

def start_claude_collection_batch(request):
    collection_id = request.POST.get('collection')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_claude_for_collection,
                        collection_id=collection_id,
                        prompt=prompt,
                        role_description=role_description)

def start_openai_collection_request(request):
    collection_id = request.POST.get('collection_id')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_openai_for_collection_item,
                        collection_id=collection_id,
                        prompt=prompt,
                        role_description=role_description)

def start_gemini_collection_request(request):
    collection_id = request.POST.get('collection_id')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_gemini_for_collection_item,
                        collection_id=collection_id,
                        prompt=prompt,
                        role_description=role_description)

def start_claude_collection_request(request):
    collection_id = request.POST.get('collection_id')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_claude_for_collection_item,
                        collection_id=collection_id,
                        prompt=prompt,
                        role_description=role_description)

def start_mistral_collection_request(request):
    collection_id = request.POST.get('collection_id')
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')

    return trigger_task(request, search_mistral_for_collection_item,
                        collection_id=collection_id,
                        prompt=prompt,
                        role_description=role_description)

def start_copy_project(request):
    new_project_name = request.POST.get('new_project_name')

    return trigger_task(request, copy_project,
                        new_project_name=new_project_name)


def start_query_project_openai(request):
    """
    Trigger an OpenAI query task for the project with multimodal support.
    
    This function extracts parameters from the request and starts a Celery task
    to process a query using OpenAI models. It fully supports multimodal prompts with
    both text and images through OpenAI's vision capabilities.
    
    The function passes the prompt_mode parameter to control how content is sent:
    - text_only: Only text content from documents is included
    - images_only: Only images from documents are included with minimal text
    - text_and_images: Both document text and images are included
    
    For image-based modes, the task will automatically select up to 5 representative
    images from each document, using the Page model's get_image_url method with 50%
    scaling to optimize for performance.
    
    Args:
        request (HttpRequest): The request object containing POST data
        
    Returns:
        JsonResponse: Response with task_id for tracking progress
        
    Post Parameters:
        prompt (str): The text prompt to send to the model
        prompt_mode (str): One of "text_only", "images_only", or "text_and_images"
        role_description (str): System role description for the AI
        documents (list): List of document IDs to include in the query
        
    Technical Details:
        - Uses OpenAI's GPT-4 Vision capabilities (or compatible models)
        - Images are sent via URLs directly to OpenAI, not uploaded first
        - Transkribus server provides the images through its API
        - IIIF protocol is used for image scaling when available
    """
    prompt = request.POST.get('prompt')
    prompt_mode = request.POST.get('prompt_mode')
    role_description = request.POST.get('role_description')
    documents = request.POST.getlist('documents')

    return trigger_task(request, query_project_openai,
                        prompt=prompt,
                        role_description=role_description,
                        documents=documents,
                        prompt_mode=prompt_mode)


def start_query_project_gemini(request):
    """
    Trigger a Google Gemini query task for the project with multimodal support.
    
    This function extracts parameters from the request and starts a Celery task
    to process a query using Google Gemini models. It fully supports multimodal prompts
    with both text and images through Gemini's vision capabilities.
    
    The function passes the prompt_mode parameter to control how content is sent:
    - text_only: Only text content from documents is included
    - images_only: Only images from documents are included with minimal text
    - text_and_images: Both document text and images are included
    
    For image-based modes, the task will automatically select up to 5 representative
    images from each document, using the Page model's get_image_url method with 50%
    scaling to optimize for performance.
    
    Args:
        request (HttpRequest): The request object containing POST data
        
    Returns:
        JsonResponse: Response with task_id for tracking progress
        
    Post Parameters:
        prompt (str): The text prompt to send to the model
        prompt_mode (str): One of "text_only", "images_only", or "text_and_images"
        role_description (str): System role description for the AI
        documents (list): List of document IDs to include in the query
        
    Technical Details:
        - Uses Google's Gemini Pro Vision capabilities (or compatible models)
        - Images are downloaded from their URLs before being sent to Gemini
        - Transkribus server provides the images through its API
        - IIIF protocol is used for image scaling when available
    """
    prompt = request.POST.get('prompt')
    prompt_mode = request.POST.get('prompt_mode')
    role_description = request.POST.get('role_description')
    documents = request.POST.getlist('documents')

    return trigger_task(request, query_project_gemini,
                        prompt=prompt,
                        role_description=role_description,
                        documents=documents,
                        prompt_mode=prompt_mode)


def start_query_project_claude(request):
    """
    Trigger an Anthropic Claude query task for the project (text-only).
    
    This function extracts parameters from the request and starts a Celery task
    to process a query using Anthropic Claude models. Note that while the prompt_mode
    parameter is accepted for API consistency, Claude implementation currently
    falls back to text-only mode regardless of the setting.
    
    The function takes the same parameters as other AI query functions for consistency,
    but internally it will convert any multimodal requests to text-only with an
    appropriate warning message in the task log.
    
    Args:
        request (HttpRequest): The request object containing POST data
        
    Returns:
        JsonResponse: Response with task_id for tracking progress
        
    Post Parameters:
        prompt (str): The text prompt to send to the model
        prompt_mode (str): Parameter accepted but internally converted to "text_only"
        role_description (str): System role description for the AI
        documents (list): List of document IDs to include in the query
        
    Implementation Notes:
        - Future versions may support multimodal content when Claude API adds this capability
        - The UI indicates this limitation to users through context variables
        - The task handling automatically converts multimodal requests to text-only
          with appropriate warnings
    """
    prompt = request.POST.get('prompt')
    prompt_mode = request.POST.get('prompt_mode', 'text_only')
    role_description = request.POST.get('role_description')
    documents = request.POST.getlist('documents')

    return trigger_task(request, query_project_claude,
                        prompt=prompt,
                        role_description=role_description,
                        documents=documents,
                        prompt_mode=prompt_mode)


def start_query_project_mistral(request):
    """
    Trigger a Mistral query task for the project (text-only).
    
    This function extracts parameters from the request and starts a Celery task
    to process a query using Mistral models. Note that while the prompt_mode
    parameter is accepted for API consistency, Mistral implementation currently
    falls back to text-only mode regardless of the setting.
    
    The function takes the same parameters as other AI query functions for consistency,
    but internally it will convert any multimodal requests to text-only with an
    appropriate warning message in the task log.
    
    Args:
        request (HttpRequest): The request object containing POST data
        
    Returns:
        JsonResponse: Response with task_id for tracking progress
        
    Post Parameters:
        prompt (str): The text prompt to send to the model
        prompt_mode (str): Parameter accepted but internally converted to "text_only"
        role_description (str): System role description for the AI
        documents (list): List of document IDs to include in the query
        
    Implementation Notes:
        - Future versions may support multimodal content when Mistral API adds this capability
        - The UI indicates this limitation to users through context variables
        - The task handling automatically converts multimodal requests to text-only
          with appropriate warnings
    """
    prompt = request.POST.get('prompt')
    prompt_mode = request.POST.get('prompt_mode', 'text_only')
    role_description = request.POST.get('role_description')
    documents = request.POST.getlist('documents')

    return trigger_task(request, query_project_mistral,
                        prompt=prompt,
                        role_description=role_description,
                        documents=documents,
                        prompt_mode=prompt_mode)


def start_export_documents(request):
    export_type = request.POST.get('export_type')
    export_single_file = request.POST.get('export_single_file')

    return trigger_task(request, export_documents_task,
                        export_type=export_type,
                        export_single_file=export_single_file)

def start_export_collections(request):
    return trigger_task(request, export_collections_task)

def start_export_project(request):
    include_dictionaries = request.POST.get('include_dictionaries', False)
    include_media_files = request.POST.get('include_media_files', False)
    return trigger_task(request, export_project_task,
                        include_dictionaries=include_dictionaries,
                        include_media_files=include_media_files)

def start_export_to_zenodo(request):
    return trigger_task(request, export_to_zenodo_task)
"""This module contains the views for triggering the Celery tasks."""
import os
import uuid

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse

from twf.models import Prompt
from twf.tasks.document_tasks import search_openai_for_docs, search_gemini_for_docs, search_claude_for_docs
from twf.tasks.structure_tasks import extract_zip_export_task
from twf.tasks.dictionary_tasks import search_gnd_entries, search_geonames_entries, search_wikidata_entries, \
    search_openai_entries, search_gnd_entry, search_geonames_entry, search_wikidata_entry, search_openai_entry, \
    search_claude_entries, search_gemini_entries, search_claude_entry, search_gemini_entry
from twf.tasks.metadata_tasks import load_sheets_metadata, load_json_metadata
from twf.tasks.tags_tasks import create_page_tags
from twf.tasks.project_tasks import copy_project
from twf.tasks.export_tasks import export_documents_task, export_collections_task, export_project_task, \
    export_to_zenodo_task
from twf.views.views_base import TWFView


def start_extraction(request):
    """Start the extraction process as a Celery task."""
    project = TWFView.s_get_project(request)
    user_id = request.user.id

    # Trigger the task
    task = extract_zip_export_task.delay(project.id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_tags_creation(request):
    """Start the extraction process as a Celery task."""
    project = TWFView.s_get_project(request)
    user_id = request.user.id

    # Trigger the task
    task = create_page_tags.delay(project.id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_gnd_batch(request):
    """Start the GND requests as a Celery task."""
    if request.method == "GET":  # Use GET to receive serialized form data
        project = TWFView.s_get_project(request)
        dictionary_id = request.GET.get('dictionary')
        user_id = request.user.id
        earliest_birth_year = request.GET.get('earliest_birth_year', None)
        latest_birth_year = request.GET.get('latest_birth_year', None)
        show_empty = request.GET.get('show_empty', False)
        if show_empty == 'on':
            show_empty = True
        if earliest_birth_year != '':
            earliest_birth_year = int(earliest_birth_year)
        if latest_birth_year != '':
            latest_birth_year = int(latest_birth_year)

        print(f"earliest_birth_year: {earliest_birth_year}")
        print(f"latest_birth_year: {latest_birth_year}")
        print(f"show_empty: {show_empty}")

        if not dictionary_id:
            return JsonResponse({'status': 'error', 'message': 'Dictionary ID is required.'}, status=400)

        # Trigger the task
        task = search_gnd_entries.delay(project.id, dictionary_id, user_id,
                                        earliest_birth_year, latest_birth_year, show_empty)

        return JsonResponse({'status': 'success', 'task_id': task.id})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def start_geonames_batch(request):
    """Start the GeoNames requests as a Celery task."""
    if request.method == "GET":  # Use GET to receive serialized form data
        project = TWFView.s_get_project(request)
        geonames_credentials = project.get_credentials('geonames')

        # Retrieve form data from POST request
        dictionary_id = request.GET.get('dictionary')
        user_id = request.user.id
        geonames_username = geonames_credentials.get('username')
        country_restriction = request.GET.get('only_search_in')
        similarity_threshold = request.GET.get('similarity_threshold')

        # Validate GeoNames username
        if not geonames_username:
            return JsonResponse({'status': 'error', 'message': 'No GeoNames username set'})

        # Trigger the task
        task = search_geonames_entries.delay(
            project.id, dictionary_id, user_id, geonames_username,
            country_restriction, similarity_threshold
        )
        return JsonResponse({'status': 'success', 'task_id': task.id})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def start_wikidata_batch(request):
    """Start the GND requests as a Celery task."""
    if request.method == "GET":  # Use GET to receive serialized form data
        project = TWFView.s_get_project(request)
        dictionary_id = request.GET.get('dictionary')
        user_id = request.user.id

        entity_type = request.GET.get('entity_type')
        language = request.GET.get('language')

        # Trigger the task
        task = search_wikidata_entries.delay(project.id, dictionary_id, user_id, entity_type, language)
        return JsonResponse({'status': 'success', 'task_id': task.id})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def start_openai_batch(request):
    """Start the GND requests as a Celery task."""
    if request.method == "GET":  # Use GET to receive serialized form data
        project = TWFView.s_get_project(request)
        dictionary_id = request.GET.get('dictionary')
        user_id = request.user.id

        prompt = request.GET.get('prompt')

        # Trigger the task
        task = search_openai_entries.delay(project.id, dictionary_id, user_id, prompt)
        return JsonResponse({'status': 'success', 'task_id': task.id})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def start_claude_batch(request):
    """Start the GND requests as a Celery task."""
    if request.method == "GET":  # Use GET to receive serialized form data
        project = TWFView.s_get_project(request)
        dictionary_id = request.GET.get('dictionary')
        user_id = request.user.id

        prompt = request.GET.get('prompt')

        # Trigger the task
        task = search_claude_entries.delay(project.id, dictionary_id, user_id, prompt)
        return JsonResponse({'status': 'success', 'task_id': task.id})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def start_gemini_batch(request):
    """Start the GND requests as a Celery task."""
    if request.method == "GET":  # Use GET to receive serialized form data
        project = TWFView.s_get_project(request)
        dictionary_id = request.GET.get('dictionary')
        user_id = request.user.id

        prompt = request.GET.get('prompt')

        # Trigger the task
        task = search_gemini_entries.delay(project.id, dictionary_id, user_id, prompt)
        return JsonResponse({'status': 'success', 'task_id': task.id})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def start_gnd_request(request):
    """Start the GND requests as a Celery task."""
    project = TWFView.s_get_project(request)
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id

    # Trigger the task
    task = search_gnd_entry.delay(project, dictionary_id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_geonames_request(request):
    """Start the GND requests as a Celery task."""
    project = TWFView.s_get_project(request)
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id

    # Trigger the task
    task = search_geonames_entry.delay(project, dictionary_id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_wikidata_request(request):
    """Start the GND requests as a Celery task."""
    project = TWFView.s_get_project(request)
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id

    # Trigger the task
    task = search_wikidata_entry.delay(project, dictionary_id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_openai_request(request):
    """Start the GND requests as a Celery task."""
    project = TWFView.s_get_project(request)
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id

    # Trigger the task
    task = search_openai_entry.delay(project, dictionary_id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_claude_request(request):
    """Start the GND requests as a Celery task."""
    project = TWFView.s_get_project(request)
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id

    # Trigger the task
    task = search_claude_entry.delay(project, dictionary_id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_gemini_request(request):
    """Start the GND requests as a Celery task."""
    project = TWFView.s_get_project(request)
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id

    # Trigger the task
    task = search_gemini_entry.delay(project, dictionary_id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_openai_doc_batch(request):
    """ Start the OpenAI requests as a Celery task."""
    return start_ai_doc_batch(request, search_openai_for_docs)


def start_gemini_doc_batch(request):
    """ Start the Gemini requests as a Celery task."""
    return start_ai_doc_batch(request, search_gemini_for_docs)


def start_claude_doc_batch(request):
    """ Start the Claude requests as a Celery task."""
    return start_ai_doc_batch(request, search_claude_for_docs)


def start_ai_doc_batch(request, task_function_name):
    """ Start the AI requests as a Celery task."""
    project = TWFView.s_get_project(request)
    user_id = request.user.id
    prompt = request.POST.get('prompt')
    role_description = request.POST.get('role_description')
    save_prompt = request.POST.get('save_prompt')

    if save_prompt:
        prompt = Prompt(project=project, prompt=prompt, system_role=role_description)
        prompt.save(current_user=request.user)

    # Trigger the task
    task = task_function_name.delay(project.id, user_id, prompt, role_description)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_json_metadata(request):
    """Start the metadata loading from JSON as a Celery task."""
    project = TWFView.s_get_project(request)
    user_id = request.user.id

    data_target_type = request.POST.get('data_target_type')
    json_data_key = request.POST.get('json_data_key')
    match_to_field = request.POST.get('match_to_field')

    data_file = request.FILES.get('data_file')

    if data_file:
        # Generate a unique filename
        file_name = f"metadata_upload_{uuid.uuid4().hex}.json"
        file_path = os.path.join(settings.MEDIA_ROOT, "temp", file_name)

        # Ensure the temp directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save the file
        with default_storage.open(file_path, 'wb') as destination:
            for chunk in data_file.chunks():
                destination.write(chunk)

    else:
        return JsonResponse({'status': 'error', 'message': 'No file uploaded'}, status=400)

    # Trigger the task with the file path
    task = load_json_metadata.delay(project.id, user_id, file_path, data_target_type, json_data_key, match_to_field)

    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_sheet_metadata(request):
    """Start the metadata loading from Google Sheets as a Celery task."""
    project = TWFView.s_get_project(request)
    user_id = request.user.id

    # Trigger the task
    task = load_sheets_metadata.delay(project.id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_test_export_task(request):
    """Start the test export task."""
    project = TWFView.s_get_project(request)
    user_id = request.user.id

    # Trigger the task
    task = extract_zip_export_task.delay(project.id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_openai_collection_batch(request):
    pass

def start_openai_collection_request(request):
    pass

def start_copy_project(request):
    project = TWFView.s_get_project(request)
    user_id = request.user.id

    new_project_name = request.GET.get('new_project_name')

    # Trigger the task
    task = copy_project.delay(project.id, user_id, new_project_name)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_export_documents(request):
    project = TWFView.s_get_project(request)
    user_id = request.user.id

    task = export_documents_task.delay(project.id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})

def start_export_collections(request):
    project = TWFView.s_get_project(request)
    user_id = request.user.id

    task = export_collections_task.delay(project.id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})

def start_export_project(request):
    project = TWFView.s_get_project(request)
    user_id = request.user.id

    task = export_project_task.delay(project.id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})

def start_export_to_zenodo(request):
    project = TWFView.s_get_project(request)
    user_id = request.user.id

    task = export_to_zenodo_task.delay(project.id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})
from django.http import JsonResponse

from twf.tasks.document_tasks import search_openai_for_docs, search_gemini_for_docs, search_claude_for_docs
from twf.tasks.structure_tasks import extract_zip_export_task
from twf.tasks.dictionary_tasks import search_gnd_entries, search_geonames_entries, search_wikidata_entries, \
    search_openai_entries, search_gnd_entry, search_geonames_entry, search_wikidata_entry, search_openai_entry
from twf.tasks.tags_tasks import create_page_tags
from twf.views.views_base import TWFView


def start_extraction(request):
    """Start the extraction process as a Celery task."""
    project = TWFView.s_get_project(request)
    user_id = request.user.id

    # Trigger the task
    task = extract_zip_export_task.delay(project.id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_task_creation(request):
    """Start the extraction process as a Celery task."""
    project = TWFView.s_get_project(request)
    user_id = request.user.id

    # Trigger the task
    task = create_page_tags.delay(project.id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_gnd_batch(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id

    # Trigger the task
    task = search_gnd_entries.delay(dictionary_id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_geonames_batch(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id
    project = TWFView.s_get_project(request)

    geonames_username = project.geonames_username
    country_restriction = request.GET.get('only_search_in')
    similarity_threshold = request.GET.get('similarity_threshold')

    if geonames_username is None or geonames_username == '':
        return JsonResponse({'status': 'error', 'message': 'No GeoNames username set'})

    # Trigger the task
    task = search_geonames_entries.delay(dictionary_id, user_id, geonames_username,
                                         country_restriction, similarity_threshold)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_wikidata_batch(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id

    entity_type = request.GET.get('entity_type')
    language = request.GET.get('language')

    # Trigger the task
    task = search_wikidata_entries.delay(dictionary_id, user_id, entity_type, language)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_openai_batch(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id

    # Trigger the task
    task = search_openai_entries.delay(dictionary_id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_gnd_request(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id

    # Trigger the task
    task = search_gnd_entry.delay(dictionary_id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_geonames_request(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id

    # Trigger the task
    task = search_geonames_entry.delay(dictionary_id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_wikidata_request(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id

    # Trigger the task
    task = search_wikidata_entry.delay(dictionary_id, user_id)
    return JsonResponse({'status': 'success', 'task_id': task.id})


def start_openai_request(request):
    """Start the GND requests as a Celery task."""
    dictionary_id = request.GET.get('dictionary_id')
    user_id = request.user.id

    # Trigger the task
    task = search_openai_entry.delay(dictionary_id, user_id)
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
    prompt = request.GET.get('prompt')
    role_description = request.GET.get('role_description')

    # Trigger the task
    task = task_function_name.delay(project.id, user_id, prompt, role_description)
    return JsonResponse({'status': 'success', 'task_id': task.id})
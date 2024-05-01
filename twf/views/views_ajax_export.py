""" This module contains the functions for the AJAX requests of the setup page. """
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from twf.models import Project
from twf.transkribus_collector import get_session_id, start_export, get_export_status


def unpack_request(request):
    """ Unpacks the request and returns the session_id and project. """
    project_id = request.POST.get('project_id')
    username = request.POST.get('username')
    password = request.POST.get('password')

    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        project = None

    session_id = get_session_id(username, password)
    return session_id, project


@require_http_methods(["POST"])
@csrf_exempt
def ajax_transkribus_request_export(request):
    """ Handles the request to start an export job."""

    session_id, project = unpack_request(request)
    if session_id is None:
        return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
    if project is None:
        return JsonResponse({'status': 'error', 'message': 'Invalid project ID'}, status=404)

    export_job_id = start_export(session_id, project.collection_id)
    if export_job_id is None:
        return JsonResponse({'status': 'error', 'message': 'Failed to start export'}, status=500)

    project.transkribus_job_id = export_job_id
    project.save(current_user=request.user)
    return JsonResponse({'status': 'success', 'job_id': export_job_id}, status=200)


@require_http_methods(["POST"])
@csrf_exempt
def ajax_transkribus_request_export_status(request):
    """ Handles the request to get the status of an export job."""

    session_id, project = unpack_request(request)
    if session_id is None:
        return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
    if project is None:
        return JsonResponse({'status': 'error', 'message': 'Invalid project ID'}, status=404)

    status = get_export_status(session_id, project.transkribus_job_id)

    if status is None:
        return JsonResponse({'status': 'error', 'message': 'Failed to get export status'}, status=500)

    if "state" in status and status["state"] == "FINISHED":
        project.job_download_url = status["result"]
        project.save(current_user=request.user)

    return JsonResponse({'status': 'success', 'data': status}, status=200)

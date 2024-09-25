import logging

from celery.result import AsyncResult
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone

from twf.models import Task

logger = logging.getLogger(__name__)


def task_status_view(request, task_id):
    try:
        # Get the task result by its task_id
        task_result = AsyncResult(task_id)

        # If the task is in progress, return the progress meta information
        if task_result.state == 'PROGRESS':
            response_data = {
                'status': 'PROGRESS',
                'current': task_result.info.get('current', 0),  # Current progress step
                'total': task_result.info.get('total', 1),  # Total steps
                'progress': (task_result.info.get('current', 0) / task_result.info.get('total', 1)) * 100,
                'text': task_result.info.get('text', '')
                # Progress percentage
            }

        # If the task is completed, return the result
        elif task_result.state == 'SUCCESS':
            response_data = {
                'status': 'SUCCESS',
                'result': task_result.result
            }

        # If the task has failed, return the error message
        elif task_result.state == 'FAILURE':
            response_data = {
                'status': 'FAILURE',
                'error': str(task_result.info) if isinstance(task_result.info, Exception) else task_result.info
            }

        # Handle other states (PENDING, REVOKED, etc.)
        else:
            response_data = {
                'status': task_result.state
            }

        # Return the response as JSON
        return JsonResponse(response_data)

    except Exception as e:
        # Catch any other unexpected exceptions and return as error
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def task_cancel_view(request, task_id):
    try:
        task = Task.objects.get(task_id=task_id)
        AsyncResult(task_id).revoke(terminate=True)
        task.status = 'CANCELED'
        task.end_time = timezone.now()
        task.save()
        return JsonResponse({'status': 'success', 'message': 'Task canceled'})
    except Task.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Task not found'}, status=404)


def task_remove_view(request, pk):
    """Remove a task from the database. """
    try:
        task = Task.objects.get(pk=pk)
        task.delete()
        messages.success(request, 'Task removed successfully.')
        # return to the task list page
        return redirect('twf:project_task_monitor')
    except Task.DoesNotExist:
        messages.error(request, 'Task not found.')
        return redirect('twf:project_task_monitor')

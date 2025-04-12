"""Views for creating, reading, updating, and deleting projects."""
from celery.result import AsyncResult
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone

from twf.models import Project, PageTag, Task
from twf.permissions import check_permission
from twf.tasks.instant_tasks import save_instant_task_delete_all_documents, save_instant_task_delete_all_tags, \
    save_instant_task_delete_all_collections
from twf.views.views_base import TWFView, get_referrer_or_default


def delete_all_documents(request):
    """Delete all documents.
    This will also delete all pages, page tags, and annotations."""
    project = TWFView.s_get_project(request)

    if not check_permission(request.user, "delete_all_documents", project):
        messages.error(request, "You do not have permission to delete all documents.")
        return redirect('twf:project_reset')

    project.documents.all().delete()

    save_instant_task_delete_all_documents(project, request.user)

    messages.success(request, "All documents deleted.")
    return redirect('twf:project_reset')


def delete_all_tags(request):
    """Delete all tags.
    This will also delete all page tags."""
    project = TWFView.s_get_project(request)

    if not check_permission(request.user, "delete_all_tags", project):
        messages.error(request, "You do not have permission to delete all tags.")
        return redirect('twf:project_reset')

    PageTag.objects.filter(page__document__project=project).select_related("page", "page__document").delete()

    save_instant_task_delete_all_tags(project, request.user)
    messages.success(request, "All tags deleted.")

    return redirect('twf:project_reset')


def delete_all_collections(request):
    """Delete all collections.
    This will also delete all collection items and annotations."""

    project = TWFView.s_get_project(request)

    if not check_permission(request.user, "delete_all_collections", project):
        messages.error(request, "You do not have permission to delete all collections.")
        return redirect('twf:project_reset')

    project.collections.all().delete()

    save_instant_task_delete_all_collections(project, request.user)
    messages.success(request, "All collections deleted.")

    return redirect('twf:project_reset')

def select_project(request, pk):
    """Select a project."""
    request.session['project_id'] = pk
    return redirect('twf:project_overview')


def delete_project(request, pk):
    """Delete a project."""

    try:
        project = Project.objects.get(pk=pk)
        if check_permission(request.user, "delete_project", project):
            project.delete()
            messages.success(request, 'Project has been deleted.')
        else:
            messages.error(request, 'You do not have the required permissions to delete this project.')
    except Project.DoesNotExist:
        messages.error(request, 'Project does not exist.')

    return get_referrer_or_default(request, default='twf:project_management')


def close_project(request, pk):
    """Close a project."""
    try:
        project = Project.objects.get(pk=pk)

        if check_permission(request.user,
                            "close_project",
                            project):
            project.status = 'closed'
            project.save(current_user=request.user)
            messages.success(request, 'Project has been closed.')
        else:
            messages.error(request, 'You do not have the required permissions to close this project.')

    except Project.DoesNotExist:
        messages.error(request, 'Project does not exist.')

    return get_referrer_or_default(request, default='twf:project_management')


def reopen_project(request, pk):
    """Reopen a closed project."""
    try:
        project = Project.objects.get(pk=pk)

        if check_permission(request.user, "close_project", project):
            project.status = 'open'
            project.save(current_user=request.user)
            messages.success(request, 'Project has been reopened.')
        else:
            messages.error(request, 'You do not have the required permissions to reopen this project.')

    except Project.DoesNotExist:
        messages.error(request, 'Project does not exist.')

    return get_referrer_or_default(request, default='twf:project_management')


def delete_prompt(request, pk):
    """Delete a prompt."""
    project = TWFView.s_get_project(request)

    if not check_permission(request.user, "delete_prompt", project):
        messages.error(request, "You do not have permission to delete a prompt.")
        return get_referrer_or_default(request, default='twf:project_prompts')

    try:
        prompt = project.prompts.get(pk=pk)
        prompt.delete()
        messages.success(request, "Prompt deleted.")
    except project.prompts.model.DoesNotExist:
        messages.error(request, "Prompt does not exist.")

    return get_referrer_or_default(request, default='twf:project_prompts')


def delete_note(request, pk):
    """Delete a note."""
    project = TWFView.s_get_project(request)

    if not check_permission(request.user, "delete_note", project):
        messages.error(request, "You do not have permission to delete a note.")
        return get_referrer_or_default(request, default='twf:project_notes')

    try:
        note = project.notes.get(pk=pk)
        note.delete()
        messages.success(request, "Note deleted.")
    except project.notes.model.DoesNotExist:
        messages.error(request, "Note does not exist.")

    return get_referrer_or_default(request, default='twf:project_notes')


def task_cancel_view(request, task_id):
    """Cancel a task by its task_id. """
    try:
        task = Task.objects.get(pk=task_id)
        AsyncResult(task.celery_task_id).revoke(terminate=True)
        task.status = 'CANCELED'
        task.end_time = timezone.now()
        task.save()
        messages.success(request, 'Task cancelled successfully.')
        return get_referrer_or_default(request, default='twf:project_task_monitor')
    except Task.DoesNotExist:
        messages.error(request, 'Task not found.')
        return get_referrer_or_default(request, default='twf:project_task_monitor')


def task_remove_view(request, task_id):
    """Remove a task from the database. """
    try:
        task = Task.objects.get(pk=task_id)

        # Prevent deletion of running tasks
        if task.status in ['STARTED', 'PENDING', 'PROGRESS']:
            messages.error(request, 'Cannot delete a running task. Please cancel it first.')
            return get_referrer_or_default(request, default='twf:project_task_monitor')

        task.delete()
        messages.success(request, 'Task removed successfully.')
        # return to the task list page
        return get_referrer_or_default(request, default='twf:project_task_monitor')
    except Task.DoesNotExist:
        messages.error(request, 'Task not found.')
        return get_referrer_or_default(request, default='twf:project_task_monitor')
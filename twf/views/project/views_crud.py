"""Views for creating, reading, updating, and deleting projects."""
from django.contrib import messages
from django.shortcuts import redirect

from twf.models import PageTag, Project
from twf.permissions import check_permission
from twf.tasks.instant_tasks import save_instant_task_delete_all_documents, save_instant_task_delete_all_tags, \
    save_instant_task_delete_all_collections
from twf.views.views_base import TWFView


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

    return redirect('twf:project_management')

def close_project(request, pk):
    """Close a project."""

    if check_permission(request.user,
                        "close_project",
                        object_id=pk):
        try:
            project = Project.objects.get(pk=pk)
            project.is_closed = True
            project.save(current_user=request.user)
            messages.success(request, 'Project has been closed.')
        except Project.DoesNotExist:
            messages.error(request, 'Project does not exist.')
    else:
        messages.error(request, 'You do not have the required permissions to close this project.')

    return redirect('twf:project_management')
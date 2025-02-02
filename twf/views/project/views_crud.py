from django.contrib import messages
from django.shortcuts import redirect

from twf.models import PageTag
from twf.permissions import check_permission
from twf.tasks.instant_tasks import save_instant_task_delete_all_documents, save_instant_task_delete_all_tags, \
    save_instant_task_delete_all_collections
from twf.views.views_base import TWFView


def delete_all_documents(request):
    """Delete all documents."""
    project = TWFView.s_get_project(request)

    if not check_permission(request.user, "delete_all_documents", project):
        messages.error(request, "You do not have permission to delete all documents.")
        return redirect('twf:project_reset')

    project.documents.all().delete()

    save_instant_task_delete_all_documents(project, request.user)

    messages.success(request, "All documents deleted.")
    return redirect('twf:project_reset')

def delete_all_tags(request):
    """Delete all tags."""
    project = TWFView.s_get_project(request)

    if not check_permission(request.user, "delete_all_tags", project):
        messages.error(request, "You do not have permission to delete all tags.")
        return redirect('twf:project_reset')

    PageTag.objects.filter(page__document__project=project).select_related("page", "page__document").delete()

    save_instant_task_delete_all_tags(project, request.user)
    messages.success(request, "All tags deleted.")

    return redirect('twf:project_reset')

def delete_all_collections(request):
    """Delete all collections."""
    project = TWFView.s_get_project(request)

    if not check_permission(request.user, "delete_all_collections", project):
        messages.error(request, "You do not have permission to delete all collections.")
        return redirect('twf:project_reset')

    project.collections.all().delete()

    save_instant_task_delete_all_collections(project, request.user)
    messages.success(request, "All collections deleted.")

    return redirect('twf:project_reset')

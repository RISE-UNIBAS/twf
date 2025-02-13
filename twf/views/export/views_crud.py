from django.contrib import messages
from django.shortcuts import redirect

from twf.models import Export
from twf.permissions import check_permission
from twf.views.views_base import TWFView


def delete_export(request, pk):
    """Delete an export."""

    project = TWFView.s_get_project(request)

    if not check_permission(request.user, "exports_delete", project):
        messages.error(request, "You do not have permission to delete exports.")
        return redirect('twf:project_reset')

    try:
        export = Export.objects.get(pk=pk)
        export.delete()
        messages.success(request, 'Export deleted successfully.')
    except Export.DoesNotExist:
        messages.error(request, 'Export does not exist.')

    return redirect('twf:export_view_exports')
from django.contrib import messages
from django.shortcuts import redirect

from twf.models import Export, ExportConfiguration
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


def delete_export_configuration(request, pk):
    """Delete an export configuration."""

    project = TWFView.s_get_project(request)

    if not check_permission(request.user, "exports_delete", project):
        messages.error(request, "You do not have permission to delete export configurations.")
        return redirect('twf:project_reset')

    try:
        export_config = ExportConfiguration.objects.get(pk=pk)
        export_config.delete()
        messages.success(request, 'Export configuration deleted successfully.')
    except Export.DoesNotExist:
        messages.error(request, 'Export configuration does not exist.')

    return redirect('twf:export_view_export_confs')
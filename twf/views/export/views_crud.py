from django.contrib import messages
from django.shortcuts import redirect

from twf.clients.zenodo_client import create_new_deposition
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


def disconnect_zenodo(request):
    """Disconnect Zenodo from the project."""

    project = TWFView.s_get_project(request)

    if not check_permission(request.user, "exports_delete", project):
        messages.error(request, "You do not have permission to disconnect Zenodo.")
        return redirect('twf:export_to_zenodo')

    try:
        project.zenodo_deposition_id = None
        project.save()
        messages.success(request, 'Zenodo disconnected successfully.')
    except Exception as e:
        messages.error(request, f'Error disconnecting Zenodo: {str(e)}')

    return redirect('twf:export_to_zenodo')


def connect_zenodo(request, deposition_id):
    """Connect Zenodo to the project."""

    project = TWFView.s_get_project(request)

    if not check_permission(request.user, "exports_delete", project):
        messages.error(request, "You do not have permission to connect Zenodo.")
        return redirect('twf:export_to_zenodo')

    project.zenodo_deposition_id = deposition_id
    project.save(current_user=request.user)

    messages.success(request, 'Zenodo connected successfully.')
    return redirect('twf:export_to_zenodo')


def create_zenodo_connection(request):
    """Connect Zenodo to the project."""

    project = TWFView.s_get_project(request)

    if not check_permission(request.user, "exports_delete", project):
        messages.error(request, "You do not have permission to connect Zenodo.")
        return redirect('twf:export_to_zenodo')

    try:
        deposition = create_new_deposition(project)
        print("DEPO:", deposition)
        project.zenodo_deposition_id = deposition['id']
        project.save(current_user=request.user)
        messages.success(request, 'Zenodo connected successfully.')
    except Exception as e:
        messages.error(request, f'Error connecting Zenodo: {str(e)}')

    return redirect('twf:export_to_zenodo')
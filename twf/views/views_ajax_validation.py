from django.http import JsonResponse

from twf.forms.dynamic_forms import DynamicForm
from twf.views.views_base import TWFView


def validate_page_field(request):
    """Ajax view to validate a page metadata field."""
    field_name = request.POST.get('field_name')
    field_value = request.POST.get('field_value')

    project = TWFView.s_get_project(request)
    is_valid = DynamicForm.validation_logic(field_value, project.page_metadata_fields[field_name])
    return JsonResponse({'is_valid': is_valid})


def validate_document_field(request):
    """Ajax view to validate a document metadata field."""
    field_name = request.POST.get('field_name')
    field_value = request.POST.get('field_value')

    project = TWFView.s_get_project(request)
    is_valid = DynamicForm.validation_logic(field_value, project.document_metadata_fields[field_name])
    return JsonResponse({'is_valid': is_valid})
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import FormView

from twf.forms.export_forms import ExportConfigForm
from twf.views.export.export_utils import create_data, flatten_dict_keys
from twf.views.project.views_project import TWFProjectView
from twf.views.views_base import TWFView


class TWFExportView(LoginRequiredMixin, TWFView):
    template_name = "twf/export/export_documents.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_navigation_index(self):
        return 7

    def get_sub_navigation(self):
        sub_nav = [

        ]
        return sub_nav


class TWFExportDocumentsView(FormView, TWFExportView):
    template_name = "twf/export/export_documents.html"
    page_title = 'Export Data'
    form_class = ExportConfigForm
    success_url = reverse_lazy('twf:project_export_documents')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()

        sample_document = project.documents.order_by('?').first()
        transformed_metadata, warnings = create_data(sample_document, return_warnings=True)
        context['json_data'] = transformed_metadata
        context['available_doc_data'] = flatten_dict_keys(sample_document.metadata)
        context['available_page_data'] = (flatten_dict_keys(sample_document.pages.first().parsed_data) +
                                          flatten_dict_keys(sample_document.pages.first().metadata))

        context['warnings'] = warnings
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_project()
        return kwargs

    def form_valid(self, form):
        form.save()

        if 'export' in form.cleaned_data:
            project = self.get_project()
            # Start the export process using Celery
            # task = export_data_task.delay(project.id, export_type, export_format, schema)
            # Return the task ID for progress tracking (assuming this view is called via AJAX)
            return JsonResponse({'status': 'success', 'task_id': 0})
        return super().form_valid(form)


    def form_invalid(self, form):
        # If the form is invalid, return the errors
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


class TWFExportCollectionsView(FormView, TWFExportView):
    template_name = "twf/export/export_collections.html"
    page_title = 'Export Collections'
    form_class = ExportConfigForm
    success_url = reverse_lazy('twf:project_export_collections')

    def form_valid(self, form):
        project = self.get_project()
        # Start the export process using Celery
        # task = export_data_task.delay(project.id, export_type, export_format, schema)
        # Return the task ID for progress tracking (assuming this view is called via AJAX)
        return JsonResponse({'status': 'success', 'task_id': 0}) # task.id})

    def form_invalid(self, form):
        # If the form is invalid, return the errors
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


class TWFExportProjectView(TWFExportView):
    template_name = "twf/export/export_project.html"
    page_title = 'Export Project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

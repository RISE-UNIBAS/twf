"""Views for exporting data from the TWF."""
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.views.generic import FormView

from twf.forms.dictionaries.dictionary_forms import DictionaryImportForm
from twf.forms.project.project_forms import ExportSettingsForm
from twf.utils.create_export_utils import create_data, flatten_dict_keys
from twf.utils.export_utils import get_dictionary_json_data, get_dictionary_csv_data, get_tags_json_data, \
    get_tags_csv_data
from twf.views.views_base import TWFView


class TWFExportView(LoginRequiredMixin, TWFView):
    """Base view for all export views."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_navigation_index(self):
        return 7

    def get_sub_navigation(self):
        sub_nav = [
            {
                'name': 'Overview',
                'options': [
                    {'url': reverse_lazy('twf:export_overview'), 'value': 'Export Overview'},
                ]
            },
            {
                'name': 'Import Data',
                'options': [
                    {'url': reverse_lazy('twf:import_dictionaries'), 'value': 'Import Dictionaries'},
                ]
            },
            {
                'name': 'Export Data',
                'options': [
                    {'url': reverse_lazy('twf:export_documents'), 'value': 'Export Documents'},
                    {'url': reverse_lazy('twf:export_collections'), 'value': 'Export Collections'},
                    {'url': reverse_lazy('twf:export_dictionaries'), 'value': 'Export Dictionaries'},
                    {'url': reverse_lazy('twf:export_tags'), 'value': 'Export Tags'},
                ]
            },

            {
                'name': 'Export Project',
                'options': [
                    {'url': reverse_lazy('twf:export_project'), 'value': 'Export Project'},
                ]
            },
        ]
        return sub_nav


class TWFExportOverviewView(TWFExportView):
    """View for the export overview."""

    template_name = "twf/export/export_overview.html"
    page_title = 'Export Overview'

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        return context


class TWFExportDocumentsView(FormView, TWFExportView):
    """View for exporting documents."""

    template_name = "twf/export/export_documents.html"
    page_title = 'Export Data'
    form_class = ExportSettingsForm
    success_url = reverse_lazy('twf:export_documents')

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        project = self.get_project()

        sample_document = project.documents.order_by('?').first()
        if not sample_document:
            return context
        
        transformed_metadata, warnings = create_data(sample_document, return_warnings=True)
        context['json_data'] = transformed_metadata
        doc_key_list = []
        for key in sample_document.metadata:
            doc_key_list.append({"group": key, "data": sample_document.metadata[key]})
        context['doc_key_list'] = doc_key_list
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
        print("Forms Saved")
        form.save()

        if 'export' in form.cleaned_data:
            project = self.get_project()
            # Start the export process using Celery
            # task = export_data_task.delay(project.id, export_type, export_format, schema)
            # Return the task ID for progress tracking (assuming this view is called via AJAX)
            print('Exporting data...')
        return super().form_valid(form)


    def form_invalid(self, form):
        # If the form is invalid, return the errors
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


class TWFExportCollectionsView(FormView, TWFExportView):
    """View for exporting collections."""
    template_name = "twf/export/export_collections.html"
    page_title = 'Export Collections'
    form_class = ExportSettingsForm
    success_url = reverse_lazy('twf:export_collections')

    def form_valid(self, form):
        project = self.get_project()
        # Start the export process using Celery
        # task = export_data_task.delay(project.id, export_type, export_format, schema)
        # Return the task ID for progress tracking (assuming this view is called via AJAX)
        return JsonResponse({'status': 'success', 'task_id': 0}) # task.id})

    def form_invalid(self, form):
        # If the form is invalid, return the errors
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


class TWFExportDictionariesView(TWFExportView):
    """View for exporting dictionaries."""
    template_name = "twf/export/export_dictionaries.html"
    page_title = 'Export Dictionaries'

    def post(self, request, *args, **kwargs):
        """Handle the POST request."""
        pk = request.POST.get('dictionary_id', 0)
        if "export_json" in request.POST:
            json_data = get_dictionary_json_data(pk)
            json_str = json.dumps(json_data, indent=4)
            filename = f'dictionary_{pk}.json'
            response = HttpResponse(json_str, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        elif "export_json_w_uses" in request.POST:
            json_data = get_dictionary_json_data(pk, include_uses=True)
            json_str = json.dumps(json_data, indent=4)
            filename = f'dictionary_{pk}_with_uses.json'
            response = HttpResponse(json_str, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        elif "export_simple_csv" in request.POST:
            csv_data = get_dictionary_csv_data(pk, include_metadata=False, include_uses=False)
            filename = f'dictionary_simple_{pk}.csv'
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        elif "export_csv" in request.POST:
            csv_data = get_dictionary_csv_data(pk, include_metadata=True, include_uses=False)
            filename = f'dictionary_{pk}.csv'
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        elif "export_csv_w_uses" in request.POST:
            csv_data = get_dictionary_csv_data(pk, include_metadata=True, include_uses=True)
            filename = f'dictionary_{pk}_with_uses.csv'
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            response = redirect('twf:export_dictionaries')

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TWFExportTagsView(TWFExportView):
    """View for exporting tags."""

    template_name = "twf/export/export_tags.html"
    page_title = 'Export Tags'

    def post(self, request, *args, **kwargs):
        """Handle the POST request."""
        pk = self.get_project().id
        if "export_json" in request.POST:
            json_data = get_tags_json_data(pk)
            json_str = json.dumps(json_data, indent=4)
            filename = f'tags_{pk}.json'
            response = HttpResponse(json_str, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        elif "export_csv" in request.POST:
            csv_data = get_tags_csv_data(pk)
            filename = f'tags_{pk}.csv'
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            response = redirect('twf:export_tags')

        return response

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        return context


class TWFExportProjectView(TWFExportView):
    """View for exporting a project"""

    template_name = "twf/export/export_project.html"
    page_title = 'Export Project'

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        return context


class TWFImportDictionaryView(FormView, TWFExportView):
    """View for importing a dictionary."""

    template_name = 'twf/export/import_dictionaries.html'
    page_title = 'Import Dictionary'
    form_class = DictionaryImportForm   # TODO Move form class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

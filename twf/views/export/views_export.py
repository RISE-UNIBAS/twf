import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.views.generic import FormView

from twf.forms.dictionaries.dictionary_forms import DictionaryImportForm
from twf.forms.export_forms import ExportConfigForm
from twf.models import Dictionary
from twf.export_utils import create_data, flatten_dict_keys
from twf.views.views_base import TWFView


class TWFExportView(LoginRequiredMixin, TWFView):

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
    template_name = "twf/export/export_overview.html"
    page_title = 'Export Overview'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TWFExportDocumentsView(FormView, TWFExportView):
    template_name = "twf/export/export_documents.html"
    page_title = 'Export Data'
    form_class = ExportConfigForm
    success_url = reverse_lazy('twf:export_documents')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()

        sample_document = project.documents.order_by('?').first()
        if not sample_document:
            return context
        
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
    template_name = "twf/export/export_dictionaries.html"
    page_title = 'Export Dictionaries'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TWFExportDictionaryView(TWFExportView):
    """Export a dictionary."""
    template_name = 'twf/export/export_dictionary.html'
    page_title = 'Export Dictionary'

    def post(self, request, *args, **kwargs):
        """Handle the POST request."""
        if "export_json" in request.POST:
            json_data = self.get_json_data()
            json_str = json.dumps(json_data, indent=4)
            response = HttpResponse(json_str, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="data.json"'
        elif "export_csv" in request.POST:
            csv_data = self.get_csv_data()
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="data.csv"'
        else:
            response = redirect('twf:dictionary', pk=self.kwargs.get('pk'))

        return response

    def get_json_data(self):
        """Get the JSON data for the dictionary."""
        dictionary = Dictionary.objects.get(pk=self.kwargs.get('pk'))

        json_data = {
            "name": dictionary.label,
            "type": dictionary.type,
            "metadata": {},
            "entries": []
        }

        entries = dictionary.entries.all()
        for entry in entries:
            json_data["entries"].append(
                {
                    "label": entry.label,
                    "variations": list(entry.variations.all().values_list('variation', flat=True))
                }
            )
        return json_data

    def get_csv_data(self):
        csv_data = 'entry;variations\n'
        dictionary = Dictionary.objects.get(pk=self.kwargs.get('pk'))
        entries = dictionary.entries.all()
        for entry in entries:
            csv_data += f'{entry.label};'
            variations = entry.variations.all()
            for variation in variations:
                csv_data += f'{variation.variation},'
            csv_data += '\n'
        return csv_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['dictionary'] = Dictionary.objects.get(pk=self.kwargs.get('pk')) if self.kwargs.get('pk') else None
        return context


class TWFExportTagsView(TWFExportView):
    template_name = "twf/export/export_tags.html"
    page_title = 'Export Tags'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TWFExportProjectView(TWFExportView):
    template_name = "twf/export/export_project.html"
    page_title = 'Export Project'

    def get_context_data(self, **kwargs):
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

    def form_valid(self, form):
        return super().form_valid(form)
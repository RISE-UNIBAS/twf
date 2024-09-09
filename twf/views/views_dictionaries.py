"""Views for the dictionary overview and the dictionary entries."""
import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from twf.filters import DictionaryEntryFilter
from twf.forms.batch_forms import GeonamesBatchForm
from twf.forms.dictionary_forms import DictionaryForm, DictionaryEntryForm, DictionaryImportForm
from twf.forms.enrich_forms import EnrichEntryManualForm, EnrichEntryForm
from twf.models import Dictionary, DictionaryEntry, Variation, PageTag, Project
from twf.tables.tables_dictionary import DictionaryTable, DictionaryEntryTable, DictionaryEntryVariationTable
from twf.views.views_base import TWFView


class TWFDictionaryView(LoginRequiredMixin, TWFView):
    """Base view for all dictionary views."""
    template_name = 'twf/dictionaries/overview.html'

    def get_sub_navigation(self):
        """Get the sub navigation."""
        dicts = self.get_dictionaries()
        options = []
        for twf_dict in dicts:
            options.append({'url': reverse('twf:dictionaries_view', kwargs={'pk': twf_dict.pk}),
                            'value': twf_dict.label,
                            'active_on': [
                                reverse('twf:dictionaries_edit', kwargs={'pk': twf_dict.pk}),
                                reverse('twf:dictionaries_export', kwargs={'pk': twf_dict.pk}),
                            ]})

        sub_nav = [
            {
                'name': 'Dictionaries Options',
                'options': [
                    {'url': reverse('twf:dictionaries'), 'value': 'Overview'},
                    {'url': reverse('twf:dictionaries_import'), 'value': 'Import'},
                    {'url': reverse('twf:dictionaries_normalization'), 'value': 'Norm Data Wizard'},
                ]
            },
            {
                'name': 'Dictionaries',
                'options': options
            },
            {
                'name': 'Batch Workflows',
                'options': [
                    {'url': reverse('twf:dictionaries_batch_gnd'), 'value': 'GND'},
                    {'url': reverse('twf:dictionaries_batch_wikidata'), 'value': 'Wikidata'},
                    {'url': reverse('twf:dictionaries_batch_geonames'), 'value': 'Geonames'},
                    {'url': reverse('twf:dictionaries_batch_openai'), 'value': 'Open AI'},
                ]
            }
        ]
        return sub_nav

    def get_dictionaries(self):
        """Get the dictionaries."""
        project = self.get_project()
        return project.selected_dictionaries.all()

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context['navigation']['items'][4]['active'] = True
        return context

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.page_title is None:
            self.page_title = kwargs.get('page_title', 'Project View')


class TWFDictionaryOverviewView(SingleTableView, TWFDictionaryView):
    """View for the dictionary overview. Provides a table of all dictionaries.
    The table is filterable and sortable."""
    template_name = 'twf/dictionaries/overview.html'
    page_title = 'Dictionaries Overview'
    table_class = DictionaryTable
    paginate_by = 10
    model = Dictionary

    def get_queryset(self):
        project = self.get_project()
        return project.selected_dictionaries.all()

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['context_sub_nav'] = {"options": [
            {"url": reverse('twf:dictionaries'), "value": "Overview"},
            {"url": reverse('twf:dictionary_create'), "value": "Create New Dictionary"},
            {"url": reverse('twf:project_settings'),
             "value": mark_safe('<i class="fa-solid fa-arrow-right-from-bracket"></i> Project Settings')},
        ]}
        return context


class TWFDictionaryCreateView(FormView, TWFDictionaryView):
    """Create a new dictionary."""
    template_name = 'twf/dictionaries/create.html'
    form_class = DictionaryForm
    success_url = reverse_lazy('twf:dictionaries')

    def form_valid(self, form):
        # Save the form
        form.instance.save(current_user=self.request.user)
        project = self.get_project()
        project.selected_dictionaries.add(form.instance)
        project.save()

        # Add a success message
        messages.success(self.request, 'Dictionary has been created successfully and has been added to your project.')

        # Redirect to the success URL
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create New Dictionary'
        context['context_sub_nav'] = {"options": [
            {"url": reverse('twf:dictionaries'), "value": "Overview"},
            {"url": reverse('twf:dictionary_create'), "value": "Create New Dictionary"},
            {"url": reverse('twf:project_settings'),
             "value": mark_safe('<i class="fa-solid fa-arrow-right-from-bracket"></i> Project Settings')},
        ]}
        return context


class TWFDictionaryDictionaryView(SingleTableView, FilterView, TWFDictionaryView):
    """View for the dictionary entries. Provides a table of dictionary entries of a single dictionary.
    The table is filterable and sortable."""
    template_name = 'twf/dictionaries/dictionary.html'
    page_title = 'View Dictionary'
    table_class = DictionaryEntryTable
    filterset_class = DictionaryEntryFilter
    paginate_by = 10
    model = DictionaryEntry

    def get_queryset(self):
        queryset = DictionaryEntry.objects.filter(dictionary_id=self.kwargs.get('pk'))
        self.filterset = self.filterset_class(self.request.GET,
                                              queryset=queryset)
        return self.filterset.qs

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['dictionary'] = Dictionary.objects.get(pk=self.kwargs.get('pk'))
        context['filter'] = self.get_filterset(self.filterset_class)
        return context


class TWFDictionaryDictionaryEntryView(SingleTableView, TWFDictionaryView):
    """View for a single dictionary entry."""
    template_name = 'twf/dictionaries/dictionary_entry.html'
    page_title = 'View Dictionary Entry'
    table_class = DictionaryEntryVariationTable

    def get_queryset(self):
        return Variation.objects.filter(entry_id=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['entry'] = DictionaryEntry.objects.get(pk=self.kwargs.get('pk'))
        return context


class TWFDictionaryImportView(FormView, TWFDictionaryView):
    """View for importing a dictionary."""
    template_name = 'twf/dictionaries/import.html'
    page_title = 'Import Dictionary'
    form_class = DictionaryImportForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        return super().form_valid(form)


class TWFDictionaryDictionaryEditView(FormView, TWFDictionaryView):
    """Edit a dictionary."""
    template_name = 'twf/dictionaries/dictionary_edit.html'
    page_title = 'Edit Dictionary'
    form_class = DictionaryForm
    success_url = reverse_lazy('twf:dictionaries')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['dictionary'] = Dictionary.objects.get(pk=self.kwargs.get('pk')) if self.kwargs.get('pk') else None
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.kwargs.get('pk'):
            kwargs['instance'] = Dictionary.objects.get(pk=self.kwargs.get('pk'))
        return kwargs

    def form_valid(self, form):
        # Save the form
        form.instance.save(current_user=self.request.user)
        # Add a success message
        messages.success(self.request, 'Dictionary settings have been updated successfully.')
        # Redirect to the success URL
        return super().form_valid(form)


class TWFDictionaryDictionaryExportView(TWFDictionaryView):
    """Export a dictionary."""
    template_name = 'twf/dictionaries/dictionary_export.html'
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


class TWFDictionaryNormDataView(TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/normalization_wizard.html'
    page_title = 'Normalization Data Wizard'

    def post(self, request, *args, **kwargs):
        if "submit_geonames" in request.POST:
            print('submit_geonames')
        elif "submit_gnd" in request.POST:
            print('submit_gnd')
        elif "submit_wikidata" in request.POST:
            print('submit_wikidata')
        elif "submit_openai" in request.POST:
            print('submit_openai')

        return redirect('twf:dictionaries_normalization')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        dictionaries = self.get_dictionaries()
        context['selected_dict'] = self.request.GET.get('selected_dict', dictionaries[0].type)
        context['next_unenriched_entry'] = self.get_next_unenriched_entry(context['selected_dict'])

        label = context['next_unenriched_entry'].label if context['next_unenriched_entry'] else None
        context['form_manual'] = EnrichEntryManualForm(instance=context['next_unenriched_entry'])
        context['form_geonames'] = EnrichEntryForm(search_term=label, form_name='geonames')
        context['form_gnd'] = EnrichEntryForm(search_term=label, form_name='gnd')
        context['form_wikidata'] = EnrichEntryForm(search_term=label, form_name='wikidata')
        context['form_openai'] = GeonamesBatchForm()

        return context

    def get_next_unenriched_entry(self, selected_dict):
        dictionary = self.get_project().selected_dictionaries.get(type=selected_dict)
        entry = dictionary.entries.filter(authorization_data={}).order_by('modified_at').first()
        return entry


class TWFDictionaryDictionaryEntryEditView(FormView, TWFDictionaryView):
    """Edit a dictionary entry."""
    template_name = 'twf/dictionaries/dictionary_entry_edit.html'
    page_title = 'Edit Dictionary Entry'
    form_class = DictionaryEntryForm
    success_url = reverse_lazy('twf:dictionaries')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.kwargs.get('pk'):
            kwargs['instance'] = DictionaryEntry.objects.get(pk=self.kwargs.get('pk'))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['entry'] = DictionaryEntry.objects.get(pk=self.kwargs.get('pk')) if self.kwargs.get('pk') else None
        return context

    def form_valid(self, form):
        # Save the form
        form.instance.save(current_user=self.request.user)
        # Add a success message
        messages.success(self.request, 'Dictionary Entry settings have been updated successfully.')
        # Redirect to the success URL
        return super().form_valid(form)


class TWFDictionaryBatchGNDView(FormView, TWFDictionaryView):
    """Batch process for GND."""
    template_name = 'twf/dictionaries/batches/geonames.html'
    page_title = 'Batch Geonames'
    form_class = GeonamesBatchForm


class TWFDictionaryBatchWikidataView(FormView, TWFDictionaryView):
    """Batch process for Wikidata."""
    template_name = 'twf/dictionaries/batches/geonames.html'
    page_title = 'Batch Geonames'
    form_class = GeonamesBatchForm


class TWFDictionaryBatchGeonamesView(FormView, TWFDictionaryView):
    """Batch process for Geonames."""
    template_name = 'twf/dictionaries/batches/geonames.html'
    page_title = 'Batch Geonames'
    form_class = GeonamesBatchForm


class TWFDictionaryBatchOpenaiView(FormView, TWFDictionaryView):
    """Batch process for OpenAI."""
    template_name = 'twf/dictionaries/batches/geonames.html'
    page_title = 'Batch Geonames'
    form_class = GeonamesBatchForm


def delete_variation(request, pk):
    """Delete a variation."""
    variation = get_object_or_404(Variation, pk=pk)

    all_page_tags = PageTag.objects.filter(variation=variation)
    for page_tag in all_page_tags:
        page_tag.dictionary_entry = None
        page_tag.save()

    variation.delete()

    messages.success(request, f'Variation {pk} has been deleted.')

    # Get the HTTP referer URL
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)

    return redirect('twf:dictionaries_view', pk=variation.entry.dictionary.pk)


def delete_entry(request, pk):
    """Delete a dictionary entry."""
    entry = get_object_or_404(DictionaryEntry, pk=pk)
    entry.delete()
    messages.success(request, f'Dictionary entry {pk} has been deleted.')

    # Get the HTTP referer URL
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)

    return redirect('twf:dictionary', pk=entry.dictionary.pk)


def skip_entry(request, pk):
    """Skip a dictionary entry."""
    entry = get_object_or_404(DictionaryEntry, pk=pk)
    entry.save(current_user=request.user)
    messages.success(request, f'Dictionary entry {pk} has been skipped.')

    # Get the HTTP referer URL
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)

    return redirect('twf:dictionaries_normalization')

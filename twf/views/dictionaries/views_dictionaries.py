"""Views for the dictionary overview and the dictionary entries."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from twf.filters import DictionaryEntryFilter
from twf.forms.dictionaries.batch_forms import GeonamesBatchForm
from twf.forms.dictionaries.dictionary_forms import DictionaryForm, DictionaryEntryForm
from twf.forms.enrich_forms import EnrichEntryManualForm, EnrichEntryForm
from twf.models import Dictionary, DictionaryEntry, Variation, PageTag
from twf.utils.project_statistics import get_dictionary_statistics
from twf.tables.tables_dictionary import DictionaryTable, DictionaryEntryTable, DictionaryEntryVariationTable
from twf.views.views_base import TWFView


class TWFDictionaryView(LoginRequiredMixin, TWFView):
    """Base view for all dictionary views."""
    template_name = None

    def get_sub_navigation(self):
        """Get the sub navigation."""
        sub_nav = [
            {
                'name': 'Dictionaries Options',
                'options': [
                    {'url': reverse('twf:dictionaries_overview'), 'value': 'Overview'},
                    {'url': reverse('twf:dictionaries'), 'value': 'Dictionaries'},
                    {'url': reverse('twf:dictionaries_add'), 'value': 'Add Dictionaries'},
                    {"url": reverse('twf:dictionary_create'), "value": "Create New Dictionary"},
                ]
            },
            {
                'name': 'Automated Workflows',
                'options': [
                    {'url': reverse('twf:dictionaries_batch_gnd'), 'value': 'GND'},
                    {'url': reverse('twf:dictionaries_batch_wikidata'), 'value': 'Wikidata'},
                    {'url': reverse('twf:dictionaries_batch_geonames'), 'value': 'Geonames'},
                    {'url': reverse('twf:dictionaries_batch_openai'), 'value': 'Open AI'},
                ]
            },
            {
                'name': 'Supervised Workflows',
                'options': [
                    {'url': reverse('twf:dictionaries_request_gnd'), 'value': 'GND'},
                    {'url': reverse('twf:dictionaries_request_wikidata'), 'value': 'Wikidata'},
                    {'url': reverse('twf:dictionaries_request_geonames'), 'value': 'Geonames'},
                    {'url': reverse('twf:dictionaries_request_openai'), 'value': 'Open AI'},
                ]
            },
            {
                'name': 'Manual Workflows',
                'options': [
                    {'url': reverse('twf:dictionaries_normalization'), 'value': 'Manual Assignment'},
                    {'url': reverse('twf:dictionaries_entry_merging'), 'value': 'Merge Entries'},
                ]
            }
        ]
        return sub_nav

    def get_navigation_index(self):
        """Get the navigation index."""
        return 5

    def get_dictionaries(self):
        """Get the dictionaries."""
        project = self.get_project()
        return project.selected_dictionaries.all()

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        return context

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.page_title is None:
            self.page_title = kwargs.get('page_title', 'Dictionary View')


class TWFDictionaryOverviewView(TWFDictionaryView):
    """View for the dictionary overview."""
    template_name = 'twf/dictionaries/overview.html'
    page_title = 'Dictionaries Overview'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        context['dict_stats'] = get_dictionary_statistics(project)
        return context


class TWFDictionaryDictionariesView(SingleTableView, TWFDictionaryView):
    """View for the dictionaries. Provides a table of all dictionaries.
    The table is filterable and sortable."""
    template_name = 'twf/dictionaries/dictionaries.html'
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


class TWFDictionaryAddView(SingleTableView, TWFDictionaryView):
    """View for the dictionary overview."""
    template_name = 'twf/dictionaries/dictionaries_add.html'
    page_title = 'Add Dictionaries'
    table_class = DictionaryTable
    paginate_by = 10
    model = Dictionary

    def get_queryset(self):
        return Dictionary.objects.all()

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)


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
        table = self.table_class(self.object_list, project=self.get_project())
        context['table'] = table

        context['page_title'] = self.page_title
        context['entry'] = DictionaryEntry.objects.get(pk=self.kwargs.get('pk'))
        return context


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
        # context['form_openai'] = GeonamesBatchForm()

        return context

    def get_next_unenriched_entry(self, selected_dict):
        dictionary = self.get_project().selected_dictionaries.get(type=selected_dict)
        entry = dictionary.entries.filter(authorization_data={}).order_by('modified_at').first()
        return entry


class TWFDictionaryMergeEntriesView(TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/merge_entries.html'
    page_title = 'Merge Dictionary Entries'

    def post(self, request, *args, **kwargs):
        """Handle the POST request to merge entries."""
        remaining_entry_id = request.POST.get('remaining_entry')
        merge_entry_id = request.POST.get('merge_entry')

        if not remaining_entry_id or not merge_entry_id:
            messages.error(request, "Both entries must be selected.")
            return redirect(self.request.path)

        if remaining_entry_id == merge_entry_id:
            messages.error(request, "You cannot merge an entry into itself.")
            return redirect(self.request.path)

        try:
            remaining_entry = DictionaryEntry.objects.get(pk=remaining_entry_id)
            merge_entry = DictionaryEntry.objects.get(pk=merge_entry_id)
        except DictionaryEntry.DoesNotExist:
            messages.error(request, "One of the selected entries does not exist.")
            return redirect(self.request.path)

        # Update all PageTags pointing to the entry to merge
        PageTag.objects.filter(dictionary_entry=merge_entry).update(dictionary_entry=remaining_entry)

        # Optionally, merge other fields like notes or authorization data
        remaining_entry.notes += f"\nMerged Notes:\n{merge_entry.notes}"
        for key, value in merge_entry.authorization_data.items():
            if key not in remaining_entry.authorization_data:
                remaining_entry.authorization_data[key] = value

        remaining_entry.save()
        merge_entry.delete()  # Delete the merged entry

        messages.success(request, f"Successfully merged entry '{merge_entry}' into '{remaining_entry}'.")
        return redirect(self.request.path)

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        project = self.get_project()

        # Get all dictionaries in the project
        dictionaries = project.selected_dictionaries.all()

        # Fetch all entries from these dictionaries
        entries = DictionaryEntry.objects.filter(dictionary__in=dictionaries).select_related('dictionary').order_by(
            'dictionary__label', 'label')

        # Add formatted entries for display
        formatted_entries = [
            {'id': entry.id, 'label': f"{entry.dictionary.label} - {entry.label}"}
            for entry in entries
        ]

        context['entries'] = formatted_entries
        return context


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

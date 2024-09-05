from collections import defaultdict
from io import StringIO

import pandas as pd
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from twf.filters import TagFilter
from twf.models import PageTag, DateVariation, Dictionary, DictionaryEntry, Variation
from twf.tables.tables_tags import TagTable, TagDateTable
from twf.views.views_base import TWFView


class TWFTagsView(LoginRequiredMixin, TWFView):
    """Base class for all tag views."""

    template_name = 'twf/project/setup.html'

    def get_sub_navigation(self):
        """Get the sub navigation."""
        sub_nav = [
            {
                'name': 'Tag Data',
                'options': [
                    {'url': reverse('twf:tags_overview'), 'value': 'Overview'},
                    {'url': reverse('twf:tags_all'), 'value': 'All Tags'},
                    {'url': reverse('twf:tags_settings'), 'value': 'Settings'},
                ]
            },
            {
                'name': 'Tag Workflows',
                'options': [
                    {'url': reverse('twf:tags_group'), 'value': 'Grouping Wizard'},
                    {'url': reverse('twf:tags_dates'), 'value': 'Date Tags'},
                ]
            },
            {
                'name': 'Tag Views',
                'options': [
                    {'url': reverse('twf:tags_view_open'), 'value': 'Open Tags'},
                    {'url': reverse('twf:tags_view_parked'), 'value': 'Parked Tags'},
                    {'url': reverse('twf:tags_view_resolved'), 'value': 'Resolved Tags'},
                    {'url': reverse('twf:tags_view_ignored'), 'value': 'Ignored Tags'},
                ]
            },
        ]
        return sub_nav

    def get_tag_types(self):
        """Get the distinct tag types."""
        project = self.get_project()
        distinct_variation_types = (
            PageTag.objects.filter(page__document__project=project)
            .exclude(variation_type__in=self.get_excluded_types())
            .exclude(variation_type__in=self.get_date_types())
            .values('variation_type')
            .annotate(count=Count('variation_type'))
            .order_by('variation_type')
        )

        # Extracting the distinct variation types from the queryset
        distinct_variation_types_list = [item['variation_type'] for item in distinct_variation_types]
        return distinct_variation_types_list

    def get_excluded_types(self):
        """Get the excluded tag types."""
        project = self.get_project()
        try:
            excluded = project.ignored_tag_types["ignored"]
        except KeyError:
            excluded = []
        return excluded

    def get_date_types(self):
        """Get the date tag types."""
        project = self.get_project()
        try:
            date_types = project.ignored_tag_types["dates"]
        except KeyError:
            date_types = []
        return date_types

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context['navigation']['items'][2]['active'] = True
        return context

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        """Check if a project is selected."""
        project = self.get_project()
        if not project:
            messages.warning(self.request, 'Please select a project first.')
            return redirect('twf:home')  # Replace with your redirect URL
        return super().dispatch(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.page_title is None:
            self.page_title = kwargs.get('page_title', 'Tags View')


class TWFTagsOverviewView(TWFTagsView):
    """View for the tags overview."""
    template_name = 'twf/tags/overview.html'
    page_title = 'Tags Overview'

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)

        project = self.get_project()
        total_pagetags = PageTag.objects.filter(page__document__project=project).count()

        # Organize by dictionary type to find the most used entry per type
        entry_counts = PageTag.objects.filter(
            page__document__project=project
        ).values(
            'dictionary_entry__id',
            'dictionary_entry__label',
            'dictionary_entry__dictionary__type'
        ).annotate(
            count=Count('id')
        ).order_by('dictionary_entry__dictionary__type', '-count')

        # Prepare a dictionary to hold top 10 entries for each dictionary type
        top_entries_per_type = defaultdict(list)

        for entry in entry_counts:
            dtype = entry['dictionary_entry__dictionary__type']
            if len(top_entries_per_type[dtype]) < 20 :
                top_entries_per_type[dtype].append(entry)

        # Counting each variation_type in PageTags within a specific project
        variation_type_counts = PageTag.objects.filter(
            page__document__project=project
        ).values('variation_type').annotate(
            count=Count('variation_type')
        ).order_by('-count')

        # Calculate percentages
        for variation in variation_type_counts:
            variation['percentage'] = (variation['count'] / total_pagetags * 100) if total_pagetags > 0 else 0

        # Counting each variation_type in PageTags within a specific project
        variation_type_edit_counts = PageTag.objects.filter(
            page__document__project=project
        ).values('variation_type').annotate(
            count=Count('variation_type')
        ).order_by('-count')

        for variation in variation_type_edit_counts:
            if variation['variation_type'] in self.get_date_types():
                variation['grouped'] = PageTag.objects.filter(page__document__project=project,
                                                              variation_type=variation['variation_type'],
                                                              date_variation_entry__isnull=False).count()

                variation['unresolved'] = PageTag.objects.filter(page__document__project=project,
                                                                 variation_type=variation['variation_type'],
                                                                 date_variation_entry__isnull=True,
                                                                 is_parked=False).count()
            else:
                variation['grouped'] = PageTag.objects.filter(page__document__project=project,
                                                              variation_type=variation['variation_type'],
                                                              dictionary_entry__isnull=False).count()
                variation['unresolved'] = PageTag.objects.filter(page__document__project=project,
                                                                 variation_type=variation['variation_type'],
                                                                 dictionary_entry__isnull=True,
                                                                 is_parked=False).count()

            variation['grouped_percentage'] = (variation['grouped'] / variation['count'] * 100) if variation[
                                                                                                       'count'] > 0 else 0
            variation['parked'] = PageTag.objects.filter(page__document__project=project,
                                                         variation_type=variation['variation_type'],
                                                         is_parked=True).count()
            variation['parked_percentage'] = (variation['parked'] / variation['count'] * 100) if variation[
                                                                                                     'count'] > 0 else 0


        context['stats'] = {
            'most_used_entries_per_type': dict(top_entries_per_type),
            'variation_type_counts': variation_type_counts,
            'variation_type_edit_counts': variation_type_edit_counts
        }

        return context


class TWFTagsGroupView(TWFTagsView):
    """View for the tag grouping wizard."""
    template_name = 'twf/tags/grouping.html'
    page_title = 'Tag Grouping Wizard'

    def post(self, request, *args, **kwargs):
        """Handle the post request."""

        project = self.get_project()

        # Create a new dictionary entry
        if 'create_new' in request.POST:
            new_entry_label = request.POST.get('new_entry_label', None)
            if new_entry_label:
                tag_to_assign = PageTag.objects.get(pk=request.POST.get('tag_id', None))
                dictionary = Dictionary.objects.get(pk=request.POST.get('dictionary_id', None))
                new_entry = DictionaryEntry(dictionary=dictionary, label=new_entry_label,
                                            notes=self.request.POST.get('notes_on_entry', ''))
                new_entry.save(current_user=self.request.user)

                variation = Variation(entry=new_entry, variation=tag_to_assign.variation)
                variation.save(current_user=self.request.user)
                tag_to_assign.dictionary_entry = new_entry
                tag_to_assign.save(current_user=self.request.user)

                number_of_tags = self.save_other_tags(tag_to_assign, new_entry, self.request.user)
                messages.success(request, f'Created "{new_entry_label}" and assigned {number_of_tags+1} tags to it.')
            else:
                messages.error(request, 'Please provide a label for the new entry.')

        # Add to existing dictionary entry
        elif 'add_to_existing' in request.POST:
            selected_entry = request.POST.get('selected_entry', None)
            if selected_entry:
                self.add_variation_to_entry(selected_entry, request.POST.get('tag_id', ''), self.request.user)
            else:
                messages.error(request, 'Please select an entry to add the tag to.')
        # Add to selected existing dictionary entry
        else:
            for key in request.POST.keys():
                if key.startswith('add_to_'):
                    selected_entry = key.replace('add_to_', '')
                    if selected_entry:
                        self.add_variation_to_entry(selected_entry, request.POST.get('tag_id', ''), self.request.user)
                    else:
                        messages.error(request, 'Please select an entry to add the tag to.')
        return super().get(request, *args, **kwargs)

    def add_variation_to_entry(self, entry_id, tag_id, user):
        """Add a variation to an existing dictionary entry."""
        try:
            entry = DictionaryEntry.objects.get(pk=entry_id)
            tag = PageTag.objects.get(pk=tag_id)
            variation = Variation(entry=entry, variation=tag.variation)
            variation.save(current_user=user)
            tag.dictionary_entry = entry
            tag.save(current_user=user)

            number_of_tags =  self.save_other_tags(tag, entry, user)

            messages.success(self.request, f'Variation added to entry {entry.label} (and {number_of_tags} other tags).')
        except DictionaryEntry.DoesNotExist:
            messages.error(self.request, 'Entry does not exist: ' + entry_id)

    @staticmethod
    def save_other_tags(tag, entry, user):
        """Save all other tags of the same variation to the same dictionary entry."""
        other_tags = PageTag.objects.filter(variation=tag.variation, dictionary_entry=None)
        for other_tag in other_tags:
            other_tag.dictionary_entry = entry
            other_tag.save(current_user=user)
        return other_tags.count()

    def get_next_unassigned_tag(self, tag_type):
        """Get the next unassigned tag."""
        project = self.get_project()
        unassigned_tag = PageTag.objects.filter(page__document__project=project,
                                                dictionary_entry=None,
                                                variation_type=tag_type,
                                                is_parked=False).first()
        return unassigned_tag

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        tag_types = self.get_tag_types()
        selected_type = self.request.GET.get('tag_type', tag_types[0])
        dict_type = selected_type
        if selected_type in self.get_project().tag_type_translator:
            dict_type = self.get_project().tag_type_translator[selected_type]
        unassigned_tag = self.get_next_unassigned_tag(selected_type)

        context['tag_types'] = tag_types
        context['selected_type'] = selected_type
        context['selected_dict_type'] = dict_type
        context['tag'] = unassigned_tag
        if unassigned_tag:
            context['closest'] = unassigned_tag.get_closest_variations()
        try:
            context['dictionary'] = self.get_project().selected_dictionaries.get(type=dict_type)
        except Dictionary.DoesNotExist:
            context['dictionary'] = None

        return context


class TWFProjectTagsView(SingleTableMixin, FilterView, TWFTagsView):
    """Base class for all tag views."""
    template_name = 'twf/tags/all_tags.html'
    page_title = 'Project Documents'
    filterset_class = TagFilter
    table_class = TagTable
    paginate_by = 20
    model = PageTag

    def post(self, request, *args, **kwargs):
        if "export_tags" in request.POST:

            result = []
            queryset = self.get_filterset(self.filterset_class).qs
            for item in queryset:
                result.append({
                    'Document ID': item.page.document.id,
                    'Transkribus ID': item.page.document.document_id,
                    'Transkribus Doc URL': item.page.document.get_transkribus_url(),
                    'Document Title': item.page.document.title,
                    'Page ID': item.page.id,
                    'Transkribus Page ID': item.page.tk_page_id,
                    'Transkribus Page URL': item.get_transkribus_url(),
                    'Page Number': item.page.tk_page_number,
                    'Tag ID': item.id,
                    'Tag Type': item.variation_type,
                    'Tag Variation': item.variation,
                    'Tag Additional Information': item.additional_information,
                    'Tag Dictionary Entry': item.dictionary_entry.label if item.dictionary_entry else '',
                    'Tag Date Variation': item.date_variation_entry.edtf_of_normalized_variation
                        if item.date_variation_entry else '',
                    'Tag Is Parked': item.is_parked,
                    'Tag Is Resolved': item.dictionary_entry is not None or item.date_variation_entry is not None
                })

            df = pd.DataFrame(result)
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="data.csv"'
            return response

        return redirect('twf:tags_all')

    def get_filterset(self, filterset_class):
        project = self.get_project()
        excluded = self.get_excluded_types()
        return filterset_class(self.request.GET, queryset=self.get_queryset(),
                               project=project, excluded=excluded)

    def get_queryset(self):
        project = self.get_project()
        excluded_types = self.get_excluded_types()

        base_queryset = PageTag.objects.filter(
            page__document__project=project
        ).exclude(variation_type__in=excluded_types)

        self.filterset = self.filterset_class(self.request.GET,
                                              queryset=base_queryset,
                                              project=project,
                                              excluded=excluded_types)
        return self.filterset.qs

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['filter'] = self.get_filterset(self.filterset_class)
        return context


class TWFProjectTagsOpenView(TWFProjectTagsView):
    template_name = 'twf/tags/open.html'
    page_title = 'Open Tags'

    def get_queryset(self):
        project = self.get_project()
        excluded = self.get_excluded_types()
        queryset = self.model.objects.filter(page__document__project=project,
                                         dictionary_entry=None,
                                         is_parked=False).exclude(variation_type__in=excluded)
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset,
                                              project=project,
                                              excluded=excluded)
        return self.filterset.qs


class TWFProjectTagsParkedView(TWFProjectTagsView):
    template_name = 'twf/tags/parked.html'
    page_title = 'Parked Tags'

    def get_queryset(self):
        project = self.get_project()
        excluded = self.get_excluded_types()
        queryset = self.model.objects.filter(page__document__project=project,
                                         dictionary_entry=None,
                                         is_parked=True).exclude(variation_type__in=excluded)
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset,
                                              project=project,
                                              excluded=excluded)
        return self.filterset.qs


class TWFProjectTagsResolvedView(TWFProjectTagsView):
    template_name = 'twf/tags/resolved.html'
    page_title = 'Resolved Tags'

    def get_queryset(self):
        project = self.get_project()
        excluded = self.get_excluded_types()
        queryset1 = self.model.objects.filter(page__document__project=project,
                                              dictionary_entry__isnull=False,
                                              is_parked=False).exclude(variation_type__in=excluded)
        queryset2 = self.model.objects.filter(page__document__project=project,
                                              date_variation_entry__isnull=False,
                                              variation_type__in=self.get_date_types(),
                                              is_parked=False).exclude(variation_type__in=excluded)
        queryset = queryset1 | queryset2
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset,
                                              project=project,
                                              excluded=excluded)
        return self.filterset.qs


class TWFProjectTagsIgnoredView(TWFProjectTagsView):
    template_name = 'twf/tags/ignored.html'
    page_title = 'Ignored Tags'

    def get_queryset(self):
        project = self.get_project()
        excluded = self.get_excluded_types()
        queryset = self.model.objects.filter(page__document__project=project,
                                             variation_type__in=excluded)
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset,
                                              project=project,
                                              excluded=excluded)
        return self.filterset.qs


class TWFTagsDatesView(TWFProjectTagsView):
    template_name = 'twf/tags/dates.html'
    page_title = 'Date Tags'
    table_class = TagDateTable

    def get_queryset(self):
        project = self.get_project()
        date_types = self.get_date_types()
        queryset = self.model.objects.filter(page__document__project=project,
                                         variation_type__in=date_types,
                                         date_variation_entry__isnull=True)
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def post(self, request, *args, **kwargs):

        if self.request.POST.get('save_date', None):
            tag_id = self.request.POST.get('tag_id', None)
            tag = PageTag.objects.get(pk=tag_id)
            tag_edtf = self.request.POST.get('tag_edtf', None)

            d_var = DateVariation(
                variation=tag.variation,
                normalized_variation=tag.additional_information,
                edtf_of_normalized_variation=tag_edtf
            )
            d_var.save(current_user=self.request.user)
            tag.date_variation_entry = d_var
            tag.save(current_user=self.request.user)

        return super().get(request, *args, **kwargs)
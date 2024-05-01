"""Views for the project overview."""
from collections import defaultdict
from statistics import median

from django.db.models import Count, Avg
from django.views.generic import TemplateView

from main.models import Document, Page, PageTag
from main.views.views_base import BaseProjectView


class ProjectOverView(BaseProjectView, TemplateView):
    """View for the project overview."""
    template_name = 'main/overview.html'

    def get_context_data(self, **kwargs):
        """Add statistics to the context."""
        context = super().get_context_data(**kwargs)

        project = self.get_project()
        document_count = Document.objects.filter(project=project).count()
        page_count = Page.objects.filter(document__project=project).count()
        ignored_pages = Page.objects.filter(document__project=project, is_ignored=True).count()
        ignored_percentage = (ignored_pages / page_count * 100) if page_count > 0 else 0
        largest_document = (Document.objects.annotate(num_pages=Count('pages'))
                            .filter(project=project).order_by('-num_pages').first())
        smallest_document = (Document.objects.annotate(num_pages=Count('pages'))
                             .filter(project=project).order_by('num_pages').first())
        pagetag_count = PageTag.objects.filter(page__document__project=project).count()
        unique_pagetag_count = (PageTag.objects.filter(page__document__project=project)
                                .aggregate(unique_variations=Count('variation',
                                                                   distinct=True))['unique_variations'])
        average_pagetags_per_document = (Document.objects.annotate(num_pagetags=Count('pages__tags'))
                                         .filter(project=project)
                                         .aggregate(average_pagetags=Avg('num_pagetags'))['average_pagetags'])
        pagetags_per_document_list = (Document.objects.annotate(num_pagetags=Count('pages__tags'))
                                      .filter(project=project).values_list('num_pagetags', flat=True))
        median_pagetags_per_document = median(pagetags_per_document_list) if pagetags_per_document_list else 0
        total_pagetags = PageTag.objects.filter(page__document__project=project).count()
        pagetags_with_dictionaryentry = PageTag.objects.filter(page__document__project=project,
                                                               dictionary_entry__isnull=False).count()
        percentage_with_dictionaryentry = (pagetags_with_dictionaryentry / total_pagetags * 100)\
            if total_pagetags > 0 else 0

        # First, gather counts for each DictionaryEntry
        entry_counts = PageTag.objects.filter(
            page__document__project=project
        ).values('dictionary_entry__id', 'dictionary_entry__label', 'dictionary_entry__dictionary__type').annotate(
            count=Count('id')
        ).order_by('-count')

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
            if len(top_entries_per_type[dtype]) < 10:
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

        context['stats'] = {
            'document_count': document_count,
            'page_count': page_count,
            'ignored_pages': ignored_pages,
            'ignored_percentage': ignored_percentage,
            'largest_document': largest_document,
            'smallest_document': smallest_document,
            'pagetag_count': pagetag_count,
            'unique_pagetag_count': unique_pagetag_count,
            'average_pagetags_per_document': average_pagetags_per_document,
            'median_pagetags_per_document': median_pagetags_per_document,
            'total_pagetags': total_pagetags,
            'pagetags_with_dictionaryentry': pagetags_with_dictionaryentry,
            'percentage_with_dictionaryentry': percentage_with_dictionaryentry,
            'most_used_entries_per_type': dict(top_entries_per_type),
            'variation_type_counts': variation_type_counts,
        }

        return context

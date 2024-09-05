"""Filter classes for the twf app."""
import django_filters
from .models import Document, DictionaryEntry, PageTag


class TagFilter(django_filters.FilterSet):
    """Filter for the tags table."""

    variation_type = django_filters.ChoiceFilter(
        field_name='variation_type',
        label='Variation Type',
        choices=[],  # Placeholder for choices, will populate dynamically
    )

    class Meta:
        """Meta class for the tag filter."""
        model = PageTag
        fields = {
            'variation': ['icontains'],
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        excluded = kwargs.pop('excluded', [])

        super().__init__(*args, **kwargs)

        # Dynamically populate the choices for variation_type
        distinct_variation_types = (
            PageTag.objects.filter(page__document__project=project)
            .exclude(variation_type__in=excluded)
            .distinct()
            .values('variation_type')
            .order_by('variation_type')
        )

        choices = [(vt['variation_type'], vt['variation_type']) for vt in distinct_variation_types]
        # print(choices)
        self.filters['variation_type'].extra.update({
            'choices': choices
        })


class DocumentFilter(django_filters.FilterSet):
    """Filter for the documents taBLE."""

    class Meta:
        """Meta class for the document filter."""
        model = Document
        fields = {
            'document_id': ['icontains'],
            'title': ['icontains'],  # assuming you have a title field you want to filter
        }


class DictionaryEntryFilter(django_filters.FilterSet):
    """Filter for the dictionary entry table."""

    class Meta:
        """Meta class for the dictionary entry filter."""
        model = DictionaryEntry
        fields = {
            'label': ['icontains'],
        }

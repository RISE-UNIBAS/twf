"""Filter classes for the main app."""
import django_filters
from .models import Document, DictionaryEntry


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

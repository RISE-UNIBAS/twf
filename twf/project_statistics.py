"""This module contains functions to gather statistics for a project."""
from collections import defaultdict

from django.db.models import Avg, Count
from .models import Document, Page, PageTag, Dictionary, Collection


def get_document_statistics(project):
    """Get statistics for documents.
    Args:
        project: Project
    Returns:
        dict: Dictionary with statistics for documents.
    """
    total_documents = project.documents.count()
    total_pages = Page.objects.filter(document__project=project).count()
    average_pages_per_document = Page.objects.filter(document__project=project).values('document').annotate(count=Count('id')).aggregate(Avg('count'))
    ignored_pages = Page.objects.filter(document__project=project, is_ignored=True).count()
    largest_document = (Document.objects.annotate(num_pages=Count('pages'))
                        .filter(project=project).order_by('-num_pages').first())
    smallest_document = (Document.objects.annotate(num_pages=Count('pages'))
                         .filter(project=project).order_by('num_pages').first())

    return {
        'total_documents': total_documents,
        'total_pages': total_pages,
        'ignored_pages': ignored_pages,
        'ignored_percentage': (ignored_pages / total_pages * 100) if total_pages > 0 else 0,
        'average_pages_per_document': average_pages_per_document,
        'largest_document': largest_document,
        'smallest_document': smallest_document
    }


def get_tag_statistics(project):
    """Get statistics for tags.
    Args:
        project: Project
    Returns:
        dict: Dictionary with statistics for tags.
    """
    total_tags = PageTag.objects.filter(page__document__project=project).count()
    return {
        'total_tags': total_tags
    }


def get_dictionary_statistics(project):
    # Example: total number of dictionaries
    total_dictionaries = Dictionary.objects.count()

    top_entries_per_type = defaultdict(list)

    entry_counts = PageTag.objects.filter(
        page__document__project=project
    ).values(
        'dictionary_entry__id',
        'dictionary_entry__label',
        'dictionary_entry__dictionary__type'
    ).annotate(
        count=Count('id')
    ).order_by('dictionary_entry__dictionary__type', '-count')

    for entry in entry_counts:
        dtype = entry['dictionary_entry__dictionary__type']
        if len(top_entries_per_type[dtype]) < 20:
            top_entries_per_type[dtype].append(entry)

    return {
        'total_dictionaries': total_dictionaries,
        'top_entries_per_type': dict(top_entries_per_type)
    }


def get_collection_statistics():
    # Example: total number of collections
    total_collections = Collection.objects.count()
    return {
        'total_collections': total_collections
    }


def get_import_export_statistics():
    # Here you can add stats for import/export operations if tracked
    pass


def gather_statistics():
    return {
        'documents': get_document_statistics(),
        'tags': get_tag_statistics(),
        'dictionaries': get_dictionary_statistics(),
        'collections': get_collection_statistics(),
        # Add more sections as needed
    }

"""This module contains the functions to export dictionaries and tags to JSON and CSV formats."""
import json
from twf.models import Dictionary, PageTag, Document


def get_dictionary_json_data(dictionary_id, include_uses=True):
    """Get the JSON data for the dictionary."""
    dictionary = Dictionary.objects.get(pk=dictionary_id)

    json_data = {
        "name": dictionary.label,
        "type": dictionary.type,
        "metadata": {},
        "entries": []
    }

    entries = dictionary.entries.all()
    for entry in entries:
        entry_d = {
                "label": entry.label,
                "variations": list(entry.variations.all().values_list('variation', flat=True))
            }
        if include_uses:
            entry_d["uses"] = list(Document.objects.filter(pages__tags__dictionary_entry=entry).distinct().values_list('document_id', flat=True))

        json_data["entries"].append(entry_d)
    return json_data


def get_dictionary_csv_data(pk, include_metadata=True, include_uses=False):
    """Get the CSV data for the dictionary."""

    dictionary = Dictionary.objects.get(pk=pk)
    entries = dictionary.entries.all()

    # Create the CSV header
    csv_header = 'entry;variations'
    if include_metadata:
        csv_header += ';metadata'
    if include_uses:
        csv_header += ';documents;collection_items'
    csv_header += '\n'

    csv_body = ''
    for entry in entries:
        # Add label
        csv_line = f'{entry.label};'

        # Add variations
        variations = entry.variations.all().values_list('variation', flat=True)
        csv_line += ','.join(variations)

        # Add metadata
        if include_metadata:
            csv_line += f';{json.dumps(entry.authorization_data)}'

        # Add uses
        if include_uses:
            documents_list = Document.objects.filter(pages__tags__dictionary_entry=entry).distinct().values_list('document_id', flat=True)
            csv_line += f';{",".join(documents_list)};niy'

        csv_line += '\n'
        csv_body += csv_line

    return csv_header + csv_body


def get_tags_json_data(project_id):
    """Get the JSON data for the tags."""
    tags = PageTag.objects.filter(page__document__project_id=project_id)

    json_data = {
        "entries": []
    }

    for entry in tags:
        json_data["entries"].append(
            {
                "label": entry.variation,
                "type": entry.variation_type,
                "documents": list(Document.objects.filter(pages__tags=entry).distinct().values_list('document_id', flat=True))
            }
        )
    return json_data


def get_tags_csv_data(project_id):
    """Get the CSV data for the tags."""
    csv_data = 'entry;type;documents\n'
    tags = PageTag.objects.filter(page__document__project_id=project_id)
    for tag in tags:
        documents = Document.objects.filter(pages__tags=tag).distinct().values_list('document_id', flat=True)
        csv_data += f'{tag.variation};{tag.variation_type};{",".join(documents)}\n'
    return csv_data


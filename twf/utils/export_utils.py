"""This module contains the functions to export dictionaries and tags to JSON and CSV formats."""
import json
import re

from django.db.models.functions import Random

from twf.models import Dictionary, PageTag, Document, Page, Project


class ExportCreator:
    """Class to create export data."""

    def __init__(self, project, configuration):
        self.project = project
        self.configuration = configuration

    def create_item_data(self, item):
        data = {}
        config = self.configuration.config

        if isinstance(item, Project):
            config = self.configuration.config["general"]
        elif isinstance(item, Document):
            config = self.configuration.config["documents"]
        elif isinstance(item, Page):
            config = self.configuration.config["pages"]

        for field_key, field_config in config.items():
            source_type = field_config.get("source_type", "static")
            source = field_config.get("source", None)
            fallback = field_config.get("fallback", None)

            value = None

            if source_type == "static":
                value = str(source)
            elif source_type == "db_field":
                field_name = source.split(".")[1]
                value = getattr(item, field_name, None)
            elif source_type == "metadata":
                meta_source = getattr(item, "metadata", None)
                if meta_source:
                    value = self.get_nested_metadata(meta_source, source)
            elif source_type == "special":
                value = self.compute_special_field(field_key, item)


            if value in [None, ""]:
                value = fallback

            data[field_key] = value

        return data

    def compute_special_field(self, field_key, item):
        if field_key == "tag_list":
            return [tag.variation for tag in item.tags.all()]
        elif field_key == "tag_list_unique":
            return list(set(tag.variation for tag in item.tags.all()))
        elif field_key == "tags_count":
            return item.tags.count()
        elif field_key == "linked_tags_list":
            return [tag.dictionary_entry.label for tag in item.tags.all() if tag.dictionary_entry]
        elif field_key == "linked_tags_list_unique":
            return list(set(tag.dictionary_entry.label for tag in item.tags.all() if tag.dictionary_entry))
        elif field_key == "linked_tags_count":
            return sum(1 for tag in item.tags.all() if tag.dictionary_entry)
        elif field_key == "entry_list":
            return [
                {"label": tag.dictionary_entry.label, "id": tag.dictionary_entry.id}
                for tag in item.tags.all() if tag.dictionary_entry
            ]
        elif field_key == "word_count":
            return len(item.get_text().split())
        elif field_key == "no_of_annotations":
            return len(item.document_configuration.get("annotations", []))
        elif field_key == "item_context":
            if hasattr(item, 'document'):
                return {"type": "document", "id": item.document.id}
            return {}
        elif field_key == "project_members":
            return [
                {
                    "name": p.user.get_full_name() or p.user.username,
                    "orcid": p.orc_id
                }
                for p in self.project.get_project_members()
            ]
        elif field_key == "dictionaries":
            return [
                {"name": d.label, "id": d.id}
                for d in self.project.selected_dictionaries.all()
            ]
        elif field_key == "no_of_docs":
            return self.project.documents.count()
        elif field_key == "collection_items_count":
            return self.project.collections.count()
        elif field_key == "last_twf_edit":
            return item.modified_at.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None

    import re

    def get_nested_metadata(self, metadata, field_key):
        """Safely retrieve nested metadata using dot and bracket notation."""
        parts = re.split(r'\.(?![^\[]*\])', field_key)  # split on '.' outside of brackets
        current = metadata
        for part in parts:
            if isinstance(current, dict):
                # handle dict key or indexed key like key[0]
                match = re.match(r'([^\[]+)(\[(\d+)\])?', part)
                if match:
                    key = match.group(1)
                    index = match.group(3)
                    current = current.get(key)
                    if index is not None and isinstance(current, list):
                        try:
                            current = current[int(index)]
                        except (IndexError, ValueError):
                            return None
            else:
                return None
        return current

    def create_sample_data(self):
        """Create sample data."""
        random_document = self.project.documents.order_by(Random()).first()

        if self.configuration.export_type == 'document':
            return self.create_item_data(random_document)
        elif self.configuration.export_type == 'page':
            random_page = random_document.pages.order_by(Random()).first()
            return self.create_item_data(random_page)
        elif self.configuration.export_type == 'collection':
            random_collection = self.project.collections.order_by(Random()).first()
            random_item = random_collection.items.order_by(Random()).first()
            return self.create_item_data(random_item)
        elif self.configuration.export_type == 'dictionary':
            return {"msg": "niy"}
        elif self.configuration.export_type == 'tag_report':
            return {"msg": "niy"}
        else:
            raise ValueError("Invalid export type")

    def get_number_of_items(self):
        if self.configuration.export_type == 'document':
            return self.project.documents.count()
        elif self.configuration.export_type == 'page':
            return Page.objects.filter(document__project=self.project).count()
        elif self.configuration.export_type == 'collection':
            return 0
        elif self.configuration.export_type == 'dictionary':
            return 0
        elif self.configuration.export_type == 'tag_report':
            return 0
        else:
            raise ValueError("Invalid export type")

    def get_items(self):
        if self.configuration.export_type == 'document':
            return self.project.documents.all().order_by('document_id')
        elif self.configuration.export_type == 'page':
            return Page.objects.filter(document__project=self.project).all().order_by('document__document_id', 'tk_page_number')
        elif self.configuration.export_type == 'collection':
            return []
        elif self.configuration.export_type == 'dictionary':
            return []
        elif self.configuration.export_type == 'tag_report':
            return []
        else:
            raise ValueError("Invalid export type")


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
            entry_d["uses"] = list(Document.objects.filter(pages__tags__dictionary_entry=entry).
                                   distinct().values_list('document_id', flat=True))

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
            csv_line += f';{json.dumps(entry.metadata)}'

        # Add uses
        if include_uses:
            documents_list = (Document.objects.filter(pages__tags__dictionary_entry=entry).distinct().
                              values_list('document_id', flat=True))
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
                "documents": list(Document.objects.filter(pages__tags=entry).distinct().
                                  values_list('document_id', flat=True))
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


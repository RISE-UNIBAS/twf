# pylint: disable=too-few-public-methods
"""This module contains the tables for displaying documents and dictionary entries."""
import django_tables2 as tables
from django.urls import reverse
from django.utils.safestring import mark_safe

from twf.models import DictionaryEntry, Dictionary, Variation, PageTag, Document


class DictionaryTable(tables.Table):
    """Table for displaying dictionaries."""
    label = tables.Column(verbose_name="Dictionary")
    type = tables.Column(verbose_name="Type")
    information = tables.Column(verbose_name="Information", orderable=False, accessor='id')
    options = tables.TemplateColumn(template_name='twf/tables/dictionary_table_options.html',
                                    verbose_name="Options", orderable=False, attrs={"td": {"width": "10%"}})

    class Meta:
        """Meta class for the DictionaryTable."""
        model = Dictionary
        template_name = "django_tables2/bootstrap.html"  # Using Bootstrap template
        fields = ("label", "type")

    def render_label(self, value, record):
        """Renders the label column with the label and the type of the dictionary."""
        formatted_date = record.modified_at.strftime("%a, %d %b %Y %H:%M")
        return mark_safe(f"{value}<br/>"
                         f"<span class='small text-muted'>ID: {record.id}</span><br/>"
                         f"<span class='small text-muted'>{record.modified_by}, {formatted_date}</span>")

    def render_information(self, value, record):
        """Renders the information column with the number of entries and the number of variations."""
        return mark_safe(f"Entries: {record.entries.count()}")


class DictionaryAddTable(DictionaryTable):
    """Table for displaying dictionaries to add to a project."""

    options = tables.TemplateColumn(template_name='twf/tables/dictionary_table_add_options.html',
                                    verbose_name="Options", orderable=False, attrs={"td": {"width": "15%"}})



class DictionaryEntryTable(tables.Table):
    """Table for displaying dictionary entries."""
    variations = tables.Column(verbose_name="Variations", orderable=False)
    authorization_data = tables.Column(verbose_name="Norm Data", orderable=False)
    options = tables.TemplateColumn(template_name='twf/tables/dictionary_entry_table_options.html',
                                    verbose_name="Options", orderable=False, attrs={"td": {"width": "10%"}})

    class Meta:
        """Meta class for the DictionaryEntryTable."""
        model = DictionaryEntry
        template_name = "django_tables2/bootstrap.html"  # Using Bootstrap template
        fields = ("label", )

    def render_variations(self, record):
        """Renders the variations column with a delete button for each variation."""
        variations = record.variations.all()
        html = ""
        record_html = """<span class="badge bg-secondary">{}</span>&nbsp;"""
        for var in variations:
            html += record_html.format(var.variation)

        return mark_safe(html)

    def render_label(self, value, record):
        """Renders the label column with the label and the type of the dictionary."""
        formatted_date = record.modified_at.strftime("%a, %d %b %Y %H:%M")
        return mark_safe(f"<strong>{value}</strong><br/>"
                         f"<span class='small text-muted'>ID: {record.id}</span><br/>"
                         f"<span class='small text-muted'>{record.modified_by}, {formatted_date}</span>")


class DictionaryEntryVariationTable(tables.Table):
    """Table for displaying dictionary entries."""

    information = tables.Column(accessor="id", verbose_name="Options", orderable=False, attrs={"td": {"width": "10%"}})

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

    from django.urls import reverse

    def render_information(self, value, record):
        """Renders the information column with the number of entries and the number of variations."""
        variation_usage_count = PageTag.objects.filter(
            page__document__project=self.project, variation=record.variation
        ).count()

        documents = (
            Document.objects.filter(
                project=self.project, pages__tags__variation=record.variation
            )
            .distinct()
        )

        # Generate document links using reverse()
        document_links = " | ".join(
            f'<a href="{reverse("twf:view_document", args=[doc.pk])}">{doc.title or doc.document_id}</a>'
            for doc in documents
        )

        return mark_safe(
            f"Usages: {variation_usage_count} <br/> Documents: {document_links}"
        )

    class Meta:
        """Meta class for the DictionaryEntryTable."""
        model = Variation
        template_name = "django_tables2/bootstrap.html"  # Using Bootstrap template
        fields = ("variation", )

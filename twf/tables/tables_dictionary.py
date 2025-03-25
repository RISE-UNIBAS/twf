# pylint: disable=too-few-public-methods
"""This module contains the tables for displaying documents and dictionary entries."""
import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from twf.models import DictionaryEntry, Dictionary, Variation, PageTag, Document


class DictionaryTable(tables.Table):
    label = tables.Column(verbose_name="Dictionary", attrs={"td": {"class": "fw-bold"}})
    type = tables.Column(verbose_name="Type")

    information = tables.Column(empty_values=(), verbose_name="Information", orderable=False)
    options = tables.Column(empty_values=(), verbose_name="Options", orderable=False)

    class Meta:
        model = Dictionary
        fields = ("label", "type")
        attrs = {"class": "table table-striped table-hover table-sm"}

    def render_label(self, value, record):
        modified = record.modified_at.strftime("%Y-%m-%d %H:%M")
        return format_html(
            '{}<br><span class="text-muted small">ID: {}<br>{}, {}</span>',
            value,
            record.id,
            record.modified_by or "—",
            modified
        )

    def render_information(self, record):
        entry_count = record.entries.count()
        variation_count = sum(e.variations.count() for e in record.entries.all())
        return format_html(
            '<span class="small">Entries: {}<br>Variations: {}</span>',
            entry_count,
            variation_count
        )

    def render_options(self, record):
        return format_html(
            '{} {}',
            format_html(
                '<a href="/dictionaries/{}/edit" class="btn btn-sm btn-dark me-1" title="Edit">'
                '<i class="fa fa-pen"></i></a>',
                record.pk
            ),
            format_html(
                '<a href="/dictionaries/{}/delete" class="btn btn-sm btn-danger" title="Delete">'
                '<i class="fa fa-trash"></i></a>',
                record.pk
            )
        )


class DictionaryAddTable(DictionaryTable):
    """Table for displaying dictionaries to add to a project."""

    options = tables.TemplateColumn(template_name='twf/tables/dictionary_table_add_options.html',
                                    verbose_name="Options", orderable=False, attrs={"td": {"width": "15%"}})



class DictionaryEntryTable(tables.Table):
    """Table for displaying dictionary entries."""
    variations = tables.Column(verbose_name="Variations", orderable=False)
    metadata = tables.Column(verbose_name="Norm Data", orderable=False)
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

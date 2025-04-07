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
        from django.urls import reverse
        
        return format_html(
            '{} {}',
            format_html(
                '<a href="{}" class="btn btn-sm btn-dark me-1" title="View">'
                '<i class="fa fa-eye"></i></a>',
                reverse('twf:dictionaries_view', args=[record.pk])
            ),
            format_html(
                '<a href="{}" class="btn btn-sm btn-dark me-1" title="Edit">'
                '<i class="fa fa-pen"></i></a>',
                reverse('twf:dictionaries_edit', args=[record.pk])
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
    options = tables.Column(empty_values=(), verbose_name="Options", orderable=False)

    class Meta:
        """Meta class for the DictionaryEntryTable."""
        model = DictionaryEntry
        template_name = "django_tables2/bootstrap.html"  # Using Bootstrap template
        fields = ("label", )
        attrs = {"class": "table table-striped table-hover table-sm"}

    def render_variations(self, record):
        """Renders the variations column with a delete button for each variation."""
        variations = record.variations.all()
        html = ""
        record_html = """<span class="badge bg-secondary">{}</span>&nbsp;"""
        for var in variations:
            html += record_html.format(var.variation)

        return mark_safe(html)
    
    def render_metadata(self, record):
        """Renders the metadata column with truncated content."""
        if not record.metadata:
            return "—"
            
        # Convert to string and truncate if necessary
        metadata_str = str(record.metadata)
        if len(metadata_str) > 100:
            metadata_str = metadata_str[:97] + "..."
            
        return format_html(
            '<span title="{}">{}</span>',
            str(record.metadata).replace('"', '&quot;'),  # Escape quotes for the title attribute
            metadata_str
        )

    def render_label(self, value, record):
        """Renders the label column with the label and the type of the dictionary."""
        formatted_date = record.modified_at.strftime("%a, %d %b %Y %H:%M")
        return mark_safe(f"<strong>{value}</strong><br/>"
                         f"<span class='small text-muted'>ID: {record.id}</span><br/>"
                         f"<span class='small text-muted'>{record.modified_by}, {formatted_date}</span>")
                         
    def render_options(self, record):
        """Renders the actions column with buttons."""
        from django.urls import reverse
        
        return format_html(
            '{} {}',
            format_html(
                '<a href="{}" class="btn btn-sm btn-dark me-1" title="View">'
                '<i class="fa fa-eye"></i></a>',
                reverse('twf:dictionaries_entry_view', args=[record.pk])
            ),
            format_html(
                '<a href="{}" class="btn btn-sm btn-dark me-1" title="Edit">'
                '<i class="fa fa-pen"></i></a>',
                reverse('twf:dictionaries_entry_edit', args=[record.pk])
            )
        )


class DictionaryEntryVariationTable(tables.Table):
    """Table for displaying dictionary entry variations."""

    information = tables.Column(accessor="id", verbose_name="Usages", orderable=False)
    options = tables.Column(empty_values=(), verbose_name="Options", orderable=False)

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

    def render_information(self, value, record):
        """Renders the information column with usage statistics."""
        from django.urls import reverse
        
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
        
        # Truncate document links if they're too long
        if len(document_links) > 100:
            # This is a simplification; in real life we might want to keep complete links
            truncated_links = "Multiple documents"
            return format_html(
                '<span title="{}">Usages: {}<br/>Documents: {}</span>',
                document_links,
                variation_usage_count,
                truncated_links
            )
        
        return format_html(
            'Usages: {}<br/>Documents: {}',
            variation_usage_count,
            mark_safe(document_links) if document_links else "None"
        )
    
    def render_options(self, record):
        """Renders the options column with delete button."""
        from django.urls import reverse
        
        delete_url = reverse('twf:dictionaries_delete_variation', args=[record.pk])
        
        return format_html(
            '<a href="#" class="btn btn-sm btn-danger show-danger-modal" '
            'data-redirect-url="{}" '
            'data-message="Are you sure you want to delete this variation? Any tags using this variation will be unlinked." '
            'title="Delete"><i class="fa fa-trash"></i></a>',
            delete_url
        )

    class Meta:
        """Meta class for the DictionaryEntryVariationTable."""
        model = Variation
        template_name = "django_tables2/bootstrap.html"
        fields = ("variation", )
        attrs = {"class": "table table-striped table-hover table-sm"}

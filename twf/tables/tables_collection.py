"""Table classes for displaying CollectionItem objects."""
import django_tables2 as tables
from django.utils.safestring import mark_safe

from twf.models import CollectionItem

class CollectionItemTable(tables.Table):
    """Table for displaying CollectionItem objects."""

    document_id = tables.Column(accessor="document.document_id", verbose_name="Document ID")
    title = tables.Column(verbose_name="Item Title")
    document_title = tables.Column(accessor="document.title", verbose_name="Document Title")
    options = tables.Column(accessor="id",
                            verbose_name="Options", orderable=False,
                            attrs={"td": {"width": "10%"}})

    def render_document_id(self, record, value):
        """Render the document ID."""
        status = f'<span class="badge bg-info">{record.status}</span>'
        if record.status == "reviewed":
            status = f'<span class="badge bg-success">{record.status}</span>'
        if record.status == "faulty":
            status = f'<span class="badge bg-warning">{record.status}</span>'

        in_workflow = ''
        if record.is_reserved:
            in_workflow = '<span class="badge bg-secondary">In Workflow</span>'

        return mark_safe(f'{value}<br/>{status}<br/>{in_workflow}')


    class Meta:
        """Meta class for the CollectionItemTable."""
        model = CollectionItem
        fields = ("document_id", "title", "document_title")  # Specify fields to include
        template_name = "twf/tables/custom_table.html"

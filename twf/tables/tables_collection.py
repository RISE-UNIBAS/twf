"""Table classes for displaying CollectionItem objects."""
import django_tables2 as tables
from twf.models import CollectionItem

class CollectionItemTable(tables.Table):
    """Table for displaying CollectionItem objects."""

    document_id = tables.Column(accessor="document.document_id", verbose_name="Document ID")
    title = tables.Column(verbose_name="Item Title")
    document_title = tables.Column(accessor="document.title", verbose_name="Document Title")
    options = tables.Column(accessor="id",
                            verbose_name="Options", orderable=False,
                            attrs={"td": {"width": "10%"}})

    class Meta:
        """Meta class for the CollectionItemTable."""
        model = CollectionItem
        fields = ("document_id", "title", "document_title")  # Specify fields to include
        template_name = "twf/tables/custom_table.html"

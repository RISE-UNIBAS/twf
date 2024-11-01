# pylint: disable=too-few-public-methods
"""Table classes for displaying tags."""
import django_tables2 as tables

from twf.models import PageTag


class TagTable(tables.Table):
    """Table for displaying tags."""

    entry = tables.Column(accessor="dictionary_entry", verbose_name="Entry", empty_values=())

    options = tables.TemplateColumn(template_name='twf/tables/tag_table_options.html',
                                    verbose_name="Options",
                                    attrs={"td": {"width": "10%"}},
                                    orderable=False)

    class Meta:
        """Meta class for the TagTable."""
        model = PageTag
        template_name = "django_tables2/bootstrap.html"
        fields = ("variation", "variation_type", "entry")
        attrs = {
            'class': 'table table-striped'
        }

    def render_entry(self, value, record):
        """Render entry field based on variation_type."""
        date_types = self.get_date_types()
        print(f"Variation Type: {record.variation_type}, Value: {value}")
        if record.variation_type in date_types:
            return record.date_variation_entry.edtf_of_normalized_variation or "-"
        return record.dictionary_entry or "-"

    def get_date_types(self):
        """Retrieve or define the date types here."""
        # Define or fetch your date types. Example:
        return ["date", "date_type_2"]  # Replace with actual date types


class TagDateTable(tables.Table):
    """Table for displaying tags."""
    wf_options = tables.TemplateColumn(template_name='twf/tables/tag_date_table_options.html',
                                       verbose_name="Options",
                                       orderable=False)

    options = tables.TemplateColumn(template_name='twf/tables/tag_table_options.html',
                                    verbose_name="Options",
                                    attrs={"td": {"width": "10%"}},
                                    orderable=False)

    class Meta:
        """Meta class for the TagTable."""
        model = PageTag
        template_name = "django_tables2/bootstrap.html"
        fields = ("variation", "additional_information")
        attrs = {
            'class': 'table table-striped'
        }

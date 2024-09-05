import django_tables2 as tables

from twf.models import PageTag


class TagTable(tables.Table):
    """Table for displaying tags."""
    options = tables.TemplateColumn(template_name='twf/tables/tag_table_options.html',
                                    verbose_name="Options",
                                    attrs={"td": {"width": "10%"}},
                                    orderable=False)

    class Meta:
        model = PageTag
        template_name = "django_tables2/bootstrap.html"
        fields = ("variation", "variation_type", "dictionary_entry")
        attrs = {
            'class': 'table table-striped'
        }


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
        model = PageTag
        template_name = "django_tables2/bootstrap.html"
        fields = ("variation", "additional_information")
        attrs = {
            'class': 'table table-striped'
        }

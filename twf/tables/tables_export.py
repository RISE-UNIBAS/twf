import django_tables2 as tables
from django.utils.html import format_html
from twf.models import Export


class ExportTable(tables.Table):
    export_type = tables.Column(verbose_name="Type")
    created = tables.DateTimeColumn(verbose_name="Created At")
    created_by = tables.Column(verbose_name="By")
    actions = tables.Column(empty_values=(), verbose_name="Options", orderable=False)

    class Meta:
        model = Export
        fields = ("export_type", "created", "created_by")
        attrs = {"class": "table table-striped table-hover table-sm"}

    def render_export_type(self, value):
        label = value.title() if value else "Unknown"
        return format_html('<span class="fw-bold">{}</span>', label)

    def render_actions(self, record):
        return format_html(
            '<a href="{}" class="btn btn-sm btn-primary me-1" download>'
            '<i class="fa fa-download"></i> Download</a>'
            '<a href="/exports/{}/delete" class="btn btn-sm btn-danger">'
            '<i class="fa fa-trash"></i> Delete</a>',
            record.export_file.url,
            record.pk
        )

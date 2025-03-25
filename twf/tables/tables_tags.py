# pylint: disable=too-few-public-methods
"""Table classes for displaying tags."""
import django_tables2 as tables
from django.utils.html import format_html
from twf.models import PageTag


class TagTable(tables.Table):
    variation = tables.Column(verbose_name="Variation", attrs={"td": {"class": "fw-bold"}})
    variation_type = tables.Column(verbose_name="Type")

    entry = tables.Column(accessor="dictionary_entry", verbose_name="Entry", empty_values=())

    options = tables.Column(empty_values=(), verbose_name="Options", orderable=False)

    class Meta:
        model = PageTag
        fields = ("variation", "variation_type", "entry")
        attrs = {"class": "table table-striped table-hover table-sm"}

    def render_entry(self, value, record):
        date_types = self.get_date_types()
        if record.variation_type in date_types:
            if record.date_variation_entry:
                return record.date_variation_entry.edtf_of_normalized_variation or "-"
            return "-"
        return record.dictionary_entry or "-"

    def get_date_types(self):
        return ["date", "date_type_2"]  # Replace with actual variation types for dates

    def render_options(self, record):

        return format_html(
            '{} {} {} {} {}',
            format_html(
                '<a href="/tags/{}/edit" class="btn btn-sm btn-dark me-1"'
                '  data-bs-toggle="tooltip" data-bs-placement="bottom" title="Edit tag">'
                '<i class="fa fa-pen"></i></a>',
                record.pk
            ),
            format_html(
                '<a href="/tags/{}/edit" class="btn btn-sm btn-dark me-1"'
                '  data-bs-toggle="tooltip" data-bs-placement="bottom" title="Park tag (put aside for later)">'
                '<i class="fa fa-box-archive"></i></a>',
                record.pk
            ),
            format_html(
                '<a href="/tags/{}/edit" class="btn btn-sm btn-dark me-1"'
                '  data-bs-toggle="tooltip" data-bs-placement="bottom" title="View on Transkribus">'
                '<i class="fa fa-scroll"></i></a>',
                record.pk
            ),
            format_html(
                '<a href="/tags/{}/edit" class="btn btn-sm btn-dark me-1"'
                '  data-bs-toggle="tooltip" data-bs-placement="bottom" title="Assign to dictionary">'
                '<i class="fa fa-hand-point-right"></i></a>',
                record.pk
            ),
            format_html(
                '<a href="/tags/{}/delete" class="btn btn-sm btn-danger"'
                '  data-bs-toggle="tooltip" data-bs-placement="bottom" title="Delete tag">'
                '<i class="fa fa-trash"></i></a>',
                record.pk
            )
        )

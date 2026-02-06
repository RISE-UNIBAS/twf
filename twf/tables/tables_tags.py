# pylint: disable=too-few-public-methods
"""Table classes for displaying tags."""
import django_tables2 as tables
from django.urls import reverse_lazy
from django.utils.html import format_html
from twf.models import PageTag


class TagTable(tables.Table):
    """
    Table for displaying tags associated with pages.
    """
    variation = tables.Column(
        verbose_name="Variation", attrs={"td": {"class": "fw-bold"}}
    )
    variation_type = tables.Column(verbose_name="Type")
    is_parked = tables.Column(
        verbose_name="Parked",
        orderable=False,
        attrs={"th": {"class": "text-center"}, "td": {"class": "text-center"}},
    )
    entry = tables.Column(
        accessor="dictionary_entry", verbose_name="Entry", empty_values=()
    )
    options = tables.Column(empty_values=(), verbose_name="Options", orderable=False)

    def render_is_parked(self, value):
        """
        Render parked status badge for a tag.

        Args:
            value: Boolean indicating if tag is parked

        Returns:
            SafeString: Formatted HTML badge with parked status
        """
        if value:
            return format_html(
                '<span class="badge bg-warning text-dark" data-bs-toggle="tooltip" title="{}">'
                '<i class="fa fa-box-archive me-1"></i>{}</span>',
                "This tag is parked",
                "Yes",
            )
        else:
            return format_html(
                '<span class="badge bg-success" data-bs-toggle="tooltip" title="{}">'
                '<i class="fa fa-check-circle me-1"></i>{}</span>',
                "This tag is active",
                "No",
            )

    class Meta:
        """
        Table metadata configuration.
        """
        model = PageTag
        fields = ("variation", "variation_type", "entry")
        template_name = "django_tables2/bootstrap4.html"
        attrs = {"class": "table table-striped table-hover"}

    def render_entry(self, value, record):
        """
        Render the dictionary entry or date variation for a tag.

        Args:
            value: Dictionary entry value
            record: PageTag model instance

        Returns:
            str: Dictionary entry label or date variation or "-"
        """
        date_types = self.get_date_types()
        if record.variation_type in date_types:
            if record.date_variation_entry:
                return record.date_variation_entry.edtf_of_normalized_variation or "-"
            return "-"
        return record.dictionary_entry or "-"

    def get_date_types(self):
        """
        Get the list of variation types that should be treated as dates.

        Returns:
            list: List of variation type strings for date fields
        """
        return ["date", "date_type_2"]  # Replace with actual variation types for dates

    def render_options(self, record):
        """
        Render action buttons for tag operations.

        Args:
            record: PageTag model instance

        Returns:
            SafeString: Formatted HTML with action buttons
        """
        from django.utils.safestring import mark_safe

        park_button = format_html(
            '<a href="{}" class="btn btn-sm btn-dark me-1"'
            '  data-bs-toggle="tooltip" data-bs-placement="bottom" title="Park tag (put aside for later)">'
            '<i class="fa fa-box-archive"></i></a>',
            reverse_lazy("twf:tags_park", kwargs={"pk": record.pk}),
        )

        transkribus_button = format_html(
            '<a href="{}" class="btn btn-sm btn-ext me-1" target="_blank"'
            '  data-bs-toggle="tooltip" data-bs-placement="bottom" title="View on Transkribus">'
            '<i class="fa fa-scroll"></i></a>',
            record.get_transkribus_url(),
        )

        assign_button = format_html(
            '<a href="{}" class="btn btn-sm btn-dark me-1"'
            '  data-bs-toggle="tooltip" data-bs-placement="bottom" title="Assign to dictionary entry">'
            '<i class="fa fa-hand-point-right"></i></a>',
            reverse_lazy("twf:tags_assign", kwargs={"pk": record.pk}),
        )

        delete_button = format_html(
            '<a href="#" class="btn btn-sm btn-danger show-danger-modal"'
            '  data-message="Are you sure you want to delete this tag?" '
            '  data-redirect-url="{}" '
            '  data-bs-toggle="tooltip" data-bs-placement="bottom" title="Delete tag">'
            '<i class="fa fa-trash"></i></a>',
            reverse_lazy("twf:tags_delete", kwargs={"pk": record.pk}),
        )

        return mark_safe(
            # f"{park_button}{transkribus_button}{assign_button}{delete_button}"
            f"{park_button}{transkribus_button}"
        )

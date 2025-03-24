"""Table classes for displaying user permissions."""
import django_tables2 as tables
from django.contrib.auth import get_user_model
from django.utils.html import format_html

from twf.models import Project

User = get_user_model()

class ProjectManagementTable(tables.Table):
    title = tables.Column(verbose_name="Project", attrs={"td": {"class": "fw-bold"}})
    created = tables.DateTimeColumn(format="Y-m-d H:i", verbose_name="Created")
    modified = tables.DateTimeColumn(format="Y-m-d H:i", verbose_name="Last Updated")
    status = tables.Column()

    actions = tables.Column(empty_values=(), verbose_name="Options")

    class Meta:
        model = Project
        fields = ("title", "created", "modified", "status")
        attrs = {"class": "table table-striped table-hover table-sm"}

    def render_status(self, value):
        class_map = {
            "open": "success",
            "closed": "secondary",
        }
        color = class_map.get(value.lower(), "dark")
        return format_html('<span class="badge bg-{}">{}</span>', color, value.capitalize())

    def render_actions(self, record):
        return format_html(
            '{} {} {}',
            format_html(
                '<a href="{}" class="btn btn-sm btn-secondary me-1" title="View"><i class="fa fa-eye"></i></a>',
                f"/project/{record.pk}/view",
            ),
            format_html(
                '<a href="{}" class="btn btn-sm btn-warning me-1" title="{} Project">'
                '<i class="fa fa-toggle-{}"></i></a>',
                f"/project/{record.pk}/toggle-status",
                "Close" if record.status == "open" else "Reopen",
                "off" if record.status == "open" else "on",
            ),
            format_html(
                '<a href="{}" class="btn btn-sm btn-danger" title="Delete"><i class="fa fa-trash"></i></a>',
                f"/project/{record.pk}/delete",
            )
        )


class UserManagementTable(tables.Table):
    username = tables.Column(verbose_name="Username")
    email = tables.Column(verbose_name="Email")
    status = tables.Column(empty_values=(), verbose_name="Status")
    actions = tables.Column(empty_values=(), verbose_name="Options")

    class Meta:
        model = User
        fields = ("username", "email")
        attrs = {"class": "table table-striped table-hover table-sm"}

    def render_status(self, record):
        status_tags = []

        if record.is_superuser:
            status_tags.append('<span class="badge bg-success">admin</span>')

        if not record.is_active:
            status_tags.append('<span class="badge bg-dark">inactive</span>')

        if record == self.context.get("request").user:
            status_tags.append('<span class="badge bg-info">You</span>')

        return format_html(" ".join(status_tags))

    def render_actions(self, record):
        if record.is_active:
            toggle_btn = format_html(
                '<a href="/users/{}/deactivate" class="btn btn-sm btn-dark me-1"'
                            '   data-bs-toggle="tooltip" data-bs-placement="top" title="Deactivate User">'
                            '  <i class="fa-solid fa-lock"></i>'
                            '</a>',
                record.pk,
            )
        else:
            toggle_btn = format_html(
                '<a href="/users/{}/activate" class="btn btn-sm btn-success me-1"'
                            '  data-bs-toggle="tooltip" data-bs-placement="top" title="Activate User">'
                            '  <i class="fa-solid fa-unlock"></i>'
                            '</a>',
                record.pk,
            )

        return format_html(
            '{}{}{}',
            format_html(
                '<a href="/users/{}/reset-password" class="btn btn-sm btn-dark me-1"'
                            '  data-bs-toggle="tooltip" data-bs-placement="top" title="Reset Password">'
                            '  <i class="fa-solid fa-rotate"></i>'
                            '</a>',
                record.pk,
            ),
            toggle_btn,
            format_html(
                '<a href="/users/{}/delete" class="btn btn-sm btn-danger"'
                            ' data-bs-toggle="tooltip" data-bs-placement="top" title="Delete User">'
                            '  <i class="fa-solid fa-trash"></i>'
                            '</a>',
                record.pk,
            )
        )

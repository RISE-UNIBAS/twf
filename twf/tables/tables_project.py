import django_tables2 as tables
from twf.models import Task, Prompt
from django.utils.html import format_html
from django.utils.timezone import localtime

class TaskTable(tables.Table):
    title = tables.Column(verbose_name="Task")
    status = tables.Column()
    user = tables.Column(verbose_name="Started By")
    start_time = tables.DateTimeColumn(verbose_name="Start", format="Y-m-d H:i")
    end_time = tables.DateTimeColumn(verbose_name="End", format="Y-m-d H:i")
    progress = tables.Column(empty_values=())

    actions = tables.Column(empty_values=(), verbose_name="Options")

    def render_status(self, value):
        class_map = {
            "SUCCESS": "success",
            "FAILURE": "danger",
            "STARTED": "info",
            "PENDING": "secondary",
            "CANCELLED": "dark",
        }
        color = class_map.get(value.upper(), "secondary")
        return format_html('<span class="badge bg-{}">{}</span>', color, value.capitalize())

    def render_progress(self, record):
        if record.status == "STARTED":
            return format_html(
                '<div class="progress" style="height: 20px;"><div class="progress-bar progress-bar-striped progress-bar-animated bg-dark" '
                'role="progressbar" style="width: {}%">{}</div></div>',
                record.progress,
                f"{record.progress}%",
            )
        return "-"

    def render_actions(self, record):
        return format_html(
            '<a href="#" class="btn btn-sm btn-outline-dark me-1" title="View"><i class="fa fa-eye"></i></a>'
            '<a href="#" class="btn btn-sm btn-outline-danger me-1" title="Cancel"><i class="fa fa-ban"></i></a>'
            '<a href="#" class="btn btn-sm btn-outline-secondary" title="Remove"><i class="fa fa-trash"></i></a>'
        )

    class Meta:
        model = Task
        template_name = "django_tables2/bootstrap4.html"
        fields = ("title", "status", "user", "start_time", "end_time", "progress")



class PromptTable(tables.Table):
    system_role = tables.Column(verbose_name="Role", attrs={"td": {"class": "fw-bold"}})

    prompt_preview = tables.Column(empty_values=(), verbose_name="Prompt")

    created_at = tables.DateTimeColumn(format="Y-m-d H:i", verbose_name="Created")
    modified_at = tables.DateTimeColumn(format="Y-m-d H:i", verbose_name="Modified")

    actions = tables.Column(empty_values=(), verbose_name="Options")

    class Meta:
        model = Prompt
        fields = ("system_role", "prompt_preview", "created_at", "modified_at")
        attrs = {"class": "table table-striped table-hover table-sm"}

    def render_prompt_preview(self, record):
        return format_html('<span title="{}">{}</span>', record.prompt,
                           record.prompt[:80] + "..." if len(record.prompt) > 80 else record.prompt)

    def render_actions(self, record):
        return format_html(
            '<a href="{}" class="btn btn-sm btn-outline-dark me-1" title="View"><i class="fa fa-eye"></i></a>'
            '<a href="{}" class="btn btn-sm btn-outline-secondary me-1" title="Edit"><i class="fa fa-edit"></i></a>'
            '<a href="{}" class="btn btn-sm btn-outline-danger" title="Delete"><i class="fa fa-trash"></i></a>',
            f"/prompt/{record.pk}/view",
            f"/prompt/{record.pk}/edit",
            f"/prompt/{record.pk}/delete",
        )

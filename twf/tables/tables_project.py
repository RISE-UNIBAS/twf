import django_tables2 as tables
from twf.models import Task, Prompt, Note
from django.utils.html import format_html

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
        if record.status in ["STARTED", "PROGRESS"]:
            return format_html(
                '<div class="progress" style="height: 20px;"><div class="progress-bar progress-bar-striped progress-bar-animated bg-dark" '
                'role="progressbar" style="width: {}%">{}</div></div>',
                record.progress,
                f"{record.progress}%",
            )
        elif record.status == "SUCCESS":
            return format_html(
                '<div class="progress" style="height: 20px;"><div class="progress-bar bg-success" '
                'role="progressbar" style="width: 100%">Completed</div></div>'
            )
        elif record.status == "FAILURE":
            return format_html(
                '<div class="progress" style="height: 20px;"><div class="progress-bar bg-danger" '
                'role="progressbar" style="width: 100%">Failed</div></div>'
            )
        elif record.status == "CANCELED":
            return format_html(
                '<div class="progress" style="height: 20px;"><div class="progress-bar bg-dark" '
                'role="progressbar" style="width: 100%">Cancelled</div></div>'
            )
        return "-"

    def render_actions(self, record):
        from django.urls import reverse
        view_url = reverse('twf:task_detail', kwargs={'pk': record.pk})
        cancel_url = reverse('twf:celery_task_cancel', kwargs={'task_id': record.pk})
        remove_url = reverse('twf:celery_task_remove', kwargs={'task_id': record.pk})
        
        # Only show cancel button for tasks that are in progress
        cancel_button = ''
        if record.status in ['STARTED', 'PENDING', 'PROGRESS']:
            cancel_button = format_html(
                '<a href="#" class="btn btn-sm btn-warning me-1 show-confirm-modal" '
                'data-redirect-url="{}" '
                'data-message="Are you sure you want to cancel this task? This will interrupt any ongoing processing." '
                'title="Cancel Task"><i class="fa fa-ban"></i></a>',
                cancel_url
            )
        
        # Delete button uses the danger modal - only show for completed or cancelled tasks
        delete_button = ''
        if record.status in ['SUCCESS', 'FAILURE', 'CANCELED']:  
            delete_button = format_html(
                '<a href="#" class="btn btn-sm btn-danger show-danger-modal" '
                'data-redirect-url="{}" '
                'data-message="Are you sure you want to remove this task? This action cannot be undone." '
                'title="Remove Task"><i class="fa fa-trash"></i></a>',
                remove_url
            )
        
        # View button stays the same
        view_button = format_html(
            '<a href="{}" class="btn btn-sm btn-dark me-1" title="View Details"><i class="fa fa-eye"></i></a>',
            view_url
        )
        
        return format_html(
            '{}{}{}'.format(view_button, cancel_button, delete_button)
        )

    class Meta:
        model = Task
        template_name = "django_tables2/bootstrap4.html"
        fields = ("title", "status", "user", "start_time", "end_time", "progress")
        attrs = {"class": "table table-striped table-hover"}



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
            '<a href="{}" class="btn btn-sm btn-dark me-1" title="View"><i class="fa fa-eye"></i></a>'
            '<a href="{}" class="btn btn-sm btn-secondary me-1" title="Edit"><i class="fa fa-edit"></i></a>'
            '<a href="{}" class="btn btn-sm btn-danger" title="Delete"><i class="fa fa-trash"></i></a>',
            f"/prompt/{record.pk}/view",
            f"/prompt/{record.pk}/edit",
            f"/prompt/{record.pk}/delete",
        )


class NoteTable(tables.Table):
    note = tables.Column(verbose_name="Note")
    created_at = tables.DateTimeColumn(format="Y-m-d H:i", verbose_name="Created")
    modified_at = tables.DateTimeColumn(format="Y-m-d H:i", verbose_name="Modified")

    actions = tables.Column(empty_values=(), verbose_name="Options")

    class Meta:
        model = Note
        fields = ("note", "created_at", "modified_at")
        attrs = {"class": "table table-striped table-hover table-sm"}

    def render_note(self, record):
        return format_html('<span>{}</span>',
                           record.prompt[:80] + "..." if len(record.prompt) > 80 else record.prompt)

    def render_actions(self, record):
        return format_html(
            '<a href="{}" class="btn btn-sm btn-dark me-1" title="View"><i class="fa fa-eye"></i></a>'
            '<a href="{}" class="btn btn-sm btn-secondary me-1" title="Edit"><i class="fa fa-edit"></i></a>'
            '<a href="{}" class="btn btn-sm btn-danger" title="Delete"><i class="fa fa-trash"></i></a>',
            f"/prompt/{record.pk}/view",
            f"/prompt/{record.pk}/edit",
            f"/prompt/{record.pk}/delete",
        )
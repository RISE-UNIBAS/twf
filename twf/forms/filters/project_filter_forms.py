from django import forms

from twf.models import User, Task


class TaskFilterForm(forms.Form):
    """Form for filtering tasks."""

    started_by = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Started by",
    )
    status = forms.ChoiceField(
        choices=[("", "All")] + Task.TASK_STATUS_CHOICES,
        required=False,
        label="Status",
    )
    date_range = forms.ChoiceField(
        choices=[
            ("", "All time"),
            ("last_week", "Last week"),
            ("last_month", "Last month"),
            ("last_year", "Last year"),
        ],
        required=False,
        label="Date Range",
    )


class PromptFilterForm(forms.Form):
    """Form for filtering prompts."""

    system_role = forms.CharField(
        required=False,
        label="System Role",
        widget=forms.TextInput(attrs={"placeholder": "Enter system role"}),
    )
    prompt = forms.CharField(
        required=False,
        label="Prompt",
        widget=forms.TextInput(attrs={"placeholder": "Enter prompt"}),
    )

"""Forms for managing AI configurations."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML
from django import forms

from twf.models import AIConfiguration


class AIConfigurationForm(forms.ModelForm):
    """Form for creating/editing AI configurations."""

    class Meta:
        model = AIConfiguration
        fields = [
            "name",
            "description",
            "provider",
            "model",
            "api_key",
            "system_role",
            "prompt_template",
            "temperature",
            "max_tokens",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
            "seed",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "provider": forms.Select(attrs={"class": "form-control"}),
            "model": forms.TextInput(attrs={"class": "form-control"}),
            "api_key": forms.PasswordInput(
                attrs={"class": "form-control", "render_value": True}
            ),
            "system_role": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
            "prompt_template": forms.Textarea(
                attrs={"class": "form-control", "rows": 8}
            ),
            "temperature": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "min": "0", "max": "2"}
            ),
            "max_tokens": forms.NumberInput(
                attrs={"class": "form-control", "min": "1"}
            ),
            "top_p": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "min": "0", "max": "1"}
            ),
            "frequency_penalty": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "min": "-2", "max": "2"}
            ),
            "presence_penalty": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "min": "-2", "max": "2"}
            ),
            "seed": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add help text
        self.fields["prompt_template"].help_text = (
            "Use {placeholders} for context variables. "
            "Common placeholders: {document_text}, {page_text}, {tag_variation}, "
            "{collection_item_text}, {metadata}"
        )

        # Set up crispy forms
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "Configuration Identity",
                "name",
                "description",
            ),
            Fieldset(
                "Provider & Model",
                Row(
                    Column("provider", css_class="col-md-6"),
                    Column("model", css_class="col-md-6"),
                ),
                "api_key",
            ),
            Fieldset(
                "Prompt Configuration",
                "system_role",
                "prompt_template",
            ),
            Fieldset(
                "Execution Settings",
                Row(
                    Column("temperature", css_class="col-md-4"),
                    Column("max_tokens", css_class="col-md-4"),
                    Column("top_p", css_class="col-md-4"),
                ),
                Row(
                    Column("frequency_penalty", css_class="col-md-6"),
                    Column("presence_penalty", css_class="col-md-6"),
                ),
                "seed",
            ),
            Fieldset(
                "Status",
                HTML(
                    '<div class="form-check">'
                    '<input type="checkbox" class="form-check-input" name="is_active" id="id_is_active"'
                    '{% if form.is_active.value %}checked{% endif %}>'
                    '<label class="form-check-label" for="id_is_active">'
                    "Active (visible in workflow selectors)"
                    "</label>"
                    "</div>"
                ),
            ),
            Submit("submit", "Save Configuration", css_class="btn btn-primary mt-3"),
        )


class AIConfigurationTestForm(forms.Form):
    """Form for testing an AI configuration with sample context."""

    test_context = forms.JSONField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 10}),
        help_text="Provide JSON context variables for testing. "
        'Example: {"document_text": "Sample text to analyze"}',
        initial={},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "test_context",
            Submit("test", "Test Configuration", css_class="btn btn-success"),
        )

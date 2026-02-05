"""Forms for creating and updating documents."""

from crispy_forms.layout import Row, Column
from django import forms

from twf.forms.base_batch_forms import BaseMultiModalAIBatchForm


class DocumentBatchAIForm(BaseMultiModalAIBatchForm):
    """Form for running a batch of documents through OpenAI."""

    REQUEST_LEVEL_CHOICES = [("document", "Document"), ("page", "Page")]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        super().__init__(*args, **kwargs)
        self.fields["request_level"] = forms.ChoiceField(
            label="Request Level",
            choices=self.REQUEST_LEVEL_CHOICES,
            initial="document",
            help_text="Select the level of detail for the request.",
        )

    def get_dynamic_fields(self):
        fields = super().get_dynamic_fields()
        fields.append(
            Row(
                Column("request_level", css_class="form-group col-12 mb-0"),
                css_class="row form-row",
            )
        )
        return fields


class UnifiedDocumentBatchAIForm(DocumentBatchAIForm):
    """
    Unified form for batch processing documents with any AI provider.

    This form provides a dropdown to select from available AI providers
    and dynamically adjusts multimodal support based on the selected provider.
    """

    # Provider configuration with multimodal support flags
    PROVIDER_CONFIG = {
        "openai": {"label": "OpenAI (ChatGPT)", "multimodal": True},
        "genai": {"label": "Google Gemini", "multimodal": True},
        "anthropic": {"label": "Anthropic Claude", "multimodal": True},
        "mistral": {"label": "Mistral", "multimodal": False},
        "deepseek": {"label": "DeepSeek", "multimodal": True},
        "qwen": {"label": "Qwen", "multimodal": True},
    }

    ai_provider = forms.ChoiceField(
        label="AI Provider",
        required=True,
        help_text="Select the AI provider to use for batch processing.",
        widget=forms.Select(attrs={"class": "form-select", "style": "width: 100%;"}),
    )

    model = forms.CharField(
        label="Model",
        required=True,
        help_text="The AI model to use (e.g., gpt-4o, claude-3-5-sonnet-20241022, gemini-2.0-flash-exp).",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "width: 100%;",
                "placeholder": "Model name",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the unified document batch AI form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Extract project to check enabled providers
        project = kwargs.get("project")

        # Determine multimodal support based on provider (if specified in data)
        provider = None
        if args and isinstance(args[0], dict):
            provider = args[0].get("ai_provider")
        elif "data" in kwargs and kwargs["data"]:
            provider = kwargs["data"].get("ai_provider")

        # Set multimodal support based on provider
        if provider and provider in self.PROVIDER_CONFIG:
            kwargs["multimodal_support"] = self.PROVIDER_CONFIG[provider]["multimodal"]
        else:
            # Default to True for initial form display
            kwargs["multimodal_support"] = True

        super().__init__(*args, **kwargs)

        # Build provider choices based on project configuration
        if project:
            display_conf = project.conf_display.get("ai_providers", {})
            enabled_providers = []

            for provider_key, provider_info in self.PROVIDER_CONFIG.items():
                # Check if provider is enabled (default to True if not specified)
                provider_enabled_key = f"enable_{provider_key.replace('genai', 'gemini').
                replace('anthropic', 'claude')}"
                if display_conf.get(provider_enabled_key, True):
                    enabled_providers.append((provider_key, provider_info["label"]))

            self.fields["ai_provider"].choices = enabled_providers
        else:
            # Fallback to all providers if no project
            self.fields["ai_provider"].choices = [
                (key, info["label"]) for key, info in self.PROVIDER_CONFIG.items()
            ]

        # Set default model from credentials if available
        if project and provider:
            creds = project.get_credentials(provider)
            if creds and "default_model" in creds and creds["default_model"]:
                self.fields["model"].initial = creds["default_model"]

    def get_button_label(self):
        """
        Get the label for the submit button.

        Returns:
            str: The button label.
        """
        return "Run AI Batch"

    def get_dynamic_fields(self):
        """
        Get the dynamic fields for the form.

        Returns:
            list: A list of form field layouts including provider selection.
        """
        # Add provider and model selection at the top
        provider_fields = [
            Row(
                Column("ai_provider", css_class="form-group col-6 mb-3"),
                Column("model", css_class="form-group col-6 mb-3"),
                css_class="row form-row",
            ),
        ]
        # Then add parent fields (prompt, role, request_level, etc.)
        return provider_fields + super().get_dynamic_fields()

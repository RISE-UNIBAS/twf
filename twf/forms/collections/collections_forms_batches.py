from crispy_forms.layout import Row, Column
from django import forms

from twf.forms.base_batch_forms import BaseAIBatchForm
from twf.models import Collection


class CollectionBatchForm(BaseAIBatchForm):
    """Form for batch processing Geonames data."""

    collection = forms.ModelChoiceField(
        queryset=Collection.objects.none(),
        label="Collection",
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["collection"].choices = [("", "Select a Collection")] + [
            (c.pk, c.title) for c in Collection.objects.filter(project=self.project)
        ]

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return super().get_dynamic_fields() + [
            Row(
                Column("collection", css_class="form-group col-12 mb-3"),
                css_class="row form-row",
            )
        ]

    def get_button_label(self):
        """Get the label for the submit button."""
        return "Start Batch"


class UnifiedCollectionAIBatchForm(CollectionBatchForm):
    """
    Unified form for AI batch processing of collections.

    This form provides a dropdown to select from available AI providers
    for automated batch processing of collection items.
    """

    # Provider configuration (only 4 providers for collections)
    PROVIDER_CONFIG = {
        "openai": {"label": "OpenAI (ChatGPT)"},
        "genai": {"label": "Google Gemini"},
        "anthropic": {"label": "Anthropic Claude"},
        "mistral": {"label": "Mistral"},
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
        Initialize the unified collection AI batch form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        # Build provider choices based on project configuration
        project = kwargs.get("project") or self.project
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
        provider = None
        if args and isinstance(args[0], dict):
            provider = args[0].get("ai_provider")
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
        return "Start AI Batch"

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
        # Then add parent fields (prompt, role, collection)
        return provider_fields + super().get_dynamic_fields()


class UnifiedCollectionAIRequestForm(CollectionBatchForm):
    """
    Unified form for AI request (supervised) processing of collection items.

    This form provides a dropdown to select from available AI providers
    for supervised, single-item processing of collection items.
    """

    # Provider configuration (same 4 providers)
    PROVIDER_CONFIG = {
        "openai": {"label": "OpenAI (ChatGPT)"},
        "genai": {"label": "Google Gemini"},
        "anthropic": {"label": "Anthropic Claude"},
        "mistral": {"label": "Mistral"},
    }

    ai_provider = forms.ChoiceField(
        label="AI Provider",
        required=True,
        help_text="Select the AI provider to use for this request.",
        widget=forms.Select(attrs={"class": "form-select", "style": "width: 100%;"}),
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the unified collection AI request form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        # Build provider choices based on project configuration
        project = kwargs.get("project") or self.project
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
        provider = None
        if args and isinstance(args[0], dict):
            provider = args[0].get("ai_provider")
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
        return "Send AI Request"

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
        # Then add parent fields (prompt, role, collection)
        return provider_fields + super().get_dynamic_fields()

"""
Project batch processing forms.

This module contains forms for project-level batch processing operations,
including document extraction, project copying, and AI queries with multimodal support.
"""

from crispy_forms.layout import Row, Column
from django import forms
from django_select2.forms import Select2MultipleWidget

from twf.forms.base_batch_forms import BaseBatchForm, BaseMultiModalAIBatchForm
from twf.models import Document


class TranskribusEnrichmentBatchForm(BaseBatchForm):
    """
    Form for enriching documents with Transkribus API metadata.

    This form provides the interface for fetching additional document and page metadata
    (labels, tags, excluded status) from the Transkribus API that is not available in
    the PageXML export.
    """

    force = forms.BooleanField(
        label='Force Re-Enrichment',
        required=False,
        initial=False,
        help_text='If checked, re-fetch API metadata even for documents that already have it. '
                  'Leave unchecked to only enrich documents without existing API metadata.'
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the enrichment form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        """
        Get the label for the submit button.

        Returns:
            str: The button label.
        """
        return 'Enrich with API Metadata'

    def get_dynamic_fields(self):
        """
        Get the dynamic fields for the form.

        Returns:
            list: A list of form field layouts.
        """
        return [
            Row(
                Column('force', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            )
        ]


class DocumentExtractionBatchForm(BaseBatchForm):
    """
    Form for extracting documents from a Transkribus export with smart sync.

    This form provides the interface for the unified synchronization of documents,
    pages, and tags from Transkribus exports. It includes options to control the
    sync behavior.
    """

    force_recreate_tags = forms.BooleanField(
        label='Force Recreate All Tags',
        required=False,
        initial=False,
        help_text='If checked, all tags will be deleted and recreated from scratch. '
                  'This will lose all dictionary assignments and parked statuses. '
                  'Leave unchecked to use smart sync that preserves user work.'
    )

    delete_removed_documents = forms.BooleanField(
        label='Delete Documents Not in Export',
        required=False,
        initial=True,
        help_text='If checked, documents that exist in the database but are not found '
                  'in the Transkribus export will be deleted. Uncheck to keep all existing documents.'
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the document extraction form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        """
        Get the label for the submit button.

        Returns:
            str: The button label.
        """
        return 'Synchronize Transkribus Export'

    def get_dynamic_fields(self):
        """
        Get the dynamic fields for the form.

        Returns:
            list: A list of form field layouts.
        """
        return [
            Row(
                Column('force_recreate_tags', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('delete_removed_documents', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            )
        ]


class ProjectCopyBatchForm(BaseBatchForm):
    """
    Form for copying a project.

    This form provides the interface for creating a copy of an existing project.
    """
    new_project_name = forms.CharField(label='New Project Name', required=True,
                                        help_text='Please enter a name for the new project. Must be unique.',
                                        widget=forms.TextInput(attrs={'style': 'width: 100%;'}))

    def __init__(self, *args, **kwargs):
        """
        Initialize the project copy form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        # Set the initial value for the new project name
        self.fields['new_project_name'].initial = f"{self.project.title} (Copy)"

    def get_button_label(self):
        """
        Get the label for the submit button.

        Returns:
            str: The button label.
        """
        return 'Copy Project'

    def get_dynamic_fields(self):
        """
        Get the dynamic fields for the form.

        Returns:
            list: A list of form field layouts.
        """
        return [
            Row(
                Column('new_project_name', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            )
        ]


class ProjectAIBaseForm(BaseMultiModalAIBatchForm):
    """
    Base form for querying AI models with project documents and optional images.

    This form extends the multimodal AI batch form with project-specific functionality
    for selecting documents to include in AI queries.
    """

    documents = forms.ModelMultipleChoiceField(label='Documents', required=True,
                                               help_text='Please select the documents to query.',
                                               widget=Select2MultipleWidget(attrs={'style': 'width: 100%;'}),
                                               queryset=Document.objects.none())

    def __init__(self, *args, **kwargs):
        """
        Initialize the project AI base form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
                multimodal_support (bool): Whether this form should include multimodal fields.
                                          Defaults to False. Provider-specific forms will override.
        """
        # Default to False - provider-specific forms will override as needed
        kwargs.setdefault('multimodal_support', False)
        super().__init__(*args, **kwargs)
        self.fields['documents'].queryset = Document.objects.filter(project=self.project)

    def get_dynamic_fields(self):
        """
        Get the dynamic fields for the form.

        Returns:
            list: A list of form field layouts including document selection.
        """
        return super().get_dynamic_fields() + [
            Row(
                Column('documents', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
        ]

    def get_cancel_button_label(self):
        """
        Get the label for the cancel button.

        Returns:
            str: The cancel button label.
        """
        return 'Cancel'


class UnifiedAIQueryForm(ProjectAIBaseForm):
    """
    Unified form for querying any AI provider with dynamic provider selection.

    This form provides a dropdown to select from available AI providers
    and dynamically adjusts multimodal support based on the selected provider.
    """

    # Provider configuration with multimodal support flags
    PROVIDER_CONFIG = {
        'openai': {'label': 'OpenAI (ChatGPT)', 'multimodal': True},
        'genai': {'label': 'Google Gemini', 'multimodal': True},
        'anthropic': {'label': 'Anthropic Claude', 'multimodal': True},
        'mistral': {'label': 'Mistral', 'multimodal': False},
        'deepseek': {'label': 'DeepSeek', 'multimodal': True},
        'qwen': {'label': 'Qwen', 'multimodal': True},
    }

    ai_provider = forms.ChoiceField(
        label='AI Provider',
        required=True,
        help_text='Select the AI provider to use for this query.',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'width: 100%;'
        })
    )

    model = forms.CharField(
        label='Model',
        required=True,
        help_text='The AI model to use (e.g., gpt-4o, claude-3-5-sonnet-20241022, gemini-2.0-flash-exp).',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'width: 100%;',
            'placeholder': 'Model name'
        })
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the unified AI query form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Extract project to check enabled providers
        project = kwargs.get('project')

        # Determine multimodal support based on provider (if specified in data)
        provider = None
        if args and isinstance(args[0], dict):
            provider = args[0].get('ai_provider')
        elif 'data' in kwargs and kwargs['data']:
            provider = kwargs['data'].get('ai_provider')

        # Set multimodal support based on provider
        if provider and provider in self.PROVIDER_CONFIG:
            kwargs['multimodal_support'] = self.PROVIDER_CONFIG[provider]['multimodal']
        else:
            # Default to True for initial form display
            kwargs['multimodal_support'] = True

        super().__init__(*args, **kwargs)

        # Build provider choices based on project configuration
        if project:
            display_conf = project.conf_display.get('ai_providers', {})
            enabled_providers = []

            for provider_key, provider_info in self.PROVIDER_CONFIG.items():
                # Check if provider is enabled (default to True if not specified)
                provider_enabled_key = f"enable_{provider_key.replace('genai', 'gemini').replace('anthropic', 'claude')}"
                if display_conf.get(provider_enabled_key, True):
                    enabled_providers.append((provider_key, provider_info['label']))

            self.fields['ai_provider'].choices = enabled_providers
        else:
            # Fallback to all providers if no project
            self.fields['ai_provider'].choices = [
                (key, info['label']) for key, info in self.PROVIDER_CONFIG.items()
            ]

        # Set default model from credentials if available
        if project and provider:
            creds = project.get_credentials(provider)
            if creds and 'default_model' in creds and creds['default_model']:
                self.fields['model'].initial = creds['default_model']

    def get_button_label(self):
        """
        Get the label for the submit button.

        Returns:
            str: The button label.
        """
        return 'Ask AI'

    def get_dynamic_fields(self):
        """
        Get the dynamic fields for the form.

        Returns:
            list: A list of form field layouts including provider selection.
        """
        # Add provider and model selection at the top
        provider_fields = [
            Row(
                Column('ai_provider', css_class='form-group col-6 mb-3'),
                Column('model', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
        ]
        # Then add parent fields (prompt, role, etc.) and documents
        return provider_fields + super().get_dynamic_fields()

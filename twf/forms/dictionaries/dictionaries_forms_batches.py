"""Contains all forms concerning batch processes."""
from crispy_forms.layout import Row, Column
from django import forms
from django_select2.forms import Select2Widget

from twf.forms.base_batch_forms import BaseBatchForm, BaseAIBatchForm


class DictionaryBatchForm(BaseBatchForm):
    """ Base form for batches of dictionaries. """

    dictionary = forms.ChoiceField(label='Dictionary', required=True,
                                   widget=Select2Widget(attrs={'style': 'width: 100%;'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['dictionary'].choices = ([('', 'Select a dictionary')] +
                                             [(d.pk, d.label) for d in self.project.selected_dictionaries.all()])

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Batch'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return super().get_dynamic_fields() + [Row(
            Column('dictionary', css_class='form-group col-12 mb-0'),
            css_class='row form-row'
        )]


class DictionaryAIBatchForm(BaseAIBatchForm):
    """ Base form for batches of dictionaries. """

    dictionary = forms.ChoiceField(label='Dictionary', required=True,
                                   widget=Select2Widget(attrs={'style': 'width: 100%;'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['dictionary'].choices = ([('', 'Select a dictionary')] +
                                             [(d.pk, d.label) for d in self.project.selected_dictionaries.all()])

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Batch'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return super().get_dynamic_fields() + [Row(
            Column('dictionary', css_class='form-group col-12 mb-0'),
            css_class='row form-row'
        )]


class UnifiedDictionaryAIBatchForm(DictionaryAIBatchForm):
    """
    Unified form for AI batch processing of dictionary entries.

    This form provides a dropdown to select from available AI providers
    for automated batch processing of dictionary entries.
    """

    # Provider configuration (only 4 providers for dictionaries)
    PROVIDER_CONFIG = {
        'openai': {'label': 'OpenAI (ChatGPT)'},
        'genai': {'label': 'Google Gemini'},
        'anthropic': {'label': 'Anthropic Claude'},
        'mistral': {'label': 'Mistral'},
    }

    ai_provider = forms.ChoiceField(
        label='AI Provider',
        required=True,
        help_text='Select the AI provider to use for batch processing.',
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
        Initialize the unified dictionary AI batch form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        # Build provider choices based on project configuration
        project = kwargs.get('project') or self.project
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
        provider = None
        if args and isinstance(args[0], dict):
            provider = args[0].get('ai_provider')
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
        return 'Start AI Batch'

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
        # Then add parent fields (prompt, role, dictionary)
        return provider_fields + super().get_dynamic_fields()


class UnifiedDictionaryAIRequestForm(DictionaryAIBatchForm):
    """
    Unified form for AI request (supervised) processing of dictionary entries.

    This form provides a dropdown to select from available AI providers
    for supervised, single-entry processing of dictionary entries.
    """

    # Provider configuration (same 4 providers)
    PROVIDER_CONFIG = {
        'openai': {'label': 'OpenAI (ChatGPT)'},
        'genai': {'label': 'Google Gemini'},
        'anthropic': {'label': 'Anthropic Claude'},
        'mistral': {'label': 'Mistral'},
    }

    ai_provider = forms.ChoiceField(
        label='AI Provider',
        required=True,
        help_text='Select the AI provider to use for this request.',
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
        Initialize the unified dictionary AI request form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        # Build provider choices based on project configuration
        project = kwargs.get('project') or self.project
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
        provider = None
        if args and isinstance(args[0], dict):
            provider = args[0].get('ai_provider')
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
        return 'Send AI Request'

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
        # Then add parent fields (prompt, role, dictionary)
        return provider_fields + super().get_dynamic_fields()


class GeonamesBatchForm(DictionaryBatchForm):
    """Form for batch processing Geonames data."""

    only_search_in = forms.CharField(label='Only search in', required=False,
                                     help_text='Enter a country code (ISO-3166) to only search in that country.'
                                               'Leave empty to search in all countries.')
    similarity_threshold = forms.IntegerField(label='Similarity threshold', required=False,
                                              help_text='The similarity threshold for the search results. '
                                                        'Default is 80.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['similarity_threshold'].initial = 80

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Geonames Batch'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        fields = super().get_dynamic_fields()
        fields.append(Row(
            Column('only_search_in', css_class='form-group col-6 mb-0'),
            Column('similarity_threshold', css_class='form-group col-6 mb-0'),
            css_class='row form-row'
        ))
        return fields


class GNDBatchForm(DictionaryBatchForm):
    """Form for batch processing Geonames data."""

    earliest_birth_year = forms.IntegerField(label='Earliest Birth Year', required=False)
    latest_birth_year = forms.IntegerField(label='Latest Birth Year', required=False)
    show_empty = forms.BooleanField(label='Include results without birth dates/years', required=False)

    def get_button_label(self):
        return 'Start GND Batch'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        fields = super().get_dynamic_fields()
        fields.append(Row(
            Column('earliest_birth_year', css_class='form-group col-4 mb-0'),
            Column('latest_birth_year', css_class='form-group col-4 mb-0'),
            Column('show_empty', css_class='form-group col-4 mb-0'),
            css_class='row form-row'
        ))
        return fields


class WikidataBatchForm(DictionaryBatchForm):
    """Form for batch processing Geonames data."""

    entity_type = forms.ChoiceField(label='Entity Type', required=True,
                                    choices=[('city', 'City'), ('person', 'Person'), ('event', 'Event'),
                                             ('ship', 'Ship'), ('building', 'Building')],
                                    widget=Select2Widget(attrs={'style': 'width: 100%;'}))
    language = forms.CharField(label='Language', required=True, initial='en')

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Wikidata Batch'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        fields = super().get_dynamic_fields()
        fields.append(Row(
            Column('entity_type', css_class='form-group col-6 mb-0'),
            Column('language', css_class='form-group col-6 mb-0'),
            css_class='row form-row'
        ))
        return fields

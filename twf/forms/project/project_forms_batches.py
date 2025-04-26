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


class DocumentExtractionBatchForm(BaseBatchForm):
    """
    Form for extracting documents from a Transkribus export.
    
    This form provides the interface for the batch extraction of documents
    from Transkribus exports.
    """

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
        return 'Extract Documents From Transkribus Export'

    def get_dynamic_fields(self):
        """
        Get the dynamic fields for the form.
        
        Returns:
            list: A list of form field layouts.
        """
        return []


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


class OpenAIQueryDatabaseForm(ProjectAIBaseForm):
    """
    Form for querying OpenAI models with multimodal support.
    
    This form configures the project AI form for OpenAI models,
    enabling multimodal capabilities for GPT-4 Vision models.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the OpenAI query form.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # OpenAI supports multimodal 
        kwargs['multimodal_support'] = True
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        """
        Get the label for the submit button.
        
        Returns:
            str: The button label.
        """
        return 'Ask ChatGPT'


class GeminiQueryDatabaseForm(ProjectAIBaseForm):
    """
    Form for querying Google Gemini models with multimodal support.
    
    This form configures the project AI form for Google Gemini models,
    which have native multimodal capabilities.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the Gemini query form.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Gemini supports multimodal
        kwargs['multimodal_support'] = True
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        """
        Get the label for the submit button.
        
        Returns:
            str: The button label.
        """
        return 'Ask Gemini'


class ClaudeQueryDatabaseForm(ProjectAIBaseForm):
    """
    Form for querying Anthropic Claude models.
    
    This form configures the project AI form for Claude models.
    Multimodal support is currently disabled but will be enabled
    for Claude 3 models in a future update.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the Claude query form.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Temporarily disable multimodal for Claude
        kwargs['multimodal_support'] = True
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        """
        Get the label for the submit button.
        
        Returns:
            str: The button label.
        """
        return 'Ask Claude'


class MistralQueryDatabaseForm(ProjectAIBaseForm):
    """
    Form for querying Mistral models.
    
    This form configures the project AI form for Mistral models,
    which currently do not support multimodal inputs.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the Mistral query form.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Mistral doesn't support multimodal
        kwargs['multimodal_support'] = False
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        """
        Get the label for the submit button.
        
        Returns:
            str: The button label.
        """
        return 'Ask Mistral'


class DeepSeekQueryDatabaseForm(ProjectAIBaseForm):
    """
    Form for querying DeepSeek models.

    This form configures the project AI form for DeepSeek models,
    which currently do not support multimodal inputs.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the DeepSeek query form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # DeepSeek doesn't support multimodal
        kwargs['multimodal_support'] = True
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        """
        Get the label for the submit button.

        Returns:
            str: The button label.
        """
        return 'Ask DeepSeek'


class QwenQueryDatabaseForm(ProjectAIBaseForm):
    """
    Form for querying Qwen models.

    This form configures the project AI form for Qwen models,
    which currently do not support multimodal inputs.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the Qwen query form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Qwen doesn't support multimodal
        kwargs['multimodal_support'] = True
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        """
        Get the label for the submit button.

        Returns:
            str: The button label.
        """
        return 'Ask Qwen'

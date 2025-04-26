"""Forms for creating and updating documents."""
from crispy_forms.layout import Row, Column
from django import forms

from twf.forms.base_batch_forms import BaseMultiModalAIBatchForm


class DocumentBatchAIForm(BaseMultiModalAIBatchForm):
    """Form for running a batch of documents through OpenAI."""

    REQUEST_LEVEL_CHOICES = [
        ('document', 'Document'),
        ('page', 'Page')
    ]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        super().__init__(*args, **kwargs)
        self.fields['request_level'] = forms.ChoiceField(
            label='Request Level',
            choices=self.REQUEST_LEVEL_CHOICES,
            initial='document',
            help_text='Select the level of detail for the request.'
        )

    def get_dynamic_fields(self):
        fields = super().get_dynamic_fields()
        fields.append(
            Row(
                Column('request_level', css_class='form-group col-12 mb-0'),
                css_class='row form-row'
            )
        )
        return fields


class DocumentBatchOpenAIForm(DocumentBatchAIForm):
    """Form for running a batch of documents through OpenAI."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Run ChatGPT Batch'


class DocumentBatchGeminiForm(DocumentBatchAIForm):
    """Form for running a batch of documents through OpenAI."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Run Gemini Project Batch'


class DocumentBatchClaudeForm(DocumentBatchAIForm):
    """Form for running a batch of documents through OpenAI."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Run Claude Project Batch'


class DocumentBatchMistralForm(DocumentBatchAIForm):
    """Form for running a batch of documents through OpenAI."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Run Mistral Project Batch'


class DocumentBatchDeepSeekForm(DocumentBatchAIForm):
    """Form for running a batch of documents through DeepSeek."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Run DeepSeek Project Batch'


class DocumentBatchQwenForm(DocumentBatchAIForm):
    """Form for running a batch of documents through Qwen."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Run Qwen Project Batch'
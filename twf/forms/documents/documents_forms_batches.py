"""Forms for creating and updating documents."""
from crispy_forms.layout import Row, Column
from django import forms

from twf.forms.base_batch_forms import BaseAIBatchForm


class DocumentBatchOpenAIForm(BaseAIBatchForm):
    """Form for running a batch of documents through OpenAI."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Run ChatGPT Batch'


class DocumentBatchGeminiForm(BaseAIBatchForm):
    """Form for running a batch of documents through OpenAI."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Run Gemini Project Batch'


class DocumentBatchClaudeForm(BaseAIBatchForm):
    """Form for running a batch of documents through OpenAI."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Run Claude Project Batch'


class DocumentBatchMistralForm(BaseAIBatchForm):
    """Form for running a batch of documents through OpenAI."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Run Mistral Project Batch'
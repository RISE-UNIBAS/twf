"""Forms for creating and updating documents."""
from twf.forms.base_batch_forms import BaseAIBatchForm, BaseMultiModalAIBatchForm


class DocumentBatchOpenAIForm(BaseMultiModalAIBatchForm):
    """Form for running a batch of documents through OpenAI."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Run ChatGPT Batch'


class DocumentBatchGeminiForm(BaseMultiModalAIBatchForm):
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
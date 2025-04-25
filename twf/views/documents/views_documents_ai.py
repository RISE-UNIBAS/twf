"""Views for AI document processing."""
from django.urls import reverse_lazy

from twf.forms.documents.documents_forms_batches import DocumentBatchOpenAIForm, DocumentBatchGeminiForm, \
    DocumentBatchClaudeForm, DocumentBatchMistralForm
from twf.views.documents.views_documents import TWFDocumentView
from twf.views.views_base import AIFormView



class TWFDocumentOpenAIBatchView(AIFormView, TWFDocumentView):
    """Ask ChatGPT."""

    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'ChatGPT Batch'
    form_class = DocumentBatchOpenAIForm
    success_url = reverse_lazy('twf:documents_batch_openai')
    start_url = reverse_lazy('twf:task_documents_batch_openai')
    message = "Do you want to start the ChatGPT batch process now?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'ChatGPT Document Batch'
        context['ai_lead'] = ('ChatGPT will generate a separate response for each document by combining your '
                              'prompt with its content. All documents are processed in one batch.')
        context['has_ai_credentials'] = self.has_ai_credentials('openai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=openai'
        return context


class TWFDocumentGeminiBatchView(AIFormView, TWFDocumentView):
    """Ask Gemini."""

    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Gemini Batch'
    form_class = DocumentBatchGeminiForm
    success_url = reverse_lazy('twf:documents_batch_gemini')
    start_url = reverse_lazy('twf:task_documents_batch_gemini')
    message = "Are you sure you want to start the gemini task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Ask Gemini'
        context['ai_lead'] = ('Ask Gemini to generate text based on the provided prompt.'
                              'Your prompt will be expanded with the document text.')
        context['has_ai_credentials'] = self.has_ai_credentials('genai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=genai'
        return context


class TWFDocumentClaudeBatchView(AIFormView, TWFDocumentView):
    """Ask Claude."""

    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Claude Batch'
    form_class = DocumentBatchClaudeForm
    success_url = reverse_lazy('twf:documents_batch_claude')
    start_url = reverse_lazy('twf:task_documents_batch_claude')
    message = "Are you sure you want to start the claude task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Ask Claude'
        context['ai_lead'] = ('Ask Claude to generate text based on the provided prompt.'
                              'Your prompt will be expanded with the document text.')
        context['has_ai_credentials'] = self.has_ai_credentials('anthropic')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=anthropic'
        return context


class TWFDocumentMistralBatchView(AIFormView, TWFDocumentView):
    """Ask Mistral."""

    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Mistral Batch'
    form_class = DocumentBatchMistralForm
    success_url = reverse_lazy('twf:documents_batch_claude')
    start_url = reverse_lazy('twf:task_documents_batch_claude')
    message = "Are you sure you want to start the mistral task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Ask Mistral'
        context['ai_lead'] = ('Ask Mistral to generate text based on the provided prompt.'
                              'Your prompt will be expanded with the document text.')
        context['has_ai_credentials'] = self.has_ai_credentials('mistral')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=mistral'
        return context


class TWFDocumentOpenAIPageBatchView(AIFormView, TWFDocumentView):
    """Ask ChatGPT."""

    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'OpenAI Page Batch'
    form_class = DocumentBatchOpenAIForm
    success_url = reverse_lazy('twf:documents_page_batch_openai')
    start_url = reverse_lazy('twf:task_documents_page_batch_openai')
    message = "Are you sure you want to start the openai task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Ask ChatGPT'
        context['ai_lead'] = ('Ask ChatGPT to generate text based on the provided prompt.'
                              'Your prompt will be expanded with the page text.')
        context['has_ai_credentials'] = self.has_ai_credentials('openai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=openai'
        return context


class TWFDocumentGeminiPageBatchView(AIFormView, TWFDocumentView):
    """Ask Gemini."""

    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Gemini Batch'
    form_class = DocumentBatchGeminiForm
    success_url = reverse_lazy('twf:documents_page_batch_gemini')
    start_url = reverse_lazy('twf:task_documents_page_batch_gemini')
    message = "Are you sure you want to start the gemini task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Ask Gemini'
        context['ai_lead'] = ('Ask Gemini to generate text based on the provided prompt.'
                              'Your prompt will be expanded with the page text.')
        context['has_ai_credentials'] = self.has_ai_credentials('genai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=genai'
        return context


class TWFDocumentClaudePageBatchView(AIFormView, TWFDocumentView):
    """Ask Claude."""

    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Claude Batch'
    form_class = DocumentBatchClaudeForm
    success_url = reverse_lazy('twf:documents_page_batch_claude')
    start_url = reverse_lazy('twf:task_documents_page_batch_claude')
    message = "Are you sure you want to start the claude task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Ask Claude'
        context['ai_lead'] = ('Ask Claude to generate text based on the provided prompt.'
                              'Your prompt will be expanded with the page text.')
        context['has_ai_credentials'] = self.has_ai_credentials('anthropic')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=anthropic'
        return context


class TWFDocumentMistralPageBatchView(AIFormView, TWFDocumentView):
    """Ask Mistral."""

    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Mistral Batch'
    form_class = DocumentBatchMistralForm
    success_url = reverse_lazy('twf:documents_page_batch_mistral')
    start_url = reverse_lazy('twf:task_documents_page_batch_mistral')
    message = "Are you sure you want to start the mistral task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Ask Mistral'
        context['ai_lead'] = ('Ask Mistral to generate text based on the provided prompt.'
                              'Your prompt will be expanded with the page text.')
        context['has_ai_credentials'] = self.has_ai_credentials('mistral')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=mistral'
        return context

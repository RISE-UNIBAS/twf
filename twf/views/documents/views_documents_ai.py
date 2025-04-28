"""Views for AI document processing."""
from django.urls import reverse_lazy

from twf.forms.documents.documents_forms_batches import DocumentBatchOpenAIForm, DocumentBatchGeminiForm, \
    DocumentBatchClaudeForm, DocumentBatchMistralForm, DocumentBatchDeepSeekForm, DocumentBatchQwenForm
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
        context['supports_multimodal'] = True
        context['multimodal_info'] = 'The default ChatGPT-4o model supports text-only, image-only, and text+image modes.'
        return context


class TWFDocumentGeminiBatchView(AIFormView, TWFDocumentView):
    """Ask Gemini."""

    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Gemini Batch'
    form_class = DocumentBatchGeminiForm
    success_url = reverse_lazy('twf:documents_batch_gemini')
    start_url = reverse_lazy('twf:task_documents_batch_gemini')
    message = "Do you want to start the Gemini batch process now?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Gemini Document Batch'
        context['ai_lead'] = ('Gemini will generate a separate response for each document by combining your '
                              'prompt with its content. All documents are processed in one batch.')
        context['has_ai_credentials'] = self.has_ai_credentials('genai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=genai'
        context['supports_multimodal'] = True
        context['multimodal_info'] = 'Gemini supports text-only, image-only, and text+image modes.'
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
        context['supports_multimodal'] = True
        context['multimodal_info'] = 'Claude supports text-only, image-only, and text+image modes.'
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


class TWFDocumentDeepSeekBatchView(AIFormView, TWFDocumentView):
    """Ask DeepSeek."""

    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'DeepSeek Batch'
    form_class = DocumentBatchDeepSeekForm
    success_url = reverse_lazy('twf:documents_batch_deepseek')
    start_url = reverse_lazy('twf:task_documents_batch_deepseek')
    message = "Are you sure you want to start the DeepSeek task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Ask DeepSeek'
        context['ai_lead'] = ('Ask DeepSeek to generate text based on the provided prompt.'
                              'Your prompt will be expanded with the document text.')
        context['has_ai_credentials'] = self.has_ai_credentials('deepseek')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=deepseek'
        context['supports_multimodal'] = True
        context['multimodal_info'] = 'DeepSeek supports text-only, image-only, and text+image modes.'
        return context


class TWFDocumentQwenBatchView(AIFormView, TWFDocumentView):
    """Ask Qwen."""

    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Qwen Batch'
    form_class = DocumentBatchQwenForm
    success_url = reverse_lazy('twf:documents_batch_qwen')
    start_url = reverse_lazy('twf:task_documents_batch_qwen')
    message = "Are you sure you want to start the Qwen task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Ask Qwen'
        context['ai_lead'] = ('Ask Qwen to generate text based on the provided prompt.'
                              'Your prompt will be expanded with the document text.')
        context['has_ai_credentials'] = self.has_ai_credentials('qwen')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=qwen'
        context['supports_multimodal'] = True
        context['multimodal_info'] = 'Qwen supports text-only, image-only, and text+image modes.'
        return context


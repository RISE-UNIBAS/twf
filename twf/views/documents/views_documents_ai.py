"""Views for AI document processing."""
import logging

from django.urls import reverse_lazy
from django.views.generic import FormView

from twf.forms.documents.documents_forms_batches import DocumentBatchOpenAIForm, DocumentBatchGeminiForm, DocumentBatchClaudeForm
from twf.views.documents.views_documents import TWFDocumentView


logger = logging.getLogger(__name__)


class TWFDocumentOpenAIBatchView(FormView, TWFDocumentView):
    """Ask ChatGPT."""
    template_name = 'twf/documents/batches/openai_batch_query.html'
    page_title = 'Geonames Batch'
    form_class = DocumentBatchOpenAIForm
    success_url = reverse_lazy('twf:documents_batch_openai')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_documents_batch_openai')
        kwargs['data-message'] = "Are you sure you want to start the openai task?"

        return kwargs


class TWFDocumentGeminiBatchView(FormView, TWFDocumentView):
    """Ask Gemini."""
    template_name = 'twf/documents/batches/gemini_batch_query.html'
    page_title = 'Gemini Batch'
    form_class = DocumentBatchGeminiForm
    success_url = reverse_lazy('twf:documents_batch_gemini')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_documents_batch_gemini')
        kwargs['data-message'] = "Are you sure you want to start the gemini task?"

        return kwargs


class TWFDocumentClaudeBatchView(FormView, TWFDocumentView):
    """Ask Claude."""
    template_name = 'twf/documents/batches/claude_batch_query.html'
    page_title = 'Claude Batch'
    form_class = DocumentBatchClaudeForm
    success_url = reverse_lazy('twf:documents_batch_claude')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_documents_batch_claude')
        kwargs['data-message'] = "Are you sure you want to start the claude task?"

        return kwargs


class TWFDocumentOpenAIPageBatchView(FormView, TWFDocumentView):
    """Ask ChatGPT."""
    template_name = 'twf/documents/batches/openai_page_batch_query.html'
    page_title = 'OpenAI Page Batch'
    form_class = DocumentBatchOpenAIForm
    success_url = reverse_lazy('twf:documents_page_batch_openai')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_documents_page_batch_openai')
        kwargs['data-message'] = "Are you sure you want to start the openai task?"

        return kwargs


class TWFDocumentGeminiPageBatchView(FormView, TWFDocumentView):
    """Ask Gemini."""
    template_name = 'twf/documents/batches/gemini_page_batch_query.html'
    page_title = 'Gemini Batch'
    form_class = DocumentBatchGeminiForm
    success_url = reverse_lazy('twf:documents_page_batch_gemini')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_documents_page_batch_gemini')
        kwargs['data-message'] = "Are you sure you want to start the gemini task?"

        return kwargs


class TWFDocumentClaudePageBatchView(FormView, TWFDocumentView):
    """Ask Claude."""
    template_name = 'twf/documents/batches/claude_page_batch_query.html'
    page_title = 'Claude Batch'
    form_class = DocumentBatchClaudeForm
    success_url = reverse_lazy('twf:documents_page_batch_claude')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_documents_page_batch_claude')
        kwargs['data-message'] = "Are you sure you want to start the claude task?"

        return kwargs

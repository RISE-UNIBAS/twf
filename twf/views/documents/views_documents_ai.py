"""Views for AI document processing."""
from django.urls import reverse_lazy
from django.views.generic import FormView

from twf.forms.documents.documents_forms_batches import DocumentBatchOpenAIForm, DocumentBatchGeminiForm, DocumentBatchClaudeForm
from twf.views.documents.views_documents import TWFDocumentView
from twf.views.views_base import AIFormView


class TWFDocumentOpenAIBatchView(FormView, TWFDocumentView):
    """Ask ChatGPT."""
    template_name = 'twf/documents/batches/openai_batch_query.html'
    page_title = 'Geonames Batch'
    form_class = DocumentBatchOpenAIForm
    success_url = reverse_lazy('twf:documents_batch_openai')
    start_url = reverse_lazy('twf:task_documents_batch_openai')
    message = "Are you sure you want to start the openai task?"


class TWFDocumentGeminiBatchView(AIFormView, TWFDocumentView):
    """Ask Gemini."""
    template_name = 'twf/documents/batches/gemini_batch_query.html'
    page_title = 'Gemini Batch'
    form_class = DocumentBatchGeminiForm
    success_url = reverse_lazy('twf:documents_batch_gemini')
    start_url = reverse_lazy('twf:task_documents_batch_gemini')
    message = "Are you sure you want to start the gemini task?"


class TWFDocumentClaudeBatchView(AIFormView, TWFDocumentView):
    """Ask Claude."""
    template_name = 'twf/documents/batches/claude_batch_query.html'
    page_title = 'Claude Batch'
    form_class = DocumentBatchClaudeForm
    success_url = reverse_lazy('twf:documents_batch_claude')
    start_url = reverse_lazy('twf:task_documents_batch_claude')
    message = "Are you sure you want to start the claude task?"


class TWFDocumentOpenAIPageBatchView(AIFormView, TWFDocumentView):
    """Ask ChatGPT."""
    template_name = 'twf/documents/batches/openai_page_batch_query.html'
    page_title = 'OpenAI Page Batch'
    form_class = DocumentBatchOpenAIForm
    success_url = reverse_lazy('twf:documents_page_batch_openai')
    start_url = reverse_lazy('twf:task_documents_page_batch_openai')
    message = "Are you sure you want to start the openai task?"


class TWFDocumentGeminiPageBatchView(AIFormView, TWFDocumentView):
    """Ask Gemini."""
    template_name = 'twf/documents/batches/gemini_page_batch_query.html'
    page_title = 'Gemini Batch'
    form_class = DocumentBatchGeminiForm
    success_url = reverse_lazy('twf:documents_page_batch_gemini')
    start_url = reverse_lazy('twf:task_documents_page_batch_gemini')
    message = "Are you sure you want to start the gemini task?"


class TWFDocumentClaudePageBatchView(AIFormView, TWFDocumentView):
    """Ask Claude."""
    template_name = 'twf/documents/batches/claude_page_batch_query.html'
    page_title = 'Claude Batch'
    form_class = DocumentBatchClaudeForm
    success_url = reverse_lazy('twf:documents_page_batch_claude')
    start_url = reverse_lazy('twf:task_documents_page_batch_claude')
    message = "Are you sure you want to start the claude task?"

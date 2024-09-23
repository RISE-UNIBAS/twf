import logging

from django.http import JsonResponse

from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView

from twf.forms.project_forms import AIQueryDatabaseForm, BatchOpenAIForm
from twf.clients.simple_ai_clients import AiApiClient
from twf.views.documents.views_documents import TWFDocumentView
from twf.views.project.views_project import TWFProjectView
from twf.tasks.openai_tasks import ask_chatgpt_task

logger = logging.getLogger(__name__)


class TWFDocumentOpenAIBatchView(FormView, TWFDocumentView):
    """Ask ChatGPT."""
    template_name = 'twf/documents/batches/openai_batch_query.html'
    page_title = 'Geonames Batch'
    form_class = BatchOpenAIForm
    success_url = reverse_lazy('twf:documents_batch_openai')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs


class TWFDocumentGeminiBatchView(FormView, TWFDocumentView):
    """Ask Gemini."""
    template_name = 'twf/documents/batches/gemini_batch_query.html'
    page_title = 'Gemini Batch'
    form_class = BatchOpenAIForm
    success_url = reverse_lazy('twf:documents_batch_gemini')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs


class TWFDocumentClaudeBatchView(FormView, TWFDocumentView):
    """Ask Claude."""
    template_name = 'twf/documents/batches/claude_batch_query.html'
    page_title = 'Claude Batch'
    form_class = BatchOpenAIForm
    success_url = reverse_lazy('twf:documents_batch_claude')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs

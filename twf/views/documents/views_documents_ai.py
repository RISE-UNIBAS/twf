import logging

from django.http import JsonResponse

from django.contrib import messages
from django.shortcuts import render
from django.views.generic import FormView

from twf.forms.project_forms import AIQueryDatabaseForm, BatchOpenAIForm
from twf.clients.simple_ai_clients import AiApiClient
from twf.views.project.views_project import TWFProjectView
from twf.tasks.openai_tasks import ask_chatgpt_task

logger = logging.getLogger(__name__)


class TWFDocumentAIBatchView(FormView, TWFProjectView):
    template_name = 'twf/documents/batches/ai_batch_query.html'
    page_title = 'AI Query'
    form_class = BatchOpenAIForm
    results = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Add your custom argument here
        kwargs['project'] = self.get_project()
        return kwargs

    def form_valid(self, form):
        project = self.get_project()

        # Ensure form is valid before processing
        if form.is_valid():
            selection = form.cleaned_data['selection']
            role_description = form.cleaned_data['role_description']
            prompt = form.cleaned_data['prompt']

            # Correct project.id instead of project.d
            task = ask_chatgpt_task.delay(project.id, selection, role_description, prompt)

            return JsonResponse({'status': 'success', 'task_id': task.id})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    def form_invalid(self, form):
        # If form is invalid, return an error response
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

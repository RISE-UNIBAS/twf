""" Views for the AI model. """
from django.urls import reverse_lazy
from django.views.generic import FormView

from twf.forms.project.project_forms_batches import OpenAIQueryDatabaseForm, GeminiQueryDatabaseForm, ClaudeQueryDatabaseForm
from twf.views.project.views_project import TWFProjectView
from twf.views.views_base import AIFormView


class TWFProjectAIQueryView(AIFormView, TWFProjectView):
    """View for querying the AI model."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'OpenAI Query'
    form_class = OpenAIQueryDatabaseForm
    success_url = reverse_lazy('twf:project_ai_query')
    start_url = reverse_lazy('twf:task_project_query_openai')
    message = "Are you sure you want to start the openai task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'AI Query'
        context['ai_lead'] = 'Query the AI model for predictions.'
        return context


class TWFProjectGeminiQueryView(AIFormView, TWFProjectView):
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Gemini Query'
    form_class = GeminiQueryDatabaseForm
    success_url = reverse_lazy('twf:project_gemini_query')
    start_url = reverse_lazy('twf:task_project_query_gemini')
    message = "Are you sure you want to start the gemini task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Gemini Query'
        context['ai_lead'] = 'Query the Gemini model for predictions.'
        return context


class TWFProjectClaudeQueryView(AIFormView, TWFProjectView):
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Claude Query'
    form_class = ClaudeQueryDatabaseForm
    success_url = reverse_lazy('twf:project_claude_query')
    start_url = reverse_lazy('twf:task_project_query_claude')
    message = "Are you sure you want to start the claude task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Claude Query'
        context['ai_lead'] = 'Query the Claude model for predictions.'
        return context

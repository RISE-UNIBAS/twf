""" Views for the AI model. """
import logging

from django.urls import reverse_lazy
from django.views.generic import FormView

from twf.forms.project.project_forms_batches import OpenAIQueryDatabaseForm, GeminiQueryDatabaseForm, ClaudeQueryDatabaseForm
from twf.views.project.views_project import TWFProjectView

logger = logging.getLogger(__name__)


class TWFProjectAIQueryView(FormView, TWFProjectView):
    """View for querying the AI model.
    """

    template_name = 'twf/project/questions/ai_query.html'
    page_title = 'OpenAI Query'
    form_class = OpenAIQueryDatabaseForm
    success_url = reverse_lazy('twf:project_ai_query')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_project_query_openai')
        kwargs['data-message'] = "Are you sure you want to start the openai task?"

        return kwargs


class TWFProjectGeminiQueryView(FormView, TWFProjectView):
    template_name = 'twf/project/questions/gemini_query.html'
    page_title = 'Gemini Query'
    form_class = GeminiQueryDatabaseForm
    success_url = reverse_lazy('twf:project_gemini_query')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_project_query_gemini')
        kwargs['data-message'] = "Are you sure you want to start the gemini task?"

        return kwargs


class TWFProjectClaudeQueryView(FormView, TWFProjectView):
    template_name = 'twf/project/questions/claude_query.html'
    page_title = 'Claude Query'
    form_class = ClaudeQueryDatabaseForm
    success_url = reverse_lazy('twf:project_claude_query')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_project_query_claude')
        kwargs['data-message'] = "Are you sure you want to start the claude task?"

        return kwargs

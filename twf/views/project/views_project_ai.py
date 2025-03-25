""" Views for the AI model. """
from django.urls import reverse_lazy

from twf.forms.project.project_forms_batches import OpenAIQueryDatabaseForm, GeminiQueryDatabaseForm, \
    ClaudeQueryDatabaseForm
from twf.views.project.views_project import TWFProjectView
from twf.views.views_base import AIFormView


class TWFProjectAIQueryView(AIFormView, TWFProjectView):
    """View for querying the AI model."""
    template_name = 'twf/project/query/openai.html'
    page_title = 'Ask ChatGPT'
    form_class = OpenAIQueryDatabaseForm
    success_url = reverse_lazy('twf:project_ai_query')
    start_url = reverse_lazy('twf:task_project_query_openai')
    message = "Are you sure you want to start the openai task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = self.page_title
        context['ai_lead'] = ('Query the OpenAI model for predictions.'
                              'Select documents to ask the AI model questions.')
        context['has_ai_credentials'] = self.has_ai_credentials('openai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=openai'
        return context


class TWFProjectGeminiQueryView(AIFormView, TWFProjectView):
    template_name = 'twf/project/query/gemini.html'
    page_title = 'Ask Gemini'
    form_class = GeminiQueryDatabaseForm
    success_url = reverse_lazy('twf:project_gemini_query')
    start_url = reverse_lazy('twf:task_project_query_gemini')
    message = "Are you sure you want to start the gemini task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = self.page_title
        context['ai_lead'] = ('Query the Gemini model for predictions.'
                              'Select documents to ask the AI model questions.')
        context['has_ai_credentials'] = self.has_ai_credentials('genai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=genai'
        return context


class TWFProjectClaudeQueryView(AIFormView, TWFProjectView):
    template_name = 'twf/project/query/claude.html'
    page_title = 'Ask Claude'
    form_class = ClaudeQueryDatabaseForm
    success_url = reverse_lazy('twf:project_claude_query')
    start_url = reverse_lazy('twf:task_project_query_claude')
    message = "Are you sure you want to start the claude task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = self.page_title
        context['ai_lead'] = ('Query the Claude model for predictions.'
                              'Select documents to ask the AI model questions.')
        context['has_ai_credentials'] = self.has_ai_credentials('anthropic')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=anthropic'
        return context


class TWFProjectMistralQueryView(AIFormView, TWFProjectView):
    template_name = 'twf/project/query/mistral.html'
    page_title = 'Ask Mistral'
    form_class = ClaudeQueryDatabaseForm
    success_url = reverse_lazy('twf:project_mistral_query')
    start_url = reverse_lazy('twf:task_project_query_mistral')
    message = "Are you sure you want to start the mistral task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = self.page_title
        context['ai_lead'] = ('Query the Mistral model for predictions.'
                              'Select documents to ask the AI model questions.')
        context['has_ai_credentials'] = self.has_ai_credentials('mistral')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=mistral'
        return context
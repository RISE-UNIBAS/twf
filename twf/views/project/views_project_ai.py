""" Views for the AI model. """
from django.urls import reverse_lazy

from twf.forms.project.project_forms_batches import OpenAIQueryDatabaseForm, GeminiQueryDatabaseForm, \
    ClaudeQueryDatabaseForm, MistralQueryDatabaseForm
from twf.views.project.views_project import TWFProjectView
from twf.views.views_base import AIFormView


class TWFProjectAIQueryView(AIFormView, TWFProjectView):
    """View for querying the AI model."""
    template_name = 'twf/project/query/openai.html'
    page_title = 'Ask ChatGPT'
    form_class = OpenAIQueryDatabaseForm
    success_url = reverse_lazy('twf:project_ai_query')
    start_url = reverse_lazy('twf:task_project_query_openai')
    message = "Do you want to go ahead and ask ChatGPT this question?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = self.page_title
        context['ai_lead'] = 'Use OpenAI models to answer questions about your documents. GPT-4 Vision models support both text and images.'
        context['has_ai_credentials'] = self.has_ai_credentials('openai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=openai'
        context['supports_multimodal'] = True
        context['multimodal_info'] = 'Supports text-only, images-only, or text+images modes. Use GPT-4 Vision models for image support.'
        return context


class TWFProjectGeminiQueryView(AIFormView, TWFProjectView):
    template_name = 'twf/project/query/gemini.html'
    page_title = 'Ask Gemini'
    form_class = GeminiQueryDatabaseForm
    success_url = reverse_lazy('twf:project_gemini_query')
    start_url = reverse_lazy('twf:task_project_query_gemini')
    message = "Are you sure you want to start the Gemini task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = self.page_title
        context['ai_lead'] = ('Query Google Gemini models for predictions. '
                              'All current Gemini models support multimodal input with both text and images.')
        context['has_ai_credentials'] = self.has_ai_credentials('genai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=genai'
        context['supports_multimodal'] = True
        context['multimodal_info'] = 'Supports text-only, images-only, or text+images modes. All Gemini models support images.'
        return context


class TWFProjectClaudeQueryView(AIFormView, TWFProjectView):
    template_name = 'twf/project/query/claude.html'
    page_title = 'Ask Claude'
    form_class = ClaudeQueryDatabaseForm
    success_url = reverse_lazy('twf:project_claude_query')
    start_url = reverse_lazy('twf:task_project_query_claude')
    message = "Are you sure you want to start the Claude task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = self.page_title
        context['ai_lead'] = ('Query Claude models for predictions. '
                              'Select documents to ask the AI model questions.')
        context['has_ai_credentials'] = self.has_ai_credentials('anthropic')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=anthropic'
        # Temporarily disable multimodal for Claude
        context['supports_multimodal'] = False
        context['multimodal_info'] = 'Currently limited to text-only mode. Image support is disabled in this version.'
        return context


class TWFProjectMistralQueryView(AIFormView, TWFProjectView):
    template_name = 'twf/project/query/mistral.html'
    page_title = 'Ask Mistral'
    form_class = MistralQueryDatabaseForm  # This is the text-only form
    success_url = reverse_lazy('twf:project_mistral_query')
    start_url = reverse_lazy('twf:task_project_query_mistral')
    message = "Are you sure you want to start the Mistral task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = self.page_title
        context['ai_lead'] = ('Query Mistral models for predictions. '
                              'Mistral models currently only support text input.')
        context['has_ai_credentials'] = self.has_ai_credentials('mistral')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=mistral'
        context['supports_multimodal'] = False
        context['multimodal_info'] = 'Limited to text-only mode. Mistral models do not support image input.'
        return context
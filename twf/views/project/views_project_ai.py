"""
Views for AI model interactions.

This module contains views for interacting with various AI providers,
including OpenAI, Google Gemini, Anthropic Claude, and Mistral.
These views support both text-only and multimodal (text + images) interactions.
"""

from django.urls import reverse_lazy

from twf.forms.project.project_forms_batches import OpenAIQueryDatabaseForm, GeminiQueryDatabaseForm, \
    ClaudeQueryDatabaseForm, MistralQueryDatabaseForm, DeepSeekQueryDatabaseForm, QwenQueryDatabaseForm
from twf.views.project.views_project import TWFProjectView
from twf.views.views_base import AIFormView


class TWFProjectAIQueryView(AIFormView, TWFProjectView):
    """
    View for querying OpenAI models.
    
    This view provides an interface for querying OpenAI models with
    both text-only and multimodal (text + images) capabilities.
    """
    template_name = 'twf/project/query/openai.html'
    page_title = 'Ask ChatGPT'
    form_class = OpenAIQueryDatabaseForm
    success_url = reverse_lazy('twf:project_ai_query')
    start_url = reverse_lazy('twf:task_project_query_openai')
    message = "Do you want to go ahead and ask ChatGPT this question?"

    def get_context_data(self, **kwargs):
        """
        Get the context data for the template.
        
        This method adds OpenAI-specific context data, including multimodal support information.
        
        Args:
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = self.page_title
        context['ai_lead'] = "Use OpenAI's ChatGPT models to answer questions about your documents."
        context['has_ai_credentials'] = self.has_ai_credentials('openai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=openai'
        context['supports_multimodal'] = True
        context['multimodal_info'] = 'The default ChatGPT-4o model supports text-only, image-only, and text+image modes.'
        return context


class TWFProjectGeminiQueryView(AIFormView, TWFProjectView):
    """
    View for querying Google Gemini models.
    
    This view provides an interface for querying Google Gemini models with
    native multimodal (text + images) capabilities.
    """
    template_name = 'twf/project/query/gemini.html'
    page_title = 'Ask Gemini'
    form_class = GeminiQueryDatabaseForm
    success_url = reverse_lazy('twf:project_gemini_query')
    start_url = reverse_lazy('twf:task_project_query_gemini')
    message = "Are you sure you want to start the Gemini task?"

    def get_context_data(self, **kwargs):
        """
        Get the context data for the template.
        
        This method adds Gemini-specific context data, including multimodal support information.
        
        Args:
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            dict: The context data.
        """
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
    """
    View for querying Anthropic Claude models.
    
    This view provides an interface for querying Claude models.
    Multimodal support is temporarily disabled but will be enabled
    for Claude 3 models in a future update.
    """
    template_name = 'twf/project/query/claude.html'
    page_title = 'Ask Claude'
    form_class = ClaudeQueryDatabaseForm
    success_url = reverse_lazy('twf:project_claude_query')
    start_url = reverse_lazy('twf:task_project_query_claude')
    message = "Are you sure you want to start the Claude task?"

    def get_context_data(self, **kwargs):
        """
        Get the context data for the template.
        
        This method adds Claude-specific context data, including multimodal support information.
        
        Args:
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            dict: The context data.
        """
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
    """
    View for querying Mistral models.
    
    This view provides an interface for querying Mistral models,
    which currently only support text-only inputs.
    """
    template_name = 'twf/project/query/mistral.html'
    page_title = 'Ask Mistral'
    form_class = MistralQueryDatabaseForm  # This is the text-only form
    success_url = reverse_lazy('twf:project_mistral_query')
    start_url = reverse_lazy('twf:task_project_query_mistral')
    message = "Are you sure you want to start the Mistral task?"

    def get_context_data(self, **kwargs):
        """
        Get the context data for the template.
        
        This method adds Mistral-specific context data, including multimodal support information.
        
        Args:
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = self.page_title
        context['ai_lead'] = 'Query Mistral models for predictions.'
        context['has_ai_credentials'] = self.has_ai_credentials('mistral')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=mistral'
        context['supports_multimodal'] = False
        context['multimodal_info'] = 'Limited to text-only mode. Mistral models do not support image input.'
        return context


class TWFProjectDeepSeekQueryView(AIFormView, TWFProjectView):
    """
    View for querying DeepSeek models.

    This view provides an interface for querying Mistral models,
    which currently only support text-only inputs.
    """
    template_name = 'twf/project/query/deepseek.html'
    page_title = 'Ask DeepSeek'
    form_class = DeepSeekQueryDatabaseForm
    success_url = reverse_lazy('twf:project_deepseek_query')
    start_url = reverse_lazy('twf:task_project_query_deepseek')
    message = "Are you sure you want to start the DeepSeek task?"

    def get_context_data(self, **kwargs):
        """
        Get the context data for the template.
        """
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = self.page_title
        context['ai_lead'] = 'Query DeepSeek models for predictions.'
        context['has_ai_credentials'] = self.has_ai_credentials('deepseek')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=deepseek'
        context['supports_multimodal'] = False
        context['multimodal_info'] = 'Limited to text-only mode. DeepSeek models do not support image input.'
        return context


class TWFProjectQwenQueryView(AIFormView, TWFProjectView):
    """
    View for querying Qwen models.

    This view provides an interface for querying Mistral models,
    which currently only support text-only inputs.
    """
    template_name = 'twf/project/query/qwen.html'
    page_title = 'Ask Qwen'
    form_class = QwenQueryDatabaseForm
    success_url = reverse_lazy('twf:project_qwen_query')
    start_url = reverse_lazy('twf:task_project_query_qwen')
    message = "Are you sure you want to start the Qwen task?"

    def get_context_data(self, **kwargs):
        """
        Get the context data for the template.
        """
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = self.page_title
        context['ai_lead'] = 'Query Qwen models for predictions.'
        context['has_ai_credentials'] = self.has_ai_credentials('qwen')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=qwen'
        context['supports_multimodal'] = False
        context['multimodal_info'] = 'Limited to text-only mode. Qwen models do not support image input.'
        return context

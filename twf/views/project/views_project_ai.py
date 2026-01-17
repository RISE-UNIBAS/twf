"""
Views for AI model interactions.

This module contains views for interacting with various AI providers,
including OpenAI, Google Gemini, Anthropic Claude, and Mistral.
These views support both text-only and multimodal (text + images) interactions.
"""

import json
from django.urls import reverse_lazy

from twf.forms.project.project_forms_batches import OpenAIQueryDatabaseForm, GeminiQueryDatabaseForm, \
    ClaudeQueryDatabaseForm, MistralQueryDatabaseForm, DeepSeekQueryDatabaseForm, QwenQueryDatabaseForm, \
    UnifiedAIQueryForm
from twf.views.project.views_project import TWFProjectView
from twf.views.views_base import AIFormView


class TWFProjectAIQueryView(AIFormView, TWFProjectView):
    """
    View for querying OpenAI models.
    
    This view provides an interface for querying OpenAI models with
    both text-only and multimodal (text + images) capabilities.
    """
    template_name = 'twf/project/query/ai.html'
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
    template_name = 'twf/project/query/ai.html'
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
    template_name = 'twf/project/query/ai.html'
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
        context['supports_multimodal'] = True
        context['multimodal_info'] = 'Claude supports text-only, image-only, and text+image modes.'
        return context


class TWFProjectMistralQueryView(AIFormView, TWFProjectView):
    """
    View for querying Mistral models.
    
    This view provides an interface for querying Mistral models,
    which currently only support text-only inputs.
    """
    template_name = 'twf/project/query/ai.html'
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
    template_name = 'twf/project/query/ai.html'
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
        context['supports_multimodal'] = True
        context['multimodal_info'] = 'DeepSeek supports text-only, image-only, and text+image modes.'
        return context


class TWFProjectQwenQueryView(AIFormView, TWFProjectView):
    """
    View for querying Qwen models.

    This view provides an interface for querying Mistral models,
    which currently only support text-only inputs.
    """
    template_name = 'twf/project/query/ai.html'
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
        context['supports_multimodal'] = True
        context['multimodal_info'] = 'Qwen supports text-only, image-only, and text+image modes.'
        return context


class TWFUnifiedAIQueryView(AIFormView, TWFProjectView):
    """
    Unified view for querying any AI provider.

    This view provides a single interface for querying all supported AI providers.
    The provider is selected via a dropdown in the form, and the view dynamically
    handles credentials, task routing, and context based on the selected provider.
    """

    template_name = 'twf/project/query/ai.html'
    page_title = 'Ask AI'
    form_class = UnifiedAIQueryForm
    success_url = reverse_lazy('twf:project_ai_query_unified')
    message = "Do you want to proceed with this AI query?"

    # Provider configuration matching the form
    PROVIDER_CONFIG = {
        'openai': {
            'label': 'OpenAI (ChatGPT)',
            'task_url': 'twf:task_project_query_openai',
            'credentials_key': 'openai',
            'credentials_tab': 'openai',
            'multimodal': True,
            'description': "Use OpenAI's ChatGPT models to answer questions about your documents.",
            'multimodal_info': 'The default ChatGPT-4o model supports text-only, image-only, and text+image modes.'
        },
        'genai': {
            'label': 'Google Gemini',
            'task_url': 'twf:task_project_query_gemini',
            'credentials_key': 'genai',
            'credentials_tab': 'genai',
            'multimodal': True,
            'description': 'Query Google Gemini models for predictions. All current Gemini models support multimodal input with both text and images.',
            'multimodal_info': 'Supports text-only, images-only, or text+images modes. All Gemini models support images.'
        },
        'anthropic': {
            'label': 'Anthropic Claude',
            'task_url': 'twf:task_project_query_claude',
            'credentials_key': 'anthropic',
            'credentials_tab': 'anthropic',
            'multimodal': True,
            'description': 'Query Anthropic Claude models for analysis and predictions.',
            'multimodal_info': 'Claude 3 models support text and image inputs.'
        },
        'mistral': {
            'label': 'Mistral',
            'task_url': 'twf:task_project_query_mistral',
            'credentials_key': 'mistral',
            'credentials_tab': 'mistral',
            'multimodal': False,
            'description': 'Query Mistral AI models for predictions.',
            'multimodal_info': 'Mistral currently supports text-only queries.'
        },
        'deepseek': {
            'label': 'DeepSeek',
            'task_url': 'twf:task_project_query_deepseek',
            'credentials_key': 'deepseek',
            'credentials_tab': 'deepseek',
            'multimodal': True,
            'description': 'Query DeepSeek models for predictions.',
            'multimodal_info': 'DeepSeek supports text-only, image-only, and text+image modes.'
        },
        'qwen': {
            'label': 'Qwen',
            'task_url': 'twf:task_project_query_qwen',
            'credentials_key': 'qwen',
            'credentials_tab': 'qwen',
            'multimodal': True,
            'description': 'Query Qwen models for predictions.',
            'multimodal_info': 'Qwen supports text-only, image-only, and text+image modes.'
        },
    }

    def get_form_kwargs(self):
        """
        Get the form kwargs with project and unified task URL.

        The unified task URL will dispatch to the correct provider based on
        the ai_provider parameter in the form data.

        Returns:
            dict: Form kwargs.
        """
        kwargs = super().get_form_kwargs()

        # Use the unified task trigger URL
        # The trigger will dispatch to the correct provider based on form data
        kwargs['data-start-url'] = reverse_lazy('twf:task_project_query_unified')
        kwargs['data-message'] = self.message

        return kwargs

    def get_context_data(self, **kwargs):
        """
        Get the context data for the template.

        This method adds provider-specific context data dynamically based on
        the selected provider in the form.

        Args:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)

        # Get selected provider from form data or default to openai
        provider = 'openai'
        if self.request.method == 'POST':
            provider = self.request.POST.get('ai_provider', 'openai')
        elif self.request.method == 'GET' and 'ai_provider' in self.request.GET:
            provider = self.request.GET.get('ai_provider', 'openai')

        # Set context based on provider
        if provider in self.PROVIDER_CONFIG:
            provider_info = self.PROVIDER_CONFIG[provider]
            creds = self.get_ai_credentials(provider_info['credentials_key'])
            has_api_key = creds and 'api_key' in creds and creds['api_key']

            context['ai_heading'] = f"{self.page_title} - {provider_info['label']}"
            context['ai_lead'] = provider_info['description']
            context['has_api_key'] = has_api_key
            context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + f"?tab={provider_info['credentials_tab']}"
            context['supports_multimodal'] = provider_info['multimodal']
            context['multimodal_info'] = provider_info['multimodal_info']
        else:
            # Fallback defaults
            context['ai_heading'] = self.page_title
            context['ai_lead'] = 'Query AI models to answer questions about your documents.'
            context['has_api_key'] = False
            context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials')
            context['supports_multimodal'] = True
            context['multimodal_info'] = 'Multimodal support varies by provider.'

        # Build provider config for JavaScript with credentials check
        provider_config_for_js = {}
        for provider_key, provider_info in self.PROVIDER_CONFIG.items():
            creds = self.get_ai_credentials(provider_info['credentials_key'])
            has_api_key = creds and 'api_key' in creds and creds['api_key']
            default_model = creds.get('default_model', '') if creds else ''

            provider_config_for_js[provider_key] = {
                'label': provider_info['label'],
                'description': provider_info['description'],
                'multimodal': provider_info['multimodal'],
                'multimodal_info': provider_info['multimodal_info'],
                'credentials_url': str(reverse_lazy('twf:project_settings_credentials')) + f"?tab={provider_info['credentials_tab']}",
                'has_api_key': has_api_key,
                'default_model': default_model
            }
        context['provider_config_json'] = json.dumps(provider_config_for_js)

        return context

import json
from django.urls import reverse_lazy

from twf.forms.collections.collections_forms_batches import CollectionOpenaiBatchForm, CollectionGeminiBatchForm, \
    CollectionClaudeBatchForm, CollectionMistralBatchForm, UnifiedCollectionAIBatchForm, UnifiedCollectionAIRequestForm
from twf.views.collections.views_collections import TWFCollectionsView
from twf.views.views_base import AIFormView


class TWFCollectionsOpenaiBatchView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'OpenAI Batch Workflow'
    form_class = CollectionOpenaiBatchForm
    start_url = reverse_lazy('twf:task_collection_batch_openai')
    message = "Are you sure you want to start the openai task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'OpenAI Batch Workflow'
        context['ai_lead'] = 'This task will request data from OpenAI.'
        context['has_ai_credentials'] = self.has_ai_credentials('openai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=openai'
        return context


class TWFCollectionsGeminiBatchView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Gemini Batch Workflow'
    form_class = CollectionGeminiBatchForm
    start_url = reverse_lazy('twf:task_collection_batch_gemini')
    message = "Are you sure you want to start the gemini task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Gemini Batch Workflow'
        context['ai_lead'] = 'This task will request data from Gemini.'
        context['has_ai_credentials'] = self.has_ai_credentials('genai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=genai'
        return context


class TWFCollectionsClaudeBatchView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Claude Batch Workflow'
    form_class = CollectionClaudeBatchForm
    start_url = reverse_lazy('twf:task_collection_batch_claude')
    message = "Are you sure you want to start the claude task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Claude Batch Workflow'
        context['ai_lead'] = 'This task will request data from Claude.'
        context['has_ai_credentials'] = self.has_ai_credentials('anthropic')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=anthropic'
        return context


class TWFCollectionsMistralBatchView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Mistral Batch Workflow'
    form_class = CollectionMistralBatchForm
    start_url = reverse_lazy('twf:task_collection_batch_mistral')
    message = "Are you sure you want to start the mistral task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Mistral Batch Workflow'
        context['ai_lead'] = 'This task will request data from Mistral.'
        context['has_ai_credentials'] = self.has_ai_credentials('mistral')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=mistral'
        return context


class TWFCollectionsOpenaiRequestView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'OpenAI Request'
    form_class = CollectionOpenaiBatchForm
    start_url = reverse_lazy('twf:task_collection_request_openai')
    message = "Are you sure you want to start the openai task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'OpenAI Request'
        context['ai_lead'] = 'This task will request data from OpenAI.'
        context['has_ai_credentials'] = self.has_ai_credentials('openai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=openai'
        return context


class TWFCollectionsGeminiRequestView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Gemini Request'
    form_class = CollectionGeminiBatchForm
    start_url = reverse_lazy('twf:task_collection_request_gemini')
    message = "Are you sure you want to start the gemini task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Gemini Request'
        context['ai_lead'] = 'This task will request data from Gemini.'
        context['has_ai_credentials'] = self.has_ai_credentials('genai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=genai'
        return context


class TWFCollectionsClaudeRequestView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Gemini Request'
    form_class = CollectionClaudeBatchForm
    start_url = reverse_lazy('twf:task_collection_request_claude')
    message = "Are you sure you want to start the claude task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Claude Request'
        context['ai_lead'] = 'This task will request data from Claude.'
        context['has_ai_credentials'] = self.has_ai_credentials('anthropic')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=anthropic'
        return context


class TWFCollectionsMistralRequestView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Mistral Request'
    form_class = CollectionMistralBatchForm
    start_url = reverse_lazy('twf:task_collection_request_mistral')
    message = "Are you sure you want to start the mistral task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Mistral Request'
        context['ai_lead'] = 'This task will request data from Mistral.'
        context['has_ai_credentials'] = self.has_ai_credentials('mistral')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=mistral'
        return context


class TWFUnifiedCollectionAIBatchView(AIFormView, TWFCollectionsView):
    """
    Unified view for AI batch processing of collections.

    This view provides a single interface for batch processing with all supported
    AI providers. The provider is selected via a dropdown in the form.
    """

    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'AI Batch Processing'
    form_class = UnifiedCollectionAIBatchForm
    success_url = reverse_lazy('twf:collections_batch_ai_unified')
    message = "Do you want to start the AI batch process now?"

    # Provider configuration (only 4 providers for collections)
    PROVIDER_CONFIG = {
        'openai': {
            'label': 'OpenAI (ChatGPT)',
            'credentials_key': 'openai',
            'credentials_tab': 'openai',
            'description': 'OpenAI will process collection items using ChatGPT models.',
        },
        'genai': {
            'label': 'Google Gemini',
            'credentials_key': 'genai',
            'credentials_tab': 'genai',
            'description': 'Gemini will process collection items.',
        },
        'anthropic': {
            'label': 'Anthropic Claude',
            'credentials_key': 'anthropic',
            'credentials_tab': 'anthropic',
            'description': 'Claude will process collection items.',
        },
        'mistral': {
            'label': 'Mistral',
            'credentials_key': 'mistral',
            'credentials_tab': 'mistral',
            'description': 'Mistral will process collection items.',
        },
    }

    def get_form_kwargs(self):
        """
        Get the form kwargs with project and unified task URL.

        Returns:
            dict: Form kwargs.
        """
        kwargs = super().get_form_kwargs()

        # Use the unified task trigger URL
        kwargs['data-start-url'] = reverse_lazy('twf:task_collections_batch_unified')
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
            context['ai_heading'] = f"{provider_info['label']} Collection Batch"
            context['ai_lead'] = provider_info['description']
            creds = self.get_ai_credentials(provider_info['credentials_key'])
            has_api_key = creds and 'api_key' in creds and creds['api_key']
            context['has_api_key'] = has_api_key
            context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + f"?tab={provider_info['credentials_tab']}"
        else:
            # Fallback defaults
            context['ai_heading'] = self.page_title
            context['ai_lead'] = 'AI will process collection items.'
            context['has_api_key'] = False
            context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials')

        # Build provider config for JavaScript with credentials check
        provider_config_for_js = {}
        for provider_key, provider_info in self.PROVIDER_CONFIG.items():
            creds = self.get_ai_credentials(provider_info['credentials_key'])
            has_api_key = creds and 'api_key' in creds and creds['api_key']
            default_model = creds.get('default_model', '') if creds else ''

            provider_config_for_js[provider_key] = {
                'label': provider_info['label'],
                'description': provider_info['description'],
                'multimodal': False,  # Collections don't support multimodal
                'multimodal_info': '',
                'credentials_url': str(reverse_lazy('twf:project_settings_credentials')) + f"?tab={provider_info['credentials_tab']}",
                'has_api_key': has_api_key,
                'default_model': default_model
            }
        context['provider_config_json'] = json.dumps(provider_config_for_js)

        return context


class TWFUnifiedCollectionAIRequestView(AIFormView, TWFCollectionsView):
    """
    Unified view for AI request (supervised) processing of collection items.

    This view provides a single interface for supervised, single-item processing
    with all supported AI providers. The provider is selected via a dropdown in the form.
    """

    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'AI Request'
    form_class = UnifiedCollectionAIRequestForm
    success_url = reverse_lazy('twf:collections_request_ai_unified')
    message = "Do you want to send this AI request now?"

    # Provider configuration (same 4 providers)
    PROVIDER_CONFIG = {
        'openai': {
            'label': 'OpenAI (ChatGPT)',
            'credentials_key': 'openai',
            'credentials_tab': 'openai',
            'description': 'OpenAI will process this collection item using ChatGPT models.',
        },
        'genai': {
            'label': 'Google Gemini',
            'credentials_key': 'genai',
            'credentials_tab': 'genai',
            'description': 'Gemini will process this collection item.',
        },
        'anthropic': {
            'label': 'Anthropic Claude',
            'credentials_key': 'anthropic',
            'credentials_tab': 'anthropic',
            'description': 'Claude will process this collection item.',
        },
        'mistral': {
            'label': 'Mistral',
            'credentials_key': 'mistral',
            'credentials_tab': 'mistral',
            'description': 'Mistral will process this collection item.',
        },
    }

    def get_form_kwargs(self):
        """
        Get the form kwargs with project and unified task URL.

        Returns:
            dict: Form kwargs.
        """
        kwargs = super().get_form_kwargs()

        # Use the unified task trigger URL
        kwargs['data-start-url'] = reverse_lazy('twf:task_collections_request_unified')
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
            context['ai_heading'] = f"{provider_info['label']} Collection Request"
            context['ai_lead'] = provider_info['description']
            creds = self.get_ai_credentials(provider_info['credentials_key'])
            has_api_key = creds and 'api_key' in creds and creds['api_key']
            context['has_api_key'] = has_api_key
            context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + f"?tab={provider_info['credentials_tab']}"
        else:
            # Fallback defaults
            context['ai_heading'] = self.page_title
            context['ai_lead'] = 'AI will process this collection item.'
            context['has_api_key'] = False
            context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials')

        # Build provider config for JavaScript with credentials check
        provider_config_for_js = {}
        for provider_key, provider_info in self.PROVIDER_CONFIG.items():
            creds = self.get_ai_credentials(provider_info['credentials_key'])
            has_api_key = creds and 'api_key' in creds and creds['api_key']
            default_model = creds.get('default_model', '') if creds else ''

            provider_config_for_js[provider_key] = {
                'label': provider_info['label'],
                'description': provider_info['description'],
                'multimodal': False,  # Collections don't support multimodal
                'multimodal_info': '',
                'credentials_url': str(reverse_lazy('twf:project_settings_credentials')) + f"?tab={provider_info['credentials_tab']}",
                'has_api_key': has_api_key,
                'default_model': default_model
            }
        context['provider_config_json'] = json.dumps(provider_config_for_js)

        return context

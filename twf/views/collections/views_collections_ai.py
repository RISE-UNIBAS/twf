from django.urls import reverse_lazy

from twf.forms.collections.collections_forms_batches import CollectionOpenaiBatchForm, CollectionGeminiBatchForm, \
    CollectionClaudeBatchForm, CollectionMistralBatchForm
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

from django.urls import reverse_lazy

from twf.forms.collections.collections_forms_batches import CollectionOpenaiBatchForm, CollectionGeminiBatchForm, \
    CollectionClaudeBatchForm
from twf.views.collections.views_collections import TWFCollectionsView
from twf.views.views_base import AIFormView


class TWFCollectionsOpenaiBatchView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/openai_batch.html'
    page_title = 'OpenAI Batch Workflow'
    form_class = CollectionOpenaiBatchForm
    start_url = reverse_lazy('twf:task_collection_batch_openai')
    message = "Are you sure you want to start the openai task?"


class TWFCollectionsGeminiBatchView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/gemini_batch.html'
    page_title = 'Gemini Batch Workflow'
    form_class = CollectionGeminiBatchForm
    start_url = reverse_lazy('twf:task_collection_batch_gemini')
    message = "Are you sure you want to start the gemini task?"


class TWFCollectionsClaudeBatchView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/claude_batch.html'
    page_title = 'Claude Batch Workflow'
    form_class = CollectionClaudeBatchForm
    start_url = reverse_lazy('twf:task_collection_batch_claude')
    message = "Are you sure you want to start the claude task?"


class TWFCollectionsOpenaiRequestView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/openai_request.html'
    page_title = 'OpenAI Request'
    form_class = CollectionOpenaiBatchForm
    start_url = reverse_lazy('twf:task_collection_request_openai')
    message = "Are you sure you want to start the openai task?"


class TWFCollectionsGeminiRequestView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/gemini_request.html'
    page_title = 'Gemini Request'
    form_class = CollectionGeminiBatchForm
    start_url = reverse_lazy('twf:task_collection_request_gemini')
    message = "Are you sure you want to start the gemini task?"


class TWFCollectionsClaudeRequestView(AIFormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/claude_request.html'
    page_title = 'Gemini Request'
    form_class = CollectionClaudeBatchForm
    start_url = reverse_lazy('twf:task_collection_request_claude')
    message = "Are you sure you want to start the claude task?"


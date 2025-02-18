from django.urls import reverse_lazy
from django.views.generic import FormView

from twf.forms.collections.collections_forms_batches import CollectionOpenaiBatchForm, CollectionGeminiBatchForm, \
    CollectionClaudeBatchForm
from twf.views.collections.views_collections import TWFCollectionsView


class TWFCollectionsOpenaiBatchView(FormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/openai_batch.html'
    page_title = 'OpenAI Batch Workflow'
    form_class = CollectionOpenaiBatchForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_collection_batch_openai')
        kwargs['data-message'] = "Are you sure you want to start the openai task?"

        return kwargs


class TWFCollectionsGeminiBatchView(FormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/gemini_batch.html'
    page_title = 'Gemini Batch Workflow'
    form_class = CollectionGeminiBatchForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_collection_batch_gemini')
        kwargs['data-message'] = "Are you sure you want to start the gemini task?"

        return kwargs


class TWFCollectionsClaudeBatchView(FormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/claude_batch.html'
    page_title = 'Claude Batch Workflow'
    form_class = CollectionClaudeBatchForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_collection_batch_claude')
        kwargs['data-message'] = "Are you sure you want to start the claude task?"

        return kwargs


class TWFCollectionsOpenaiRequestView(FormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/openai_request.html'
    page_title = 'OpenAI Request'
    form_class = CollectionOpenaiBatchForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_collection_request_openai')
        kwargs['data-message'] = "Are you sure you want to start the openai task?"

        return kwargs


class TWFCollectionsGeminiRequestView(FormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/gemini_request.html'
    page_title = 'Gemini Request'
    form_class = CollectionGeminiBatchForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_collection_request_gemini')
        kwargs['data-message'] = "Are you sure you want to start the gemini task?"

        return kwargs


class TWFCollectionsClaudeRequestView(FormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/claude_request.html'
    page_title = 'Gemini Request'
    form_class = CollectionClaudeBatchForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_collection_request_claude')
        kwargs['data-message'] = "Are you sure you want to start the claude task?"

        return kwargs

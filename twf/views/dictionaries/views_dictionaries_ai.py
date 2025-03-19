"""Dictionaries Batch Views."""
from django.urls import reverse_lazy
from django.views.generic import FormView

from twf.forms.dictionaries.dictionaries_forms_batches import GeonamesBatchForm, GNDBatchForm, WikidataBatchForm, \
    DictionariesOpenAIBatchForm, DictionariesGeminiBatchForm, DictionariesClaudeBatchForm, DictionariesMistralBatchForm
from twf.views.dictionaries.views_dictionaries import TWFDictionaryView
from twf.views.views_base import AIFormView


class TWFDictionaryGeonamesBatchView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/geonames.html'
    page_title = 'Geonames Batch'
    form_class = GeonamesBatchForm
    success_url = reverse_lazy('twf:dictionaries_batch_geonames')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_dictionaries_batch_geonames')
        kwargs['data-message'] = "Are you sure you want to start the geonames task?"

        return kwargs


class TWFDictionaryGNDBatchView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/gnd.html'
    page_title = 'GND Batch'
    form_class = GNDBatchForm
    success_url = reverse_lazy('twf:dictionaries_batch_gnd')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_dictionaries_batch_gnd')
        kwargs['data-message'] = "Are you sure you want to start the gnd task?"

        return kwargs


class TWFDictionaryWikidataBatchView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/wikidata.html'
    page_title = 'Wikidata Batch'
    form_class = WikidataBatchForm
    success_url = reverse_lazy('twf:dictionaries_batch_wikidata')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_dictionaries_batch_wikidata')
        kwargs['data-message'] = "Are you sure you want to start the wikidata task?"

        return kwargs


class TWFDictionaryOpenaiBatchView(AIFormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'OpenAI Batch'
    form_class = DictionariesOpenAIBatchForm
    success_url = reverse_lazy('twf:dictionaries_batch_openai')
    start_url = reverse_lazy('twf:task_dictionaries_batch_openai')
    message = "Are you sure you want to start the openai task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'OpenAI'
        context['ai_lead'] = 'OpenAI is an AI model that can be used to generate text based on a prompt.'
        return context


class TWFDictionaryGeminiBatchView(AIFormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Gemini Batch'
    form_class = DictionariesGeminiBatchForm
    success_url = reverse_lazy('twf:dictionaries_batch_gemini')
    start_url = reverse_lazy('twf:task_dictionaries_batch_gemini')
    message = "Are you sure you want to start the gemini task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Gemini'
        context['ai_lead'] = 'Gemini is an AI model that can be used to generate text based on a prompt.'
        context['has_ai_credentials'] = self.has_ai_credentials('genai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=genai'
        return context


class TWFDictionaryClaudeBatchView(AIFormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Claude Batch'
    form_class = DictionariesClaudeBatchForm
    success_url = reverse_lazy('twf:dictionaries_batch_claude')
    start_url = reverse_lazy('twf:task_dictionaries_batch_claude')
    message = "Are you sure you want to start the claude task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Claude'
        context['ai_lead'] = 'Claude is an AI model that can be used to generate text based on a prompt.'
        context['has_ai_credentials'] = self.has_ai_credentials('anthropic')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=anthropic'
        return context


class TWFDictionaryMistralBatchView(AIFormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Mistral Batch'
    form_class = DictionariesMistralBatchForm
    success_url = reverse_lazy('twf:dictionaries_batch_mistral')
    start_url = reverse_lazy('twf:task_dictionaries_batch_mistral')
    message = "Are you sure you want to start the mistral task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Mistral'
        context['ai_lead'] = 'Mistral is an AI model that can be used to generate text based on a prompt.'
        context['has_ai_credentials'] = self.has_ai_credentials('mistral')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=mistral'
        return context


class TWFDictionaryGeonamesRequestView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/requests/geonames.html'
    page_title = 'Geonames Request'
    form_class = GeonamesBatchForm
    success_url = reverse_lazy('twf:dictionaries_request_geonames')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs

class TWFDictionaryGNDRequestView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/requests/gnd.html'
    page_title = 'GND Request'
    form_class = GNDBatchForm
    success_url = reverse_lazy('twf:dictionaries_request_gnd')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs

class TWFDictionaryWikidataRequestView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/requests/wikidata.html'
    page_title = 'Wikidata Request'
    form_class = WikidataBatchForm
    success_url = reverse_lazy('twf:dictionaries_request_wikidata')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs

class TWFDictionaryOpenaiRequestView(AIFormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'OpenAI Request'
    form_class = DictionariesOpenAIBatchForm
    success_url = reverse_lazy('twf:dictionaries_request_openai')
    start_url = reverse_lazy('twf:task_dictionaries_request_openai')
    message = "Are you sure you want to start the openai task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'OpenAI'
        context['ai_lead'] = 'OpenAI is an AI model that can be used to generate text based on a prompt.'
        context['has_ai_credentials'] = self.has_ai_credentials('openai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=openai'
        return context


class TWFDictionaryClaudeRequestView(AIFormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Claude Request'
    form_class = DictionariesClaudeBatchForm
    success_url = reverse_lazy('twf:dictionaries_request_claude')
    start_url = reverse_lazy('twf:task_dictionaries_request_claude')
    message = "Are you sure you want to start the claude task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Claude'
        context['ai_lead'] = 'Claude is an AI model that can be used to generate text based on a prompt.'
        context['has_ai_credentials'] = self.has_ai_credentials('anthropic')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=anthropic'
        return context


class TWFDictionaryGeminiRequestView(AIFormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Gemini Request'
    form_class = DictionariesGeminiBatchForm
    success_url = reverse_lazy('twf:dictionaries_request_gemini')
    start_url = reverse_lazy('twf:task_dictionaries_request_gemini')
    message = "Are you sure you want to start the gemini task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Gemini'
        context['ai_lead'] = 'Gemini is an AI model that can be used to generate text based on a prompt.'
        context['has_ai_credentials'] = self.has_ai_credentials('genai')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=genai'
        return context


class TWFDictionaryMistralRequestView(AIFormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/base/base_ai_batch.html'
    page_title = 'Mistral Request'
    form_class = DictionariesMistralBatchForm
    success_url = reverse_lazy('twf:dictionaries_request_mistral')
    start_url = reverse_lazy('twf:task_dictionaries_request_mistral')
    message = "Are you sure you want to start the mistral task?"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_heading'] = 'Mistral'
        context['ai_lead'] = 'Mistral is an AI model that can be used to generate text based on a prompt.'
        context['has_ai_credentials'] = self.has_ai_credentials('mistral')
        context['ai_credentials_url'] = reverse_lazy('twf:project_settings_credentials') + '?tab=mistral'
        return context

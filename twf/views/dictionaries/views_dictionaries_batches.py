"""Dictionaries Batch Views."""
from django.urls import reverse_lazy
from django.views.generic import FormView

from twf.forms.dictionaries.dictionaries_forms_batches import GeonamesBatchForm, GNDBatchForm, WikidataBatchForm, \
    DictionariesOpenAIBatchForm, DictionariesGeminiBatchForm, DictionariesClaudeBatchForm
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
    template_name = 'twf/dictionaries/batches/openai.html'
    page_title = 'OpenAI Batch'
    form_class = DictionariesOpenAIBatchForm
    success_url = reverse_lazy('twf:dictionaries_batch_openai')
    start_url = reverse_lazy('twf:task_dictionaries_batch_openai')
    message = "Are you sure you want to start the openai task?"


class TWFDictionaryGeminiBatchView(AIFormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/gemini.html'
    page_title = 'Gemini Batch'
    form_class = DictionariesGeminiBatchForm
    success_url = reverse_lazy('twf:dictionaries_batch_gemini')
    start_url = reverse_lazy('twf:task_dictionaries_batch_gemini')
    message = "Are you sure you want to start the gemini task?"


class TWFDictionaryClaudeBatchView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/claude.html'
    page_title = 'Claude Batch'
    form_class = DictionariesClaudeBatchForm
    success_url = reverse_lazy('twf:dictionaries_batch_claude')
    start_url = reverse_lazy('twf:task_dictionaries_batch_claude')
    message = "Are you sure you want to start the claude task?"


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
    template_name = 'twf/dictionaries/requests/openai.html'
    page_title = 'OpenAI Request'
    form_class = DictionariesOpenAIBatchForm
    success_url = reverse_lazy('twf:dictionaries_request_openai')
    start_url = reverse_lazy('twf:task_dictionaries_request_openai')
    message = "Are you sure you want to start the openai task?"


class TWFDictionaryClaudeRequestView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/requests/claude.html'
    page_title = 'Claude Request'
    form_class = DictionariesClaudeBatchForm
    success_url = reverse_lazy('twf:dictionaries_request_claude')
    start_url = reverse_lazy('twf:task_dictionaries_request_claude')
    message = "Are you sure you want to start the claude task?"


class TWFDictionaryGeminiRequestView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/requests/gemini.html'
    page_title = 'Gemini Request'
    form_class = DictionariesGeminiBatchForm
    success_url = reverse_lazy('twf:dictionaries_request_gemini')
    start_url = reverse_lazy('twf:task_dictionaries_request_gemini')
    message = "Are you sure you want to start the gemini task?"

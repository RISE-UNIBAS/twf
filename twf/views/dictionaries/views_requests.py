"""Dictionaries Request Views."""
from django.urls import reverse_lazy
from django.views.generic import FormView

from twf.forms.dictionaries.request_forms import GeonamesRequestForm, GNDRequestForm, WikidataRequestForm, \
    OpenaiRequestForm
from twf.views.dictionaries.views_dictionaries import TWFDictionaryView


class TWFDictionaryGeonamesRequestView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/geonames.html'
    page_title = 'Geonames Request'
    form_class = GeonamesRequestForm
    success_url = reverse_lazy('twf:dictionaries_request_geonames')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs


class TWFDictionaryGNDRequestView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/gnd.html'
    page_title = 'GND Request'
    form_class = GNDRequestForm
    success_url = reverse_lazy('twf:dictionaries_request_gnd')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs


class TWFDictionaryWikidataRequestView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/wikidata.html'
    page_title = 'Wikidata Request'
    form_class = WikidataRequestForm
    success_url = reverse_lazy('twf:dictionaries_request_wikidata')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs


class TWFDictionaryOpenaiRequestView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/openai.html'
    page_title = 'OpenAI Request'
    form_class = OpenaiRequestForm
    success_url = reverse_lazy('twf:dictionaries_request_openai')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs

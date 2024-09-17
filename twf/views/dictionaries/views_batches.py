from django.urls import reverse_lazy
from django.views.generic import FormView

from twf.forms.dictionaries.batch_forms import GeonamesBatchForm, GNDBatchForm, WikidataBatchForm, OpenaiBatchForm
from twf.views.dictionaries.views_dictionaries import TWFDictionaryView


class TWFDictionaryGeonamesBatchView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/geonames.html'
    page_title = 'Geonames Batch'
    form_class = GeonamesBatchForm
    success_url = reverse_lazy('twf:dictionaries_batch_geonames')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
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
        return kwargs


class TWFDictionaryOpenaiBatchView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/openai.html'
    page_title = 'OpenAI Batch'
    form_class = OpenaiBatchForm
    success_url = reverse_lazy('twf:dictionaries_batch_openai')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs

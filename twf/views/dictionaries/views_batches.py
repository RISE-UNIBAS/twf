from django.urls import reverse
from django.views.generic import FormView

from twf.forms.dictionaries.batch_forms import GeonamesBatchForm, GNDBatchForm, WikidataBatchForm, OpenaiBatchForm
from twf.views.dictionaries.views_dictionaries import TWFDictionaryView


class TWFDictionaryGeonamesBatchView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/geonames.html'
    page_title = 'Geonames Batch'
    form_class = GeonamesBatchForm
    success_url = reverse('twf:dictionaries_batch_geonames')


class TWFDictionaryGNDBatchView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/gnd.html'
    page_title = 'GND Batch'
    form_class = GNDBatchForm
    success_url = reverse('twf:dictionaries_batch_gnd')


class TWFDictionaryWikidataBatchView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/wikidata.html'
    page_title = 'Wikidata Batch'
    form_class = WikidataBatchForm
    success_url = reverse('twf:dictionaries_batch_wikidata')


class TWFDictionaryOpenaiBatchView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/openai.html'
    page_title = 'OpenAI Batch'
    form_class = OpenaiBatchForm
    success_url = reverse('twf:dictionaries_batch_openai')

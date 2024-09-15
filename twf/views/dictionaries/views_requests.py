from django.urls import reverse
from django.views.generic import FormView

from twf.forms.dictionaries.request_forms import GeonamesRequestForm, GNDRequestForm, WikidataRequestForm, \
    OpenaiRequestForm
from twf.views.dictionaries.views_dictionaries import TWFDictionaryView


class TWFDictionaryGeonamesRequestView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/geonames.html'
    page_title = 'Geonames Request'
    form_class = GeonamesRequestForm
    success_url = reverse('twf:dictionaries_request_geonames')


class TWFDictionaryGNDRequestView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/gnd.html'
    page_title = 'GND Request'
    form_class = GNDRequestForm
    success_url = reverse('twf:dictionaries_request_gnd')


class TWFDictionaryWikidataRequestView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/wikidata.html'
    page_title = 'Wikidata Request'
    form_class = WikidataRequestForm
    success_url = reverse('twf:dictionaries_request_wikidata')


class TWFDictionaryOpenaiRequestView(FormView, TWFDictionaryView):
    """Normalization Data Wizard."""
    template_name = 'twf/dictionaries/batches/openai.html'
    page_title = 'OpenAI Request'
    form_class = OpenaiRequestForm
    success_url = reverse('twf:dictionaries_request_openai')

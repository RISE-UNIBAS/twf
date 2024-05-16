import requests
from django.shortcuts import render
from django.views import View
from lxml import etree

from twf.forms import GeonamesSearchForm, WikidataSearchForm, GNDSearchForm
from twf.models import Dictionary
from twf.views.views_base import BaseView


class DictionaryAuthView(BaseView, View):
    """View for the dictionary overview."""
    template_name = 'twf/dictionaries.html'

    def get_context_data(self, **kwargs):
        context = {'dictionaries': self.get_dictionaries()}

        dict_types = Dictionary.objects.values_list('type', flat=True).order_by('type').distinct()
        if self.request.GET.get('dict_type', None):
            dict_type = self.request.GET.get('dict_type')
        else:
            dict_type = dict_types[0]

        context['selected_type'] = dict_type
        context['dict_types'] = dict_types

        # There is a dict type selected, so we can present the first dictionary entry
        if dict_type:
            context['selected_dict'] = Dictionary.objects.get(type=dict_type)
            context['next_unauthorized_entry'] = context['selected_dict'].entries.filter(authorization_data={}).first()

        return context


class DictionaryAuthViewManual(DictionaryAuthView):
    """View for the dictionary overview."""
    template_name = 'twf/dict_auth_manual.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()

        return render(request, self.template_name, context)


class DictionaryAuthViewWikidata(DictionaryAuthView):
    """View for the dictionary overview."""
    template_name = 'twf/dict_auth_wikidata.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = WikidataSearchForm()
        return context

    def request_data(self):
        entry = self.get_context_data()['next_unauthorized_entry']
        if entry:
            entry_label = entry.label
            url = 'https://query.wikidata.org/sparql'
            query = 'SELECT ?item ?itemLabel ?itemDescription WHERE {\n' \
                    f'  ?item rdfs:label "{entry_label}"@de.\n' \
                    '  SERVICE wikibase:label { bd:serviceParam wikibase:language "de, en". }\n' \
                    '}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/58.0.3029.110 Safari/537.3',
                'Accept': 'application/json'
            }
            response = requests.get(url, headers=headers, params={'query': query, 'format': 'json'})
            if response.status_code != 200:
                print(response)
                return None
            else:
                data = response.json()
                return data['results']['bindings']

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['results'] = self.request_data()
        return render(request, self.template_name, context)


class DictionaryAuthViewGeonames(DictionaryAuthView):
    """View for the dictionary overview."""
    template_name = 'twf/dict_auth_geonames.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = GeonamesSearchForm()
        return context

    def request_data(self):
        entry = self.get_context_data()['next_unauthorized_entry']
        if entry:
            entry_label = entry.label
            username = 'sorinmarti'
            payload = {
                'q': entry_label,
                'maxRows': 5,
                'username': username,
                'type': 'json'
            }
            response = requests.get('http://api.geonames.org/search', params=payload)
            data = response.json()
            return data['geonames']

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['results'] = self.request_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        # print("POST", request.POST)
        # print("CONTEXT", context)

        if 'select_auth' in request.POST:
            authorization_data = request.POST['selected_option']
        else:
            print("FORM INVALID")

        return render(request, self.template_name, context)


class DictionaryAuthViewGND(DictionaryAuthView):
    """View for the dictionary overview."""
    template_name = 'twf/dict_auth_gnd.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = GNDSearchForm()
        return context

    def request_data(self):
        entry = self.get_context_data()['next_unauthorized_entry']
        if entry:
            endpoint = 'https://services.dnb.de/sru/authorities'

            # Parameters for the SRU request
            params = {
                'operation': 'searchRetrieve',
                'version': '1.1',
                'query': 'dnb.mat="persons" AND dnb.woe="Bach"',
                'recordSchema': 'RDFxml',
                'maximumRecords': '10'
            }

            # Send the request
            response = requests.get(endpoint, params=params)

            root = etree.fromstring(response.text.encode())

            # Define namespaces to use with XPath
            namespaces = {
                'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                'gndo': "https://d-nb.info/standards/elementset/gnd#",
                'srw': "http://www.loc.gov/zing/srw/"
            }

            # Find all person descriptions
            records = root.xpath('//srw:record', namespaces=namespaces)
            results = []
            # Process each record
            for record in records:
                # Extract preferred name and variant names within each record
                gnd_identifier = record.xpath('.//gndo:gndIdentifier/text()', namespaces=namespaces)
                preferred_name = record.xpath('.//gndo:preferredNameForThePerson/text()', namespaces=namespaces)
                variant_names = record.xpath('.//gndo:variantNameForThePerson/text()', namespaces=namespaces)

                results.append({
                    "gnd_identifier": gnd_identifier[0],
                    "preferred_name": preferred_name[0],
                    "variant_names": variant_names
                })
            return results

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['results'] = self.request_data()
        return render(request, self.template_name, context)

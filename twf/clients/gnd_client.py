""" Client for the GND (Gemeinsame Normdatei) authority file. """
import requests
from lxml import etree


def send_gnd_request(query):
    """ Send a request to the GND authority file and return the response. """
    endpoint = 'https://services.dnb.de/sru/authorities'
    params = {
        'operation': 'searchRetrieve',
        'version': '1.1',
        'query': f'dnb.mat="persons" AND dnb.woe="{query}"',
        'recordSchema': 'RDFxml',
        'maximumRecords': '10'
    }

    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException:
        return None


def parse_gnd_request(response):
    """ Parse the response from the GND authority file and return the results. """
    root = etree.fromstring(response.text.encode())

    namespaces = {
        'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        'gndo': "https://d-nb.info/standards/elementset/gnd#",
        'srw': "http://www.loc.gov/zing/srw/"
    }

    # Find all person descriptions
    records = root.xpath('//srw:record', namespaces=namespaces)

    # Process each record
    results = []
    for record in records:
        # Extract preferred name and variant names within each record
        gnd_identifier = record.xpath('.//gndo:gndIdentifier/text()', namespaces=namespaces)
        preferred_name = record.xpath('.//gndo:preferredNameForThePerson/text()', namespaces=namespaces)
        variant_names = record.xpath('.//gndo:variantNameForThePerson/text()', namespaces=namespaces)

        results.append((gnd_identifier, preferred_name, variant_names))

    return results


def search_gnd(query):
    """ Search the GND authority file for a query. """
    response = send_gnd_request(query)
    if response is None:
        return None

    results = parse_gnd_request(response)
    return results

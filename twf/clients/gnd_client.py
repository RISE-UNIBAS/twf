import requests
from lxml import etree
import json

# SRU endpoint for the DNB authorities database
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
print(response.text)

root = etree.fromstring(response.text.encode())

# Define namespaces to use with XPath
namespaces = {
    'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    'gndo': "https://d-nb.info/standards/elementset/gnd#",
    'srw': "http://www.loc.gov/zing/srw/"
}

# Find all person descriptions
records = root.xpath('//srw:record', namespaces=namespaces)

# Process each record
for record in records:
    # Extract preferred name and variant names within each record
    gnd_identifier = record.xpath('.//gndo:gndIdentifier/text()', namespaces=namespaces)
    preferred_name = record.xpath('.//gndo:preferredNameForThePerson/text()', namespaces=namespaces)
    variant_names = record.xpath('.//gndo:variantNameForThePerson/text()', namespaces=namespaces)

    print("GND Identifier:", gnd_identifier)
    print("Preferred Name:", preferred_name)
    print("Variant Names:", variant_names)
    print("------")

















    def post(self, request, *args, **kwargs):
        username = 'sorinmarti'
        payload = {
            'q': 'London',  # Query for "London"
            'maxRows': 5,  # Limit the number of results
            'username': username,  # Your GeoNames user account
            'type': 'json'  # Response format
        }
        response = requests.get('http://api.geonames.org/search', params=payload)
        data = response.json()

        print(data)
        return super().get(request, *args, **kwargs)
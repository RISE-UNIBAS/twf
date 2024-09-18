from SPARQLWrapper import SPARQLWrapper, JSON

# Set up the endpoint and query
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setMethod("POST")
sparql.setTimeout(120)

# Define entity types and their corresponding Wikidata classes (Q-values)
entity_types = {
    'city': 'wd:Q515',
    'person': 'wd:Q5',
    'event': 'wd:Q1656682',
    'ship': 'wd:Q11446',
    'building': 'wd:Q41176'
}

# Define properties to query for each entity type
property_map = {
    'city': {
        'properties': [],
        'optional': []
    },
    'person': {
        'properties': [
            'wdt:P569 ?dob',            # Date of Birth
            'wdt:P570 ?dod'             # Date of Death
        ],
        'optional': [
            'OPTIONAL { ?entity wdt:P19 ?birthPlace }',  # Birth Place (optional)
            'OPTIONAL { ?entity wdt:P21 ?gender }'       # Gender (optional)
        ]
    },
    'event': {
        'properties': [
            'wdt:P585 ?date'            # Date or point in time
        ],
        'optional': [
            'OPTIONAL { ?entity wdt:P17 ?country }',     # Country (optional)
            'OPTIONAL { ?entity wdt:P276 ?location }'    # Location (optional)
        ]
    },
    'ship': {
        'properties': [
            'wdt:P17 ?country',         # Country of origin
            'wdt:P5123 ?shipClass'      # Ship class
        ],
        'optional': [
            'OPTIONAL { ?entity wdt:P2141 ?tonnage }'    # Tonnage (optional)
        ]
    },
    'building': {
        'properties': [
            'wdt:P17 ?country',         # Country
            'wdt:P2044 ?elevation'      # Elevation above sea level
        ],
        'optional': [
            'OPTIONAL { ?entity wdt:P1619 ?dateOpened }'  # Date opened (optional)
        ]
    }
}


def query_wikidata_for_location(query_label, language="en"):
    """ Query Wikidata for a location by label and prioritize exact matches.
    :param query_label: the label to search for
    :param language: the language for the label (optional)
    :return: the query results
    """

    query = f"""
   SELECT ?entity ?entityLabel 
WHERE 
{{
  ?entity rdfs:label ?label.
  FILTER(CONTAINS(?label, "Berlin")).
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en,de". }}
}}
LIMIT 10
    """
    print(query)

    # Set the query and return format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    # Execute the query and get results
    results = sparql.query().convert()
    print(results)
    return results["results"]["bindings"]


# Example usage:
# res = query_wikidata_for_location('Berlin', 'en')
# print(res)


import requests

def search_wikidata2(query):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        'action': 'wbsearchentities',
        'language': 'en',   # Search in English (you can change to 'de' for German)
        'format': 'json',
        'search': query,    # The search term, e.g., "Berlin"
        'limit': 5          # Limit the number of results
    }

    response = requests.get(url, params=params)
    return response.json()

# Example usage:
result = search_wikidata2('Berlin')

# Print the search results
for item in result['search']:
    print(f"Label: {item['label']}, Description: {item.get('description', 'No description')}, ID: {item['id']}")

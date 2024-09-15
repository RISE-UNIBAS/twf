from SPARQLWrapper import SPARQLWrapper, JSON

# Set up the endpoint and query
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
query = """
SELECT ?city ?cityLabel ?country ?countryLabel
WHERE 
{
  ?city wdt:P31 wd:Q515;
        rdfs:label "London"@en;
        wdt:P17 ?country.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
"""

# Set the query and return format
sparql.setQuery(query)
sparql.setReturnFormat(JSON)

# Execute the query and get results
results = sparql.query().convert()

# Print results
for result in results["results"]["bindings"]:
    print(f"City: {result['cityLabel']['value']}, Country: {result['countryLabel']['value']}")
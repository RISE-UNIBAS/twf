from twf.clients.wikidata_client import search_wikidata_entities, is_entity_of_type


def main():
    for query in ["Deutschland", "Hamburg", "Paris", "Sanatorium in den Alpen"]:
        results = search_wikidata_entities(query=query, entity_type="City", language="en", limit=5)
        print("Search Results for", query)
        for result in results:
            print(result)


if __name__ == "__main__":
    main()
    #is_city = is_entity_of_type("Q64", "City")

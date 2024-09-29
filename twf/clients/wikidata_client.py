""" Simple functions to get Wikidata entities and their coordinates. """
import requests


def get_wikidata_entity(entity_id):
    """ Get the data for a Wikidata entity. """
    url = "https://www.wikidata.org/w/api.php"
    params = {
        'action': 'wbgetentities',
        'ids': entity_id,   # The Wikidata entity ID, e.g., 'Q64' for Berlin
        'format': 'json',
        'props': 'claims'   # We're only interested in the claims (properties) of the entity
    }

    response = requests.get(url, params=params, timeout=10)
    print("Entity", response.json())
    return response.json()


def has_coordinates(entity_data):
    """ Check if the Wikidata entity has coordinates. """
    claims = entity_data['entities'].get('Q64', {}).get('claims', {})
    return 'P625' in claims  # Check if the coordinates property (P625) exists


def get_coordinates(entity_data):
    """ Get the coordinates for a Wikidata entity. """
    claims = entity_data['entities'].get('Q64', {}).get('claims', {})
    if 'P625' in claims:
        # Extract the coordinates (latitude and longitude)
        coordinates_data = claims['P625'][0]['mainsnak']['datavalue']['value']
        latitude = coordinates_data['latitude']
        longitude = coordinates_data['longitude']
        return latitude, longitude
    return None


# Example usage:
"""entity_id = 'Q64'  # Berlin
entity_data = get_wikidata_entity(entity_id)
coordinates = get_coordinates(entity_data)

if coordinates:
    print(f"Coordinates for {entity_id}: Latitude = {coordinates[0]}, Longitude = {coordinates[1]}")
else:
    print(f"Entity {entity_id} does not have coordinates.")"""

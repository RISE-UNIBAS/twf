from geopy.geocoders import GeoNames

# Initialize the GeoNames client with your username
geonames_username = 'sorinmarti'  # Replace with your GeoNames username
geolocator = GeoNames(username=geonames_username)

# Example 1: Get location information by latitude and longitude (Reverse Geocoding)

def search_location(query):
    location = geolocator.geocode(query, exactly_one=False)  # `exactly_one=False` returns multiple results
    if location:
        return location
    else:
        return "Location not found"


location_info = search_location('Liestal')
for i in location_info:
    print(f"Location: {i}")
# print(f"Location: {location_info}")


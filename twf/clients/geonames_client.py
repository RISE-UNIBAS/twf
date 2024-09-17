from geopy.geocoders import GeoNames


def search_location(query, geonames_username, exactly_one=False):
    geolocator = GeoNames(username=geonames_username)

    location = geolocator.geocode(query, exactly_one=exactly_one)
    if location:
        if isinstance(location, list):
            return location
        else:
            return [location, ]
    else:
        return None

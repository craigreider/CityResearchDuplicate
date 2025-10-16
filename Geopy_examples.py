from geopy.geocoders import Nominatim

# Create the geolocator object without the timeout parameter
geolocator = Nominatim(user_agent="my_app")

# Pass the timeout value to the geocode() method call
location = geolocator.geocode("1600 Amphitheatre Parkway, Mountain View, CA",timeout=10)

if location:
    print(location.address)

#from wsgiref import headers
import requests
from geopy.geocoders import Nominatim
import json
#from geopy.distance import distance as geopy_distance
import configparser
import csv

KILOMETERS_IN_MILE = 1.60934
MILE_IN_KILOMETERS = 0.621371
"""
This module provides functionality to calculate driving distances between two cities

"""
def get_coordinates(city_name):
    """
    Geocodes a city name to get its coordinates.
    Returns a tuple (latitude, longitude) or (None, None) on failure.
    """
    geolocator = Nominatim(user_agent="distance_calculator",timeout=10)
    try:
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude
        else:
            print(f"Could not find coordinates for: {city_name}")
            return None, None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None

def get_driving_distance_osrm(origin_city, destination_city):
    """
    Calculates the driving distance between two cities using the OSRM public API.
    
    Args:
        origin_city (str): The starting city.
        destination_city (str): The destination city.
        
    Returns:
        tuple: A tuple containing the distance in kilometers and duration in minutes,
               or (None, None) if the request fails.
    """
    # Get coordinates for origin and destination cities
    orig_coords = get_coordinates(origin_city)
    dest_coords = get_coordinates(destination_city)

    if not orig_coords or not dest_coords:
        return None, None

    # OSRM expects coordinates in the format: longitude,latitude
    origin_lon, origin_lat = orig_coords[1], orig_coords[0]
    dest_lon, dest_lat = dest_coords[1], dest_coords[0]

    # Construct the OSRM API URL
    # The public demo server is located at https://router.project-osrm.org
    osrm_url = f"https://router.project-osrm.org/route/v1/driving/{origin_lon},{origin_lat};{dest_lon},{dest_lat}?overview=false"

    try:
        response = requests.get(osrm_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        # Parse the JSON response
        if data['code'] == 'Ok' and 'routes' in data:
            route = data['routes'][0]
            distance_meters = route['distance']
            duration_seconds = route['duration']
            
            distance_km = distance_meters / 1000
            duration_minutes = duration_seconds / 60
            
            return distance_km, duration_minutes
        else:
            print(f"OSRM API error: {data['code']}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Network request error: {e}")
        return None, None

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    city2 = config.get('General', 'city2')
    city2_str = city2.split(",", 1)[0]
    city2_file = city2_str.replace(" ","_")

    cities_file="./data/cities.json"
    #cities_file="./data/cities_test.json"
    with open(cities_file,'r') as json_file:
        cities_text=json_file.read()
        cities=json.loads(cities_text)

    results=[]
    header = ['City1', 'City2', 'Distance_km', 'Distance_miles', 'Duration_minutes', 'Duration_hours'] 
    print(header)
    for city1 in cities:    
        distance, duration = get_driving_distance_osrm(city1, city2)
        if distance is not None:
            #print(f"Drive distance from {city1} to {city2} is {distance:,.1f} km / {distance*MILE_IN_KILOMETERS:,.1f} mi.")
            #print(f"Drive duration is {duration:,.2f} min / {(duration/60):,.2f} hr.")
            row = [city1, city2, f"{distance:,.1f}", f"{distance*MILE_IN_KILOMETERS:,.1f}", f"{duration:,.2f}", f"{(duration/60):,.2f}"]
            print(row)
            results.append(row)
                
    output_file="./data/" + city2_file + ".csv"
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        results_sorted=sorted(results)
        results_sorted.insert(0,header)
        writer.writerows(results_sorted)

if __name__=='__main__':
    main()
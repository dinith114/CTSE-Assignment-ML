import requests

def geocode_city(city_name: str):
    """Query Nominatim API to get actual coordinates"""
    params = {
        'q': city_name,
        'limit': 1,
        'format': 'json'
    }
    
    try:
        headers = {'User-Agent': 'E-Channeling-System/1.0 (+https://github.com)'}
        response = requests.get('https://nominatim.openstreetmap.org/search', 
                              params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            result = data[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            display_name = result.get('display_name', '')
            print(f"\n{city_name}:")
            print(f"  Coordinates: [{lat}, {lon}]")
            print(f"  Location: {display_name}")
            return (lat, lon)
        else:
            print(f"\n{city_name}: NOT FOUND")
            return None
    except Exception as e:
        print(f"\n{city_name}: ERROR - {e}")
        return None

# Check what the API actually returns for these locations
kottawa = geocode_city('Kottawa, Sri Lanka')
national = geocode_city('National Hospital, Sri Lanka')
national_only = geocode_city('National Hospital')

print("\n" + "="*60)
print("Cache currently has:")
import json
with open('app/data/city_distances/city_coordinates.json', 'r') as f:
    cache = json.load(f)
    print(f"kottawa: {cache.get('kottawa')}")
    print(f"national hospital: {cache.get('national hospital')}")
    print(f"national hospital, sri lanka: {cache.get('national hospital, sri lanka')}")

import requests

def search_by_coordinates(query: str):
    """Search for a location"""
    params = {
        'q': query,
        'limit': 5,  # Get top 5 results
        'format': 'json'
    }
    
    try:
        headers = {'User-Agent': 'E-Channeling-System/1.0'}
        response = requests.get('https://nominatim.openstreetmap.org/search', 
                              params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"\nSearch results for: {query}")
        print("="*70)
        for i, result in enumerate(data, 1):
            lat = float(result['lat'])
            lon = float(result['lon'])
            display_name = result.get('display_name', '')
            print(f"{i}. [{lat}, {lon}]")
            print(f"   {display_name}\n")
            
    except Exception as e:
        print(f"Error: {e}")

# Search for National Hospital in different ways
search_by_coordinates('National Hospital Colombo')
search_by_coordinates('National Hospital Sri Lanka')
search_by_coordinates('Colombo General Hospital')

# Calculate distance from Kottawa to potential locations
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

kottawa = [6.8430139, 79.9655312]
print(f"\n\nDistance calculations from Kottawa {kottawa}:")
print("="*70)

# Known hospitals
hospitals = {
    'Beruwala National Hospital': [6.478951, 79.9909991],
    'Kings Hospital': [6.8951925, 79.8793481],
    'Nawaloka Hospitals': [6.9207188, 79.8535879],
    'Durdans Hospital': [6.9022503, 79.8533811],
    'Ninewells Hospital': [6.8950584, 79.8826074],
}

for name, coords in hospitals.items():
    dist = haversine(kottawa[0], kottawa[1], coords[0], coords[1])
    print(f"{name}: {dist:.1f} km")

import requests

def get_weather(district_name):
    """
    Fetches weather for UP districts using Open-Meteo (No API Key required).
    1. Uses Geocoding to get Lat/Long of the district.
    2. Uses Forecast API to get current Temp and Humidity.
    """
    try:
        # Step 1: Geocoding (Convert 'Kanpur, Uttar Pradesh' to Coordinates)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={district_name}&count=1&language=en&format=json"
        geo_resp = requests.get(geo_url, timeout=5).json()
        
        if not geo_resp.get('results'):
            raise Exception("District coordinates not found")
        
        lat = geo_resp['results'][0]['latitude']
        lon = geo_resp['results'][0]['longitude']

        # Step 2: Get Weather using Coordinates
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation&timezone=auto"
        weather_resp = requests.get(weather_url, timeout=5).json()

        return {
            "temp": weather_resp['current']['temperature_2m'],
            "humidity": weather_resp['current']['relative_humidity_2m'],
            "rainfall": weather_resp['current'].get('precipitation', 100.0), # Default to 100 if missing
            "success": True
        }

    except Exception as e:
        print(f"Weather Fetch Error: {e}")
        # Final safety fallback so the demo never crashes
        return {"temp": 32.0, "humidity": 55, "rainfall": 100.0, "success": False}

import requests

def get_weather(district_name):

    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={district_name}&count=1&language=en&format=json"
        geo_resp = requests.get(geo_url, timeout=5).json()

        if not geo_resp.get('results'):
            raise Exception("District coordinates not found")

        lat = geo_resp['results'][0]['latitude']
        lon = geo_resp['results'][0]['longitude']

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m&timezone=auto"
        weather_resp = requests.get(weather_url, timeout=5).json()

        return {
            "temp": weather_resp['current']['temperature_2m'],
            "humidity": weather_resp['current']['relative_humidity_2m'],
            "success": True
        }

    except Exception as e:
        print(f"Weather Fetch Error: {e}")
        return {"temp": 32.0, "humidity": 55, "success": False}

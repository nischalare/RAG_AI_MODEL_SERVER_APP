import requests
from config import settings

def get_weather(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={settings.WEATHER_API_KEY}&q={city}"
    return requests.get(url).json()
import time
import wifi
import json
import ssl
import adafruit_requests as requests
from socketpool import SocketPool, Socket
from adafruit_httpserver import Server, Request, Response, Redirect, GET, POST
# Wi-Fi settings and Weatherstack API key
try:
    from secrets import secrets
except ImportError:
    print("WiFi and API secrets are kept in secrets.py, please add them there!")
    raise

# Connect to Wi-Fi
print("Connecting to Wi-Fi...")
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to Wi-Fi!")

# Set up the Weatherstack API request
api_key = secrets['weatherstack_api_key']
weather_url = "http://api.weatherstack.com/current?access_key={}&query={}"
pool = SocketPool(wifi.radio)

cache_filename = "/weather_cache.json"
cache_duration = 45 * 60  # Cache duration in seconds (45 minutes)
ssl_context = ssl.create_default_context()
urequests = requests.Session(pool, ssl_context)
# Function to get current time from timeapi.io
def fetch_current_time():
    print("Fetching current time...")
    time_url = "https://timeapi.io/api/Time/current/coordinate?latitude=22.5744&longitude=88.3629"
    response = urequests.get(time_url)
    if response.status_code == 200:
        time_data = response.json()
        current_time = time.mktime((
            time_data['year'], time_data['month'], time_data['day'],
            time_data['hour'], time_data['minute'], time_data['seconds'],
            0, 0, 0
        ))
        return current_time
    else:
        print("Failed to fetch current time")
        return None

# Function to fetch weather data from the API
def fetch_weather(location):
    print("Fetching weather data...")
    response = urequests.get(weather_url.format(api_key,location))
    if response.status_code == 200:
        weather_data = response.json()
        current_weather = weather_data['current']
        temperature = current_weather['temperature']
        weather_descriptions = current_weather['weather_descriptions'][0]
        weather_icon_url = current_weather['weather_icons'][0]
        data = {
            'timestamp': fetch_current_time(),
            'temperature': temperature,
            'weather_descriptions': weather_descriptions,
            'weather_icon_url': weather_icon_url,
            'location' : location
        }
        # Save the data to cache
        with open(cache_filename, 'w') as cache_file:
            json.dump(data, cache_file)
        return data
    else:
        print("Failed to fetch weather data")
        return None

# Function to get weather data (from cache or API)
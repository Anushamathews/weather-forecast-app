"""Weather Forecasting App: Flask + Open-Meteo (no API key needed)."""
from datetime import datetime

import requests
from flask import Flask, render_template, request

app = Flask(__name__)

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 8  # seconds; never let a slow API hang the page

# WMO weather codes used by Open-Meteo -> (description, emoji)
WEATHER_CODES = {
    0: ("Clear sky", "☀️"), 1: ("Mainly clear", "🌤️"), 2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"), 45: ("Fog", "🌫️"), 48: ("Freezing fog", "🌫️"),
    51: ("Light drizzle", "🌦️"), 53: ("Drizzle", "🌦️"), 55: ("Heavy drizzle", "🌧️"),
    61: ("Light rain", "🌧️"), 63: ("Rain", "🌧️"), 65: ("Heavy rain", "🌧️"),
    71: ("Light snow", "🌨️"), 73: ("Snow", "🌨️"), 75: ("Heavy snow", "❄️"),
    80: ("Rain showers", "🌦️"), 81: ("Heavy showers", "🌧️"), 82: ("Violent showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"), 96: ("Thunderstorm with hail", "⛈️"), 99: ("Severe thunderstorm", "⛈️"),
}


class WeatherError(Exception):
    """A problem we can explain to the user in plain words."""


def describe(code):
    return WEATHER_CODES.get(code, ("Unknown", "❓"))


def find_city(name):
    """Turn a city name into coordinates using the geocoding API."""
    try:
        resp = requests.get(GEOCODE_URL, params={"name": name, "count": 1}, timeout=TIMEOUT)
        resp.raise_for_status()
        results = resp.json().get("results")
    except requests.RequestException:
        raise WeatherError("Could not reach the weather service. Check your internet and try again.")
    if not results:
        raise WeatherError(f'No city found for "{name}". Check the spelling and try again.')
    return results[0]


def get_forecast(lat, lon):
    """Fetch current conditions and a 7-day forecast."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 7,
    }
    try:
        resp = requests.get(FORECAST_URL, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        raise WeatherError("Could not load the forecast right now. Please try again in a moment.")


def build_view(place, data):
    """Shape the raw API data into what the template needs."""
    cur = data["current"]
    desc, icon = describe(cur["weather_code"])
    daily = data["daily"]
    days = []
    for i, day in enumerate(daily["time"]):
        d_desc, d_icon = describe(daily["weather_code"][i])
        days.append({
            "label": "Today" if i == 0 else datetime.strptime(day, "%Y-%m-%d").strftime("%a %d %b"),
            "icon": d_icon,
            "desc": d_desc,
            "high": round(daily["temperature_2m_max"][i]),
            "low": round(daily["temperature_2m_min"][i]),
            "rain": daily["precipitation_probability_max"][i],
        })
    return {
        "city": place["name"],
        "region": ", ".join(p for p in (place.get("admin1"), place.get("country")) if p),
        "temp": round(cur["temperature_2m"]),
        "feels": round(cur["apparent_temperature"]),
        "humidity": cur["relative_humidity_2m"],
        "wind": round(cur["wind_speed_10m"]),
        "desc": desc,
        "icon": icon,
        "days": days,
    }


@app.route("/")
def index():
    city = request.args.get("city", "").strip()
    weather, error = None, None
    if "city" in request.args:
        if not city:
            error = "Enter a city name to see its forecast."
        else:
            try:
                place = find_city(city)
                weather = build_view(place, get_forecast(place["latitude"], place["longitude"]))
            except WeatherError as exc:
                error = str(exc)
    return render_template("index.html", city=city, weather=weather, error=error)


if __name__ == "__main__":
    app.run(debug=True)

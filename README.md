# Weather Forecasting App

A small Flask web app that shows current weather and a 7-day forecast for any city.

## Features
- City search using the Open-Meteo geocoding API
- Current temperature, feels-like, humidity, and wind speed
- 7-day forecast with highs, lows, and chance of rain
- Friendly errors for unknown cities, empty input, and network failures
- Request timeouts so a slow API never freezes the page

## Tech stack
Python, Flask, Requests, Open-Meteo API (free, no API key), Jinja2, HTML/CSS

## Run locally
```bash
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000

## How it works
1. `find_city()` converts the city name to latitude and longitude.
2. `get_forecast()` requests current and daily weather for those coordinates.
3. `build_view()` reshapes the API data, and the Jinja template renders it.

"""Tests use fake API responses, so they run offline."""
from unittest.mock import patch, MagicMock

import requests
from app import app

GEO = {"results": [{"name": "Kochi", "admin1": "Kerala", "country": "India",
                    "latitude": 9.93, "longitude": 76.27}]}
FORECAST = {
    "current": {"temperature_2m": 29.6, "apparent_temperature": 33.2, "relative_humidity_2m": 78,
                "weather_code": 80, "wind_speed_10m": 12.4},
    "daily": {"time": [f"2026-10-{14 + i}" for i in range(7)],
              "weather_code": [80, 63, 3, 2, 1, 0, 95],
              "temperature_2m_max": [31.2] * 7, "temperature_2m_min": [25.1] * 7,
              "precipitation_probability_max": [70, 80, 40, 20, 10, 0, 60]},
}


def fake_response(payload):
    r = MagicMock()
    r.json.return_value = payload
    r.raise_for_status.return_value = None
    return r


def client():
    return app.test_client()


def test_home_page_has_search_box():
    html = client().get("/").get_data(as_text=True)
    assert "Search for any city" in html


@patch("app.requests.get")
def test_successful_search(mock_get):
    mock_get.side_effect = [fake_response(GEO), fake_response(FORECAST)]
    html = client().get("/?city=Kochi").get_data(as_text=True)
    assert "Kochi" in html and "30°C" in html and "Rain showers" in html
    assert html.count('class="day"') == 7


@patch("app.requests.get")
def test_unknown_city(mock_get):
    mock_get.return_value = fake_response({})
    html = client().get("/?city=Asdfgh").get_data(as_text=True)
    assert "No city found" in html


@patch("app.requests.get", side_effect=requests.ConnectionError)
def test_network_failure(_):
    html = client().get("/?city=Kochi").get_data(as_text=True)
    assert "Could not reach the weather service" in html


def test_empty_city():
    html = client().get("/?city=").get_data(as_text=True)
    assert "Enter a city name" in html

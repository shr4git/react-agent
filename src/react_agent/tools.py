"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

from typing import Any, Callable, List, Optional, cast

from langchain_tavily import TavilySearch
from langgraph.runtime import get_runtime

from react_agent.context import Context

import requests


async def search(query: str) -> Optional[dict[str, Any]]:
    """Search for general web results.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    """
    runtime = get_runtime(Context)
    wrapped = TavilySearch(max_results=runtime.context.max_search_results)
    return cast(dict[str, Any], await wrapped.ainvoke({"query": query}))

async def get_weather(city: str) -> str:
    """Returns current weather in the specified city via Open‑Meteo APIs."""
    try:
        # Geocode
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_resp = await asyncio.to_thread(requests.get, geo_url, timeout=10)
        geo_resp.raise_for_status()
        geo = geo_resp.json()
        if "results" not in geo or not geo["results"]:
            return f"Sorry, could not find location info for city '{city}'."

        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]

        # Weather
        wx_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        wx_resp = await asyncio.to_thread(requests.get, wx_url, timeout=10)
        wx_resp.raise_for_status()
        wx = wx_resp.json()
        t = wx["current_weather"]["temperature"]
        w = wx["current_weather"]["windspeed"]
        return f"Current weather in {city}: temperature {t}°C, windspeed {w} km/h."
    except Exception as e:
        return f"Error retrieving weather data: {e}"

async def get_weather_1(city: str) -> Optional[dict[str, Any]]:
    """Get weather info for given city. """
    geocode_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city,
        "format": "json",
        "limit": 1,
    }
    try:
        geocode_response = requests.get(geocode_url, params=params)
        geocode_response.raise_for_status()
        locations = geocode_response.json()
        if not locations:
            return {"error": f"Can't find location for '{city}'."}
        lat = locations[0]["lat"]
        lon = locations[0]["lon"]

        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
        }
        weather_response = requests.get(weather_url, params=weather_params)
        weather_response.raise_for_status()
        data = weather_response.json()
        current = data.get("current_weather", {})
        temperature = current.get("temperature")
        windspeed = current.get("windspeed")
        weather_code = current.get("weathercode")

        return {
            "city": city.title(),
            "temperature_celsius": temperature,
            "windspeed_kmh": windspeed,
            "weather_code": weather_code,
        }
    except Exception as e:
        return {"error": str(e)}

async def get_weather_str(city: str) -> str:
    """
    Fetch current weather for a city using free geocoding + Open-Meteo API.
    """
    geocode_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city,
        "format": "json",
        "limit": 1,
    }
    geocode_response = requests.get(geocode_url, params=params)

    if not geocode_response.ok or len(geocode_response.json()) == 0:
        return f"Sorry, I couldn't find location for {city}."

    data = geocode_response.json()[0]
    lat = data["lat"]
    lon = data["lon"]

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
    }
    weather_response = requests.get(weather_url, params=weather_params)

    if not weather_response.ok:
        return f"Sorry, I couldn't fetch weather data for {city}."

    weather = weather_response.json().get("current_weather", {})
    temp = weather.get("temperature")
    windspeed = weather.get("windspeed")
    weather_code = weather.get("weathercode")

    return f"The current temperature in {city.title()} is {temp}°C with wind speed {windspeed} km/h (weather code: {weather_code})."


TOOLS: List[Callable[..., Any]] = [search, get_weather]
#TOOLS: List[Callable[..., Any]] = [search]


import os
import requests
from typing import Dict, Any, Optional


class WeatherAPIError(Exception):
    pass


class WeatherAPI:


    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise WeatherAPIError("OpenWeather API key not provided. Set OPENWEATHER_API_KEY env variable.")

        self.current_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

    def _raise_for_status(self, resp: requests.Response):
        if not resp.ok:
            try:
                j = resp.json()
                msg = j.get("message") or j
            except Exception:
                msg = resp.text
            raise WeatherAPIError(f"API request failed [{resp.status_code}]: {msg}")

    def get_current(self, city: str, units: str = "metric") -> Dict[str, Any]:
        params = {"q": city, "units": units, "appid": self.api_key}
        resp = requests.get(self.current_url, params=params, timeout=10)
        self._raise_for_status(resp)
        return resp.json()

    def get_forecast(self, city: str, units: str = "metric") -> Dict[str, Any]:

        params = {"q": city, "units": units, "appid": self.api_key}
        resp = requests.get(self.forecast_url, params=params, timeout=10)
        self._raise_for_status(resp)
        return resp.json()
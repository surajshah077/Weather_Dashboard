from weather_api import WeatherAPI, WeatherAPIError
from city_manager import CityManager
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import pandas as pd


class WeatherApp:
    def __init__(self, api_key: str = None):
        self.api = WeatherAPI(api_key)
        self.store = CityManager()

    def search_city(self, city_name: str) -> Dict[str, Any]:

        try:
            current = self.api.get_current(city_name)
            forecast = self.api.get_forecast(city_name)
            data = {"current": current, "forecast": forecast, "_display_name": current.get("name")}
            self.store._append_history(city_name, None, None, "search")
            return data
        except WeatherAPIError as e:
            raise
        except Exception as e:
            raise WeatherAPIError(f"Unhandled error: {e}")

    def add_favorite_by_search(self, city_name: str) -> bool:
        cur = self.api.get_current(city_name)
        name = cur.get("name")
        return self.store.add_favorite(name, None, None)

    def get_favorites(self) -> List[Dict]:
        return self.store.list_favorites()

    def plot_temperature_trend(self, forecast: Dict[str, Any], show: bool = True, save_path: str = None):
        """
        Plot daily min/max temperatures for 5 days.
        """
        df = pd.DataFrame(forecast["list"])
        df["dt"] = pd.to_datetime(df["dt_txt"])
        df["date"] = df["dt"].dt.date
        df["temp_min"] = df["main"].apply(lambda x: x["temp_min"])
        df["temp_max"] = df["main"].apply(lambda x: x["temp_max"])

        grouped = df.groupby("date").agg({"temp_min": "min", "temp_max": "max"}).reset_index()

        plt.figure(figsize=(8, 4))
        plt.plot(grouped["date"], grouped["temp_min"], marker="o", label="Min Temp (°C)")
        plt.plot(grouped["date"], grouped["temp_max"], marker="o", label="Max Temp (°C)")
        plt.title("5-Day Temperature Trend")
        plt.xlabel("Date")
        plt.ylabel("Temperature (°C)")
        plt.legend()
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
        if show:
            plt.show()
        plt.close()
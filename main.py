import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import os

from app_controller import WeatherApp, WeatherAPIError

class WeatherDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Dashboard")
        self.root.geometry("850x600")
        self.root.resizable(False, False)

        # API Key from environment
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            messagebox.showwarning("API Key Missing", "OPENWEATHER_API_KEY not set! Using placeholder data.")
            self.api_available = False
        else:
            self.api_available = True
            self.app = WeatherApp(self.api_key)

        self.create_widgets()
        self.show_placeholder()

    def create_widgets(self):
        # Top search frame
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(top_frame, text="City:").pack(side="left")
        self.city_entry = ttk.Entry(top_frame, width=30)
        self.city_entry.pack(side="left", padx=5)
        ttk.Button(top_frame, text="Search", command=self.search_weather).pack(side="left", padx=5)

        # Favorites buttons
        fav_frame = ttk.Frame(top_frame)
        fav_frame.pack(side="right")
        ttk.Button(fav_frame, text="Add Favorite", command=self.add_favorite).pack(side="left", padx=5)
        ttk.Button(fav_frame, text="List Favorites", command=self.list_favorites).pack(side="left", padx=5)
        ttk.Button(fav_frame, text="Remove Favorite", command=self.remove_favorite).pack(side="left", padx=5)

        # Weather info display
        self.weather_text = tk.Text(self.root, height=5, width=100, state="disabled", bg="#f0f0f0")
        self.weather_text.pack(padx=10, pady=5)

        # Chart frame
        self.chart_frame = ttk.Frame(self.root)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def show_placeholder(self):
        # Show placeholder text
        self.weather_text.config(state="normal")
        self.weather_text.delete("1.0", tk.END)
        self.weather_text.insert(tk.END, "Welcome to Weather Dashboard!\n")
        self.weather_text.insert(tk.END, "Search a city to see real weather data.\n")
        self.weather_text.config(state="disabled")

        # Placeholder 5-day chart
        placeholder_data = {
            "_display_name": "Placeholder City",
            "forecast": {
                "list": [
                    {"dt_txt": "2025-09-14 12:00:00", "main": {"temp_min": 20, "temp_max": 25}},
                    {"dt_txt": "2025-09-15 12:00:00", "main": {"temp_min": 21, "temp_max": 26}},
                    {"dt_txt": "2025-09-16 12:00:00", "main": {"temp_min": 19, "temp_max": 24}},
                    {"dt_txt": "2025-09-17 12:00:00", "main": {"temp_min": 18, "temp_max": 23}},
                    {"dt_txt": "2025-09-18 12:00:00", "main": {"temp_min": 20, "temp_max": 27}}
                ]
            }
        }
        self.plot_chart(placeholder_data)

    def search_weather(self):
        if not self.api_available:
            messagebox.showinfo("Info", "API not available. Using placeholder data.")
            self.show_placeholder()
            return

        city = self.city_entry.get().strip()
        if not city:
            messagebox.showinfo("Input Required", "Please enter a city name.")
            return

        try:
            data = self.app.search_city(city)
            cur = data.get("current", {})
            main_info = cur.get("main", {})
            temp = main_info.get("temp")
            feels = main_info.get("feels_like")
            weather_list = cur.get("weather") or []
            desc = weather_list[0].get("description") if weather_list else ""

            self.weather_text.config(state="normal")
            self.weather_text.delete("1.0", tk.END)
            self.weather_text.insert(tk.END, f"Weather for {data.get('_display_name')}\n")
            self.weather_text.insert(tk.END, f"Temp: {temp}°C, Feels: {feels}°C, {desc}\n")
            self.weather_text.config(state="disabled")

            if "forecast" in data:
                self.plot_chart(data)

        except WeatherAPIError as e:
            messagebox.showerror("API Error", str(e))
            self.show_placeholder()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.show_placeholder()

    def add_favorite(self):
        if not self.api_available:
            messagebox.showinfo("Info", "API not available.")
            return
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showinfo("Input Required", "Enter city to add to favorites.")
            return
        try:
            ok = self.app.add_favorite_by_search(city)
            messagebox.showinfo("Favorite", "Added to favorites." if ok else "Already in favorites.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def list_favorites(self):
        if not self.api_available:
            messagebox.showinfo("Info", "API not available.")
            return
        favs = self.app.get_favorites()
        if not favs:
            messagebox.showinfo("Favorites", "No favorites yet.")
            return
        fav_names = "\n".join([f.get("name") for f in favs])
        messagebox.showinfo("Favorites", fav_names)

    def remove_favorite(self):
        if not self.api_available:
            messagebox.showinfo("Info", "API not available.")
            return
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showinfo("Input Required", "Enter city to remove from favorites.")
            return
        ok = self.app.store.remove_favorite(city)
        messagebox.showinfo("Remove Favorite", "Removed." if ok else "Not found.")

    def plot_chart(self, data):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        forecast = data.get("forecast")
        if not forecast:
            return

        df = pd.DataFrame(forecast["list"])
        df["dt"] = pd.to_datetime(df["dt_txt"])
        df["date"] = df["dt"].dt.date
        df["temp_min"] = df["main"].apply(lambda x: x["temp_min"])
        df["temp_max"] = df["main"].apply(lambda x: x["temp_max"])
        grouped = df.groupby("date").agg({"temp_min": "min", "temp_max": "max"}).reset_index()

        fig, ax = plt.subplots(figsize=(7, 3), dpi=100)
        ax.plot(grouped["date"], grouped["temp_min"], marker="o", label="Min Temp (°C)", color="blue")
        ax.plot(grouped["date"], grouped["temp_max"], marker="o", label="Max Temp (°C)", color="red")
        ax.set_title(f"5-Day Forecast for {data.get('_display_name')}")
        ax.set_ylabel("Temperature (°C)")
        ax.legend()
        fig.autofmt_xdate()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDashboard(root)
    root.mainloop()

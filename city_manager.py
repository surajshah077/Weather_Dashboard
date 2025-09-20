import json
import csv
from datetime import datetime
from typing import List, Dict, Any
import os

class CityFileError(Exception):
    pass

class CityManager:
    def __init__(self, favorites_path: str = "favorites.json", history_path: str = "history.csv"):
        self.favorites_path = favorites_path
        self.history_path = history_path
        # Ensure files exist
        if not os.path.exists(self.favorites_path):
            self._write_json([])
        if not os.path.exists(self.history_path):
            with open(self.history_path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(["timestamp", "city", "lat", "lon", "action"])

    def _read_json(self):
        try:
            with open(self.favorites_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as e:
            raise CityFileError(f"Could not read favorites file: {e}")

    def _write_json(self, data):
        try:
            with open(self.favorites_path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
        except Exception as e:
            raise CityFileError(f"Could not write favorites file: {e}")

    def list_favorites(self) -> List[Dict[str, Any]]:
        return self._read_json()

    def add_favorite(self, name: str, lat: float, lon: float):
        favs = self._read_json()
        # avoid duplicates by name
        if any(f.get("name") == name for f in favs):
            return False
        favs.append({"name": name, "lat": lat, "lon": lon})
        self._write_json(favs)
        self._append_history(name, lat, lon, "add_favorite")
        return True

    def remove_favorite(self, name: str):
        favs = self._read_json()
        new = [f for f in favs if f.get("name") != name]
        if len(new) == len(favs):
            return False
        self._write_json(new)
        self._append_history(name, None, None, "remove_favorite")
        return True

    def _append_history(self, city: str, lat, lon, action: str):
        try:
            with open(self.history_path, "a", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow([datetime.utcnow().isoformat(), city, lat or "", lon or "", action])
        except Exception:
            pass

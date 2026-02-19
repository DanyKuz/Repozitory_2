import os
import requests
from pathlib import Path
from typing import Optional, Tuple


class MapService:
    
    BASE_URL = "https://static-maps.yandex.ru/v1"
    
    def __init__(self, api_key: str, screen_width: int = 600, screen_height: int = 450):
        self.api_key = api_key
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_image_path = "map.png"
        self.base_step_degrees = 0.01

    def validate_coordinates(self, lat: float, lon: float) -> bool:
        return (-90 <= lat <= 90) and (-180 <= lon <= 180)

    def calculate_step(self, zoom: int) -> float:
        return self.base_step_degrees / (2 ** (zoom - 10))

    def build_map_url(self, lat: float, lon: float, zoom: int) -> str:
        formatted_coords = f"{lon},{lat}"
        return (
            f"{self.BASE_URL}"
            f"?apikey={self.api_key}"
            f"&ll={formatted_coords}"
            f"&z={zoom}"
            f"&size={self.screen_width},{self.screen_height}"
            f"&l=map"
        )

    def download_map(self, url: str) -> bool:
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            with open(self.map_image_path, "wb") as f:
                f.write(response.content)
            return True
        except requests.RequestException:
            return False

    def get_map_image_path(self) -> str:
        return self.map_image_path

    def cleanup(self):
        if os.path.exists(self.map_image_path):
            try:
                os.remove(self.map_image_path)
            except OSError:
                pass

    def pan_coordinates(
        self, 
        lat: float, 
        lon: float, 
        zoom: int, 
        dx: int, 
        dy: int
    ) -> Tuple[float, float]:
        step = self.calculate_step(zoom)
        new_lon = lon + dx * step
        new_lat = lat + dy * step
        
        new_lat = max(-90, min(90, new_lat))
        new_lon = max(-180, min(180, new_lon))
        
        return new_lat, new_lon
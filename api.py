import os
import sys
import requests

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 450
MAX_SCALE_PERCENT = 100
SCALE_CONVERSION = 0.17
MAX_ZOOM = 17

API_KEY_STATIC = '91519429-fd6f-40bb-94ed-e1962e2a8229'

class MapViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.map_image_path = "map.png"
        self.initUI()
        self.valid_inputs()
        self.fetch_map_image()
        self.setup_ui()

    def initUI(self):
        print("Введите широту и долготу через пробел:")
        input_coordinates = input().strip()

        if ',' in input_coordinates:
            print("Ошибка: введите через пробел")
            sys.exit(1)

        print("Введите масштаб в % 0–100:")
        self.raw_scale = input().strip()
        self.input_coordinates = input_coordinates

    def valid_inputs(self):
        self.formatted_coordinates = ','.join(self.input_coordinates.split())

        try:
            scale_percent = float(self.raw_scale)
        except ValueError:
            print("Ошибка: масштаб должен быть числом.")
            sys.exit(1)

        if not (0 <= scale_percent <= MAX_SCALE_PERCENT):
            print(f"Ошибка: масштаб должен находиться в диапазоне от 0 до {MAX_SCALE_PERCENT}%.")
            sys.exit(1)

        self.zoom = max(0, min(MAX_ZOOM, int(SCALE_CONVERSION * scale_percent)))

    def fetch_map_image(self):
        map_url = (
            f"https://static-maps.yandex.ru/v1"
            f"?apikey={API_KEY_STATIC}"
            f"&ll={self.formatted_coordinates}"
            f"&z={self.zoom}"
            f"&size={SCREEN_WIDTH},{SCREEN_HEIGHT}"
            f"&l=map"
        )

        response = requests.get(map_url)

        if not response.ok:
            print("Не удалось получить карту. Проверьте корректность координат.")
            print(f"URL запроса: {map_url}")
            print(f"HTTP статус: {response.status_code} ({response.reason})")
            sys.exit(1)

        with open(self.map_image_path, "wb") as image_file:
            image_file.write(response.content)
            
    def setup_ui(self):
        self.setGeometry(100, 100, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setWindowTitle("Просмотр карты")

        self.image_label = QLabel(self)
        self.pixmap = QPixmap(self.map_image_path)
        self.image_label.setPixmap(self.pixmap)
        self.image_label.move(0, 0)
        
    def close_Event(self, event):
        if os.path.exists(self.map_image_path):
            os.remove(self.map_image_path)
        event.accept()


if __name__ == '__main__':
    application = QApplication(sys.argv)
    viewer = MapViewer()
    viewer.show()
    sys.exit(application.exec())

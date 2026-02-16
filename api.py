import os
import sys

from PyQt6.QtWidgets import QApplication, QWidget, QLabel

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 450
MAX_SCALE_PERCENT = 100
SCALE_CONVERSION = 0.17
MAX_ZOOM = 17

class MapViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.map_image_path = "map.png"
        self.initUI()
        self.valid_inputs()

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

        try:
            scale_percent = float(self.raw_scale)
        except ValueError:
            print("Ошибка: масштаб должен быть числом.")
            sys.exit(1)

        if not (0 <= scale_percent <= MAX_SCALE_PERCENT):
            print(f"Ошибка: масштаб должен находиться в диапазоне от 0 до {MAX_SCALE_PERCENT}%.")
            sys.exit(1)

        self.zoom = max(0, min(MAX_ZOOM, int(SCALE_CONVERSION * scale_percent)))

    def close_Event(self, event):
        if os.path.exists(self.map_image_path):
            os.remove(self.map_image_path)
        event.accept()


if __name__ == '__main__':
    application = QApplication(sys.argv)
    viewer = MapViewer()
    viewer.show()
    sys.exit(application.exec())

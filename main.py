import sys
import os
from dotenv import load_dotenv

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from backend import MapService
from frontend import MapViewer


def main():
    load_dotenv(override=True)
    
    api_key = os.getenv("API_KEY_STATIC")
    if not api_key:
        print("Ошибка: API_KEY_STATIC не найден в .env файле")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    map_service = MapService(
        api_key=api_key,
        screen_width=MapViewer.SCREEN_WIDTH,
        screen_height=MapViewer.SCREEN_HEIGHT
    )
    
    viewer = MapViewer(map_service)
    viewer.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
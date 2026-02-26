import os
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox,
    QFormLayout, QGroupBox, QSpinBox, QGridLayout
)
from PyQt6.QtGui import QPixmap, QFont, QKeyEvent
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from backend import MapService


class MapViewer(QWidget):

    SCREEN_WIDTH = 600
    SCREEN_HEIGHT = 450
    MAX_ZOOM = 17
    MIN_ZOOM = 0

    def __init__(self, map_service: MapService):
        super().__init__()
        self.map_service = map_service
        self.current_lat: float = None
        self.current_lon: float = None
        self.current_zoom: int = 10

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Просмотр карты с навигацией")
        self.setGeometry(100, 100, self.SCREEN_WIDTH +
                         50, self.SCREEN_HEIGHT + 300)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._create_coords_group())
        main_layout.addWidget(self._create_control_group())

        self.load_button = QPushButton("Обновить карту по координатам")
        self.load_button.clicked.connect(self.load_map)
        self.load_button.setStyleSheet("padding: 8px; font-weight: bold;")
        main_layout.addWidget(self.load_button)

        main_layout.addWidget(self._create_image_label())
        self.setLayout(main_layout)

    def _create_coords_group(self) -> QGroupBox:
        group = QGroupBox("Координаты центра")
        layout = QFormLayout()

        self.lat_input = QLineEdit()
        self.lat_input.setPlaceholderText("Широта (например: 55.75)")
        self.lat_input.textChanged.connect(self._on_coords_changed)
        layout.addRow("Широта:", self.lat_input)

        self.lon_input = QLineEdit()
        self.lon_input.setPlaceholderText("Долгота (например: 37.61)")
        self.lon_input.textChanged.connect(self._on_coords_changed)
        layout.addRow("Долгота:", self.lon_input)

        group.setLayout(layout)
        return group

    def _create_control_group(self) -> QGroupBox:
        group = QGroupBox("Управление картой")
        layout = QVBoxLayout()

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Уровень зума:"))
        self.zoom_slider = QSpinBox()
        self.zoom_slider.setRange(self.MIN_ZOOM, self.MAX_ZOOM)
        self.zoom_slider.setValue(self.current_zoom)
        self.zoom_slider.valueChanged.connect(self._on_zoom_slider_changed)
        slider_layout.addWidget(self.zoom_slider)
        layout.addLayout(slider_layout)

        group.setLayout(layout)
        return group

    def _create_image_label(self) -> QLabel:
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setMinimumSize(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        label.setStyleSheet(
            "border: 2px solid #444; background-color: #f0f0f0; color: #888;"
        )
        label.setText(
            "Карта появится здесь\nВведите координаты и нажмите Загрузить")
        self.image_label = label
        return label

    def _on_coords_changed(self):
        if os.path.exists(self.map_service.map_image_path):
            try:
                os.remove(self.map_service.map_image_path)
            except OSError:
                pass

    def _on_zoom_slider_changed(self, value: int):
        self.current_zoom = value
        if self.current_lat is not None and self.current_lon is not None:
            self.load_map()

    def keyPressEvent(self, event: QKeyEvent):
        if self.current_lat is None or self.current_lon is None:
            QMessageBox.information(
                self, "Инфо", "Сначала загрузите карту, введя координаты.")
            return

        if event.key() == Qt.Key.Key_W or event.key() == Qt.Key.Key_Up:
            self._pan_map(0, 1)
        elif event.key() == Qt.Key.Key_S or event.key() == Qt.Key.Key_Down:
            self._pan_map(0, -1)
        elif event.key() == Qt.Key.Key_A or event.key() == Qt.Key.Key_Left:
            self._pan_map(-1, 0)
        elif event.key() == Qt.Key.Key_D or event.key() == Qt.Key.Key_Right:
            self._pan_map(1, 0)
        elif event.key() == Qt.Key.Key_PageUp:
            if self.current_zoom < self.MAX_ZOOM:
                self.current_zoom += 1
                self.load_map()
        elif event.key() == Qt.Key.Key_PageDown:
            if self.current_zoom > self.MIN_ZOOM:
                self.current_zoom -= 1
                self.load_map()

    def _pan_map(self, dx: int, dy: int):
        new_lat, new_lon = self.map_service.pan_coordinates(
            self.current_lat, self.current_lon, self.current_zoom, dx, dy
        )
        if -90 <= new_lat <= 90 and -180 <= new_lon <= 180:
            self.current_lat, self.current_lon = new_lat, new_lon
            self.lat_input.setText(f"{self.current_lat:.6f}")
            self.lon_input.setText(f"{self.current_lon:.6f}")
            self.load_map()
        else:
            QMessageBox.warning(self, "Предупреждение",
                                "Достигнут край карты!")

    def load_map(self):
        lat_text = self.lat_input.text().strip()
        lon_text = self.lon_input.text().strip()

        if not lat_text or not lon_text:
            QMessageBox.warning(
                self, "Ошибка", "Пожалуйста, введите широту и долготу")
            return

        try:
            lat = float(lat_text)
            lon = float(lon_text)
            if not self.map_service.validate_coordinates(lat, lon):
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверные координаты!")
            return

        self.current_lat, self.current_lon = lat, lon
        url = self.map_service.build_map_url(lat, lon, self.current_zoom)

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            if not self.map_service.download_map(url):
                raise Exception("Ошибка загрузки изображения")
            pixmap = QPixmap(self.map_service.get_map_image_path())
            if pixmap.isNull():
                raise Exception("Не удалось декодировать изображение")
            self.image_label.setPixmap(pixmap.scaled(
                self.SCREEN_WIDTH, self.SCREEN_HEIGHT,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            self.image_label.setText("")
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось загрузить карту:\n{str(e)}")
        finally:
            QApplication.restoreOverrideCursor()

    def closeEvent(self, event):
        self.map_service.cleanup()
        event.accept()
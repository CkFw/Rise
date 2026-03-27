# Этот файл является частью Rise Browser.
# Copyright (C) 2026 Clark Flow (Егор)
# 
# Rise Browser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Rise Browser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Окно для настройки внешнего вида адресной строки.
"""
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QSlider, QColorDialog, QWidget
)
from PySide6.QtCore import Qt, Signal, QTimer, QPoint
from PySide6.QtGui import QColor, QMouseEvent

logger = logging.getLogger(__name__)

class CustomizeUrlBarWindow(QDialog):
    applied = Signal()

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.setWindowTitle("Настройка адресной строки")
        self.setGeometry(300, 300, 450, 250)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setModal(True)

        self.dragging = False
        self.drag_position = QPoint()

        self._load_initial_values()
        self._setup_ui()
        self._apply_styles()
        self._load_settings()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False
        event.accept()

    def _apply_styles(self):
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 12px;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QPushButton {
                background-color: #00a8ff;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0097e6;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #252525;
            }
            QCheckBox::indicator:checked {
                background-color: #00a8ff;
                border-color: #00a8ff;
            }
            QSlider {
                background-color: transparent;
            }
            QSlider::groove:horizontal {
                border: 1px solid #444;
                height: 4px;
                background: #252525;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #00a8ff;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """)

    def _load_initial_values(self):
        self._border_enabled = self.api.get_urlbar_border_enabled()
        self._transparency = self.api.get_urlbar_transparency()
        self._bg_color = self.api.get_urlbar_bg_color()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        title_bar = QWidget()
        title_bar.setFixedHeight(5)
        title_bar.setStyleSheet("background-color: transparent;")
        main_layout.addWidget(title_bar)

        # Чекбокс "Обрамление"
        self.border_check = QCheckBox("Показывать обрамление")
        self.border_check.setChecked(self._border_enabled)
        main_layout.addWidget(self.border_check)

        # Прозрачность
        transparency_layout = QHBoxLayout()
        transparency_layout.addWidget(QLabel("Прозрачность:"))
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(0, 100)
        self.transparency_slider.setValue(self._transparency)
        self.transparency_slider.setToolTip("0 – непрозрачный, 100 – полностью прозрачный")
        transparency_layout.addWidget(self.transparency_slider)
        self.transparency_label = QLabel(f"{self._transparency}%")
        transparency_layout.addWidget(self.transparency_label)
        main_layout.addLayout(transparency_layout)

        # Цвет фона
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Цвет фона:"))
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 25)
        self.color_btn.setStyleSheet(f"background-color: {self._bg_color}; border: 1px solid gray;")
        self.color_btn.clicked.connect(self._choose_color)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        main_layout.addLayout(color_layout)

        # Кнопки
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(self._apply)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        self.transparency_slider.valueChanged.connect(self._update_transparency_label)

    def _update_transparency_label(self, value):
        self.transparency_label.setText(f"{value}%")

    def _choose_color(self):
        color = QColorDialog.getColor(QColor(self._bg_color))
        if color.isValid():
            self._bg_color = color.name()
            self.color_btn.setStyleSheet(f"background-color: {self._bg_color}; border: 1px solid gray;")

    def _load_settings(self):
        self.border_check.setChecked(self._border_enabled)
        self.transparency_slider.setValue(self._transparency)
        self._update_transparency_label(self._transparency)
        self.color_btn.setStyleSheet(f"background-color: {self._bg_color}; border: 1px solid gray;")

    def _apply(self):
        self.api.set_urlbar_border_enabled(self.border_check.isChecked())
        self.api.set_urlbar_transparency(self.transparency_slider.value())
        self.api.set_urlbar_bg_color(self._bg_color)

        self.applied.emit()
        self.accept()
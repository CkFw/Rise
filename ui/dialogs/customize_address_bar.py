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
Диалог для настройки внешнего вида адресной строки.
"""
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QColorDialog, QGroupBox, QWidget
)
from PySide6.QtCore import Qt, Signal, QTimer, QPoint
from PySide6.QtGui import QColor, QMouseEvent

logger = logging.getLogger(__name__)

class CustomizeAddressBarWindow(QDialog):
    applied = Signal()

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.setWindowTitle("Настройка адресной строки")
        self.setGeometry(300, 300, 400, 250)
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
            QGroupBox {
                color: #00a8ff;
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: transparent;
            }
            QGroupBox::title {
                left: 10px;
                padding: 0 5px 0 5px;
                color: #00a8ff;
                background-color: transparent;
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
            QPushButton#iconBtn {
                background-color: transparent;
                border: 1px solid #555;
                color: #00a8ff;
            }
            QPushButton#iconBtn:hover {
                background-color: #333;
                border-color: #00a8ff;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
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
        """)

    def _load_initial_values(self):
        self._border_enabled = self.api.get_address_bar_border_enabled()
        self._transparent_bg = self.api.get_address_bar_transparent_bg()
        self._bg_color = self.api.get_address_bar_bg_color()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Группа обрамления
        border_group = QGroupBox("Обрамление")
        border_layout = QVBoxLayout()
        self.border_check = QCheckBox("Показывать рамку вокруг адресной строки")
        self.border_check.setChecked(self._border_enabled)
        border_layout.addWidget(self.border_check)
        border_group.setLayout(border_layout)
        layout.addWidget(border_group)

        # Группа фона
        bg_group = QGroupBox("Фон")
        bg_layout = QVBoxLayout()

        self.transparent_check = QCheckBox("Прозрачный фон")
        self.transparent_check.setChecked(self._transparent_bg)
        self.transparent_check.toggled.connect(self._on_transparent_toggled)
        bg_layout.addWidget(self.transparent_check)

        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Цвет фона:"))
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(50, 25)
        self.bg_color_btn.setObjectName("iconBtn")
        self.bg_color_btn.clicked.connect(self._choose_bg_color)
        color_layout.addWidget(self.bg_color_btn)
        color_layout.addStretch()
        bg_layout.addLayout(color_layout)

        bg_group.setLayout(bg_layout)
        layout.addWidget(bg_group)

        layout.addStretch()

        # Кнопки
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(self._apply)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self._on_transparent_toggled(self._transparent_bg)

    def _on_transparent_toggled(self, checked):
        self.bg_color_btn.setEnabled(not checked)

    def _choose_bg_color(self):
        initial = QColor(self._bg_color)
        color = QColorDialog.getColor(initial)
        if color.isValid():
            self._bg_color = color.name()
            self.bg_color_btn.setStyleSheet(f"background-color: {self._bg_color}; border: 1px solid gray;")

    def _load_settings(self):
        self.border_check.setChecked(self._border_enabled)
        self.transparent_check.setChecked(self._transparent_bg)
        self.bg_color_btn.setStyleSheet(f"background-color: {self._bg_color}; border: 1px solid gray;")

    def _apply(self):
        self.api.set_address_bar_border_enabled(self.border_check.isChecked())
        self.api.set_address_bar_transparent_bg(self.transparent_check.isChecked())
        self.api.set_address_bar_bg_color(self._bg_color)

        self.applied.emit()
        self.accept()
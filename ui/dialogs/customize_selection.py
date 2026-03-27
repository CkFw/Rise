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
Окно настройки выделения текста (только сплошной цвет).
"""
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QColorDialog, QGroupBox, QWidget
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QColor, QMouseEvent

logger = logging.getLogger(__name__)

class CustomizeSelectionWindow(QDialog):
    applied = Signal()

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.setWindowTitle("Настройка выделения текста")
        self.setGeometry(300, 300, 400, 200)
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
        self._enabled = self.api.get_selection_custom_enabled()
        self._color = self.api.get_selection_color1()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        title_bar = QWidget()
        title_bar.setFixedHeight(5)
        title_bar.setStyleSheet("background-color: transparent;")
        main_layout.addWidget(title_bar)

        self.enable_check = QCheckBox("Включить кастомное выделение текста")
        self.enable_check.setChecked(self._enabled)
        main_layout.addWidget(self.enable_check)

        color_group = QGroupBox("Цвет выделения")
        color_layout = QVBoxLayout()

        color_picker_layout = QHBoxLayout()
        color_picker_layout.addWidget(QLabel("Цвет:"))
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 25)
        self.color_btn.setObjectName("iconBtn")
        self.color_btn.clicked.connect(self._choose_color)
        color_picker_layout.addWidget(self.color_btn)
        color_picker_layout.addStretch()
        color_layout.addLayout(color_picker_layout)

        color_group.setLayout(color_layout)
        main_layout.addWidget(color_group)

        main_layout.addStretch()

        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(self._apply)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        self.enable_check.toggled.connect(self._on_enabled_toggled)
        self._on_enabled_toggled(self._enabled)

    def _on_enabled_toggled(self, checked):
        self.color_btn.setEnabled(checked)

    def _choose_color(self):
        color = QColorDialog.getColor(QColor(self._color))
        if color.isValid():
            self._color = color.name()
            self.color_btn.setStyleSheet(f"background-color: {self._color}; border: 1px solid gray;")

    def _load_settings(self):
        self.enable_check.setChecked(self._enabled)
        self.color_btn.setStyleSheet(f"background-color: {self._color}; border: 1px solid gray;")
        self.color_btn.setEnabled(self._enabled)

    def _apply(self):
        self.api.set_selection_custom_enabled(self.enable_check.isChecked())
        self.api.set_selection_color1(self._color)
        self.api.set_selection_type('solid')
        self.applied.emit()
        self.accept()
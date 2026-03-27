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
Окно настройки центральной области домашней страницы.
Позволяет включать/выключать элементы и задавать их позицию по X и Y.
"""
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QGroupBox, QWidget, QScrollArea, QApplication,
    QSpinBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QTimer, QPoint
from PySide6.QtGui import QPalette, QColor, QMouseEvent

logger = logging.getLogger(__name__)

class CustomizeCenterWindow(QDialog):
    """Окно для настройки элементов центра домашней страницы."""

    applied = Signal()

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.setWindowTitle("Настройка центральной области")

        screen = QApplication.primaryScreen()
        if screen:
            screen_height = screen.availableGeometry().height()
            half_height = screen_height // 2
        else:
            half_height = 500

        self.setGeometry(250, 150, 650, half_height)
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
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()

    def _apply_styles(self):
        self.setAttribute(Qt.WA_StyledBackground, True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#1a1a1a"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333;
            }
            QGroupBox {
                color: #00a8ff;
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                left: 10px;
                padding: 0 5px;
                color: #00a8ff;
            }
            QLabel {
                color: #ffffff;
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
            QSpinBox {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px;
                min-width: 80px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #777;
            }
        """)

    def _load_initial_values(self):
        self.elements = [
            ('title', 'Заголовок RISE'),
            ('search', 'Поисковая строка'),
            ('indicator', 'Индикатор поисковой системы'),
            ('addBtn', 'Кнопка "+"'),
            ('bookmarks', 'Контейнер ярлыков'),
        ]
        self.visible = {}
        self.offset_x = {}
        self.offset_y = {}
        for key, _ in self.elements:
            self.visible[key] = self.api.get_center_element_visible(key, True)
            self.offset_x[key] = self.api.get_center_element_offset_x(key, 0)
            self.offset_y[key] = self.api.get_center_element_offset_y(key, 0)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Полоса для перетаскивания
        title_bar = QWidget()
        title_bar.setFixedHeight(5)
        title_bar.setStyleSheet("background-color: transparent;")
        main_layout.addWidget(title_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; }")
        scroll.viewport().setStyleSheet("background-color: transparent;")

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(content)
        layout.setSpacing(15)

        # Группа для каждого элемента с чекбоксом и полями X,Y
        self.widgets = {}
        for key, label in self.elements:
            group = QGroupBox(label)
            grid = QGridLayout()

            cb = QCheckBox("Видимый")
            cb.setChecked(self.visible[key])
            grid.addWidget(cb, 0, 0, 1, 2)

            grid.addWidget(QLabel("Смещение X:"), 1, 0)
            spin_x = QSpinBox()
            spin_x.setRange(-500, 500)
            spin_x.setValue(self.offset_x[key])
            grid.addWidget(spin_x, 1, 1)

            grid.addWidget(QLabel("Смещение Y:"), 2, 0)
            spin_y = QSpinBox()
            spin_y.setRange(-500, 500)
            spin_y.setValue(self.offset_y[key])
            grid.addWidget(spin_y, 2, 1)

            group.setLayout(grid)
            layout.addWidget(group)

            self.widgets[key] = (cb, spin_x, spin_y)

        layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

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

    def _load_settings(self):
        for key, (cb, spin_x, spin_y) in self.widgets.items():
            cb.setChecked(self.visible[key])
            spin_x.setValue(self.offset_x[key])
            spin_y.setValue(self.offset_y[key])

    def _apply(self):
        for key, (cb, spin_x, spin_y) in self.widgets.items():
            self.api.set_center_element_visible(key, cb.isChecked())
            self.api.set_center_element_offset_x(key, spin_x.value())
            self.api.set_center_element_offset_y(key, spin_y.value())

        self.applied.emit()
        QTimer.singleShot(100, self.accept)
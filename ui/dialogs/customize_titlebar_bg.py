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
Окно для настройки фона верхней панели (сплошной цвет, градиент, изображение).
"""
import os
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QColorDialog, QGroupBox, QWidget, QFileDialog, QMessageBox,
    QComboBox, QSpinBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QTimer, QPoint
from PySide6.QtGui import QColor, QMouseEvent, QPixmap

from ui.widgets.image_crop_widget import ImageCropWidget

logger = logging.getLogger(__name__)

class CustomizeTitleBarBgWindow(QDialog):
    applied = Signal()

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.setWindowTitle("Фон верхней панели")
        self.setGeometry(300, 300, 500, 650)
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
            QComboBox, QSpinBox {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #252525;
                color: #fff;
                selection-background-color: #00a8ff;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

    def _load_initial_values(self):
        self._bg_type = self.api.get_titlebar_bg_type()
        self._solid_color = self.api.get_titlebar_bg_color()
        self._gradient_color1 = self.api.get_titlebar_gradient_color1()
        self._gradient_color2 = self.api.get_titlebar_gradient_color2()
        self._gradient_angle = self.api.get_titlebar_gradient_angle()
        self._image_path = self.api.get_titlebar_bg_image_path()
        self._image_crop = self.api.get_titlebar_bg_image_crop()
        self._scale_mode = self._image_crop.get('scale', 'cover')

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

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

        # Тип фона
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Тип фона:"))
        self.bg_type_combo = QComboBox()
        self.bg_type_combo.addItems(["Сплошной цвет", "Градиент", "Изображение"])
        self.bg_type_combo.currentTextChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.bg_type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Сплошной цвет
        self.solid_widget = QWidget()
        solid_layout = QHBoxLayout(self.solid_widget)
        solid_layout.addWidget(QLabel("Цвет:"))
        self.solid_color_btn = QPushButton()
        self.solid_color_btn.setFixedSize(50, 25)
        self.solid_color_btn.setObjectName("iconBtn")
        self.solid_color_btn.clicked.connect(lambda: self._choose_color('solid'))
        solid_layout.addWidget(self.solid_color_btn)
        solid_layout.addStretch()
        layout.addWidget(self.solid_widget)

        # Градиент
        self.gradient_widget = QWidget()
        grad_layout = QVBoxLayout(self.gradient_widget)
        grad_layout.setContentsMargins(0, 0, 0, 0)
        grad1_layout = QHBoxLayout()
        grad1_layout.addWidget(QLabel("Цвет 1:"))
        self.grad_color1_btn = QPushButton()
        self.grad_color1_btn.setFixedSize(50, 25)
        self.grad_color1_btn.setObjectName("iconBtn")
        self.grad_color1_btn.clicked.connect(lambda: self._choose_color('grad1'))
        grad1_layout.addWidget(self.grad_color1_btn)
        grad1_layout.addStretch()
        grad_layout.addLayout(grad1_layout)
        grad2_layout = QHBoxLayout()
        grad2_layout.addWidget(QLabel("Цвет 2:"))
        self.grad_color2_btn = QPushButton()
        self.grad_color2_btn.setFixedSize(50, 25)
        self.grad_color2_btn.setObjectName("iconBtn")
        self.grad_color2_btn.clicked.connect(lambda: self._choose_color('grad2'))
        grad2_layout.addWidget(self.grad_color2_btn)
        grad2_layout.addStretch()
        grad_layout.addLayout(grad2_layout)
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("Угол (градусы):"))
        self.grad_angle_spin = QSpinBox()
        self.grad_angle_spin.setRange(0, 360)
        angle_layout.addWidget(self.grad_angle_spin)
        angle_layout.addStretch()
        grad_layout.addLayout(angle_layout)
        layout.addWidget(self.gradient_widget)

        # Изображение
        self.image_widget = QWidget()
        image_layout = QVBoxLayout(self.image_widget)
        image_layout.setContentsMargins(0, 0, 0, 0)

        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Файл:"))
        self.image_path_label = QLabel("не выбрано")
        self.image_path_label.setWordWrap(True)
        file_layout.addWidget(self.image_path_label, 1)
        choose_btn = QPushButton("Обзор...")
        choose_btn.setObjectName("iconBtn")
        choose_btn.clicked.connect(self._choose_image)
        file_layout.addWidget(choose_btn)
        image_layout.addLayout(file_layout)

        # Режим масштабирования
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Масштабирование (применяется после кадрирования):"))
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["cover", "contain", "stretch"])
        self.scale_combo.setCurrentText(self._scale_mode)
        scale_layout.addWidget(self.scale_combo)
        scale_layout.addStretch()
        image_layout.addLayout(scale_layout)

        # Виджет кадрирования
        self.crop_widget = ImageCropWidget()
        self.crop_widget.setFixedHeight(300)
        image_layout.addWidget(QLabel("Выберите область для кадрирования:"))
        image_layout.addWidget(self.crop_widget)

        layout.addWidget(self.image_widget)

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

        self._on_type_changed(self.bg_type_combo.currentText())

    def _on_type_changed(self, text):
        self.solid_widget.setVisible(text == "Сплошной цвет")
        self.gradient_widget.setVisible(text == "Градиент")
        self.image_widget.setVisible(text == "Изображение")

    def _choose_color(self, which):
        if which == 'solid':
            initial = QColor(self._solid_color)
            color = QColorDialog.getColor(initial)
            if color.isValid():
                self._solid_color = color.name()
                self.solid_color_btn.setStyleSheet(f"background-color: {self._solid_color}; border: 1px solid gray;")
        elif which == 'grad1':
            color = QColorDialog.getColor(QColor(self._gradient_color1))
            if color.isValid():
                self._gradient_color1 = color.name()
                self.grad_color1_btn.setStyleSheet(f"background-color: {self._gradient_color1}; border: 1px solid gray;")
        elif which == 'grad2':
            color = QColorDialog.getColor(QColor(self._gradient_color2))
            if color.isValid():
                self._gradient_color2 = color.name()
                self.grad_color2_btn.setStyleSheet(f"background-color: {self._gradient_color2}; border: 1px solid gray;")

    def _choose_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение для фона панели", "",
                                              "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if path:
            self._image_path = path
            self.image_path_label.setText(os.path.basename(path))
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.crop_widget.set_pixmap(pixmap)

    def _load_settings(self):
        if self._bg_type == 'gradient':
            self.bg_type_combo.setCurrentText("Градиент")
        elif self._bg_type == 'image':
            self.bg_type_combo.setCurrentText("Изображение")
        else:
            self.bg_type_combo.setCurrentText("Сплошной цвет")

        self.solid_color_btn.setStyleSheet(f"background-color: {self._solid_color}; border: 1px solid gray;")
        self.grad_color1_btn.setStyleSheet(f"background-color: {self._gradient_color1}; border: 1px solid gray;")
        self.grad_color2_btn.setStyleSheet(f"background-color: {self._gradient_color2}; border: 1px solid gray;")
        self.grad_angle_spin.setValue(self._gradient_angle)

        self.scale_combo.setCurrentText(self._scale_mode)
        if self._image_path and os.path.exists(self._image_path):
            self.image_path_label.setText(os.path.basename(self._image_path))
            pixmap = QPixmap(self._image_path)
            if not pixmap.isNull():
                self.crop_widget.set_pixmap(pixmap)
        else:
            self.image_path_label.setText("не выбрано")

    def _apply(self):
        bg_type = self.bg_type_combo.currentText()
        if bg_type == "Сплошной цвет":
            self.api.set_titlebar_bg_type('color')
            self.api.set_titlebar_bg_color(self._solid_color)
        elif bg_type == "Градиент":
            self.api.set_titlebar_bg_type('gradient')
            self.api.set_titlebar_gradient_color1(self._gradient_color1)
            self.api.set_titlebar_gradient_color2(self._gradient_color2)
            self.api.set_titlebar_gradient_angle(self.grad_angle_spin.value())
        else:  # Изображение
            self.api.set_titlebar_bg_type('image')
            self.api.set_titlebar_bg_image_path(self._image_path)
            crop = self.crop_widget.get_crop_params()
            crop['scale'] = self.scale_combo.currentText()
            self.api.set_titlebar_bg_image_crop(crop)

        self.applied.emit()
        self.accept()
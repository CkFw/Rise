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
Окно настройки фона домашней страницы.
"""
import os
import hashlib
import shutil
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QColorDialog, QGroupBox, QWidget, QFileDialog, QMessageBox,
    QComboBox, QSpinBox, QCheckBox, QScrollArea, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer, QPoint, QRect
from PySide6.QtGui import QColor, QPalette, QMouseEvent, QPixmap
from core.config import DATA_DIR
from ui.widgets.image_crop_widget import ImageCropWidget

logger = logging.getLogger(__name__)


class CustomizeHomeBackgroundWindow(QDialog):
    """Окно для настройки фона домашней страницы."""

    applied = Signal()

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.setWindowTitle("Настройка фона домашней страницы")

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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        event.accept()

    def _copy_file_to_data(self, source_path):
        """Копирует файл в папку data и возвращает просто имя файла."""
        base = os.path.basename(source_path)
        name, ext = os.path.splitext(base)
        path_hash = hashlib.md5(source_path.encode('utf-8')).hexdigest()[:8]
        dest_filename = f"{name}_{path_hash}{ext}"
        dest_path = os.path.join(DATA_DIR, dest_filename)
        if not os.path.exists(dest_path):
            try:
                shutil.copy2(source_path, dest_path)
                logger.info(f"Copied file to {dest_path}")
            except Exception as e:
                logger.error(f"Failed to copy file: {e}")
                return None
        return dest_filename

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
            QComboBox, QSpinBox {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px;
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
        self.bg_type = self.api.get_home_bg_type()
        self.color1 = self.api.get_home_bg_color1()
        self.color2 = self.api.get_home_bg_color2()
        self.gradient_angle = self.api.get_home_bg_gradient_angle()
        self.image_path = self.api.get_home_bg_image_path()
        self.image_fit = self.api.get_home_bg_image_fit()
        self.animation_enabled = self.api.get_home_bg_animation_enabled()
        self.animation_speed = self.api.get_home_bg_animation_speed()
        self.image_crop = self.api.get_home_bg_image_crop()

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
        type_group = QGroupBox("Тип фона")
        type_layout = QVBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Градиент", "Сплошной цвет", "Изображение"])
        self.type_combo.currentTextChanged.connect(self._update_type_visibility)
        type_layout.addWidget(self.type_combo)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # Градиент
        self.gradient_group = QGroupBox("Градиент")
        grad_layout = QVBoxLayout()

        color1_layout = QHBoxLayout()
        color1_layout.addWidget(QLabel("Цвет 1:"))
        self.color1_btn = QPushButton()
        self.color1_btn.setFixedSize(50, 25)
        self.color1_btn.setObjectName("iconBtn")
        self.color1_btn.clicked.connect(lambda: self._choose_color('color1'))
        color1_layout.addWidget(self.color1_btn)
        color1_layout.addStretch()
        grad_layout.addLayout(color1_layout)

        color2_layout = QHBoxLayout()
        color2_layout.addWidget(QLabel("Цвет 2:"))
        self.color2_btn = QPushButton()
        self.color2_btn.setFixedSize(50, 25)
        self.color2_btn.setObjectName("iconBtn")
        self.color2_btn.clicked.connect(lambda: self._choose_color('color2'))
        color2_layout.addWidget(self.color2_btn)
        color2_layout.addStretch()
        grad_layout.addLayout(color2_layout)

        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("Угол (градусы):"))
        self.angle_spin = QSpinBox()
        self.angle_spin.setRange(0, 360)
        self.angle_spin.setValue(self.gradient_angle)
        angle_layout.addWidget(self.angle_spin)
        angle_layout.addStretch()
        grad_layout.addLayout(angle_layout)

        self.gradient_group.setLayout(grad_layout)
        layout.addWidget(self.gradient_group)

        # Сплошной цвет
        self.solid_group = QGroupBox("Сплошной цвет")
        solid_layout = QHBoxLayout()
        solid_layout.addWidget(QLabel("Цвет:"))
        self.solid_color_btn = QPushButton()
        self.solid_color_btn.setFixedSize(50, 25)
        self.solid_color_btn.setObjectName("iconBtn")
        self.solid_color_btn.clicked.connect(lambda: self._choose_color('solid'))
        solid_layout.addWidget(self.solid_color_btn)
        solid_layout.addStretch()
        self.solid_group.setLayout(solid_layout)
        layout.addWidget(self.solid_group)

        # Изображение
        self.image_group = QGroupBox("Изображение")
        image_layout = QVBoxLayout()

        img_path_layout = QHBoxLayout()
        img_path_layout.addWidget(QLabel("Файл:"))
        self.image_path_label = QLabel(self.image_path if self.image_path else "не выбрано")
        self.image_path_label.setWordWrap(True)
        img_path_layout.addWidget(self.image_path_label, 1)
        choose_img_btn = QPushButton("Обзор...")
        choose_img_btn.setObjectName("iconBtn")
        choose_img_btn.clicked.connect(self._choose_image)
        img_path_layout.addWidget(choose_img_btn)
        image_layout.addLayout(img_path_layout)

        fit_layout = QHBoxLayout()
        fit_layout.addWidget(QLabel("Режим заполнения:"))
        self.fit_combo = QComboBox()
        self.fit_combo.addItems(["cover", "contain", "stretch"])
        self.fit_combo.setCurrentText(self.image_fit)
        fit_layout.addWidget(self.fit_combo)
        fit_layout.addStretch()
        image_layout.addLayout(fit_layout)

        # Виджет кадрирования
        self.crop_widget = ImageCropWidget()
        self.crop_widget.setFixedHeight(300)
        image_layout.addWidget(QLabel("Выберите область для кадрирования:"))
        image_layout.addWidget(self.crop_widget)

        self.image_group.setLayout(image_layout)
        layout.addWidget(self.image_group)

        # Анимация
        self.anim_group = QGroupBox("Анимация фоновых кругов")
        anim_layout = QVBoxLayout()
        self.anim_check = QCheckBox("Включить анимацию")
        self.anim_check.setChecked(self.animation_enabled)
        anim_layout.addWidget(self.anim_check)

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Скорость (длительность в сек):"))
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(5, 60)
        self.speed_spin.setValue(self.animation_speed)
        speed_layout.addWidget(self.speed_spin)
        speed_layout.addStretch()
        anim_layout.addLayout(speed_layout)

        self.anim_group.setLayout(anim_layout)
        layout.addWidget(self.anim_group)

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

        self._update_type_visibility()

    def _update_type_visibility(self):
        t = self.type_combo.currentText()
        self.gradient_group.setVisible(t == "Градиент")
        self.solid_group.setVisible(t == "Сплошной цвет")
        self.image_group.setVisible(t == "Изображение")
        self.anim_group.setVisible(t in ["Градиент", "Сплошной цвет"])

        if t == "Сплошной цвет":
            self.solid_color_btn.setStyleSheet(f"background-color: {self.color1}; border: 1px solid gray;")
        elif t == "Градиент":
            self.color1_btn.setStyleSheet(f"background-color: {self.color1}; border: 1px solid gray;")
            self.color2_btn.setStyleSheet(f"background-color: {self.color2}; border: 1px solid gray;")

    def _choose_color(self, target):
        if target == 'color1':
            initial = QColor(self.color1)
        elif target == 'color2':
            initial = QColor(self.color2)
        else:
            initial = QColor(self.color1)
        color = QColorDialog.getColor(initial)
        if color.isValid():
            if target == 'color1':
                self.color1 = color.name()
                self.color1_btn.setStyleSheet(f"background-color: {self.color1}; border: 1px solid gray;")
            elif target == 'color2':
                self.color2 = color.name()
                self.color2_btn.setStyleSheet(f"background-color: {self.color2}; border: 1px solid gray;")
            else:
                self.color1 = color.name()
                self.solid_color_btn.setStyleSheet(f"background-color: {self.color1}; border: 1px solid gray;")

    def _choose_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                              "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if path:
            file_name = self._copy_file_to_data(path)
            if file_name:
                self.image_path = file_name
                self.image_path_label.setText(file_name)
                # Загружаем изображение в виджет кадрирования
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    self.crop_widget.set_pixmap(pixmap)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось скопировать файл.")

    def _get_rect_from_crop(self, img_size):
        """Преобразует сохранённые проценты в QRect."""
        crop = self.image_crop
        x = int(crop.get('x', 0) / 100.0 * img_size.width())
        y = int(crop.get('y', 0) / 100.0 * img_size.height())
        w = int(crop.get('width', 100) / 100.0 * img_size.width())
        h = int(crop.get('height', 100) / 100.0 * img_size.height())
        return QRect(x, y, w, h)

    def _load_settings(self):
        self.type_combo.setCurrentText(
            self.bg_type if self.bg_type in ["Градиент", "Сплошной цвет", "Изображение"] else "Градиент")
        self.color1_btn.setStyleSheet(f"background-color: {self.color1}; border: 1px solid gray;")
        self.color2_btn.setStyleSheet(f"background-color: {self.color2}; border: 1px solid gray;")
        self.solid_color_btn.setStyleSheet(f"background-color: {self.color1}; border: 1px solid gray;")
        self.angle_spin.setValue(self.gradient_angle)
        self.image_path_label.setText(self.image_path if self.image_path else "не выбрано")
        self.fit_combo.setCurrentText(self.image_fit)
        self.anim_check.setChecked(self.animation_enabled)
        self.speed_spin.setValue(self.animation_speed)
        self._update_type_visibility()
        # Загружаем изображение в виджет кадрирования, если оно есть
        if self.image_path:
            full_path = os.path.join(DATA_DIR, self.image_path)
            if os.path.exists(full_path):
                pixmap = QPixmap(full_path)
                if not pixmap.isNull():
                    self.crop_widget.set_pixmap(pixmap)
                    self.crop_widget.crop_rect = self._get_rect_from_crop(pixmap.size())

    def _apply(self):
        self.api.set_home_bg_type(self.type_combo.currentText())
        self.api.set_home_bg_color1(self.color1)
        self.api.set_home_bg_color2(self.color2)
        self.api.set_home_bg_gradient_angle(self.angle_spin.value())
        self.api.set_home_bg_image_path(self.image_path if self.type_combo.currentText() == "Изображение" else "")
        self.api.set_home_bg_image_fit(self.fit_combo.currentText())
        self.api.set_home_bg_animation_enabled(self.anim_check.isChecked())
        self.api.set_home_bg_animation_speed(self.speed_spin.value())
        # Сохраняем параметры кадрирования
        if self.type_combo.currentText() == "Изображение" and self.crop_widget.pixmap:
            crop_params = self.crop_widget.get_crop_params()
            self.api.set_home_bg_image_crop(crop_params)

        self.applied.emit()
        QTimer.singleShot(100, self.accept)
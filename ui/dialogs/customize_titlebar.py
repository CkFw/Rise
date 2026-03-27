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
Окно настройки верхней панели (видимость кнопок, высота, цвета вкладок, иконки, цвет кнопок, автоскрытие).
"""
import os
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QColorDialog, QGroupBox, QWidget, QFileDialog, QMessageBox, QSpinBox,
    QScrollArea, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer, QPoint
from PySide6.QtGui import QColor, QPalette, QMouseEvent

logger = logging.getLogger(__name__)

class CustomizeTitleBarWindow(QDialog):
    """Окно для настройки внешнего вида верхней панели и вкладок (без фона)."""
    applied = Signal()

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.setWindowTitle("Верхняя панель")
        self.setGeometry(200, 200, 600, 650)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setModal(True)

        self.dragging = False
        self.drag_position = QPoint()

        self._load_initial_values()
        self._setup_ui()
        self._apply_styles()
        self._load_settings()

    # --- Перетаскивание окна ---
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
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#1a1a1a"))
        palette.setColor(QPalette.Base, QColor("#252525"))
        palette.setColor(QPalette.Text, QColor("#ffffff"))
        palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
        palette.setColor(QPalette.Button, QColor("#00a8ff"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

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
            QPushButton:disabled {
                background-color: #444;
                color: #888;
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
            QSpinBox {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px;
                min-height: 25px;
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
        self._current_height = self.api.get_titlebar_height()
        self._current_btn_color = self.api.get_titlebar_button_color()

        self._tab_custom_enabled = self.api.get_tab_custom_colors_enabled()
        self._tab_bg_color = self.api.get_tab_bg_color()
        self._tab_text_color = self.api.get_tab_text_color()
        self._tab_active_bg_color = self.api.get_tab_active_bg_color()
        self._tab_active_text_color = self.api.get_tab_active_text_color()

        self._auto_hide_enabled = self.api.get_auto_hide_enabled()
        self._auto_hide_delay = self.api.get_auto_hide_delay()

        self.buttons_with_icons = [
            ('back', 'Назад'),
            ('forward', 'Вперёд'),
            ('refresh', 'Обновить'),
            ('downloads', 'Загрузки'),
            ('history', 'История'),
            ('settings', 'Настройки'),
            ('icon', 'Логотип'),
        ]
        self.icon_enabled = {}
        self.icon_path = {}
        for name, _ in self.buttons_with_icons:
            self.icon_enabled[name] = self.api.get_icon_custom_enabled(name)
            self.icon_path[name] = self.api.get_icon_custom_path(name)

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

        # --- Видимость кнопок ---
        visibility_group = QGroupBox("Видимость элементов верхней панели")
        vis_layout = QVBoxLayout()
        self.button_checkboxes = {}
        for name, label in self.buttons_with_icons:
            cb = QCheckBox(label)
            vis_layout.addWidget(cb)
            self.button_checkboxes[name] = cb
        visibility_group.setLayout(vis_layout)
        layout.addWidget(visibility_group)

        # --- Настройки панели (высота, цвет кнопок) ---
        panel_group = QGroupBox("Верхняя панель")
        panel_layout = QVBoxLayout()
        panel_layout.setSpacing(10)

        # Высота
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Высота нижней части панели (px):"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(40, 150)
        self.height_spin.setValue(self._current_height)
        height_layout.addWidget(self.height_spin)
        height_layout.addStretch()
        panel_layout.addLayout(height_layout)

        # Цвет кнопок
        btn_color_layout = QHBoxLayout()
        btn_color_layout.addWidget(QLabel("Цвет кнопок:"))
        self.btn_color_btn = QPushButton()
        self.btn_color_btn.setFixedSize(50, 25)
        self.btn_color_btn.setObjectName("iconBtn")
        self.btn_color_btn.clicked.connect(self._choose_btn_color)
        btn_color_layout.addWidget(self.btn_color_btn)
        btn_color_layout.addStretch()
        panel_layout.addLayout(btn_color_layout)

        panel_group.setLayout(panel_layout)
        layout.addWidget(panel_group)

        # --- Вкладки ---
        tab_group = QGroupBox("Вкладки")
        tab_layout = QVBoxLayout()
        self.tab_custom_cb = QCheckBox("Включить кастомные цвета вкладок")
        self.tab_custom_cb.setChecked(self._tab_custom_enabled)
        self.tab_custom_cb.toggled.connect(self._on_tab_custom_toggled)
        tab_layout.addWidget(self.tab_custom_cb)

        tab_bg_layout = QHBoxLayout()
        tab_bg_layout.addWidget(QLabel("Фон обычной вкладки:"))
        self.tab_bg_btn = QPushButton()
        self.tab_bg_btn.setFixedSize(50, 25)
        self.tab_bg_btn.setObjectName("iconBtn")
        self.tab_bg_btn.clicked.connect(lambda: self._choose_tab_color('bg'))
        tab_bg_layout.addWidget(self.tab_bg_btn)
        tab_bg_layout.addStretch()
        tab_layout.addLayout(tab_bg_layout)

        tab_text_layout = QHBoxLayout()
        tab_text_layout.addWidget(QLabel("Текст обычной вкладки:"))
        self.tab_text_btn = QPushButton()
        self.tab_text_btn.setFixedSize(50, 25)
        self.tab_text_btn.setObjectName("iconBtn")
        self.tab_text_btn.clicked.connect(lambda: self._choose_tab_color('text'))
        tab_text_layout.addWidget(self.tab_text_btn)
        tab_text_layout.addStretch()
        tab_layout.addLayout(tab_text_layout)

        tab_active_bg_layout = QHBoxLayout()
        tab_active_bg_layout.addWidget(QLabel("Фон активной вкладки:"))
        self.tab_active_bg_btn = QPushButton()
        self.tab_active_bg_btn.setFixedSize(50, 25)
        self.tab_active_bg_btn.setObjectName("iconBtn")
        self.tab_active_bg_btn.clicked.connect(lambda: self._choose_tab_color('active_bg'))
        tab_active_bg_layout.addWidget(self.tab_active_bg_btn)
        tab_active_bg_layout.addStretch()
        tab_layout.addLayout(tab_active_bg_layout)

        tab_active_text_layout = QHBoxLayout()
        tab_active_text_layout.addWidget(QLabel("Текст активной вкладки:"))
        self.tab_active_text_btn = QPushButton()
        self.tab_active_text_btn.setFixedSize(50, 25)
        self.tab_active_text_btn.setObjectName("iconBtn")
        self.tab_active_text_btn.clicked.connect(lambda: self._choose_tab_color('active_text'))
        tab_active_text_layout.addWidget(self.tab_active_text_btn)
        tab_active_text_layout.addStretch()
        tab_layout.addLayout(tab_active_text_layout)

        tab_group.setLayout(tab_layout)
        layout.addWidget(tab_group)

        # --- Кастомные иконки ---
        icons_group = QGroupBox("Кастомные иконки")
        icons_layout = QVBoxLayout()
        self.icon_widgets = {}
        for name, label in self.buttons_with_icons:
            h_layout = QHBoxLayout()
            cb = QCheckBox(f"{label}:")
            cb.setChecked(self.icon_enabled[name])
            h_layout.addWidget(cb)

            path_btn = QPushButton("Выбрать файл...")
            path_btn.setFixedWidth(120)
            path_btn.setObjectName("iconBtn")
            path_btn.clicked.connect(lambda checked, n=name: self._choose_icon_file(n))
            h_layout.addWidget(path_btn)

            path_label = QLabel(self.icon_path[name] if self.icon_path[name] else "не выбран")
            path_label.setWordWrap(True)
            path_label.setStyleSheet("color: #aaa; font-size: 11px; background-color: transparent;")
            h_layout.addWidget(path_label, 1)

            icons_layout.addLayout(h_layout)
            self.icon_widgets[name] = (cb, path_btn, path_label)

        icons_group.setLayout(icons_layout)
        layout.addWidget(icons_group)

        # --- Автоскрытие ---
        auto_hide_group = QGroupBox("Автоскрытие верхней панели")
        auto_hide_layout = QVBoxLayout()
        self.auto_hide_check = QCheckBox("Включить автоскрытие")
        self.auto_hide_check.setChecked(self._auto_hide_enabled)
        auto_hide_layout.addWidget(self.auto_hide_check)

        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Задержка перед скрытием (сек):"))
        self.auto_hide_delay_spin = QSpinBox()
        self.auto_hide_delay_spin.setRange(1, 30)
        self.auto_hide_delay_spin.setValue(self._auto_hide_delay)
        delay_layout.addWidget(self.auto_hide_delay_spin)
        delay_layout.addStretch()
        auto_hide_layout.addLayout(delay_layout)

        auto_hide_group.setLayout(auto_hide_layout)
        layout.addWidget(auto_hide_group)

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

        self._update_tab_enabled_state()

    # --- Методы ---
    def _choose_btn_color(self):
        color = QColorDialog.getColor(QColor(self._current_btn_color))
        if color.isValid():
            self._current_btn_color = color.name()
            self.btn_color_btn.setStyleSheet(f"background-color: {self._current_btn_color}; border: 1px solid gray;")

    def _choose_tab_color(self, which):
        if which == 'bg':
            color = QColorDialog.getColor(QColor(self._tab_bg_color))
            if color.isValid():
                self._tab_bg_color = color.name()
                self.tab_bg_btn.setStyleSheet(f"background-color: {self._tab_bg_color}; border: 1px solid gray;")
        elif which == 'text':
            color = QColorDialog.getColor(QColor(self._tab_text_color))
            if color.isValid():
                self._tab_text_color = color.name()
                self.tab_text_btn.setStyleSheet(f"background-color: {self._tab_text_color}; border: 1px solid gray;")
        elif which == 'active_bg':
            color = QColorDialog.getColor(QColor(self._tab_active_bg_color))
            if color.isValid():
                self._tab_active_bg_color = color.name()
                self.tab_active_bg_btn.setStyleSheet(f"background-color: {self._tab_active_bg_color}; border: 1px solid gray;")
        elif which == 'active_text':
            color = QColorDialog.getColor(QColor(self._tab_active_text_color))
            if color.isValid():
                self._tab_active_text_color = color.name()
                self.tab_active_text_btn.setStyleSheet(f"background-color: {self._tab_active_text_color}; border: 1px solid gray;")

    def _choose_icon_file(self, name):
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Выберите иконку для {name}", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.ico);;All Files (*)"
        )
        if file_path:
            self.icon_path[name] = file_path
            self.icon_widgets[name][2].setText(file_path)
            self.icon_widgets[name][0].setChecked(True)

    def _on_tab_custom_toggled(self, checked):
        self._update_tab_enabled_state()

    def _update_tab_enabled_state(self):
        enabled = self.tab_custom_cb.isChecked()
        self.tab_bg_btn.setEnabled(enabled)
        self.tab_text_btn.setEnabled(enabled)
        self.tab_active_bg_btn.setEnabled(enabled)
        self.tab_active_text_btn.setEnabled(enabled)

    def _load_settings(self):
        for name, cb in self.button_checkboxes.items():
            cb.setChecked(self.api.get_titlebar_button_visible(name, True))

        self.height_spin.setValue(self._current_height)
        self.btn_color_btn.setStyleSheet(f"background-color: {self._current_btn_color}; border: 1px solid gray;")

        self.tab_custom_cb.setChecked(self._tab_custom_enabled)
        self._update_tab_previews()
        self._update_tab_enabled_state()

        for name, (cb, btn, label) in self.icon_widgets.items():
            cb.setChecked(self.icon_enabled[name])
            label.setText(self.icon_path[name] if self.icon_path[name] else "не выбран")

        self.auto_hide_check.setChecked(self._auto_hide_enabled)
        self.auto_hide_delay_spin.setValue(self._auto_hide_delay)

    def _update_tab_previews(self):
        self.tab_bg_btn.setStyleSheet(f"background-color: {self._tab_bg_color}; border: 1px solid gray;")
        self.tab_text_btn.setStyleSheet(f"background-color: {self._tab_text_color}; border: 1px solid gray;")
        self.tab_active_bg_btn.setStyleSheet(f"background-color: {self._tab_active_bg_color}; border: 1px solid gray;")
        self.tab_active_text_btn.setStyleSheet(f"background-color: {self._tab_active_text_color}; border: 1px solid gray;")

    def _apply(self):
        for name, (cb, btn, label) in self.icon_widgets.items():
            if cb.isChecked() and not self.icon_path[name]:
                QMessageBox.warning(self, "Ошибка", f"Для кнопки '{name}' включена кастомная иконка, но не выбран файл.")
                return

        for name, cb in self.button_checkboxes.items():
            self.api.set_titlebar_button_visible(name, cb.isChecked())

        self.api.set_titlebar_height(self.height_spin.value())
        self.api.set_titlebar_button_color(self._current_btn_color)

        self.api.set_tab_custom_colors_enabled(self.tab_custom_cb.isChecked())
        self.api.set_tab_bg_color(self._tab_bg_color)
        self.api.set_tab_text_color(self._tab_text_color)
        self.api.set_tab_active_bg_color(self._tab_active_bg_color)
        self.api.set_tab_active_text_color(self._tab_active_text_color)

        for name, (cb, btn, label) in self.icon_widgets.items():
            self.api.set_icon_custom_enabled(name, cb.isChecked())
            self.api.set_icon_custom_path(name, self.icon_path[name] if cb.isChecked() else "")

        self.api.set_auto_hide_enabled(self.auto_hide_check.isChecked())
        self.api.set_auto_hide_delay(self.auto_hide_delay_spin.value())

        self.applied.emit()
        QTimer.singleShot(100, self.accept)
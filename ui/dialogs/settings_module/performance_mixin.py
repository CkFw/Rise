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

# ui/dialogs/settings_module/performance_mixin.py
"""
Миксин для вкладки производительности.
"""
import logging
from PySide6.QtWidgets import (
    QLabel, QSpinBox, QCheckBox, QPushButton, QHBoxLayout, QVBoxLayout,
    QGroupBox, QScrollArea, QWidget, QMessageBox
)
from PySide6.QtCore import Qt

from core.config import ADBLOCK_MODE_NAMES

logger = logging.getLogger(__name__)


class PerformanceMixin:
    """Миксин для настройки производительности"""

    def setup_performance_tab(self):
        """Создаёт и возвращает вкладку производительности"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        layout.addWidget(scroll)

        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        scroll.setWidget(container)
        cl = QVBoxLayout(container)
        cl.setSpacing(10)

        cl.addWidget(QLabel("⚡ Оптимизация памяти и графики"))

        info = QLabel(
            "Браузер может автоматически выгружать из памяти старые неиспользуемые вкладки.\n"
            "Укажите интервал неактивности (в минутах), после которого вкладка будет выгружена.\n"
            "При переключении на выгруженную вкладку она загрузится заново."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        cl.addWidget(info)

        h = QHBoxLayout()
        h.addWidget(QLabel("Выгружать через (минут):"))
        self.discard_spin = QSpinBox()
        self.discard_spin.setRange(1, 120)
        self.discard_spin.setSuffix(" мин")
        self.discard_spin.setValue(self.api.get_discard_interval() // 60)
        h.addWidget(self.discard_spin)
        h.addStretch()
        cl.addLayout(h)

        # ---- Размер кэша ----
        cache_group = QGroupBox("Кэш HTTP")
        cache_layout = QVBoxLayout()
        cache_info = QLabel(
            "Кэш хранит загруженные файлы (включая видео) на диске. "
            "Увеличение размера может ускорить повторные просмотры, "
            "но потребляет больше места на диске. "
            "Изменение размера вступит в силу после перезапуска браузера."
        )
        cache_info.setWordWrap(True)
        cache_info.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        cache_layout.addWidget(cache_info)

        cache_size_layout = QHBoxLayout()
        cache_size_layout.addWidget(QLabel("Максимальный размер кэша (МБ):"))
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 2048)
        self.cache_size_spin.setSuffix(" МБ")
        self.cache_size_spin.setValue(self.api.get_cache_size_mb())
        cache_size_layout.addWidget(self.cache_size_spin)
        cache_size_layout.addStretch()
        cache_layout.addLayout(cache_size_layout)

        cache_group.setLayout(cache_layout)
        cl.addWidget(cache_group)

        # ---- Группа Vulkan ----
        cl.addWidget(self._create_vulkan_group())

        # ---- Группа отключения функций ----
        cl.addWidget(self._create_features_group())

        # ---- Видеооптимизации (новая группа) ----
        video_group = QGroupBox("Энергосбережение при просмотре видео")
        video_layout = QVBoxLayout()
        video_info = QLabel(
            "Удаление скрытых видео из DOM освобождает память и снижает нагрузку на процессор.\n"
            "Применяется для видео, которые не видны на экране и находятся в паузе.\n"
            "Работает на всех вкладках."
        )
        video_info.setWordWrap(True)
        video_info.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        video_layout.addWidget(video_info)

        self.video_optimizations_check = QCheckBox("Удалять скрытые видео из памяти (экономия ресурсов)")
        self.video_optimizations_check.setChecked(self.api.get_video_optimizations_enabled())
        video_layout.addWidget(self.video_optimizations_check)

        video_group.setLayout(video_layout)
        cl.addWidget(video_group)

        # ---- CSS content-visibility (экспериментально) ----
        css_group = QGroupBox("Экспериментальные оптимизации рендеринга")
        css_layout = QVBoxLayout()
        css_info = QLabel(
            "content-visibility: auto — современная CSS-техника, "
            "которая откладывает рендеринг элементов вне видимой области. "
            "Может ускорить прокрутку и снизить потребление CPU на длинных страницах. "
            "На некоторых сайтах может вызывать артефакты, поэтому включена по умолчанию."
        )
        css_info.setWordWrap(True)
        css_info.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        css_layout.addWidget(css_info)

        self.content_visibility_check = QCheckBox("Использовать content-visibility: auto для скрытых элементов")
        self.content_visibility_check.setChecked(self.api.get_content_visibility_enabled())
        css_layout.addWidget(self.content_visibility_check)

        css_group.setLayout(css_layout)
        cl.addWidget(css_group)

        # ---- Кнопка сохранения ----
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton("💾 Сохранить настройки производительности")
        save_btn.setProperty("class", "save-btn")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: #fff;
                border: none;
                padding: 12px 30px;
                border-radius: 25px;
                font-weight: bold;
                font-size: 15px;
                min-width: 220px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        save_btn.clicked.connect(self.save_performance_settings)
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()
        cl.addLayout(btn_layout)

        cl.addStretch()
        return tab

    def _create_vulkan_group(self):
        group = QGroupBox("Аппаратное ускорение")
        layout = QVBoxLayout()
        info = QLabel(
            "Включение аппаратного ускорения через Vulkan может снизить нагрузку на процессор.\n"
            "Требуется поддержка со стороны драйверов. При проблемах отключите эту опцию."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        layout.addWidget(info)
        self.vulkan_check = QCheckBox("Включить Vulkan (требуется перезапуск)")
        layout.addWidget(self.vulkan_check)
        group.setLayout(layout)
        return group

    def _create_features_group(self):
        group = QGroupBox("Отключение ненужных функций (экономия памяти)")
        layout = QVBoxLayout()
        info = QLabel(
            "Отключение этих функций освобождает память, занимаемую соответствующими модулями Chromium.\n"
            "Изменения вступят в силу после перезапуска браузера."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        layout.addWidget(info)

        self.print_bg_check = QCheckBox("Отключить печать фоновых элементов")
        self.print_bg_check.setChecked(not self.api.get_print_backgrounds_enabled())
        layout.addWidget(self.print_bg_check)

        self.js_windows_check = QCheckBox("Разрешить JavaScript открывать новые окна")
        self.js_windows_check.setChecked(self.api.get_javascript_can_open_windows())
        layout.addWidget(self.js_windows_check)

        self.local_storage_check = QCheckBox("Включить локальное хранилище (localStorage)")
        self.local_storage_check.setChecked(self.api.get_local_storage_enabled())
        layout.addWidget(self.local_storage_check)

        self.error_page_check = QCheckBox("Показывать страницы ошибок")
        self.error_page_check.setChecked(self.api.get_error_page_enabled())
        layout.addWidget(self.error_page_check)

        self.predictive_network_check = QCheckBox("Предзагрузка ссылок (Predictive Network Actions)")
        self.predictive_network_check.setChecked(self.api.get_predictive_network_actions_enabled())
        layout.addWidget(self.predictive_network_check)

        group.setLayout(layout)
        return group

    def save_performance_settings(self):
        """Сохраняет все настройки производительности."""
        # Интервал выгрузки вкладок
        minutes = self.discard_spin.value()
        seconds = minutes * 60
        self.api.save_discard_interval(seconds)
        if self.parent_window and hasattr(self.parent_window, 'update_discard_interval'):
            self.parent_window.update_discard_interval(seconds)

        # Размер кэша
        cache_mb = self.cache_size_spin.value()
        self.api.save_cache_size_mb(cache_mb)
        if self.parent_window and hasattr(self.parent_window, 'update_http_cache_size'):
            self.parent_window.update_http_cache_size(cache_mb)

        # Видеооптимизации
        self.api.save_video_optimizations_enabled(self.video_optimizations_check.isChecked())

        # CSS content-visibility
        self.api.save_content_visibility_enabled(self.content_visibility_check.isChecked())

        # Настройки функций
        self.api.save_print_backgrounds_enabled(not self.print_bg_check.isChecked())
        self.api.save_javascript_can_open_windows(self.js_windows_check.isChecked())
        self.api.save_local_storage_enabled(self.local_storage_check.isChecked())
        self.api.save_error_page_enabled(self.error_page_check.isChecked())
        self.api.save_predictive_network_actions_enabled(self.predictive_network_check.isChecked())

        # Настройка Vulkan (сохраняется в config.ini)
        self._save_config()

        QMessageBox.information(
            self,
            "Готово",
            "Настройки производительности сохранены.\n"
            "Изменения кэша и функций, помеченных как требующие перезапуска, вступят в силу после перезапуска браузера.\n"
            "Видеооптимизации и content-visibility применяются на всех страницах при следующей их загрузке."
        )
        logger.info("Performance settings saved")
        self.close()
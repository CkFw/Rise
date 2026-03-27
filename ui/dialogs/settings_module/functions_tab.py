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
Вкладка "Функции" в диалоге настроек.
Содержит настройки PDF, блокировщика рекламы, перевода, полноэкранного режима.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QCheckBox, QComboBox, QPushButton
)
from core.config import ADBLOCK_MODE_NAMES


def setup_functions_tab(self):
    """Создаёт и возвращает вкладку 'Функции'."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setSpacing(15)

    # ---------- Группа: Просмотр PDF ----------
    pdf_group = QGroupBox("Просмотр PDF")
    pdf_layout = QVBoxLayout()
    pdf_info = QLabel(
        "При перетаскивании PDF-файла в окно браузера можно открывать его в отдельном окне.\n"
        "Если отключено, файл будет скачиваться как обычно."
    )
    pdf_info.setWordWrap(True)
    pdf_info.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
    pdf_layout.addWidget(pdf_info)

    self.pdf_separate_check = QCheckBox("Открывать PDF в отдельном окне")
    self.pdf_separate_check.setChecked(self.api.get_pdf_separate_enabled())
    pdf_layout.addWidget(self.pdf_separate_check)

    self.pdf_viewer_check = QCheckBox("Встроенный просмотрщик PDF")
    self.pdf_viewer_check.setChecked(self.api.get_pdf_viewer_enabled())
    pdf_layout.addWidget(self.pdf_viewer_check)

    pdf_group.setLayout(pdf_layout)
    layout.addWidget(pdf_group)

    # ---------- Группа: Блокировщик рекламы ----------
    adblock_group = QGroupBox("Блокировщик рекламы")
    adblock_layout = QVBoxLayout()
    adblock_info = QLabel(
        "Выберите режим блокировки:\n"
        "• Простой — только основные домены (минимальное потребление)\n"
        "• Расширенный — использует списки EasyList (рекомендуется)\n"
        "• Интеллектуальный — анализирует типы ресурсов (максимальная защита)"
    )
    adblock_info.setWordWrap(True)
    adblock_info.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
    adblock_layout.addWidget(adblock_info)

    self.adblock_check = QCheckBox("Включить блокировщик рекламы")
    self.adblock_check.setChecked(self.api.get_adblock_enabled())
    adblock_layout.addWidget(self.adblock_check)

    mode_layout = QHBoxLayout()
    mode_layout.addWidget(QLabel("Режим:"))
    self.adblock_mode_combo = QComboBox()
    self.adblock_mode_combo.addItems(ADBLOCK_MODE_NAMES)
    current_mode = self.api.get_adblock_mode()
    mode_index = 0
    if current_mode == "advanced":
        mode_index = 1
    elif current_mode == "smart":
        mode_index = 2
    self.adblock_mode_combo.setCurrentIndex(mode_index)
    mode_layout.addWidget(self.adblock_mode_combo)
    mode_layout.addStretch()
    adblock_layout.addLayout(mode_layout)

    adblock_group.setLayout(adblock_layout)
    layout.addWidget(adblock_group)

    # ---------- Группа: Дополнительные функции ----------
    extra_group = QGroupBox("Дополнительные функции")
    extra_layout = QVBoxLayout()

    self.translate_check = QCheckBox("Включить перевод выделенного текста (ПКМ)")
    self.translate_check.setChecked(self.api.get_translate_enabled())
    extra_layout.addWidget(self.translate_check)

    self.fullscreen_check = QCheckBox("Поддержка полноэкранного режима")
    self.fullscreen_check.setChecked(self.api.get_fullscreen_support_enabled())
    extra_layout.addWidget(self.fullscreen_check)

    extra_group.setLayout(extra_layout)
    layout.addWidget(extra_group)

    # Кнопка сохранения
    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    save_btn = QPushButton("💾 Сохранить настройки функций")
    save_btn.setProperty("class", "save-btn")
    save_btn.clicked.connect(self.save_functions_settings)
    btn_layout.addWidget(save_btn)
    btn_layout.addStretch()
    layout.addLayout(btn_layout)

    layout.addStretch()
    return tab
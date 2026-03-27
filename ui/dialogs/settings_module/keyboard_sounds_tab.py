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

# ui/dialogs/settings_module/keyboard_sounds_tab.py
"""
Вкладка "Звук клавиатуры" в диалоге настроек.
"""
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QSlider, QPushButton, QFileDialog, QLineEdit
)
from PySide6.QtCore import Qt


def setup_keyboard_sounds_tab(self):
    """Создаёт и возвращает вкладку 'Звук клавиатуры'."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setSpacing(15)

    layout.addWidget(self._create_info_label(
        "⌨️ Настройка звуков нажатия клавиш.\n"
        "Вы можете включить звук, выбрать свой звуковой файл и настроить громкость.\n"
        "Поддерживаются форматы WAV, MP3, OGG."
    ))

    # Чекбокс включения звуков
    self.keyboard_sounds_check = QCheckBox("Включить звуки клавиатуры")
    self.keyboard_sounds_check.setChecked(self.api.get_keyboard_sounds_enabled())
    layout.addWidget(self.keyboard_sounds_check)

    # Выбор звукового файла
    file_layout = QHBoxLayout()
    file_layout.addWidget(QLabel("Звуковой файл:"))
    self.keyboard_sound_path_edit = QLineEdit()
    self.keyboard_sound_path_edit.setText(self.api.get_keyboard_sound_path())
    self.keyboard_sound_path_edit.setReadOnly(True)
    file_layout.addWidget(self.keyboard_sound_path_edit, 1)

    browse_btn = QPushButton("Обзор...")
    browse_btn.clicked.connect(self._browse_keyboard_sound)
    file_layout.addWidget(browse_btn)

    layout.addLayout(file_layout)

    # Регулятор громкости
    volume_layout = QHBoxLayout()
    volume_layout.addWidget(QLabel("Громкость:"))
    self.keyboard_sound_volume_slider = QSlider(Qt.Horizontal)
    self.keyboard_sound_volume_slider.setRange(0, 100)
    self.keyboard_sound_volume_slider.setValue(self.api.get_keyboard_sound_volume())
    volume_layout.addWidget(self.keyboard_sound_volume_slider)

    self.keyboard_sound_volume_label = QLabel(f"{self.keyboard_sound_volume_slider.value()}%")
    volume_layout.addWidget(self.keyboard_sound_volume_label)

    self.keyboard_sound_volume_slider.valueChanged.connect(
        lambda v: self.keyboard_sound_volume_label.setText(f"{v}%")
    )
    layout.addLayout(volume_layout)

    # Кнопка сохранения
    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    save_btn = QPushButton("💾 Сохранить настройки звука")
    save_btn.setProperty("class", "save-btn")
    save_btn.clicked.connect(self.save_keyboard_sounds_settings)
    btn_layout.addWidget(save_btn)
    btn_layout.addStretch()
    layout.addLayout(btn_layout)

    layout.addStretch()
    return tab


def _browse_keyboard_sound(self):
    """Открывает диалог выбора звукового файла."""
    filepath, _ = QFileDialog.getOpenFileName(
        self, "Выберите звуковой файл", "",
        "Audio files (*.wav *.mp3 *.ogg);;All files (*)"
    )
    if filepath:
        self.keyboard_sound_path_edit.setText(filepath)
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
Миксин для вкладки DPI.
"""
import os
import logging
from PySide6.QtWidgets import (
    QLabel, QCheckBox, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout,
    QWidget, QSpinBox, QFileDialog
)
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)

class DPIMixin:
    """Миксин для настройки обхода DPI"""

    def setup_dpi_tab(self):
        """Создаёт и возвращает вкладку DPI"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("🛡️ Обход DPI (Deep Packet Inspection)"))

        info = QLabel(
            "Используйте внешние утилиты (GoodbyeDPI, zapret) для обхода блокировок.\n"
            "Укажите путь к исполняемому файлу и параметры запуска.\n\n"
            "⚠️ При включении/выключении режима браузер будет перезапущен."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        layout.addWidget(info)

        self.dpi_check = QCheckBox("Включить обход DPI")
        self.dpi_check.setChecked(self.api.get_dpi_enabled())
        layout.addWidget(self.dpi_check)

        h = QHBoxLayout()
        h.addWidget(QLabel("Путь к утилите:"))
        self.dpi_path_edit = QLineEdit()
        self.dpi_path_edit.setText(self.api.get_dpi_path())
        h.addWidget(self.dpi_path_edit)
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_dpi)
        h.addWidget(browse_btn)
        layout.addLayout(h)

        h = QHBoxLayout()
        h.addWidget(QLabel("Параметры запуска:"))
        self.dpi_args_edit = QLineEdit()
        self.dpi_args_edit.setText(self.api.get_dpi_args())
        h.addWidget(self.dpi_args_edit)
        h.addStretch()
        layout.addLayout(h)

        h = QHBoxLayout()
        h.addWidget(QLabel("Локальный порт:"))
        self.dpi_port_spin = QSpinBox()
        self.dpi_port_spin.setRange(1024, 65535)
        self.dpi_port_spin.setValue(self.api.get_dpi_port())
        h.addWidget(self.dpi_port_spin)
        h.addStretch()
        layout.addLayout(h)

        layout.addStretch()
        return tab

    def browse_dpi(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Выберите утилиту (например, goodbyedpi.exe)", "",
            "Executable files (*.exe);;All files (*)"
        )
        if filepath:
            self.dpi_path_edit.setText(filepath)
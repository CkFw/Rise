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
Миксин для вкладки I2P.
"""
import os
import socket
import logging
from PySide6.QtWidgets import (
    QLabel, QCheckBox, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout,
    QWidget, QSpinBox, QComboBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt

from core.utils import resource_path

logger = logging.getLogger(__name__)

class I2PMixin:
    """Миксин для настройки I2P"""

    def setup_i2p_tab(self):
        """Создаёт и возвращает вкладку I2P"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("🧅 I2P (Invisible Internet Project)"))

        info = QLabel(
            "Режим I2P перенаправляет весь трафик через локальный I2P-прокси.\n"
            "Позволяет открывать .i2p сайты.\n\n"
            "⚠️ Для работы необходимо установить и запустить I2P отдельно.\n"
            "По умолчанию HTTP-прокси слушает на порту 4444, SOCKS5 на 4447.\n\n"
            "При включении этого режима весь трафик пойдёт через указанный прокси.\n"
            "Для применения изменений необходимо перезапустить браузер."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        layout.addWidget(info)

        self.i2p_check = QCheckBox("Включить I2P-режим")
        self.i2p_check.setChecked(self.api.get_i2p_enabled())
        layout.addWidget(self.i2p_check)

        h = QHBoxLayout()
        h.addWidget(QLabel("Путь к i2pd.exe:"))
        self.i2pd_path_edit = QLineEdit()
        default_path = resource_path("I2P/i2pd.exe")
        self.i2pd_path_edit.setText(self.api.get_i2pd_path() or default_path)
        h.addWidget(self.i2pd_path_edit)
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_i2pd)
        h.addWidget(browse_btn)
        layout.addLayout(h)

        h = QHBoxLayout()
        h.addWidget(QLabel("Порт:"))
        self.i2p_port_spin = QSpinBox()
        self.i2p_port_spin.setRange(1024, 65535)
        self.i2p_port_spin.setValue(self.api.get_i2p_port())
        h.addWidget(self.i2p_port_spin)
        h.addStretch()
        layout.addLayout(h)

        h = QHBoxLayout()
        h.addWidget(QLabel("Тип прокси:"))
        self.i2p_type_combo = QComboBox()
        self.i2p_type_combo.addItems(["HTTP", "SOCKS5"])
        current_type = self.api.get_i2p_type()
        self.i2p_type_combo.setCurrentText("SOCKS5" if current_type == "socks5" else "HTTP")
        h.addWidget(self.i2p_type_combo)
        h.addStretch()
        layout.addLayout(h)

        check_btn = QPushButton("Проверить порт")
        check_btn.clicked.connect(self.check_i2p_port)
        layout.addWidget(check_btn)

        self.i2p_port_status = QLabel("")
        self.i2p_port_status.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.i2p_port_status)

        apply_btn = QPushButton("Применить и перезапустить")
        apply_btn.clicked.connect(self.apply_i2p_settings)
        layout.addWidget(apply_btn)

        layout.addStretch()
        return tab

    def browse_i2pd(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Выберите i2pd.exe", "", "Executable files (*.exe)"
        )
        if filepath:
            self.i2pd_path_edit.setText(filepath)

    def check_i2p_port(self):
        port = self.i2p_port_spin.value()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result == 0:
            self.i2p_port_status.setText(f"✅ Порт {port} открыт (прокси работает)")
            self.i2p_port_status.setStyleSheet("color: #00ff88;")
        else:
            self.i2p_port_status.setText(f"❌ Порт {port} недоступен (прокси не запущен?)")
            self.i2p_port_status.setStyleSheet("color: #ff6b6b;")

    def apply_i2p_settings(self):
        self.api.save_i2p_enabled(self.i2p_check.isChecked())
        self.api.save_i2p_port(self.i2p_port_spin.value())
        proxy_type = "socks5" if self.i2p_type_combo.currentText() == "SOCKS5" else "http"
        self.api.save_i2p_type(proxy_type)
        self.api.save_i2pd_path(self.i2pd_path_edit.text())
        QMessageBox.information(
            self,
            "Перезапуск",
            "Настройки I2P сохранены. Браузер будет перезапущен для применения изменений.\n\n"
            "Пожалуйста, закройте и откройте браузер заново."
        )
        logger.info("I2P settings saved")
        self.close()
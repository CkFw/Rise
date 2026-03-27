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
Миксин для вкладки VPN.
"""
import socket
import logging
from PySide6.QtWidgets import (
    QLabel, QCheckBox, QComboBox, QSpinBox, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QStackedWidget, QWidget, QMessageBox
)
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)

class VPNMixin:
    """Миксин для настройки VPN и прокси"""

    def setup_vpn_tab(self):
        """Создаёт и возвращает вкладку VPN"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("🔐 VPN (Прокси-соединение)"))

        info = QLabel(
            "Режим VPN перенаправляет весь трафик через указанный прокси-сервер.\n"
            "Позволяет сменить IP-адрес и обходить блокировки.\n\n"
            "⚠️ Для работы необходим работающий прокси-сервер.\n"
            "Если включён I2P, VPN не будет работать (приоритет у I2P).\n\n"
            "При изменении режима необходимо перезапустить браузер."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        layout.addWidget(info)

        self.vpn_check = QCheckBox("Включить VPN-режим")
        self.vpn_check.setChecked(self.api.get_vpn_enabled())
        layout.addWidget(self.vpn_check)

        h = QHBoxLayout()
        h.addWidget(QLabel("Протокол:"))
        self.vpn_protocol_combo = QComboBox()
        self.vpn_protocol_combo.addItems([
            "SOCKS5", "HTTP", "Shadowsocks", "Trojan", "VMess", "VLESS",
            "Tuic", "Hysteria", "Juicity"
        ])
        current_protocol = self.api.get_vpn_protocol()
        display_map = {
            "socks5": "SOCKS5", "http": "HTTP", "shadowsocks": "Shadowsocks",
            "trojan": "Trojan", "vmess": "VMess", "vless": "VLESS",
            "tuic": "Tuic", "hysteria": "Hysteria", "juicity": "Juicity"
        }
        self.vpn_protocol_combo.setCurrentText(display_map.get(current_protocol, "SOCKS5"))
        h.addWidget(self.vpn_protocol_combo)
        h.addStretch()
        layout.addLayout(h)

        self.vpn_stack = QStackedWidget()
        layout.addWidget(self.vpn_stack)

        self._create_socks5_page()
        self._create_http_page()
        self._create_shadowsocks_page()
        self._create_trojan_page()
        self._create_vmess_page()
        self._create_vless_page()
        self._create_tuic_page()
        self._create_hysteria_page()
        self._create_juicity_page()

        self.vpn_protocol_combo.currentIndexChanged.connect(self.vpn_stack.setCurrentIndex)

        check_btn = QPushButton("Проверить соединение")
        check_btn.clicked.connect(self.check_vpn_connection)
        layout.addWidget(check_btn)

        self.vpn_status = QLabel("")
        self.vpn_status.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.vpn_status)

        apply_btn = QPushButton("Применить и перезапустить")
        apply_btn.clicked.connect(self.apply_vpn_settings)
        layout.addWidget(apply_btn)

        layout.addStretch()
        return tab

    def _create_socks5_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("SOCKS5 прокси"))
        h = QHBoxLayout(); h.addWidget(QLabel("Хост:")); self.vpn_host_edit = QLineEdit(self.api.get_vpn_host()); h.addWidget(self.vpn_host_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Порт:")); self.vpn_port_spin = QSpinBox(); self.vpn_port_spin.setRange(1,65535); self.vpn_port_spin.setValue(self.api.get_vpn_port()); h.addWidget(self.vpn_port_spin); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Логин:")); self.vpn_username_edit = QLineEdit(self.api.get_vpn_username()); h.addWidget(self.vpn_username_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Пароль:")); self.vpn_password_edit = QLineEdit(self.api.get_vpn_password()); self.vpn_password_edit.setEchoMode(QLineEdit.EchoMode.Password); h.addWidget(self.vpn_password_edit); layout.addLayout(h)
        layout.addStretch()
        self.vpn_stack.addWidget(page)

    def _create_http_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("HTTP прокси"))
        h = QHBoxLayout(); h.addWidget(QLabel("Хост:")); self.vpn_host_edit_http = QLineEdit(self.api.get_vpn_host()); h.addWidget(self.vpn_host_edit_http); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Порт:")); self.vpn_port_spin_http = QSpinBox(); self.vpn_port_spin_http.setRange(1,65535); self.vpn_port_spin_http.setValue(self.api.get_vpn_port()); h.addWidget(self.vpn_port_spin_http); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Логин:")); self.vpn_username_edit_http = QLineEdit(self.api.get_vpn_username()); h.addWidget(self.vpn_username_edit_http); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Пароль:")); self.vpn_password_edit_http = QLineEdit(self.api.get_vpn_password()); self.vpn_password_edit_http.setEchoMode(QLineEdit.EchoMode.Password); h.addWidget(self.vpn_password_edit_http); layout.addLayout(h)
        layout.addStretch()
        self.vpn_stack.addWidget(page)

    def _create_shadowsocks_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Shadowsocks"))
        h = QHBoxLayout(); h.addWidget(QLabel("Сервер:")); self.ss_server_edit = QLineEdit(self.api.get_vpn_host()); h.addWidget(self.ss_server_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Порт:")); self.ss_port_spin = QSpinBox(); self.ss_port_spin.setRange(1,65535); self.ss_port_spin.setValue(self.api.get_vpn_port()); h.addWidget(self.ss_port_spin); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Метод:")); self.ss_method_combo = QComboBox(); self.ss_method_combo.addItems(["aes-256-gcm","aes-192-gcm","aes-128-gcm","chacha20-ietf-poly1305"]); self.ss_method_combo.setCurrentText(self.api.get_ss_method()); h.addWidget(self.ss_method_combo); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Пароль:")); self.ss_password_edit = QLineEdit(self.api.get_ss_password()); self.ss_password_edit.setEchoMode(QLineEdit.EchoMode.Password); h.addWidget(self.ss_password_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Локальный порт:")); self.ss_local_port_spin = QSpinBox(); self.ss_local_port_spin.setRange(1025,65535); self.ss_local_port_spin.setValue(self.api.get_ss_local_port()); h.addWidget(self.ss_local_port_spin); layout.addLayout(h)
        layout.addStretch()
        self.vpn_stack.addWidget(page)

    def _create_trojan_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Trojan"))
        h = QHBoxLayout(); h.addWidget(QLabel("Сервер:")); self.trojan_server_edit = QLineEdit(self.api.get_vpn_host()); h.addWidget(self.trojan_server_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Порт:")); self.trojan_port_spin = QSpinBox(); self.trojan_port_spin.setRange(1,65535); self.trojan_port_spin.setValue(self.api.get_vpn_port()); h.addWidget(self.trojan_port_spin); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Пароль:")); self.trojan_password_edit = QLineEdit(self.api.get_trojan_password()); self.trojan_password_edit.setEchoMode(QLineEdit.EchoMode.Password); h.addWidget(self.trojan_password_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("SNI:")); self.trojan_sni_edit = QLineEdit(self.api.get_trojan_sni()); h.addWidget(self.trojan_sni_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Лок. порт:")); self.trojan_local_port_spin = QSpinBox(); self.trojan_local_port_spin.setRange(1025,65535); self.trojan_local_port_spin.setValue(self.api.get_trojan_local_port()); h.addWidget(self.trojan_local_port_spin); layout.addLayout(h)
        layout.addStretch()
        self.vpn_stack.addWidget(page)

    def _create_vmess_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("VMess"))
        h = QHBoxLayout(); h.addWidget(QLabel("Сервер:")); self.vmess_server_edit = QLineEdit(self.api.get_vpn_host()); h.addWidget(self.vmess_server_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Порт:")); self.vmess_port_spin = QSpinBox(); self.vmess_port_spin.setRange(1,65535); self.vmess_port_spin.setValue(self.api.get_vpn_port()); h.addWidget(self.vmess_port_spin); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("UUID:")); self.vmess_uuid_edit = QLineEdit(self.api.get_vmess_uuid()); h.addWidget(self.vmess_uuid_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("AlterID:")); self.vmess_alterid_spin = QSpinBox(); self.vmess_alterid_spin.setRange(0,100); self.vmess_alterid_spin.setValue(self.api.get_vmess_alterid()); h.addWidget(self.vmess_alterid_spin); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Security:")); self.vmess_security_combo = QComboBox(); self.vmess_security_combo.addItems(["auto","aes-128-gcm","chacha20-poly1305","none"]); self.vmess_security_combo.setCurrentText(self.api.get_vmess_security()); h.addWidget(self.vmess_security_combo); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Лок. порт:")); self.vmess_local_port_spin = QSpinBox(); self.vmess_local_port_spin.setRange(1025,65535); self.vmess_local_port_spin.setValue(self.api.get_vmess_local_port()); h.addWidget(self.vmess_local_port_spin); layout.addLayout(h)
        layout.addStretch()
        self.vpn_stack.addWidget(page)

    def _create_vless_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("VLESS"))
        h = QHBoxLayout(); h.addWidget(QLabel("Сервер:")); self.vless_server_edit = QLineEdit(self.api.get_vpn_host()); h.addWidget(self.vless_server_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Порт:")); self.vless_port_spin = QSpinBox(); self.vless_port_spin.setRange(1,65535); self.vless_port_spin.setValue(self.api.get_vpn_port()); h.addWidget(self.vless_port_spin); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("UUID:")); self.vless_uuid_edit = QLineEdit(self.api.get_vless_uuid()); h.addWidget(self.vless_uuid_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Лок. порт:")); self.vless_local_port_spin = QSpinBox(); self.vless_local_port_spin.setRange(1025,65535); self.vless_local_port_spin.setValue(self.api.get_vless_local_port()); h.addWidget(self.vless_local_port_spin); layout.addLayout(h)
        layout.addStretch()
        self.vpn_stack.addWidget(page)

    def _create_tuic_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Tuic"))
        h = QHBoxLayout(); h.addWidget(QLabel("Сервер:")); self.tuic_server_edit = QLineEdit(self.api.get_vpn_host()); h.addWidget(self.tuic_server_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Порт:")); self.tuic_port_spin = QSpinBox(); self.tuic_port_spin.setRange(1,65535); self.tuic_port_spin.setValue(self.api.get_vpn_port()); h.addWidget(self.tuic_port_spin); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Token:")); self.tuic_token_edit = QLineEdit(self.api.get_tuic_token()); h.addWidget(self.tuic_token_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Лок. порт:")); self.tuic_local_port_spin = QSpinBox(); self.tuic_local_port_spin.setRange(1025,65535); self.tuic_local_port_spin.setValue(self.api.get_tuic_local_port()); h.addWidget(self.tuic_local_port_spin); layout.addLayout(h)
        layout.addStretch()
        self.vpn_stack.addWidget(page)

    def _create_hysteria_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Hysteria"))
        h = QHBoxLayout(); h.addWidget(QLabel("Сервер:")); self.hysteria_server_edit = QLineEdit(self.api.get_vpn_host()); h.addWidget(self.hysteria_server_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Порт:")); self.hysteria_port_spin = QSpinBox(); self.hysteria_port_spin.setRange(1,65535); self.hysteria_port_spin.setValue(self.api.get_vpn_port()); h.addWidget(self.hysteria_port_spin); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Auth:")); self.hysteria_auth_edit = QLineEdit(self.api.get_hysteria_auth()); h.addWidget(self.hysteria_auth_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Лок. порт:")); self.hysteria_local_port_spin = QSpinBox(); self.hysteria_local_port_spin.setRange(1025,65535); self.hysteria_local_port_spin.setValue(self.api.get_hysteria_local_port()); h.addWidget(self.hysteria_local_port_spin); layout.addLayout(h)
        layout.addStretch()
        self.vpn_stack.addWidget(page)

    def _create_juicity_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Juicity"))
        h = QHBoxLayout(); h.addWidget(QLabel("Сервер:")); self.juicity_server_edit = QLineEdit(self.api.get_vpn_host()); h.addWidget(self.juicity_server_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Порт:")); self.juicity_port_spin = QSpinBox(); self.juicity_port_spin.setRange(1,65535); self.juicity_port_spin.setValue(self.api.get_vpn_port()); h.addWidget(self.juicity_port_spin); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("UUID:")); self.juicity_uuid_edit = QLineEdit(self.api.get_juicity_uuid()); h.addWidget(self.juicity_uuid_edit); layout.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Лок. порт:")); self.juicity_local_port_spin = QSpinBox(); self.juicity_local_port_spin.setRange(1025,65535); self.juicity_local_port_spin.setValue(self.api.get_juicity_local_port()); h.addWidget(self.juicity_local_port_spin); layout.addLayout(h)
        layout.addStretch()
        self.vpn_stack.addWidget(page)

    def check_vpn_connection(self):
        idx = self.vpn_protocol_combo.currentIndex()
        if idx == 0:
            host = self.vpn_host_edit.text().strip()
            port = self.vpn_port_spin.value()
        elif idx == 1:
            host = self.vpn_host_edit_http.text().strip()
            port = self.vpn_port_spin_http.value()
        elif idx == 2:
            host = self.ss_server_edit.text().strip()
            port = self.ss_port_spin.value()
        elif idx == 3:
            host = self.trojan_server_edit.text().strip()
            port = self.trojan_port_spin.value()
        elif idx == 4:
            host = self.vmess_server_edit.text().strip()
            port = self.vmess_port_spin.value()
        elif idx == 5:
            host = self.vless_server_edit.text().strip()
            port = self.vless_port_spin.value()
        elif idx == 6:
            host = self.tuic_server_edit.text().strip()
            port = self.tuic_port_spin.value()
        elif idx == 7:
            host = self.hysteria_server_edit.text().strip()
            port = self.hysteria_port_spin.value()
        elif idx == 8:
            host = self.juicity_server_edit.text().strip()
            port = self.juicity_port_spin.value()
        else:
            return

        if not host:
            self.vpn_status.setText("❌ Введите адрес сервера")
            self.vpn_status.setStyleSheet("color: #ff6b6b;")
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        try:
            result = sock.connect_ex((host, port))
            if result == 0:
                self.vpn_status.setText(f"✅ Сервер {host}:{port} доступен")
                self.vpn_status.setStyleSheet("color: #00ff88;")
            else:
                self.vpn_status.setText(f"❌ Сервер {host}:{port} недоступен (код {result})")
                self.vpn_status.setStyleSheet("color: #ff6b6b;")
        except Exception as e:
            self.vpn_status.setText(f"❌ Ошибка: {str(e)}")
            self.vpn_status.setStyleSheet("color: #ff6b6b;")
        finally:
            sock.close()

    def apply_vpn_settings(self):
        self.api.save_vpn_enabled(self.vpn_check.isChecked())
        idx = self.vpn_protocol_combo.currentIndex()
        protocol_map = ["socks5", "http", "shadowsocks", "trojan", "vmess", "vless", "tuic", "hysteria", "juicity"]
        self.api.save_vpn_protocol(protocol_map[idx])

        if idx == 0:
            self.api.save_vpn_host(self.vpn_host_edit.text())
            self.api.save_vpn_port(self.vpn_port_spin.value())
            self.api.save_vpn_username(self.vpn_username_edit.text())
            self.api.save_vpn_password(self.vpn_password_edit.text())
        elif idx == 1:
            self.api.save_vpn_host(self.vpn_host_edit_http.text())
            self.api.save_vpn_port(self.vpn_port_spin_http.value())
            self.api.save_vpn_username(self.vpn_username_edit_http.text())
            self.api.save_vpn_password(self.vpn_password_edit_http.text())
        elif idx == 2:
            self.api.save_vpn_host(self.ss_server_edit.text())
            self.api.save_vpn_port(self.ss_port_spin.value())
            self.api.save_ss_method(self.ss_method_combo.currentText())
            self.api.save_ss_password(self.ss_password_edit.text())
            self.api.save_ss_local_port(self.ss_local_port_spin.value())
        elif idx == 3:
            self.api.save_vpn_host(self.trojan_server_edit.text())
            self.api.save_vpn_port(self.trojan_port_spin.value())
            self.api.save_trojan_password(self.trojan_password_edit.text())
            self.api.save_trojan_sni(self.trojan_sni_edit.text())
            self.api.save_trojan_local_port(self.trojan_local_port_spin.value())
        elif idx == 4:
            self.api.save_vpn_host(self.vmess_server_edit.text())
            self.api.save_vpn_port(self.vmess_port_spin.value())
            self.api.save_vmess_uuid(self.vmess_uuid_edit.text())
            self.api.save_vmess_alterid(self.vmess_alterid_spin.value())
            self.api.save_vmess_security(self.vmess_security_combo.currentText())
            self.api.save_vmess_local_port(self.vmess_local_port_spin.value())
        elif idx == 5:
            self.api.save_vpn_host(self.vless_server_edit.text())
            self.api.save_vpn_port(self.vless_port_spin.value())
            self.api.save_vless_uuid(self.vless_uuid_edit.text())
            self.api.save_vless_local_port(self.vless_local_port_spin.value())
        elif idx == 6:
            self.api.save_vpn_host(self.tuic_server_edit.text())
            self.api.save_vpn_port(self.tuic_port_spin.value())
            self.api.save_tuic_token(self.tuic_token_edit.text())
            self.api.save_tuic_local_port(self.tuic_local_port_spin.value())
        elif idx == 7:
            self.api.save_vpn_host(self.hysteria_server_edit.text())
            self.api.save_vpn_port(self.hysteria_port_spin.value())
            self.api.save_hysteria_auth(self.hysteria_auth_edit.text())
            self.api.save_hysteria_local_port(self.hysteria_local_port_spin.value())
        elif idx == 8:
            self.api.save_vpn_host(self.juicity_server_edit.text())
            self.api.save_vpn_port(self.juicity_port_spin.value())
            self.api.save_juicity_uuid(self.juicity_uuid_edit.text())
            self.api.save_juicity_local_port(self.juicity_local_port_spin.value())

        QMessageBox.information(
            self,
            "Перезапуск",
            "Настройки VPN сохранены. Браузер будет перезапущен для применения изменений.\n\n"
            "Пожалуйста, закройте и откройте браузер заново."
        )
        logger.info("VPN settings saved")
        self.close()
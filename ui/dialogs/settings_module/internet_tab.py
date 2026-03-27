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

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QCheckBox, QComboBox, QSpinBox, QPushButton
from PySide6.QtCore import Qt

def setup_internet_tab(self):
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setSpacing(15)

    layout.addWidget(self._create_info_label(
        "🌐 Расширенные сетевые настройки: DNS-over-HTTPS, HTTP/3 (QUIC), WebRTC, IPv6 и TCP-буфер."
    ))

    # DNS-over-HTTPS
    dns_group = QGroupBox("DNS-over-HTTPS (DoH)")
    dns_layout = QVBoxLayout()
    dns_info = QLabel("DoH шифрует DNS-запросы, повышая приватность и безопасность.")
    dns_info.setWordWrap(True)
    dns_info.setStyleSheet("color: #aaa; font-size: 12px;")
    dns_layout.addWidget(dns_info)

    self.doh_check = QCheckBox("Включить DoH")
    self.doh_check.setChecked(self.api.get_doh_enabled())
    dns_layout.addWidget(self.doh_check)

    provider_layout = QHBoxLayout()
    provider_layout.addWidget(QLabel("Провайдер:"))
    self.doh_combo = QComboBox()
    self.doh_combo.addItems(["google", "cloudflare", "quad9", "system"])
    self.doh_combo.setCurrentText(self.api.get_doh_provider())
    provider_layout.addWidget(self.doh_combo)
    provider_layout.addStretch()
    dns_layout.addLayout(provider_layout)

    dns_group.setLayout(dns_layout)
    layout.addWidget(dns_group)

    # HTTP/3 (QUIC)
    quic_group = QGroupBox("HTTP/3 (QUIC)")
    quic_layout = QVBoxLayout()
    quic_info = QLabel("QUIC уменьшает задержки и улучшает производительность, особенно на мобильных сетях.")
    quic_info.setWordWrap(True)
    quic_info.setStyleSheet("color: #aaa; font-size: 12px;")
    quic_layout.addWidget(quic_info)

    self.quic_check = QCheckBox("Включить QUIC (ускорение загрузки на поддерживаемых сайтах)")
    self.quic_check.setChecked(self.api.get_quic_enabled())
    quic_layout.addWidget(self.quic_check)

    quic_group.setLayout(quic_layout)
    layout.addWidget(quic_group)

    # WebRTC
    webrtc_group = QGroupBox("WebRTC")
    webrtc_layout = QVBoxLayout()
    webrtc_info = QLabel(
        "Если отключить, некоторые функции (видеозвонки, торренты в браузере) могут не работать, "
        "но повысится приватность (предотвратит утечку IP)."
    )
    webrtc_info.setWordWrap(True)
    webrtc_info.setStyleSheet("color: #aaa; font-size: 12px;")
    webrtc_layout.addWidget(webrtc_info)

    self.webrtc_check = QCheckBox("Включить WebRTC (для видеочатов и P2P)")
    self.webrtc_check.setChecked(self.api.get_webrtc_enabled())
    webrtc_layout.addWidget(self.webrtc_check)

    webrtc_group.setLayout(webrtc_layout)
    layout.addWidget(webrtc_group)

    # IPv6
    ipv6_group = QGroupBox("IPv6")
    ipv6_layout = QVBoxLayout()
    ipv6_info = QLabel("IPv6 необходим для современных сетей. Отключайте только при проблемах с соединением.")
    ipv6_info.setWordWrap(True)
    ipv6_info.setStyleSheet("color: #aaa; font-size: 12px;")
    ipv6_layout.addWidget(ipv6_info)

    self.ipv6_check = QCheckBox("Включить IPv6")
    self.ipv6_check.setChecked(self.api.get_ipv6_enabled())
    ipv6_layout.addWidget(self.ipv6_check)

    ipv6_group.setLayout(ipv6_layout)
    layout.addWidget(ipv6_group)

    # Настройки TCP
    tcp_group = QGroupBox("TCP буфер (экспертно)")
    tcp_layout = QVBoxLayout()
    tcp_info = QLabel(
        "Увеличение буфера может повысить скорость на высокоскоростных каналах, "
        "но потребляет больше памяти. 0 = системный размер."
    )
    tcp_info.setWordWrap(True)
    tcp_info.setStyleSheet("color: #aaa; font-size: 12px;")
    tcp_layout.addWidget(tcp_info)

    size_layout = QHBoxLayout()
    size_layout.addWidget(QLabel("Размер буфера приёма (КБ):"))
    self.tcp_spin = QSpinBox()
    self.tcp_spin.setRange(0, 65535)
    self.tcp_spin.setValue(self.api.get_tcp_buffer_size())
    size_layout.addWidget(self.tcp_spin)
    size_layout.addStretch()
    tcp_layout.addLayout(size_layout)

    tcp_group.setLayout(tcp_layout)
    layout.addWidget(tcp_group)

    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    save_btn = QPushButton("💾 Сохранить настройки сети")
    save_btn.setProperty("class", "save-btn")
    save_btn.clicked.connect(self.save_internet_settings)
    btn_layout.addWidget(save_btn)
    btn_layout.addStretch()
    layout.addLayout(btn_layout)

    layout.addStretch()
    return tab
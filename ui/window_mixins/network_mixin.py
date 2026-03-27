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
Настройка I2P, VPN, DPI, прокси.
"""
import os
import logging
from PySide6.QtCore import QTimer
from PySide6.QtNetwork import QNetworkProxy
from PySide6.QtWidgets import QMessageBox

from core.i2p_manager import I2PManager
from core.dpi_manager import DPIManager
from core.shadowsocks_manager import ShadowsocksManager
from core.trojan_manager import TrojanManager
from core.utils import resource_path
from core.config import DATA_DIR

logger = logging.getLogger(__name__)

class NetworkMixin:
    """Управление сетевыми сервисами: I2P, VPN, DPI."""

    def _setup_network_mixins(self):
        """Инициализирует менеджеры I2P, DPI и прокси (вызывается в __init__)."""
        self._setup_i2p_manager()
        self._setup_proxy()
        self.dpi_manager = DPIManager(
            exe_path=self.api.get_dpi_path(),
            args=self.api.get_dpi_args(),
            local_port=self.api.get_dpi_port()
        )
        self.dpi_manager.started.connect(self._on_dpi_started)
        self.dpi_manager.error.connect(self._on_dpi_error)

    def _start_services(self):
        """Запускает I2P и DPI, если они включены."""
        if self.i2p_manager.enabled:
            self._start_i2p()
        if self.api.get_dpi_enabled():
            self._start_dpi()

    # ---------- I2P ----------
    def _setup_i2p_manager(self):
        i2p_enabled = self.api.get_i2p_enabled()
        self.i2p_port = self.api.get_i2p_port()
        self.i2p_type = self.api.get_i2p_type()
        i2pd_path = self.api.get_i2pd_path() or resource_path("I2P/i2pd.exe")
        i2p_data_dir = os.path.join(DATA_DIR, 'i2pd_data')
        os.makedirs(i2p_data_dir, exist_ok=True)

        self.i2p_manager = I2PManager(
            api=self.api,
            i2pd_path=i2pd_path,
            data_dir=i2p_data_dir,
            enabled=i2p_enabled,
            http_port=4444,
            socks_port=4447
        )
        self.i2p_manager.started.connect(self._on_i2p_started)
        self.i2p_manager.error.connect(self._on_i2p_error)
        self.i2p_manager.progress.connect(self._on_i2p_progress)

    def _start_i2p(self):
        self.i2p_progress.show()
        self.i2p_manager.start()

    def _on_i2p_progress(self, percent, message):
        self.i2p_progress.set_status(percent, message)

    def _on_i2p_started(self):
        self.api.set_default_i2p_search_engine()
        self.i2p_progress.finish_success()

    def _on_i2p_error(self, msg):
        self.i2p_progress.hide()
        QMessageBox.critical(self, "Ошибка I2P", f"{msg}\n\nI2P отключён.")
        self.api.save_i2p_enabled(False)
        self.i2p_manager.enabled = False
        if self.browsers:
            self._load_home_to_browser(self.browsers[self.current_browser_index])

    def _cancel_i2p_startup(self):
        self.i2p_manager.stop()
        self.i2p_progress.hide()
        self.api.save_i2p_enabled(False)
        self.i2p_manager.enabled = False
        if self.browsers:
            self._load_home_to_browser(self.browsers[self.current_browser_index])

    # ---------- Прокси и VPN ----------
    def _setup_proxy(self):
        if self.i2p_manager.enabled:
            return
        vpn_enabled = self.api.get_vpn_enabled()
        if vpn_enabled:
            protocol = self.api.get_vpn_protocol()
            if protocol == "socks5":
                proxy = QNetworkProxy(QNetworkProxy.ProxyType.Socks5Proxy,
                                      self.api.get_vpn_host(), self.api.get_vpn_port(),
                                      self.api.get_vpn_username(), self.api.get_vpn_password())
                QNetworkProxy.setApplicationProxy(proxy)
            elif protocol == "http":
                proxy = QNetworkProxy(QNetworkProxy.ProxyType.HttpProxy,
                                      self.api.get_vpn_host(), self.api.get_vpn_port(),
                                      self.api.get_vpn_username(), self.api.get_vpn_password())
                QNetworkProxy.setApplicationProxy(proxy)
            elif protocol == "shadowsocks":
                self._start_shadowsocks()
            elif protocol == "trojan":
                self._start_trojan()
        else:
            QNetworkProxy.setApplicationProxy(QNetworkProxy())

    def _start_shadowsocks(self):
        self.ss_manager = ShadowsocksManager(
            server=self.api.get_vpn_host(),
            port=self.api.get_vpn_port(),
            password=self.api.get_ss_password(),
            method=self.api.get_ss_method(),
            local_port=self.api.get_ss_local_port()
        )
        self.ss_manager.started.connect(self._on_ss_started)
        self.ss_manager.error.connect(self._on_ss_error)
        self.ss_manager.start()

    def _on_ss_started(self):
        self.ss_manager.enable_proxy()
        self.logger.info("Shadowsocks started")

    def _on_ss_error(self, msg):
        QMessageBox.critical(self, "Ошибка Shadowsocks", msg)
        self.api.save_vpn_enabled(False)

    def _start_trojan(self):
        self.trojan_manager = TrojanManager(
            server=self.api.get_vpn_host(),
            port=self.api.get_vpn_port(),
            password=self.api.get_trojan_password(),
            sni=self.api.get_trojan_sni(),
            local_port=self.api.get_trojan_local_port()
        )
        self.trojan_manager.started.connect(self._on_trojan_started)
        self.trojan_manager.error.connect(self._on_trojan_error)
        self.trojan_manager.start()

    def _on_trojan_started(self):
        self.trojan_manager.enable_proxy()
        self.logger.info("Trojan started")

    def _on_trojan_error(self, msg):
        QMessageBox.critical(self, "Ошибка Trojan", msg)
        self.api.save_vpn_enabled(False)

    # ---------- DPI ----------
    def _start_dpi(self):
        self.dpi_manager.exe_path = self.api.get_dpi_path()
        self.dpi_manager.args = self.api.get_dpi_args()
        self.dpi_manager.local_port = self.api.get_dpi_port()
        self.dpi_manager.start()

    def _stop_dpi(self):
        self.dpi_manager.stop()

    def _on_dpi_started(self):
        self.logger.info("DPI started")
        proxy = QNetworkProxy(QNetworkProxy.ProxyType.Socks5Proxy, "127.0.0.1", self.dpi_manager.local_port)
        QNetworkProxy.setApplicationProxy(proxy)

    def _on_dpi_error(self, msg):
        QMessageBox.critical(self, "Ошибка DPI", msg)
        self.api.save_dpi_enabled(False)
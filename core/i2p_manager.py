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
Менеджер для управления I2P-режимом (PySide6) – исправленная версия для работы в EXE
"""
import os
import sys
import ctypes
import logging
from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QNetworkProxy
from PySide6.QtCore import QProcess
from core.i2p_launcher import I2PLauncher
from core.utils import resource_path

logger = logging.getLogger(__name__)

class I2PManager(QObject):
    started = Signal()
    error = Signal(str)
    progress = Signal(int, str)

    def __init__(self, api, i2pd_path, data_dir, enabled=False, http_port=4444, socks_port=4447):
        super().__init__()
        self.api = api
        self.i2pd_path = i2pd_path
        self.data_dir = data_dir
        self.http_port = http_port
        self.socks_port = socks_port
        self.enabled = enabled
        self.launcher = None
        self.proxy_type = self.api.get_i2p_type()
        self.proxy_port = self.api.get_i2p_port()

    def start(self):
        if not self.enabled:
            self.error.emit("I2P режим отключён в настройках.")
            return
        if self.launcher and self.launcher.process and self.launcher.process.state() == QProcess.ProcessState.Running:
            return

        self._sanitize_environment_for_external_process()

        exe_path = resource_path(self.i2pd_path) if not os.path.isabs(self.i2pd_path) else self.i2pd_path
        if not os.path.exists(exe_path):
            self.error.emit(f"i2pd не найден по пути: {exe_path}")
            return

        self.launcher = I2PLauncher(
            i2pd_exe_path=exe_path,
            data_dir=self.data_dir,
            http_port=self.http_port,
            socks_port=self.socks_port
        )
        self.launcher.started.connect(self._on_launcher_started)
        self.launcher.error.connect(self._on_launcher_error)
        self.launcher.progress.connect(self._on_launcher_progress)
        self.launcher.start()

    def _sanitize_environment_for_external_process(self):
        if getattr(sys, 'frozen', False) and sys.platform == 'win32':
            try:
                ctypes.windll.kernel32.SetDllDirectoryW(None)
                logger.info("I2P Manager: DllDirectory cleared for external process")
            except Exception as e:
                logger.error(f"I2P Manager: Failed to clear DllDirectory: {e}")

    def stop(self):
        if self.launcher:
            self.launcher.stop()
        self.enabled = False

    def _on_launcher_started(self):
        self._enable_proxy()
        self.started.emit()

    def _on_launcher_error(self, msg):
        self.error.emit(msg)

    def _on_launcher_progress(self, percent, message):
        prog = self._parse_progress(message)
        self.progress.emit(prog, message)

    def _parse_progress(self, message):
        msg_lower = message.lower()
        if "starting" in msg_lower:
            return 5
        elif "creating new keys" in msg_lower:
            return 20
        elif "loading" in msg_lower:
            return 35
        elif "reserved" in msg_lower:
            return 50
        elif "establishing" in msg_lower:
            return 65
        elif "testing" in msg_lower:
            return 75
        elif "accepting" in msg_lower:
            return 85
        elif "ready" in msg_lower or "success" in msg_lower:
            return 95
        else:
            return 0

    def _enable_proxy(self):
        if self.proxy_type == "socks5":
            proxy = QNetworkProxy(QNetworkProxy.ProxyType.Socks5Proxy, "127.0.0.1", self.proxy_port)
        else:
            proxy = QNetworkProxy(QNetworkProxy.ProxyType.HttpProxy, "127.0.0.1", self.proxy_port)
        QNetworkProxy.setApplicationProxy(proxy)
        logger.info(f"I2P proxy enabled: {self.proxy_type} on port {self.proxy_port}")
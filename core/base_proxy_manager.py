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
Базовый класс для всех прокси-менеджеров (PySide6)
Исправлено: логирование, использование QTimer и QProcess.
"""
import socket
import logging
from PySide6.QtCore import QObject, Signal, QTimer, QElapsedTimer, QProcess

logger = logging.getLogger(__name__)

class BaseProxyManager(QObject):
    started = Signal()
    error = Signal(str)

    def __init__(self, local_port):
        super().__init__()
        self.local_port = local_port
        self.check_timer = None
        self.elapsed_timer = None
        self.max_wait = 30
        self.process = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def start(self):
        raise NotImplementedError

    def stop(self):
        if self.check_timer:
            self.check_timer.stop()
            self.check_timer = None
        if self.process:
            self.logger.info("Stopping process...")
            if self.process.state() == QProcess.ProcessState.Running:
                self.process.terminate()
                if not self.process.waitForFinished(5000):
                    self.process.kill()
            self.process = None

    def enable_proxy(self):
        from PySide6.QtNetwork import QNetworkProxy
        proxy = QNetworkProxy(QNetworkProxy.ProxyType.Socks5Proxy, "127.0.0.1", self.local_port)
        QNetworkProxy.setApplicationProxy(proxy)
        self.logger.info(f"Proxy enabled: SOCKS5 on port {self.local_port}")

    def disable_proxy(self):
        from PySide6.QtNetwork import QNetworkProxy
        QNetworkProxy.setApplicationProxy(QNetworkProxy())
        self.logger.info("Proxy disabled")

    def _start_check_timer(self):
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_port)
        self.check_timer.start(500)

    def _check_port(self):
        if self._is_port_open(self.local_port):
            self.check_timer.stop()
            self.check_timer = None
            self.started.emit()
            self.logger.info(f"Port {self.local_port} is open, proxy ready")
            return
        if self.elapsed_timer.elapsed() > self.max_wait * 1000:
            self.check_timer.stop()
            self.check_timer = None
            if self.process:
                self.process.kill()
            self.error.emit(f"Timeout starting proxy on port {self.local_port}")

    def _is_port_open(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
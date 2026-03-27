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
Менеджер для Trojan (PySide6)
Исправлено: использование QProcess, логирование, BaseProxyManager.
"""
import os
import json
import tempfile
import logging
from PySide6.QtCore import QElapsedTimer, QProcess
from .base_proxy_manager import BaseProxyManager

logger = logging.getLogger(__name__)

class TrojanManager(BaseProxyManager):
    def __init__(self, server, port, password, sni="", local_port=1082):
        super().__init__(local_port)
        self.server = server
        self.remote_port = port
        self.password = password
        self.sni = sni

    def start(self):
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            return

        if self._is_port_open(self.local_port):
            self.error.emit(f"Port {self.local_port} is already in use.")
            return

        config = {
            "run_type": "client",
            "local_addr": "127.0.0.1",
            "local_port": self.local_port,
            "remote_addr": self.server,
            "remote_port": self.remote_port,
            "password": [self.password],
            "ssl": {
                "sni": self.sni if self.sni else self.server
            }
        }
        fd, config_path = tempfile.mkstemp(suffix='.json', prefix='trojan_')
        with os.fdopen(fd, 'w') as f:
            json.dump(config, f)

        self.process = QProcess()
        self.process.setProgram("trojan")
        self.process.setArguments(["-c", config_path])
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.finished.connect(self._on_finished)

        self.logger.info(f"Starting Trojan: trojan -c {config_path}")
        self.process.start()

        if not self.process.waitForStarted(3000):
            self.error.emit("Failed to start trojan. Make sure trojan is installed.")
            return

        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        self._start_check_timer()

    def _read_output(self):
        data = self.process.readAllStandardOutput().data().decode(errors='ignore')
        if data:
            self.logger.debug(f"Trojan output: {data.strip()}")

    def _on_finished(self, exit_code, exit_status):
        self.logger.info(f"Trojan process finished with code {exit_code}")
        self.process = None
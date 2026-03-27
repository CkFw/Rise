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
Менеджер для управления внешними DPI-обходчиками (GoodbyeDPI, zapret и т.п.)
Исправлено: логирование, обработка ошибок, использование QProcess вместо subprocess.
"""
import os
import logging
from PySide6.QtCore import QObject, Signal, QTimer, QProcess

logger = logging.getLogger(__name__)

class DPIManager(QObject):
    """Управляет запуском/остановкой внешнего процесса для обхода DPI"""
    started = Signal()
    error = Signal(str)
    output = Signal(str)

    def __init__(self, exe_path="", args="", local_port=1080):
        super().__init__()
        self.exe_path = exe_path
        self.args = args
        self.local_port = local_port
        self.process = None
        self.check_timer = None
        self.port_ready = False
        self.logger = logging.getLogger(f"{__name__}.DPIManager")

    def start(self):
        """Запускает внешний процесс"""
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.error.emit("Процесс уже запущен")
            return

        if not os.path.exists(self.exe_path):
            self.error.emit(f"Файл не найден: {self.exe_path}")
            return

        # Формируем команду
        cmd = f'"{self.exe_path}" {self.args}'
        self.logger.info(f"Запуск DPI: {cmd}")

        try:
            self.process = QProcess()
            self.process.setProgram(self.exe_path)
            self.process.setArguments(self.args.split() if self.args else [])
            self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
            self.process.readyReadStandardOutput.connect(self._read_output)
            self.process.finished.connect(self._on_finished)

            self.process.start()
            if not self.process.waitForStarted(3000):
                self.error.emit("Не удалось запустить процесс")
                return

            # Запускаем таймер проверки порта
            self.port_ready = False
            self._start_check_timer()
        except Exception as e:
            self.logger.error(f"Ошибка запуска DPI: {e}")
            self.error.emit(f"Не удалось запустить процесс: {e}")

    def stop(self):
        """Останавливает внешний процесс"""
        if self.check_timer:
            self.check_timer.stop()
            self.check_timer = None
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.logger.info("Останавливаем DPI процесс...")
            self.process.terminate()
            if not self.process.waitForFinished(5000):
                self.process.kill()
            self.process = None

    def _read_output(self):
        data = self.process.readAllStandardOutput().data().decode(errors='ignore')
        if data:
            self.output.emit(data)
            self.logger.debug(f"DPI output: {data.strip()}")

    def _on_finished(self, exit_code, exit_status):
        if self.process:
            self.logger.info(f"DPI процесс завершился с кодом {exit_code}")
            if not self.port_ready:
                self.error.emit(f"Процесс завершился до открытия порта (код {exit_code})")
            self.process = None

    def _start_check_timer(self):
        """Запускает таймер для проверки доступности порта"""
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_port)
        self.check_timer.start(500)

    def _check_port(self):
        """Проверяет, открыт ли локальный порт (прокси готов)"""
        if self._is_port_open(self.local_port):
            self.port_ready = True
            self.check_timer.stop()
            self.check_timer = None
            self.logger.info(f"DPI порт {self.local_port} открыт, процесс готов")
            self.started.emit()
            return

        if self.process and self.process.state() != QProcess.ProcessState.Running:
            self.check_timer.stop()
            self.check_timer = None
            self.error.emit("Процесс завершился раньше времени")

    def _is_port_open(self, port):
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
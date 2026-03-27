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
Менеджер для запуска встроенного роутера I2P (i2pd) (PySide6)
"""
import os
import socket
from PySide6.QtCore import QObject, Signal, QProcess, QTimer, QElapsedTimer


class I2PLauncher(QObject):
    """
    Запускает i2pd.exe как внешний процесс и управляет им.
    Сигналы:
        started() - когда прокси готов к работе
        error(str) - при ошибке запуска
        progress(int, str) - прогресс bootstrap (процент, сообщение)
        output(str) - для логирования вывода i2pd (опционально)
    """
    started = Signal()
    error = Signal(str)
    progress = Signal(int, str)
    output = Signal(str)

    def __init__(self, i2pd_exe_path, data_dir=None, http_port=4444, socks_port=4447):
        super().__init__()
        self.i2pd_exe_path = i2pd_exe_path
        self.data_dir = data_dir
        self.http_port = http_port
        self.socks_port = socks_port
        self.process = None
        self.check_timer = None
        self.elapsed_timer = None
        self.max_wait = 60
        self.output_buffer = []
        self.port_ready = False

    def start(self):
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            return

        if not os.path.exists(self.i2pd_exe_path):
            self.error.emit(f"i2pd не найден по пути: {self.i2pd_exe_path}")
            return

        work_dir = os.path.dirname(self.i2pd_exe_path)

        args = [
            '--httpproxy.port', str(self.http_port),
            '--socksproxy.port', str(self.socks_port),
        ]
        if self.data_dir:
            args.extend(['--datadir', self.data_dir])

        self.process = QProcess()
        self.process.setWorkingDirectory(work_dir)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.finished.connect(self._on_finished)

        print(f"Запуск I2P: {self.i2pd_exe_path} {' '.join(args)} (cwd={work_dir})")
        self.process.start(self.i2pd_exe_path, args)

        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        self.output_buffer = []
        self.port_ready = False
        self._start_check_timer()

    def _start_check_timer(self):
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_ports)
        self.check_timer.start(500)

    def _check_ports(self):
        if self.port_ready:
            return

        http_ready = self._is_port_open(self.http_port)
        socks_ready = self._is_port_open(self.socks_port)

        if http_ready or socks_ready:
            self.port_ready = True
            self.check_timer.stop()
            self.check_timer = None
            self.started.emit()
            return

        elapsed = self.elapsed_timer.elapsed() / 1000
        if elapsed > self.max_wait:
            self.check_timer.stop()
            self.check_timer = None
            if self.process and self.process.state() == QProcess.ProcessState.Running:
                self.process.kill()
            error_summary = '\n'.join(self.output_buffer[-20:])
            self.error.emit(
                f"Таймаут запуска I2P за {self.max_wait} сек.\n"
                f"Последний вывод i2pd:\n{error_summary}"
            )

    def _read_output(self):
        data = self.process.readAllStandardOutput().data().decode(errors='ignore')
        if not data:
            return
        self.output_buffer.extend(data.splitlines())
        self.output.emit(data)
        lines = data.strip().split('\n')
        for line in lines:
            if line.strip():
                self.progress.emit(0, line.strip())

    def _on_finished(self, exit_code, exit_status):
        if self.process and self.process.state() == QProcess.ProcessState.NotRunning:
            if self.port_ready:
                return
            error_summary = '\n'.join(self.output_buffer[-20:])
            self.error.emit(
                f"Процесс i2pd неожиданно завершился с кодом {exit_code}.\n"
                f"Последний вывод:\n{error_summary}"
            )

    def stop(self):
        if self.check_timer:
            self.check_timer.stop()
            self.check_timer = None
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            print("Останавливаем I2P...")
            self.process.terminate()
            if not self.process.waitForFinished(5000):
                self.process.kill()

    def _is_port_open(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
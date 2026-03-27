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
Панель прогресса запуска I2P, отображаемая внизу окна - PySide6
Исправлено: добавлено логирование.
"""
import logging
from PySide6.QtWidgets import QWidget, QHBoxLayout, QProgressBar, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QTimer

logger = logging.getLogger(__name__)

class I2PProgressBar(QWidget):
    """Виджет для отображения прогресса запуска I2P"""
    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        self.setVisible(False)
        self._setup_ui()
        self._progress_value = 0
        self._progress_timer = QTimer()
        self._progress_timer.timeout.connect(self._increase_progress)
        logger.debug("I2PProgressBar initialized")

    def _setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-top: 2px solid #ffaa00;
            }
            QLabel {
                color: #fff;
                font-size: 14px;
                font-weight: bold;
            }
            QProgressBar {
                border: 2px solid #ffaa00;
                border-radius: 5px;
                text-align: center;
                color: #fff;
                background-color: #2a2a2a;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #ffaa00;
            }
            QPushButton {
                background-color: transparent;
                color: #aaa;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #333;
                color: #fff;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        self.label = QLabel("🧅 Запуск I2P...")
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar, 1)

        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.cancelled)
        layout.addWidget(self.cancel_btn)

    def set_status(self, percent, message):
        self.progress_bar.setValue(percent)
        self.label.setText(f"🧅 {message}")
        logger.debug(f"I2P progress: {percent}% - {message}")

    def start_auto_progress(self):
        self._progress_value = self.progress_bar.value()
        self._progress_timer.start(500)

    def _increase_progress(self):
        if self._progress_value < 90:
            self._progress_value += 1
            self.progress_bar.setValue(self._progress_value)

    def stop_auto_progress(self):
        self._progress_timer.stop()

    def finish_success(self):
        self.progress_bar.setValue(100)
        self.label.setText("🧅 I2P готов!")
        logger.info("I2P finished successfully")
        QTimer.singleShot(1500, self.hide)
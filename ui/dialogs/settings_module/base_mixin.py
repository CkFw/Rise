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
Базовый миксин для диалога настроек.
Содержит общие методы: перетаскивание окна, загрузка/сохранение config.ini,
а также вспомогательные методы для работы с настройками.
"""
import os
import configparser
import logging
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from core.config import CONFIG_PATH

logger = logging.getLogger(__name__)

class BaseMixin:
    """Миксин с базовыми методами для диалога настроек"""

    def _load_config(self):
        """Загрузка настроек из config.ini (для Vulkan и других)"""
        self.config = configparser.ConfigParser()
        if os.path.exists(CONFIG_PATH):
            self.config.read(CONFIG_PATH)
        else:
            self.config['Performance'] = {}
        vulkan = self.config.getboolean('Performance', 'vulkan_enabled', fallback=False)
        self.vulkan_check.setChecked(vulkan)

    def _save_config(self):
        """Сохранение настроек в config.ini"""
        self.config['Performance']['vulkan_enabled'] = str(self.vulkan_check.isChecked())
        try:
            with open(CONFIG_PATH, 'w') as f:
                self.config.write(f)
            logger.info("Config saved")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        event.accept()
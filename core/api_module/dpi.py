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
Миксин для настроек обхода DPI (PySide6)
Исправлено: использование единого экземпляра Database, логирование.
"""
import logging
from core.database import db

logger = logging.getLogger(__name__)

class DPIMixin:
    """Миксин для работы с настройками DPI"""

    def _get_setting(self, key, default):
        try:
            result = db.execute(
                "SELECT value FROM settings WHERE key = ?",
                (key,), fetchone=True
            )
            return result['value'] if result else default
        except Exception as e:
            logger.error(f"Error getting setting {key}: {e}")
            return default

    def _save_setting(self, key, value):
        try:
            db.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, str(value))
            )
        except Exception as e:
            logger.error(f"Error saving setting {key}: {e}")

    def _get_bool(self, key, default):
        val = self._get_setting(key, '1' if default else '0')
        return val == '1'

    def _save_bool(self, key, value):
        self._save_setting(key, '1' if value else '0')

    def _get_int(self, key, default):
        try:
            return int(self._get_setting(key, str(default)))
        except:
            return default

    def _save_int(self, key, value):
        self._save_setting(key, str(value))

    def get_dpi_enabled(self):
        return self._get_bool('dpi_enabled', False)

    def save_dpi_enabled(self, enabled):
        self._save_bool('dpi_enabled', enabled)

    def get_dpi_path(self):
        return self._get_setting('dpi_path', "")

    def save_dpi_path(self, path):
        self._save_setting('dpi_path', path)

    def get_dpi_args(self):
        return self._get_setting('dpi_args', "")

    def save_dpi_args(self, args):
        self._save_setting('dpi_args', args)

    def get_dpi_port(self):
        return self._get_int('dpi_port', 1080)

    def save_dpi_port(self, port):
        self._save_int('dpi_port', port)
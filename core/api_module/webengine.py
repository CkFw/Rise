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
Миксин для настроек WebEngine (PySide6)
Исправлено: использование единого экземпляра Database, логирование.
"""
import logging
from core.database import db
from core.config import DEFAULT_PRINT_BACKGROUNDS_ENABLED, DEFAULT_PDF_SEPARATE_ENABLED

logger = logging.getLogger(__name__)

# Мобильный User-Agent по умолчанию
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
)

class WebEngineMixin:
    """Миксин для работы с настройками WebEngine"""

    def _get_bool(self, key, default):
        try:
            result = db.execute(
                "SELECT value FROM settings WHERE key = ?",
                (key,), fetchone=True
            )
            if result:
                return result['value'] == '1'
            return default
        except Exception as e:
            logger.error(f"Error getting setting {key}: {e}")
            return default

    def _save_bool(self, key, value):
        try:
            db.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, '1' if value else '0')
            )
        except Exception as e:
            logger.error(f"Error saving setting {key}: {e}")

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

    def get_print_backgrounds_enabled(self):
        return self._get_bool('print_backgrounds_enabled', DEFAULT_PRINT_BACKGROUNDS_ENABLED)

    def save_print_backgrounds_enabled(self, enabled):
        self._save_bool('print_backgrounds_enabled', enabled)

    def get_pdf_separate_enabled(self):
        return self._get_bool('pdf_separate_enabled', DEFAULT_PDF_SEPARATE_ENABLED)

    def save_pdf_separate_enabled(self, enabled):
        self._save_bool('pdf_separate_enabled', enabled)

    # Новые методы для User-Agent
    def get_user_agent(self):
        """Возвращает сохранённый User-Agent или мобильный по умолчанию."""
        return self._get_setting('user_agent', DEFAULT_USER_AGENT)

    def save_user_agent(self, user_agent):
        """Сохраняет пользовательский User-Agent."""
        self._save_setting('user_agent', user_agent)
        logger.info(f"User-Agent saved: {user_agent[:50]}...")
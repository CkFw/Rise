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
Миксин для работы с историей посещений (PySide6)
Исправлено: использование единого экземпляра Database, логирование, буферизация.
"""
import logging
from PySide6.QtCore import QTimer
from core.database import db

logger = logging.getLogger(__name__)

class HistoryMixin:
    """Миксин для работы с историей посещений"""

    def __init__(self):
        self.history_buffer = []
        self.history_timer = None

    def add_history(self, url, title=""):
        self.history_buffer.append((url, title))
        if self.history_timer is None:
            self.history_timer = QTimer()
            self.history_timer.setSingleShot(True)
            self.history_timer.timeout.connect(self._flush_history)
            self.history_timer.start(3000)
        else:
            self.history_timer.start(3000)

    def _flush_history(self):
        if not self.history_buffer:
            return
        try:
            for url, title in self.history_buffer:
                db.execute(
                    "INSERT INTO history (url, title) VALUES (?, ?)",
                    (url, title)
                )
            logger.info(f"Flushed {len(self.history_buffer)} history items")
        except Exception as e:
            logger.error(f"Error flushing history: {e}")
        finally:
            self.history_buffer.clear()
            self.history_timer = None

    def get_history(self):
        try:
            rows = db.execute(
                'SELECT * FROM history ORDER BY visited_at DESC LIMIT 50',
                fetchall=True
            )
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []

    def clear_history(self):
        try:
            db.execute('DELETE FROM history')
            logger.info("History cleared")
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
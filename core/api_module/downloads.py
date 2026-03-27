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
Миксин для работы с загрузками (PySide6)
Исправлено: использование единого экземпляра Database, логирование.
"""
import os
import logging
from core.database import db

logger = logging.getLogger(__name__)

class DownloadsMixin:
    """Миксин для работы с загрузками"""

    def add_download(self, filename, filepath, url="", file_size=0):
        try:
            db.execute(
                'INSERT INTO downloads (filename, filepath, url, file_size) VALUES (?, ?, ?, ?)',
                (filename, filepath, url, file_size)
            )
            logger.info(f"Download added: {filename}, size={file_size}")
            return True
        except Exception as e:
            logger.error(f"Error adding download: {e}")
            return False

    def get_downloads(self):
        try:
            rows = db.execute('SELECT * FROM downloads ORDER BY downloaded_at DESC', fetchall=True)
            results = [dict(row) for row in rows]
            for download in results:
                download['exists'] = os.path.exists(download['filepath'])
            return results
        except Exception as e:
            logger.error(f"Error getting downloads: {e}")
            return []

    def clear_downloads(self):
        try:
            db.execute('DELETE FROM downloads')
            logger.info("Downloads cleared")
        except Exception as e:
            logger.error(f"Error clearing downloads: {e}")

    def open_file_location(self, filepath):
        try:
            if os.path.exists(filepath):
                os.startfile(os.path.dirname(filepath))
                return True
            return False
        except Exception as e:
            logger.error(f"Error opening location: {e}")
            return False

    def update_download_size(self, filepath, size):
        try:
            db.execute(
                "UPDATE downloads SET file_size = ? WHERE filepath = ?",
                (size, filepath)
            )
            logger.info(f"Updated download size for {filepath} to {size}")
            return True
        except Exception as e:
            logger.error(f"Error updating download size: {e}")
            return False

    def remove_download_by_path(self, filepath):
        try:
            db.execute("DELETE FROM downloads WHERE filepath = ?", (filepath,))
            logger.info(f"Removed download record for {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error removing download: {e}")
            return False
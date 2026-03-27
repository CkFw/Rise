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
Миксин для работы с паролями (PySide6)
Исправлено: использование единого экземпляра Database, логирование.
"""
import csv
import logging
from core.database import db

logger = logging.getLogger(__name__)

class PasswordsMixin:
    def add_password(self, site, username, password):
        try:
            db.execute(
                'INSERT INTO passwords (site, username, password) VALUES (?, ?, ?)',
                (site, username, password)
            )
            logger.info(f"Password added for {site}")
            return True
        except Exception as e:
            logger.error(f"Error adding password: {e}")
            return False

    def get_passwords(self):
        try:
            rows = db.execute('SELECT * FROM passwords ORDER BY site', fetchall=True)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting passwords: {e}")
            return []

    def delete_password(self, password_id):
        try:
            db.execute('DELETE FROM passwords WHERE id = ?', (password_id,))
            logger.info(f"Password {password_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting password: {e}")
            return False

    def export_passwords(self, filepath):
        try:
            passwords = self.get_passwords()
            with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['site', 'username', 'password'])
                for pwd in passwords:
                    writer.writerow([pwd.get('site', ''), pwd.get('username', ''), pwd.get('password', '')])
            logger.info(f"Passwords exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting passwords: {e}")
            return False

    def import_passwords(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    db.execute(
                        'INSERT INTO passwords (site, username, password) VALUES (?, ?, ?)',
                        (row.get('site', ''), row.get('username', ''), row.get('password', ''))
                    )
            logger.info(f"Passwords imported from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error importing passwords: {e}")
            return False
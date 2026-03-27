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

import os
import logging
from core.database import db

logger = logging.getLogger(__name__)

class ProfileMixin:
    """Управление профилями пользователей."""

    def _create_profiles_table(self):
        try:
            db.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 0
                )
            ''')
            # Если нет активного профиля, создаём "По умолчанию"
            active = db.execute("SELECT id FROM profiles WHERE is_active=1", fetchone=True)
            if not active:
                self.add_profile("По умолчанию", set_active=True)
        except Exception as e:
            logger.error(f"Error creating profiles table: {e}")

    def add_profile(self, name, set_active=False):
        """Добавляет новый профиль."""
        try:
            # Проверяем уникальность
            existing = db.execute("SELECT id FROM profiles WHERE name=?", (name,), fetchone=True)
            if existing:
                logger.warning(f"Profile {name} already exists")
                return False
            db.execute("INSERT INTO profiles (name, is_active) VALUES (?, ?)", (name, 1 if set_active else 0))
            if set_active:
                # Снимаем флаг активного с других профилей
                db.execute("UPDATE profiles SET is_active=0 WHERE name!=?", (name,))
            logger.info(f"Profile '{name}' added")
            return True
        except Exception as e:
            logger.error(f"Error adding profile: {e}")
            return False

    def get_profiles(self):
        """Возвращает список всех профилей."""
        try:
            rows = db.execute("SELECT * FROM profiles ORDER BY name", fetchall=True)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting profiles: {e}")
            return []

    def get_active_profile(self):
        """Возвращает активный профиль."""
        try:
            row = db.execute("SELECT * FROM profiles WHERE is_active=1", fetchone=True)
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting active profile: {e}")
            return None

    def set_active_profile(self, profile_id):
        """Устанавливает активный профиль по ID."""
        try:
            db.execute("UPDATE profiles SET is_active=0")
            db.execute("UPDATE profiles SET is_active=1 WHERE id=?", (profile_id,))
            logger.info(f"Active profile set to id {profile_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting active profile: {e}")
            return False

    def delete_profile(self, profile_id):
        """Удаляет профиль."""
        try:
            active = self.get_active_profile()
            if active and active['id'] == profile_id:
                logger.warning("Cannot delete active profile")
                return False
            db.execute("DELETE FROM profiles WHERE id=?", (profile_id,))
            logger.info(f"Profile {profile_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting profile: {e}")
            return False

    def get_profile_dir(self, profile_name=None):
        """Возвращает путь к папке профиля WebEngine."""
        home_dir = os.path.expanduser("~")
        base_dir = os.path.join(home_dir, ".risebrowser", "profiles")
        if profile_name:
            return os.path.join(base_dir, profile_name)
        else:
            active = self.get_active_profile()
            if active:
                return os.path.join(base_dir, active['name'])
            else:
                return os.path.join(base_dir, "По умолчанию")
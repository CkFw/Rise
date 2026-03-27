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
Модуль для работы с базой данных SQLite.
Исправлено: единый класс Database с контекстным менеджером, логирование.
"""
import sqlite3
import os
import logging
from contextlib import contextmanager
from core.config import DATA_DIR

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(DATA_DIR, 'rise.db')

class Database:
    """Класс для работы с базой данных SQLite"""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Создаёт все необходимые таблицы, если они ещё не существуют."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # === История посещений ===
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    visit_count INTEGER DEFAULT 1
                )
            ''')

            # === Закладки ===
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT,
                    type TEXT DEFAULT 'bookmark',
                    parent_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES bookmarks(id) ON DELETE CASCADE
                )
            ''')

            # === Пароли ===
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    notes TEXT
                )
            ''')

            # === Настройки (ключ-значение) ===
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')

            # === Загрузки ===
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    filepath TEXT,
                    filename TEXT,
                    file_size INTEGER DEFAULT 0,
                    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # === Сессия (список открытых вкладок при закрытии) ===
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    position INTEGER DEFAULT 0
                )
            ''')

            conn.commit()
            logger.info("Database initialized")

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для соединения с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def execute(self, query, params=(), fetchone=False, fetchall=False):
        """Выполнить запрос и вернуть результат"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()
            conn.commit()
            return cursor.lastrowid

# Глобальный экземпляр для использования во всех миксинах
db = Database()

def get_connection():
    """Для обратной совместимости"""
    return db.get_connection()

def init_db():
    """Для обратной совместимости"""
    db._init_db()
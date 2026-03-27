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
Миксин для работы с поисковыми системами (PySide6)
Исправлено: использование единого экземпляра Database.
"""
import logging
from core.database import db
from core.config import DEFAULT_SEARCH_ENGINE, SEARCH_ENGINES, I2P_SEARCH_ENGINES

logger = logging.getLogger(__name__)

class SearchMixin:
    def get_search_engine(self):
        if hasattr(self, '_search_engine'):
            return self._search_engine
        result = db.execute(
            "SELECT value FROM settings WHERE key='search_engine'",
            fetchone=True
        )
        self._search_engine = result['value'] if result else DEFAULT_SEARCH_ENGINE
        return self._search_engine

    def save_search_engine(self, engine):
        db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ('search_engine', engine)
        )
        self.search_engine = engine
        self._search_engine = engine
        logger.info(f"Search engine saved: {engine}")

    def get_search_engines_dict(self):
        if self.get_i2p_enabled():
            combined = SEARCH_ENGINES.copy()
            combined.update(I2P_SEARCH_ENGINES)
            return combined
        else:
            return SEARCH_ENGINES.copy()

    def get_search_engine_names(self):
        return list(self.get_search_engines_dict().keys())

    def get_search_url(self, query):
        engines = self.get_search_engines_dict()
        base_url = engines.get(self.search_engine, SEARCH_ENGINES["Google"])
        return base_url + query.replace(' ', '+')

    def set_default_i2p_search_engine(self):
        i2p_names = list(I2P_SEARCH_ENGINES.keys())
        if i2p_names and self.search_engine not in self.get_search_engines_dict():
            self.save_search_engine(i2p_names[0])
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
Миксин для вкладки поиска.
"""
import logging
from PySide6.QtWidgets import QLabel, QComboBox, QPushButton, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)

class SearchMixin:
    """Миксин для настройки поисковой системы"""

    def setup_search_tab(self):
        """Создаёт и возвращает вкладку поиска"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Выберите поисковую систему:"))

        self.combo = QComboBox()
        self.combo.addItems(self.api.get_search_engine_names())
        self.combo.setCurrentText(self.api.search_engine)
        layout.addWidget(self.combo)
        self.combo.currentTextChanged.connect(self.on_search_changed)

        self.status_label = QLabel("✓ Поисковик применяется автоматически")
        self.status_label.setStyleSheet("color: #00ff88; font-size: 12px;")
        layout.addWidget(self.status_label)

        refresh_btn = QPushButton("🔄 Обновить список поисковиков")
        refresh_btn.clicked.connect(self.refresh_search_engines)
        layout.addWidget(refresh_btn)

        layout.addStretch()
        return tab

    def on_search_changed(self, engine):
        self.api.save_search_engine(engine)
        self.status_label.setText(f"✓ Применено: {engine}")
        if self.parent_window and hasattr(self.parent_window, 'update_current_home_page'):
            self.parent_window.update_current_home_page()
        logger.info(f"Search engine changed to {engine}")

    def refresh_search_engines(self):
        current = self.combo.currentText()
        self.combo.clear()
        self.combo.addItems(self.api.get_search_engine_names())
        if current in self.api.get_search_engine_names():
            self.combo.setCurrentText(current)
        else:
            self.combo.setCurrentText(self.api.search_engine)
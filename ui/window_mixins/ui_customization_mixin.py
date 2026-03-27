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
Применение кастомизации интерфейса: верхняя панель, адресная строка.
"""
import logging

logger = logging.getLogger(__name__)

class UICustomizationMixin:
    """Применяет настройки кастомизации к UI."""

    def apply_titlebar_customization(self):
        """Обновляет верхнюю панель (после изменений в настройках)."""
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.apply_customization()
            # Обновляем настройки автоскрытия
            self.update_auto_hide_settings()

    def apply_urlbar_customization(self):
        """Обновляет адресную строку (после изменений в настройках)."""
        if hasattr(self, 'nav_bar') and self.nav_bar:
            self.nav_bar.apply_urlbar_customization()
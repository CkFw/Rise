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
Диалоги истории, избранного, настроек и AI-чата.
"""
import logging

logger = logging.getLogger(__name__)

class HistoryFavoritesMixin:
    """Открытие диалогов истории, избранного, настроек, AI-чата."""

    def show_favorites_dialog(self, current_url, current_title):
        if hasattr(self, 'favorites_dialog') and self.favorites_dialog and self.favorites_dialog.isVisible():
            self.favorites_dialog.raise_()
            return
        from ui.dialogs.favorites import FavoritesDialog
        self.favorites_dialog = FavoritesDialog(self, self.api, current_url, current_title)
        self.favorites_dialog.finished.connect(lambda: setattr(self, 'favorites_dialog', None))
        self.favorites_dialog.show()

    def show_history_dialog(self):
        if hasattr(self, 'history_dialog') and self.history_dialog and self.history_dialog.isVisible():
            self.history_dialog.raise_()
            return
        from ui.dialogs.history import HistoryDialog
        self.history_dialog = HistoryDialog(self, self, self.api.get_history())
        self.history_dialog.finished.connect(lambda: setattr(self, 'history_dialog', None))
        self.history_dialog.show()

    def show_settings_dialog(self):
        if hasattr(self, 'settings_dialog') and self.settings_dialog and self.settings_dialog.isVisible():
            self.settings_dialog.raise_()
            return
        from ui.dialogs.settings import SettingsDialog
        self.settings_dialog = SettingsDialog(self, self.api)
        self.settings_dialog.finished.connect(lambda: setattr(self, 'settings_dialog', None))
        self.settings_dialog.show()

    def show_ai_chat(self):
        if hasattr(self, 'ai_chat') and self.ai_chat and self.ai_chat.isVisible():
            self.ai_chat.raise_()
            return
        if not self.api.get_ai_chat_enabled():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "AI Чат", "AI-чат отключён в настройках.\nВключите его в Настройках → AI Чат.")
            return
        from ui.dialogs.ai_chat import AIChatWindow
        self.ai_chat = AIChatWindow(self.api, self)
        self.ai_chat.finished.connect(lambda: setattr(self, 'ai_chat', None))
        self.ai_chat.show()
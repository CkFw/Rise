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
Обработка событий клавиатуры, мыши, автоскрытия панели.
(Звуки клавиатуры удалены)
"""
import logging
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent, QCursor, QShortcut, QKeySequence

logger = logging.getLogger(__name__)

class EventHandlingMixin:
    """Обработка глобальных событий: клавиши, мышь, автоскрытие панели."""

    def _setup_global_shortcuts(self):
        """Создаёт глобальные горячие клавиши (работают даже когда фокус на WebEngine)."""
        # F5 - обновление страницы
        self.f5_shortcut = QShortcut(QKeySequence(Qt.Key_F5), self)
        self.f5_shortcut.activated.connect(self.refresh_page)

        # F11 - полноэкранный режим
        self.f11_shortcut = QShortcut(QKeySequence(Qt.Key_F11), self)
        self.f11_shortcut.activated.connect(self._toggle_fullscreen)

        # Shift+I - AI чат
        self.ai_shortcut = QShortcut(QKeySequence("Shift+I"), self)
        self.ai_shortcut.activated.connect(self.show_ai_chat)

        logger.info("Global shortcuts (F5, F11, Shift+I) initialized")

    def _toggle_fullscreen(self):
        """Переключает полноэкранный режим."""
        self._handle_fullscreen_request(not self.isFullScreen())

    def _init_global_shortcuts(self):
        self._setup_global_shortcuts()

    def eventFilter(self, obj, event):
        """
        Фильтр событий (оставлен для F5, F11 и автоскрытия).
        """
        # Обработка горячих клавиш (F5, F11, Shift+I)
        if event.type() == QEvent.Type.KeyPress and isinstance(event, QKeyEvent):
            key = event.key()
            if key == Qt.Key.Key_F5:
                self.refresh_page()
                return True
            elif key == Qt.Key.Key_I and event.modifiers() == Qt.ShiftModifier:
                self.show_ai_chat()
                return True
            elif key == Qt.Key.Key_F11:
                self._handle_fullscreen_request(not self.isFullScreen())
                return True

        # Автоскрытие панели – обрабатываем движение мыши
        if event.type() == QEvent.Type.MouseMove:
            if self.auto_hide_enabled and not self.is_fullscreen:
                cursor_pos = QCursor.pos()
                local_pos = self.mapFromGlobal(cursor_pos)
                if local_pos.y() <= 2:
                    self.show_title_bar()
                else:
                    if hasattr(self, 'title_bar') and self.title_bar and self.title_bar.isVisible():
                        self._restart_auto_hide_timer()

        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent):
        """
        Запасной обработчик (для случаев, когда фокус не на WebEngine).
        """
        if event.key() == Qt.Key.Key_F5:
            self.refresh_page()
            event.accept()
            return
        elif event.key() == Qt.Key.Key_I and event.modifiers() == Qt.ShiftModifier:
            self.show_ai_chat()
            event.accept()
            return
        elif event.key() == Qt.Key.Key_F11:
            self._handle_fullscreen_request(not self.isFullScreen())
            event.accept()
            return
        else:
            super().keyPressEvent(event)
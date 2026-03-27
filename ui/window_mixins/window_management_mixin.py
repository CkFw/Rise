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
Управление окном: создание UI, полноэкранный режим, автоскрытие панели, Aero Snap.
"""
import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt, QTimer, QEvent, QRect
from PySide6.QtGui import QMouseEvent, QCursor

from core.config import STYLES
from ui.title_bar import CustomTitleBar
from ui.nav_bar import NavBar
from ui.tabs import TabBar
from ui.i2p_progress_bar import I2PProgressBar

logger = logging.getLogger(__name__)

class WindowManagementMixin:
    """Управление геометрией окна, полноэкранный режим, автоскрытие панели, Aero Snap."""

    # Порог появления панели (пикселей от верхнего края окна)
    SHOW_THRESHOLD = 5   # измените на нужное значение

    def _setup_ui(self):
        self.setWindowTitle("Rise Browser")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.nav_bar = NavBar(self)
        self.tab_bar = TabBar(self)
        self.title_bar = CustomTitleBar(self, self.tab_bar, self.nav_bar)
        self.stack = QStackedWidget()

        layout.addWidget(self.title_bar)
        layout.addWidget(self.stack)

        self.i2p_progress = I2PProgressBar(self)
        self.i2p_progress.cancelled.connect(self._cancel_i2p_startup)
        layout.addWidget(self.i2p_progress)

        self._prepare_home_page()
        self.setStyleSheet(STYLES['main_window'])

    def _init_auto_hide(self):
        """Инициализирует таймеры автоскрытия."""
        self.auto_hide_enabled = self.api.get_auto_hide_enabled()
        self.auto_hide_delay = self.api.get_auto_hide_delay()
        self._mouse_check_timer = QTimer(self)
        self._mouse_check_timer.timeout.connect(self._check_mouse_position)
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._hide_title_bar)
        self.update_auto_hide_settings()

    def update_auto_hide_settings(self):
        """Обновляет состояние автоскрытия после изменения настроек."""
        self.auto_hide_enabled = self.api.get_auto_hide_enabled()
        self.auto_hide_delay = self.api.get_auto_hide_delay()
        if self.auto_hide_enabled:
            self._mouse_check_timer.start(100)
            self._set_title_bar_visible(True)
        else:
            self._mouse_check_timer.stop()
            self._hide_timer.stop()
            self._set_title_bar_visible(True)

    def _check_mouse_position(self):
        """Проверяет позицию мыши и управляет видимостью панели."""
        if not self.auto_hide_enabled or self.is_fullscreen:
            return

        cursor_global = QCursor.pos()
        # Глобальные координаты окна
        window_rect = self.geometry()
        window_top_y = window_rect.top()
        window_bottom_y = window_rect.bottom()
        window_left_x = window_rect.left()
        window_right_x = window_rect.right()

        # Проверка, находится ли курсор в пределах окна по горизонтали
        inside_horizontally = (window_left_x <= cursor_global.x() <= window_right_x)

        # Проверка, находится ли курсор в верхней зоне окна (до SHOW_THRESHOLD пикселей от верха)
        on_top_edge = inside_horizontally and (window_top_y <= cursor_global.y() <= window_top_y + self.SHOW_THRESHOLD)

        # Проверка, находится ли курсор на панели (если панель видима)
        on_panel = False
        if self.title_bar.isVisible():
            panel_rect = self.title_bar.geometry()
            panel_global_top_left = self.title_bar.mapToGlobal(panel_rect.topLeft())
            panel_global_rect = QRect(panel_global_top_left, panel_rect.size())
            on_panel = panel_global_rect.contains(cursor_global)

        # Отладочный вывод
        # print(f"cursor: {cursor_global.x()},{cursor_global.y()}  window top={window_top_y}  threshold={window_top_y+self.SHOW_THRESHOLD}  on_top_edge={on_top_edge}  on_panel={on_panel}")

        if on_top_edge:
            # Курсор в верхней зоне – показываем панель и отменяем таймер
            if not self.title_bar.isVisible():
                self._set_title_bar_visible(True)
            if self._hide_timer.isActive():
                self._hide_timer.stop()
        elif on_panel:
            # Курсор на панели – также показываем (на случай, если она скрылась) и отменяем таймер
            if not self.title_bar.isVisible():
                self._set_title_bar_visible(True)
            if self._hide_timer.isActive():
                self._hide_timer.stop()
        else:
            # Курсор вне зон – если панель видима, запускаем таймер скрытия
            if self.title_bar.isVisible() and not self._hide_timer.isActive():
                self._hide_timer.start(self.auto_hide_delay * 1000)

    def _hide_title_bar(self):
        """Скрывает панель, если мышь всё ещё вне панели и вне верхней зоны."""
        if not self.auto_hide_enabled or self.is_fullscreen:
            return

        cursor_global = QCursor.pos()
        # Глобальные координаты окна
        window_rect = self.geometry()
        window_top_y = window_rect.top()
        window_left_x = window_rect.left()
        window_right_x = window_rect.right()
        inside_horizontally = (window_left_x <= cursor_global.x() <= window_right_x)
        on_top_edge = inside_horizontally and (window_top_y <= cursor_global.y() <= window_top_y + self.SHOW_THRESHOLD)

        on_panel = False
        if self.title_bar.isVisible():
            panel_rect = self.title_bar.geometry()
            panel_global_top_left = self.title_bar.mapToGlobal(panel_rect.topLeft())
            panel_global_rect = QRect(panel_global_top_left, panel_rect.size())
            on_panel = panel_global_rect.contains(cursor_global)

        if not (on_top_edge or on_panel):
            self._set_title_bar_visible(False)

    def _set_title_bar_visible(self, visible):
        """Устанавливает видимость панели."""
        if self.title_bar and self.title_bar.isVisible() != visible:
            self.title_bar.setVisible(visible)
            logger.debug(f"Title bar visible set to {visible}")

    # ----- Полноэкранный режим -----
    def _handle_fullscreen_request(self, on):
        try:
            if on:
                self.is_fullscreen = True
                self._set_title_bar_visible(False)
                self.showFullScreen()
                self._mouse_check_timer.stop()
                self._hide_timer.stop()
            else:
                self.is_fullscreen = False
                self._set_title_bar_visible(True)
                self.showNormal()
                if self.auto_hide_enabled:
                    self._mouse_check_timer.start(100)
        except Exception as e:
            self.logger.error(f"Fullscreen error: {e}")

    # ----- Aero Snap по положению курсора (используется в title_bar) -----
    def _get_current_screen_geometry(self, cursor_pos):
        from PySide6.QtWidgets import QApplication
        screen = QApplication.screenAt(cursor_pos)
        if not screen:
            screen = QApplication.primaryScreen()
        return screen.availableGeometry()

    # ----- Перетаскивание окна (через title_bar) -----
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if hasattr(self, 'title_bar') and self.title_bar:
                self.title_bar.mousePressEvent(event)
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.mouseMoveEvent(event)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.mouseReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)

    # ----- События изменения состояния окна -----
    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMinimized():
                self._suspend_tabs_on_minimize()
            else:
                self._resume_tabs_on_restore()
        super().changeEvent(event)

    def _suspend_tabs_on_minimize(self):
        pass

    def _resume_tabs_on_restore(self):
        pass
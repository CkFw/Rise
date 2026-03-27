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
Панель навигации с адресной строкой, кнопками навигации и обновления - PySide6
Добавлена индикация загрузки страницы в адресной строке (непрозрачный сплошной цвет).
Исправлено: предотвращение множественного открытия диалогов через вызов методов главного окна.
"""
import os
import logging
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt

from core.config import ICONS_DIR
from core.utils import resource_path

logger = logging.getLogger(__name__)

class NavBar(QWidget):
    def __init__(self, browser_instance):
        super().__init__()
        self.browser = browser_instance
        self.api = browser_instance.api
        self.setFixedHeight(45)
        self._setup_styles()
        self._setup_ui()
        self.default_style = self.url_bar.styleSheet()
        # Применяем настройки внешнего вида адресной строки
        self.apply_urlbar_customization()

    def _setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #fff;
                font-size: 18px;
                padding: 4px 8px;
                min-width: 30px;
                max-width: 30px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
            }
        """)

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.back_btn = QPushButton("←")
        self.back_btn.setToolTip("Назад")
        self.back_btn.clicked.connect(self.on_back)
        layout.addWidget(self.back_btn)

        self.forward_btn = QPushButton("→")
        self.forward_btn.setToolTip("Вперёд")
        self.forward_btn.clicked.connect(self.on_forward)
        layout.addWidget(self.forward_btn)

        self.home_btn = QPushButton("🏠")
        self.home_btn.setToolTip("Домой")
        self.home_btn.clicked.connect(self.on_home)
        layout.addWidget(self.home_btn)

        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setToolTip("Обновить страницу (F5)")
        self.refresh_btn.clicked.connect(self.on_refresh)
        layout.addWidget(self.refresh_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Введите URL или поиск...")
        self.url_bar.returnPressed.connect(self.on_url_return)
        layout.addWidget(self.url_bar, 1)

        icon_path = resource_path("icons/star.png")
        if os.path.exists(icon_path):
            star_icon = QIcon(icon_path)
            self.fav_action = QAction(star_icon, "Избранное")
        else:
            logger.warning("Иконка star.png не найдена, используем символ")
            self.fav_action = QAction("★")

        self.fav_action.setToolTip("Избранное (добавить текущую страницу)")
        self.fav_action.triggered.connect(self.on_favorites)
        self.url_bar.addAction(self.fav_action, QLineEdit.ActionPosition.TrailingPosition)

        logger.debug("NavBar created with load progress indicator (solid colors)")

    def apply_urlbar_customization(self):
        """Применяет настройки внешнего вида адресной строки."""
        border_enabled = self.api.get_urlbar_border_enabled()
        transparency = self.api.get_urlbar_transparency()
        bg_color = self.api.get_urlbar_bg_color()

        alpha = 255 - int(transparency * 255 / 100)  # 0% прозрачность -> 255, 100% -> 0
        # Преобразуем цвет в rgba
        if bg_color.startswith('#'):
            r = int(bg_color[1:3], 16)
            g = int(bg_color[3:5], 16)
            b = int(bg_color[5:7], 16)
        else:
            r, g, b = 15, 15, 15
        rgba = f"rgba({r}, {g}, {b}, {alpha/255})"

        border_style = "1px solid #5a5a5a" if border_enabled else "none"
        style = f"""
            QLineEdit {{
                background-color: {rgba};
                color: #fff;
                border: {border_style};
                border-radius: 20px;
                padding: 4px 10px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: #00a8ff;
            }}
        """
        self.url_bar.setStyleSheet(style)
        self.default_style = style  # обновляем дефолтный стиль для индикации загрузки

    def on_load_started(self):
        self._update_progress_style(0)

    def on_load_progress(self, progress):
        self._update_progress_style(progress)

    def on_load_finished(self):
        self.url_bar.setStyleSheet(self.default_style)

    def _update_progress_style(self, progress):
        p = progress / 100.0
        style = f"""
            QLineEdit {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgb(0, 168, 255),
                                            stop:{p} rgb(0, 168, 255),
                                            stop:{p} {self.default_style.split('background-color:')[1].split(';')[0] if 'background-color:' in self.default_style else '#0f0f0f'},
                                            stop:1 #0f0f0f);
                color: #fff;
                border: {self.default_style.split('border:')[1].split(';')[0] if 'border:' in self.default_style else '1px solid #5a5a5a'};
                border-radius: 20px;
                padding: 4px 10px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: #00a8ff;
            }}
        """
        self.url_bar.setStyleSheet(style)

    def on_url_return(self):
        url = self.url_bar.text().strip()
        if url:
            self.browser.navigate(url)

    def on_favorites(self):
        current_url = self.browser.browsers[self.browser.current_browser_index].url().toString()
        current_title = self.browser.browsers[self.browser.current_browser_index].page().title()
        self.browser.show_favorites_dialog(current_url, current_title)

    def on_downloads(self):
        self.browser._show_downloads_dialog()

    def on_history(self):
        self.browser.show_history_dialog()

    def on_settings(self):
        self.browser.show_settings_dialog()

    def on_back(self):
        try:
            if hasattr(self.browser, 'browsers') and self.browser.browsers:
                browser = self.browser.browsers[self.browser.current_browser_index]
                if browser and browser.page().history().canGoBack():
                    browser.back()
        except Exception as e:
            logger.error(f"Error in on_back: {e}")

    def on_forward(self):
        try:
            if hasattr(self.browser, 'browsers') and self.browser.browsers:
                browser = self.browser.browsers[self.browser.current_browser_index]
                if browser and browser.page().history().canGoForward():
                    browser.forward()
        except Exception as e:
            logger.error(f"Error in on_forward: {e}")

    def on_home(self):
        try:
            self.browser.go_home()
        except Exception as e:
            logger.error(f"Error in on_home: {e}")

    def on_refresh(self):
        try:
            self.browser.refresh_page()
        except Exception as e:
            logger.error(f"Error in on_refresh: {e}")
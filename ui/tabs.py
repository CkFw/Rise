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
Панель вкладок браузера с горизонтальной прокруткой - PySide6
Добавлена поддержка кастомизации цветов.
"""
import logging
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QScrollArea, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

logger = logging.getLogger(__name__)

class TabBar(QWidget):
    """Панель вкладок"""

    def __init__(self, browser_instance):
        super().__init__()
        self.browser = browser_instance
        self.api = browser_instance.api
        self.setFixedHeight(40)
        self.current_index = 0
        self.tabs = []
        self.tab_indices = []
        self._setup_ui()
        self.apply_customization()
        logger.debug("TabBar initialized")

    def _setup_ui(self):
        # Делаем фон самого TabBar прозрачным
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("TabBar { background-color: transparent; }")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        self.add_btn = QPushButton("+")
        self.add_btn.setObjectName("addTab")
        self.add_btn.setFixedSize(35, 35)
        self.add_btn.clicked.connect(self.add_new_tab)
        main_layout.addWidget(self.add_btn)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        # Делаем фон scroll_area прозрачным
        self.scroll_area.setStyleSheet("QScrollArea { background-color: transparent; }")

        self.tabs_container = QWidget()
        # Делаем фон контейнера прозрачным
        self.tabs_container.setStyleSheet("background-color: transparent;")
        self.tabs_layout = QHBoxLayout(self.tabs_container)
        self.tabs_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs_layout.setSpacing(5)

        self.scroll_area.setWidget(self.tabs_container)
        main_layout.addWidget(self.scroll_area, 1)

        # Стиль по умолчанию для кнопки "+"
        self.add_btn.setStyleSheet("""
            QPushButton#addTab {
                background-color: transparent;
                color: #00a8ff;
                border: none;
                font-size: 20px;
                border-radius: 17px;
            }
            QPushButton#addTab:hover {
                background-color: rgba(0, 168, 255, 100);
                color: #fff;
            }
        """)

    def add_tab(self, title, is_home=False, browser_index=0):
        btn = QPushButton(title)
        if is_home:
            btn.setObjectName("activeTab")
        btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        btn.customContextMenuRequested.connect(lambda pos: self.close_tab_immediately(btn, is_home))
        btn.clicked.connect(lambda: self.switch_tab(btn))

        # Фиксированный размер для кнопок вкладок
        btn.setMinimumWidth(120)
        btn.setMaximumWidth(150)
        btn.setFixedHeight(30)

        self.tabs_layout.addWidget(btn)

        self.tabs.append(btn)
        self.tab_indices.append(browser_index)

        self._apply_colors_to_button(btn)

        self.update_tab_styles()
        logger.debug(f"Tab added: {title}, index {browser_index}")

    def _apply_colors_to_button(self, btn):
        """Применяет настройки цветов к одной кнопке вкладки."""
        if self.api.get_tab_custom_colors_enabled():
            bg_color = self.api.get_tab_bg_color()
            text_color = self.api.get_tab_text_color()
            active_bg = self.api.get_tab_active_bg_color()
            active_text = self.api.get_tab_active_text_color()

            style = f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: none;
                    border-radius: 6px;
                    padding: 5px 15px;
                    font-size: 12px;
                    margin: 0 2px;
                }}
                QPushButton:hover {{
                    background-color: {QColor(bg_color).lighter(120).name()};
                }}
                QPushButton#activeTab {{
                    background-color: {active_bg};
                    color: {active_text};
                    font-weight: bold;
                }}
            """
            btn.setStyleSheet(style)
        else:
            # Стиль по умолчанию
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(50, 50, 50, 200);
                    color: #ccc;
                    border: none;
                    border-radius: 6px;
                    padding: 5px 15px;
                    font-size: 12px;
                    margin: 0 2px;
                }
                QPushButton:hover {
                    background-color: rgba(70, 70, 70, 230);
                    color: #fff;
                }
                QPushButton#activeTab {
                    background-color: rgba(0, 168, 255, 220);
                    color: #fff;
                    font-weight: bold;
                }
            """)

    def apply_customization(self):
        """Применяет настройки цветов ко всем существующим вкладкам."""
        for btn in self.tabs:
            self._apply_colors_to_button(btn)

        # Кнопка "+" остаётся без изменений
        self.update_tab_styles()

    def add_new_tab(self):
        if hasattr(self.browser, 'is_adding_tab') and self.browser.is_adding_tab:
            return
        self.browser.add_browser_tab()

    def remove_tab(self, index):
        if 0 <= index < len(self.tabs):
            btn = self.tabs.pop(index)
            self.tab_indices.pop(index)
            btn.deleteLater()
            self.update_tab_styles()
            logger.debug(f"Tab {index} removed")

    def switch_tab(self, clicked_btn):
        for i, btn in enumerate(self.tabs):
            if btn == clicked_btn:
                self.current_index = i
                self.browser.switch_to_tab(self.tab_indices[i])
        self.update_tab_styles()

    def close_tab_immediately(self, btn, is_home):
        if is_home:
            return
        index = self.tabs.index(btn)
        self.browser.close_tab(index)

    def update_tab_styles(self):
        for i, btn in enumerate(self.tabs):
            if i == self.current_index:
                btn.setObjectName("activeTab")
            else:
                btn.setObjectName("")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def update_active_tab(self, index):
        self.current_index = index
        self.update_tab_styles()

    def update_tab_title(self, index, title):
        if 0 <= index < len(self.tabs):
            current_text = self.tabs[index].text()
            icon = current_text[0] if current_text and current_text[0] in ['🏠', '📑', '🌐'] else '🌐'
            self.tabs[index].setText(f"{icon} {title}")
            logger.debug(f"Tab {index} title updated to {title}")
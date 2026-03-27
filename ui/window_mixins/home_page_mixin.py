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

# ui/window_mixins/home_page_mixin.py
"""
Миксин для управления домашней страницей.
"""
import os
import shutil
import logging
from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor

from core.config import DATA_DIR
from core.utils import resource_path

logger = logging.getLogger(__name__)

HOME_FILE = os.path.join(DATA_DIR, 'home.html')
HOME_TEMP_FILE = os.path.join(DATA_DIR, 'home_temp.html')


class HomePageMixin:
    """Управление домашней страницей: подготовка, генерация, загрузка."""

    def _prepare_home_page(self):
        """Копирует домашнюю страницу из assets, если она отсутствует."""
        if not os.path.exists(HOME_FILE):
            src_path = resource_path("assets/home.html")
            if os.path.exists(src_path):
                try:
                    shutil.copy2(src_path, HOME_FILE)
                    logger.info(f"Home page copied to {HOME_FILE}")
                except Exception as e:
                    logger.error(f"Error copying home.html: {e}")
            else:
                logger.error("Source home.html not found in assets")
        if os.path.exists(HOME_FILE):
            self.home_page_path = HOME_FILE
            logger.info(f"Home page will be loaded from {HOME_FILE}")
        else:
            self.home_page_path = None
            logger.error("Home page file not available")

    def restore_session(self):
        """Восстанавливает сессию (открытые вкладки) при запуске."""
        if not self.api.get_restore_session():
            self._add_browser_tab_internal("🏠 Главная", is_home=True)
            return
        urls = self.api.get_session_urls()
        if urls:
            for url in urls:
                if url and url != "about:blank":
                    self.add_browser_tab(url=url, is_home=False)
            if not self.browsers:
                self._add_browser_tab_internal("🏠 Главная", is_home=True)
        else:
            self._add_browser_tab_internal("🏠 Главная", is_home=True)

    def _generate_home_html(self):
        """Генерирует HTML домашней страницы с учётом настроек."""
        if not self.home_page_path or not os.path.exists(self.home_page_path):
            return None

        with open(self.home_page_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        html_content = html_content.replace('{{SEARCH_ENGINE}}', self.api.search_engine)

        elements = [
            ('.title', 'title'),
            ('#searchInput', 'search'),
            ('#searchEngineName', 'indicator'),
            ('#addBtn', 'addBtn'),
            ('#bookmarksContainer', 'bookmarks'),
        ]

        style_lines = []

        for selector, key in elements:
            visible = self.api.get_center_element_visible(key, True)
            if not visible:
                style_lines.append(f"{selector} {{ display: none !important; }}")
            else:
                offset_x = self.api.get_center_element_offset_x(key, 0)
                offset_y = self.api.get_center_element_offset_y(key, 0)
                if offset_x != 0 or offset_y != 0:
                    style_lines.append(f"{selector} {{ transform: translate({offset_x}px, {offset_y}px); }}")

        if style_lines:
            style_block = "<style>\n" + "\n".join(style_lines) + "\n</style>"
            html_content = html_content.replace('</head>', style_block + '</head>')

        bg_type = self.api.get_home_bg_type()
        color1 = self.api.get_home_bg_color1()
        color2 = self.api.get_home_bg_color2()
        image_file = self.api.get_home_bg_image_path()
        image_fit = self.api.get_home_bg_image_fit()
        anim_enabled = self.api.get_home_bg_animation_enabled()
        anim_speed = self.api.get_home_bg_animation_speed()
        crop = self.api.get_home_bg_image_crop()

        def hex_to_rgba(hex_color, alpha=0.3):
            c = QColor(hex_color)
            return f"rgba({c.red()}, {c.green()}, {c.blue()}, {alpha})"

        if bg_type == "Изображение" and image_file:
            abs_path = os.path.join(DATA_DIR, image_file)
            if os.path.exists(abs_path):
                file_url = QUrl.fromLocalFile(abs_path).toString()
                # Скрываем все элементы анимированного фона (круги, звёзды)
                hide_bg_style = """
                    <style>
                        .bg, .bg-circle, .star {
                            display: none !important;
                        }
                    </style>
                """
                html_content = html_content.replace('</head>', hide_bg_style + '</head>')

                if image_file.lower().endswith('.gif'):
                    # Для GIF используем тег <img> с абсолютным позиционированием
                    img_style = f"""
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        object-fit: {image_fit};
                        z-index: 0;
                    """
                    img_tag = f'<img src="{file_url}" style="{img_style}" alt="background">'
                    # Сбрасываем фон body
                    body_reset = '<style>body { background: none !important; }</style>'
                    html_content = html_content.replace('<body>', f'<body>{img_tag}')
                    html_content = html_content.replace('</head>', body_reset + '</head>')
                else:
                    # Статичное изображение через CSS
                    bg_style = f"""
                        <style>
                            body {{
                                background-image: url('{file_url}') !important;
                                background-size: {image_fit} !important;
                                background-position: center !important;
                                background-repeat: no-repeat !important;
                            }}
                        </style>
                    """
                    html_content = html_content.replace('</head>', bg_style + '</head>')
            else:
                logger.warning(f"Image file not found: {abs_path}")

        elif bg_type == "Сплошной цвет":
            style = f"""
                <style>
                    body {{
                        background: {color1} !important;
                    }}
                </style>
            """
            html_content = html_content.replace('</head>', style + '</head>')

        else:  # Градиент
            html_content = html_content.replace('rgba(0, 100, 255, 0.3)', hex_to_rgba(color1, 0.3))
            html_content = html_content.replace('rgba(0, 200, 255, 0.2)', hex_to_rgba(color2, 0.2))
            html_content = html_content.replace('rgba(100, 80, 255, 0.25)', hex_to_rgba(color1, 0.25))
            html_content = html_content.replace('rgba(0, 150, 200, 0.2)', hex_to_rgba(color2, 0.2))

            if anim_enabled:
                html_content = html_content.replace('animation-duration: 25s;', f'animation-duration: {anim_speed}s;')
                html_content = html_content.replace('animation-duration: 30s;', f'animation-duration: {anim_speed+5}s;')
                html_content = html_content.replace('animation-duration: 28s;', f'animation-duration: {anim_speed+3}s;')
                html_content = html_content.replace('animation-duration: 32s;', f'animation-duration: {anim_speed+7}s;')
            else:
                html_content = html_content.replace('animation: bg-move 20s infinite alternate ease-in-out;', 'animation: none;')

        return html_content

    def _load_home_to_browser(self, browser):
        """Загружает домашнюю страницу в указанный браузер."""
        try:
            html_content = self._generate_home_html()
            if html_content is None:
                browser.setHtml("<h1 style='color:#fff'>Домашняя страница не найдена</h1>")
                return

            with open(HOME_TEMP_FILE, 'w', encoding='utf-8') as f:
                f.write(html_content)

            browser.load(QUrl.fromLocalFile(HOME_TEMP_FILE))
            logger.info(f"Home page loaded from temporary file {HOME_TEMP_FILE}")
        except Exception as e:
            logger.error(f"Error generating home page: {e}")
            browser.setHtml("<h1 style='color:#fff'>Ошибка загрузки домашней страницы</h1>")

    def update_current_home_page(self):
        """Обновляет домашнюю страницу в текущей вкладке (после изменения настроек)."""
        if self.browsers and self.home_page_path:
            cur = self.browsers[self.current_browser_index]
            self._load_home_to_browser(cur)

    def _load_url_with_buffer(self, browser, url):
        """Загружает URL с использованием умного буфера, если включён."""
        if hasattr(self, 'smart_buffer') and self.api.get_smart_buffer_enabled():
            cached = self.smart_buffer.get_cached_page(url)
            if cached:
                browser.load(QUrl.fromLocalFile(cached))
                return True
        return False
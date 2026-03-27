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
Управление вкладками: добавление, закрытие, переключение, выгрузка.
"""
import time
import logging
from PySide6.QtCore import QUrl, QTimer

from core.browser_tab import BrowserTab

logger = logging.getLogger(__name__)

class TabManagementMixin:
    """Управление вкладками браузера."""

    def _add_browser_tab_internal(self, title, is_home=False, url=None, empty=False):
        tab = BrowserTab(self.api, main_window=self, adblock_manager=self.adblock_manager, is_home=is_home, parent=self)
        tab.titleChanged.connect(lambda t: self.tab_bar.update_tab_title(self.stack.currentIndex(), t[:30] if t else ""))
        tab.urlChanged.connect(self._on_url_changed)
        tab.page().profile().downloadRequested.connect(self.download_manager.handle_download_requested)

        index = len(self.browsers)
        tab.loadStarted.connect(lambda: self._on_tab_load_started(index))
        tab.loadProgress.connect(lambda p: self._on_tab_load_progress(index, p))
        tab.loadFinished.connect(lambda ok: self._on_tab_load_finished(index))

        self.stack.addWidget(tab)
        self.browsers.append(tab)
        self.browser_last_active.append(time.time())
        self.tabs_audible.append(False)
        self.tab_load_progress.append(None)

        self.tab_bar.add_tab(title, is_home, index)

        if url:
            if not self._load_url_with_buffer(tab, url):
                tab.load_url(url)
        elif not getattr(self, 'i2p_manager', None) or not self.i2p_manager.enabled and not empty:
            self._load_home_to_browser(tab)

        self.switch_to_tab(index)
        return tab

    def add_browser_tab(self, title=None, is_home=False, url=None, empty=False):
        if self.is_adding_tab:
            return None
        self.is_adding_tab = True
        try:
            title = title or f"Вкладка {len(self.browsers)+1}"
            return self._add_browser_tab_internal(title, is_home, url, empty)
        finally:
            self.is_adding_tab = False

    def close_tab(self, index):
        if len(self.browsers) == 1:
            self.close()
            return
        if not (0 <= index < len(self.browsers)) or index == 0:
            return
        b = self.browsers.pop(index)
        self.browser_last_active.pop(index)
        self.tabs_audible.pop(index)
        self.tab_load_progress.pop(index)
        self.stack.removeWidget(b)
        b.deleteLater()
        self.tab_bar.remove_tab(index)
        if self.current_browser_index >= len(self.browsers):
            self.current_browser_index = len(self.browsers) - 1
        self.switch_to_tab(self.current_browser_index)

    def switch_to_tab(self, index):
        if 0 <= index < len(self.browsers):
            self.browser_last_active[index] = time.time()
            b = self.browsers[index]
            if hasattr(b, '_discarded_url') and b._discarded_url:
                b.setUrl(QUrl(b._discarded_url))
                del b._discarded_url

            self.stack.setCurrentIndex(index)
            self.current_browser_index = index
            self.tab_bar.update_active_tab(index)

            if self.nav_bar:
                url = b.url().toString()
                self.nav_bar.url_bar.setText(url if not url.startswith('rise:') else "")

            prog = self.tab_load_progress[index]
            if prog is None:
                self.nav_bar.on_load_finished()
            else:
                self.nav_bar.on_load_started()
                self.nav_bar.on_load_progress(prog)

    def _on_tab_load_started(self, index):
        self.tab_load_progress[index] = 0
        if index == self.current_browser_index:
            self.nav_bar.on_load_started()

    def _on_tab_load_progress(self, index, progress):
        self.tab_load_progress[index] = progress
        if index == self.current_browser_index:
            self.nav_bar.on_load_progress(progress)

    def _on_tab_load_finished(self, index):
        self.tab_load_progress[index] = None
        if index == self.current_browser_index:
            self.nav_bar.on_load_finished()

    def _on_url_changed(self, url):
        url_str = url.toString()
        if url_str and not url_str.startswith(('file:', 'rise:')):
            self.api.add_history(url_str)
            if hasattr(self, 'smart_buffer'):
                self.smart_buffer.record_visit(url_str)
            if self.nav_bar and self.stack.currentIndex() == self.current_browser_index:
                self.nav_bar.url_bar.setText(url_str)

    # ----- Выгрузка старых вкладок -----
    def update_discard_interval(self, seconds=None):
        sec = seconds or self.api.get_discard_interval()
        if hasattr(self, 'discard_timer'):
            self.discard_timer.stop()
            self.discard_timer.start(sec * 1000)

    def discard_old_tabs(self):
        now = time.time()
        interval = self.api.get_discard_interval()
        for i, b in enumerate(self.browsers):
            if i == self.current_browser_index:
                continue
            if hasattr(b, 'is_home') and b.is_home:
                continue
            if now - self.browser_last_active[i] > interval:
                if not hasattr(b, '_discarded_url'):
                    url = b.url().toString()
                    if url and not url.startswith(('about:', 'file:', 'rise://')):
                        b._discarded_url = url
                        b.setUrl(QUrl("about:blank"))
                        self.logger.debug(f"Tab {i} discarded")

    # ----- Навигация -----
    def refresh_page(self):
        try:
            self.browsers[self.current_browser_index].reload_page()
        except Exception as e:
            self.logger.error(f"Refresh error: {e}")

    def go_back(self):
        try:
            self.browsers[self.current_browser_index].go_back()
        except Exception as e:
            self.logger.error(f"Back error: {e}")

    def go_forward(self):
        try:
            self.browsers[self.current_browser_index].go_forward()
        except Exception as e:
            self.logger.error(f"Forward error: {e}")

    def go_home(self):
        self._load_home_to_browser(self.browsers[self.current_browser_index])
        if self.nav_bar:
            self.nav_bar.url_bar.setText("")

    def navigate(self, url):
        self.logger.info(f"Navigate: {url}")
        try:
            if not url:
                return
            if not url.startswith(('http://', 'https://', 'file://')):
                if '.' in url and not url.startswith('localhost'):
                    url = 'https://' + url
                else:
                    url = self.api.get_search_url(url)
            if not self._load_url_with_buffer(self.browsers[self.current_browser_index], url):
                self.browsers[self.current_browser_index].load_url(url)
        except Exception as e:
            self.logger.error(f"Navigate error: {e}")
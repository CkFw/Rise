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
Менеджер умного буфера: предзагружает популярные сайты в фоне.
"""
import os
import time
import json
import threading
import logging
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse
from PySide6.QtCore import QObject, QTimer, QUrl
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile  # правильные импорты

logger = logging.getLogger(__name__)

class SmartBufferManager(QObject):
    """Управляет предзагрузкой популярных страниц."""

    def __init__(self, api, profile: QWebEngineProfile, parent=None):
        super().__init__(parent)
        self.api = api
        self.profile = profile
        self.stats_file = os.path.join(api.get_data_dir(), 'visit_stats.json')
        self.cache_dir = os.path.join(api.get_data_dir(), 'smart_buffer_cache')
        os.makedirs(self.cache_dir, exist_ok=True)

        self.visit_counter = Counter()
        self.last_update = None
        self._load_stats()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_popular_pages)
        self.update_timer.start(6 * 60 * 60 * 1000)  # 6 часов

        self.save_timer = QTimer(self)
        self.save_timer.timeout.connect(self._save_stats)
        self.save_timer.start(60 * 1000)

    def record_visit(self, url: str):
        domain = urlparse(url).netloc
        if domain:
            self.visit_counter[domain] += 1
            logger.debug(f"Visit recorded for {domain}")

    def _load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.visit_counter = Counter(data.get('counts', {}))
                    last = data.get('last_update')
                    if last:
                        self.last_update = datetime.fromisoformat(last)
            except Exception as e:
                logger.error(f"Error loading visit stats: {e}")

    def _save_stats(self):
        try:
            data = {
                'counts': dict(self.visit_counter),
                'last_update': datetime.now().isoformat()
            }
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving visit stats: {e}")

    def _update_popular_pages(self):
        if not self.api.get_smart_buffer_enabled():
            return
        top_domains = [domain for domain, _ in self.visit_counter.most_common(5)]
        if not top_domains:
            return
        logger.info(f"Smart buffer updating popular pages: {top_domains}")
        threading.Thread(target=self._preload_pages, args=(top_domains,), daemon=True).start()

    def _preload_pages(self, domains):
        for domain in domains:
            url = f"https://{domain}"
            cache_path = os.path.join(self.cache_dir, f"{domain}.html")
            if os.path.exists(cache_path):
                mtime = os.path.getmtime(cache_path)
                if time.time() - mtime < 24 * 60 * 60:
                    continue

            page = QWebEnginePage(self.profile, self)
            page.loadFinished.connect(lambda ok, p=page, u=url: self._on_page_loaded(ok, p, u))
            page.setUrl(QUrl(url))
            time.sleep(0.1)

    def _on_page_loaded(self, ok, page, url):
        if ok:
            domain = urlparse(url).netloc
            cache_path = os.path.join(self.cache_dir, f"{domain}.html")
            page.toHtml(lambda html: self._save_html(html, cache_path))
        page.deleteLater()

    def _save_html(self, html, path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Smart buffer saved: {path}")
        except Exception as e:
            logger.error(f"Error saving smart buffer page: {e}")

    def get_cached_page(self, url):
        domain = urlparse(url).netloc
        cache_path = os.path.join(self.cache_dir, f"{domain}.html")
        if os.path.exists(cache_path):
            if time.time() - os.path.getmtime(cache_path) < 24 * 60 * 60:
                return cache_path
        return None
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
Модуль блокировщика рекламы с поддержкой разных режимов (PySide6) – с отладкой
Исправлено: логирование, оптимизация кэша.
"""
from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide6.QtCore import QUrl
from collections import OrderedDict
import adblock
import logging

logger = logging.getLogger(__name__)

class LRUCache:
    def __init__(self, capacity=100):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


class SimpleAdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, ad_domains, cache_size=200):
        super().__init__()
        self.ad_domains = {domain.lower() for domain in ad_domains}
        self.cache = LRUCache(cache_size)
        self.logger = logging.getLogger(f"{__name__}.SimpleAdBlockInterceptor")

    def _is_blocked(self, url):
        host = url.host()
        if not host:
            return False
        host_lower = host.lower()
        cached = self.cache.get(host_lower)
        if cached is not None:
            return cached
        for domain in self.ad_domains:
            if host_lower == domain or host_lower.endswith('.' + domain):
                self.cache.put(host_lower, True)
                self.logger.debug(f"Blocked {host} (domain {domain})")
                return True
        self.cache.put(host_lower, False)
        return False

    def interceptRequest(self, info):
        try:
            if self._is_blocked(info.requestUrl()):
                info.block(True)
        except Exception as e:
            self.logger.error(f"Exception in interceptRequest: {e}", exc_info=True)


class RustAdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, rules_list, cache_size=500):
        super().__init__()
        if isinstance(rules_list, list):
            rules_str = '\n'.join(rules_list)
        else:
            rules_str = rules_list
        filter_set = adblock.FilterSet()
        filter_set.add_filter_list(rules_str)
        self.engine = adblock.Engine(filter_set, optimize=True)
        self.cache = LRUCache(cache_size)
        self.logger = logging.getLogger(f"{__name__}.RustAdBlockInterceptor")

    def _get_resource_type(self, info):
        resource_map = {
            QWebEngineUrlRequestInterceptor.ResourceType.MainFrame: "document",
            QWebEngineUrlRequestInterceptor.ResourceType.SubFrame: "subdocument",
            QWebEngineUrlRequestInterceptor.ResourceType.Stylesheet: "stylesheet",
            QWebEngineUrlRequestInterceptor.ResourceType.Script: "script",
            QWebEngineUrlRequestInterceptor.ResourceType.Image: "image",
            QWebEngineUrlRequestInterceptor.ResourceType.FontResource: "font",
            QWebEngineUrlRequestInterceptor.ResourceType.Object: "object",
            QWebEngineUrlRequestInterceptor.ResourceType.Media: "media",
            QWebEngineUrlRequestInterceptor.ResourceType.Xhr: "xmlhttprequest",
            QWebEngineUrlRequestInterceptor.ResourceType.Ping: "ping",
            QWebEngineUrlRequestInterceptor.ResourceType.Favicon: "image",
        }
        return resource_map.get(info.resourceType(), "other")

    def interceptRequest(self, info):
        try:
            url = info.requestUrl().toString()
            cached = self.cache.get(url)
            if cached is not None:
                if cached:
                    info.block(True)
                return

            resource_type = self._get_resource_type(info)
            result = self.engine.check_network_urls(url, "", resource_type)

            self.cache.put(url, result)

            if result:
                self.logger.debug(f"Blocked {url} (type: {resource_type})")
                info.block(True)
        except Exception as e:
            self.logger.error(f"Exception in interceptRequest: {e}", exc_info=True)


class SmartAdBlockInterceptor(RustAdBlockInterceptor):
    def __init__(self, rules_list, cache_size=500):
        super().__init__(rules_list, cache_size)
        self.critical_domains = {'jquery.com', 'googleapis.com', 'cloudflare.com',
                                  'gstatic.com', 'github.com', 'stackoverflow.com'}
        self.logger = logging.getLogger(f"{__name__}.SmartAdBlockInterceptor")

    def interceptRequest(self, info):
        try:
            url = info.requestUrl().toString()
            host = info.requestUrl().host()

            if any(crit in host for crit in self.critical_domains):
                return

            cached = self.cache.get(url)
            if cached is not None:
                if cached:
                    info.block(True)
                return

            resource_type = self._get_resource_type(info)
            result = self.engine.check_network_urls(url, "", resource_type)

            if not result and 'ad' in url.lower() and resource_type in ('image', 'script'):
                result = True

            self.cache.put(url, result)

            if result:
                self.logger.debug(f"Blocked {url} (smart mode)")
                info.block(True)
        except Exception as e:
            self.logger.error(f"Exception in interceptRequest: {e}", exc_info=True)
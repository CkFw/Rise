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
Менеджер для продвинутого блокировщика рекламы (PySide6)
"""
import os
import logging
import requests
from PySide6.QtCore import QObject, QTimer, Signal

from core.config import FILTERS_DIR, SIMPLE_AD_DOMAINS, ADBLOCK_MODES
from core.adblock import SimpleAdBlockInterceptor, RustAdBlockInterceptor, SmartAdBlockInterceptor

logger = logging.getLogger(__name__)

class FilterListUpdater(QObject):
    update_finished = Signal()
    update_error = Signal(str)

    def __init__(self):
        super().__init__()
        self.lists = {
            'easylist': 'https://easylist.to/easylist/easylist.txt',
            'easyprivacy': 'https://easylist.to/easylist/easyprivacy.txt',
            'ublock': 'https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/filters.txt'
        }

    def update_all(self):
        for name, url in self.lists.items():
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    path = os.path.join(FILTERS_DIR, f'{name}.txt')
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    logger.info(f"Filter list updated: {name}")
                else:
                    self.update_error.emit(f"Failed to download {name}: HTTP {response.status_code}")
            except Exception as e:
                self.update_error.emit(f"Error updating {name}: {str(e)}")
        self.update_finished.emit()

    def load_combined_rules(self):
        rules = []
        for name in self.lists.keys():
            path = os.path.join(FILTERS_DIR, f'{name}.txt')
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        rules.extend([line.strip() for line in f if line.strip() and not line.startswith('!')])
                except Exception as e:
                    logger.error(f"Error reading {name}: {e}")
        return rules


class AdBlockManager(QObject):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.updater = FilterListUpdater()
        self.combined_rules = None
        self.logger = logging.getLogger(f"{__name__}.AdBlockManager")

    def get_interceptor(self):
        if not self.api.get_adblock_enabled():
            return None
        mode = self.api.get_adblock_mode()
        self.logger.info(f"Creating interceptor for mode: {mode}")

        if mode == "simple":
            return SimpleAdBlockInterceptor(SIMPLE_AD_DOMAINS)
        else:
            rules = self.updater.load_combined_rules()
            if mode == "advanced":
                return RustAdBlockInterceptor(rules)
            else:  # smart
                return SmartAdBlockInterceptor(rules)

    def schedule_update(self, interval_ms=3600000):
        timer = QTimer()
        timer.timeout.connect(self.updater.update_all)
        timer.start(interval_ms)
        return timer
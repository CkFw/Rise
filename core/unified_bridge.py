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
Единый мост для JavaScript, объединяющий функционал закладок и клавиатуры.
"""
import json
import logging
from PySide6.QtCore import QObject, Signal, Slot

logger = logging.getLogger(__name__)


class UnifiedBridge(QObject):
    """Предоставляет JavaScript методы для работы с закладками и передачу нажатий клавиш."""

    keyPressed = Signal(int)

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api

    @Slot(str, str)
    def addBookmark(self, name, url):
        self.api.add_bookmark(name, url, 'bookmark')
        logger.info(f"Bookmark added via bridge: {name} - {url}")

    @Slot(int)
    def deleteBookmark(self, bookmark_id):
        self.api.delete_bookmark(bookmark_id)
        logger.info(f"Bookmark deleted via bridge: id={bookmark_id}")

    @Slot(result=str)
    def getBookmarks(self):
        all_bm = self.api.get_bookmarks()
        bookmarks = [bm for bm in all_bm if bm.get('type') == 'bookmark']
        return json.dumps(bookmarks)

    @Slot(int)
    def onKeyPress(self, keyCode):
        logger.info(f"UnifiedBridge.onKeyPress called with keyCode={keyCode}")
        self.keyPressed.emit(keyCode)
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
Миксин для работы с закладками через JSON-файл.
"""
import logging
from core.bookmarks_json import BookmarksJSONManager

logger = logging.getLogger(__name__)

class BookmarksJSONMixin:
    def __init__(self):
        self.bookmarks_manager = BookmarksJSONManager()

    def add_bookmark(self, name, url, bookmark_type='bookmark', parent_id=None):
        return self.bookmarks_manager.add_bookmark(name, url, bookmark_type, parent_id)

    def get_bookmarks(self):
        return self.bookmarks_manager.get_bookmarks()

    def delete_bookmark(self, bookmark_id):
        return self.bookmarks_manager.delete_bookmark(bookmark_id)

    def get_bookmarks_by_parent(self, parent_id=None):
        return self.bookmarks_manager.get_bookmarks_by_parent(parent_id)
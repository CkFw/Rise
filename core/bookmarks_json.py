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
Менеджер для хранения закладок в JSON-файле (в папке data).
"""
import json
import os
import logging
from core.config import DATA_DIR

logger = logging.getLogger(__name__)

BOOKMARKS_FILE = os.path.join(DATA_DIR, 'bookmarks.json')

class BookmarksJSONManager:
    def __init__(self):
        self.bookmarks = []
        self.load()

    def load(self):
        if os.path.exists(BOOKMARKS_FILE):
            try:
                with open(BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
                    self.bookmarks = json.load(f)
                logger.info(f"Loaded {len(self.bookmarks)} bookmarks from {BOOKMARKS_FILE}")
            except Exception as e:
                logger.error(f"Error loading bookmarks: {e}")
                self.bookmarks = []
        else:
            self.bookmarks = []

    def save(self):
        try:
            with open(BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {len(self.bookmarks)} bookmarks to {BOOKMARKS_FILE}")
        except Exception as e:
            logger.error(f"Error saving bookmarks: {e}")

    def add_bookmark(self, name, url, bookmark_type='bookmark', parent_id=None):
        new_id = max([b.get('id', 0) for b in self.bookmarks], default=0) + 1
        bookmark = {
            'id': new_id,
            'name': name,
            'url': url,
            'type': bookmark_type,
            'parent_id': parent_id,
        }
        self.bookmarks.append(bookmark)
        self.save()
        logger.info(f"Bookmark added: {name} ({bookmark_type})")
        return True

    def get_bookmarks(self):
        return self.bookmarks

    def delete_bookmark(self, bookmark_id):
        self.bookmarks = [b for b in self.bookmarks if b.get('id') != bookmark_id]
        self.save()
        logger.info(f"Bookmark deleted: id={bookmark_id}")
        return True

    def get_bookmarks_by_parent(self, parent_id=None):
        if parent_id is None:
            return [b for b in self.bookmarks if b.get('parent_id') is None]
        else:
            return [b for b in self.bookmarks if b.get('parent_id') == parent_id]
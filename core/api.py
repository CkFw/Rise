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
API для работы с данными браузера – сборка из модулей (PySide6)
"""
from core.api_module.profiles import ProfileMixin
from core.api_module.search import SearchMixin
from core.api_module.performance import PerformanceMixin
from core.api_module.webengine import WebEngineMixin
from core.api_module.i2p import I2PMixin
from core.api_module.vpn import VPNMixin
from core.api_module.history import HistoryMixin
from core.api_module.bookmarks_json import BookmarksJSONMixin
from core.api_module.passwords import PasswordsMixin
from core.api_module.downloads import DownloadsMixin
from core.api_module.dpi import DPIMixin
from core.api_module.customization import CustomizationMixin

class BrowserAPI(
    SearchMixin,
    PerformanceMixin,
    WebEngineMixin,
    I2PMixin,
    VPNMixin,
    HistoryMixin,
    BookmarksJSONMixin,
    PasswordsMixin,
    DownloadsMixin,
    DPIMixin,
    CustomizationMixin,
    ProfileMixin
):
    def __init__(self):
        HistoryMixin.__init__(self)
        BookmarksJSONMixin.__init__(self)
        self.search_engine = self.get_search_engine()
        self._create_profiles_table()
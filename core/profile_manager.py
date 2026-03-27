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
Управление профилями браузера.
"""
import json
import os
import shutil
import logging
from core.config import DATA_DIR

logger = logging.getLogger(__name__)

PROFILES_FILE = os.path.join(DATA_DIR, 'profiles.json')
DEFAULT_PROFILE_NAME = "Основной"

class ProfileManager:
    def __init__(self):
        self.profiles = []
        self.current_profile = DEFAULT_PROFILE_NAME
        self.load()

    def load(self):
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.profiles = data.get('profiles', [DEFAULT_PROFILE_NAME])
                    self.current_profile = data.get('current', DEFAULT_PROFILE_NAME)
            except Exception as e:
                logger.error(f"Error loading profiles: {e}")
                self.profiles = [DEFAULT_PROFILE_NAME]
                self.current_profile = DEFAULT_PROFILE_NAME
        else:
            self.profiles = [DEFAULT_PROFILE_NAME]
            self.current_profile = DEFAULT_PROFILE_NAME
            self.save()

    def save(self):
        try:
            with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'profiles': self.profiles,
                    'current': self.current_profile
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving profiles: {e}")

    def get_profiles(self):
        return self.profiles

    def get_current(self):
        return self.current_profile

    def set_current(self, name):
        if name in self.profiles:
            self.current_profile = name
            self.save()
            return True
        return False

    def add_profile(self, name):
        if name and name not in self.profiles:
            self.profiles.append(name)
            self.save()
            return True
        return False

    def delete_profile(self, name):
        if name == DEFAULT_PROFILE_NAME:
            return False
        if name in self.profiles and name != self.current_profile:
            self.profiles.remove(name)
            self.save()
            # Удаляем папку с данными профиля
            profile_dir = os.path.join(os.path.expanduser("~"), ".risebrowser", f"profile_{name}")
            if os.path.exists(profile_dir):
                try:
                    shutil.rmtree(profile_dir)
                except Exception as e:
                    logger.error(f"Error deleting profile folder: {e}")
            return True
        return False

    def get_profile_path(self, name):
        return os.path.join(os.path.expanduser("~"), ".risebrowser", f"profile_{name}")
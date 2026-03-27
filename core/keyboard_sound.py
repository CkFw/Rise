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

# core/keyboard_sound.py
import logging
import os
from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

logger = logging.getLogger(__name__)


class KeyboardSoundManager(QObject):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, api=None):
        if not hasattr(self, '_initialized'):
            super().__init__()
            self.api = api
            self.enabled = False
            self.sound_path = ""
            self.volume = 0.5
            self._player = None
            self._audio_output = None
            self._initialized = True
            self._load_settings()

    def _load_settings(self):
        if self.api:
            self.enabled = self.api.get_keyboard_sounds_enabled()
            self.sound_path = self.api.get_keyboard_sound_path()
            self.volume = self.api.get_keyboard_sound_volume() / 100.0
            logger.info(f"KeyboardSoundManager loaded: enabled={self.enabled}, path={self.sound_path}, volume={self.volume}")

    def update_settings(self, enabled=None, path=None, volume=None):
        if enabled is not None:
            self.enabled = enabled
        if path is not None:
            self.sound_path = path
        if volume is not None:
            self.volume = volume / 100.0
        logger.debug(f"KeyboardSoundManager updated: enabled={self.enabled}, path={self.sound_path}, volume={self.volume}")

    def play_key_sound(self):
        if not self.enabled:
            return
        if not self.sound_path:
            logger.warning("Keyboard sound enabled but no sound file set")
            return
        if not os.path.exists(self.sound_path):
            logger.error(f"Sound file not found: {self.sound_path}")
            return
        try:
            if self._player is None:
                self._player = QMediaPlayer()
                self._audio_output = QAudioOutput()
                self._player.setAudioOutput(self._audio_output)
            self._player.setSource(QUrl.fromLocalFile(self.sound_path))
            self._audio_output.setVolume(self.volume)
            self._player.play()
            logger.debug(f"Playing keyboard sound: {self.sound_path}")
        except Exception as e:
            logger.error(f"Error playing keyboard sound: {e}", exc_info=True)
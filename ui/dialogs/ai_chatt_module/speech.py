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

# speech.py
import logging
import os
import threading
import asyncio
import tempfile
import edge_tts
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl as QUrl_core

logger = logging.getLogger(__name__)

class SpeechManager(QObject):
    """Управление озвучиванием ответов AI через Edge-TTS."""
    speech_ready = Signal(str)  # сигнал с путём к сгенерированному аудиофайлу

    def __init__(self, parent=None):
        super().__init__(parent)
        self.voice_code = "ru-RU-DmitryNeural"
        self.is_speaking = False
        self.current_player = None
        self.current_generation_file = None
        self.enabled = False

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def set_voice(self, voice_code: str):
        self.voice_code = voice_code

    def stop(self):
        if self.current_player:
            self.current_player.stop()
            self.current_player = None
        if self.current_generation_file and os.path.exists(self.current_generation_file):
            try:
                os.unlink(self.current_generation_file)
                logger.debug(f"Deleted generation file {self.current_generation_file}")
            except Exception as e:
                logger.error(f"Failed to delete {self.current_generation_file}: {e}")
        self.current_generation_file = None
        self.is_speaking = False

    def speak(self, text: str):
        if not self.enabled:
            return
        if self.is_speaking:
            self.stop()

        clean_text = self._clean_text(text)
        if not clean_text:
            return

        self.is_speaking = True
        logger.info(f"Speaking: {clean_text[:50]}...")

        def run():
            async def generate():
                try:
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                        tmp_path = tmp.name
                    self.current_generation_file = tmp_path
                    communicate = edge_tts.Communicate(clean_text, self.voice_code)
                    await communicate.save(tmp_path)
                    if self.is_speaking and os.path.exists(tmp_path):
                        self.speech_ready.emit(tmp_path)
                    else:
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                except Exception as e:
                    logger.error(f"Edge-TTS error: {e}", exc_info=True)
                    self.is_speaking = False
                finally:
                    self.current_generation_file = None

            asyncio.run(generate())

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def _clean_text(self, text: str) -> str:
        from .markdown_utils import clean_markdown_for_tts
        return clean_markdown_for_tts(text)

    def play_file(self, file_path: str):
        logger.info(f"Playing audio: {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return
        if self.current_player:
            self.current_player.stop()
        self.current_player = QMediaPlayer()
        audio_output = QAudioOutput()
        self.current_player.setAudioOutput(audio_output)
        self.current_player.setSource(QUrl_core.fromLocalFile(file_path))
        self.current_player.play()

        def on_state_changed(state):
            if state == QMediaPlayer.PlaybackState.StoppedState:
                logger.debug("Playback stopped")
                self.current_player = None
                if self.is_speaking:
                    self.is_speaking = False

        self.current_player.playbackStateChanged.connect(on_state_changed)

        def delete_file():
            QTimer.singleShot(2000, lambda: self._delete_audio_file(file_path))

        QTimer.singleShot(2000, delete_file)

    def _delete_audio_file(self, file_path):
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug(f"Deleted temp speech file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}")
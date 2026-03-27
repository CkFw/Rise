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

import os
import threading
import asyncio
import tempfile
import edge_tts
from PySide6.QtCore import Signal, QObject, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

class SpeechHandler(QObject):
    speech_ready = Signal(str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.current_player = None
        self.current_generation_file = None
        self.is_speaking = False

    def speak_text(self, text, voice_code):
        if not text or self.is_speaking:
            return
        self.is_speaking = True
        self._speak_text_edge(text, voice_code)

    def stop(self):
        if self.current_player:
            self.current_player.stop()
            self.current_player = None
        if self.current_generation_file and os.path.exists(self.current_generation_file):
            try:
                os.unlink(self.current_generation_file)
            except Exception as e:
                pass
        self.current_generation_file = None
        self.is_speaking = False

    def _speak_text_edge(self, text, voice_code):
        def run():
            async def generate():
                try:
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                        tmp_path = tmp.name
                    self.current_generation_file = tmp_path
                    communicate = edge_tts.Communicate(text, voice_code)
                    await communicate.save(tmp_path)
                    if self.is_speaking and os.path.exists(tmp_path):
                        self.speech_ready.emit(tmp_path)
                    else:
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                except Exception as e:
                    pass
                finally:
                    self.current_generation_file = None
            asyncio.run(generate())
        threading.Thread(target=run, daemon=True).start()

    def play_audio(self, file_path):
        if not os.path.exists(file_path):
            return
        if self.current_player:
            self.current_player.stop()
        self.current_player = QMediaPlayer()
        audio_output = QAudioOutput()
        self.current_player.setAudioOutput(audio_output)
        self.current_player.setSource(file_path)
        self.current_player.play()

        def on_state_changed(state):
            if state == QMediaPlayer.PlaybackState.StoppedState:
                self.current_player = None
                self.is_speaking = False
                self.parent._set_send_button_stop_mode(False)

        self.current_player.playbackStateChanged.connect(on_state_changed)
        QTimer.singleShot(2000, lambda: self._delete_audio_file(file_path))

    def _delete_audio_file(self, file_path):
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except:
            pass
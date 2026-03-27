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

# bridge.py
import json
import logging
import asyncio
import threading
import tempfile
import os
import re
from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtTextToSpeech import QTextToSpeech
import edge_tts
from pydub import AudioSegment

from .api_client import AIClient

logger = logging.getLogger(__name__)

CONTEXT_LIMIT = 5

class AIChatBridge(QObject):
    reply_ready = Signal(str)
    error_occurred = Signal(str)
    speech_ready = Signal(str)

    loading_changed = Signal(bool)
    speaking_changed = Signal(bool)

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.ai_client = AIClient(api, self)
        self.ai_client.response_received.connect(self._on_response)
        self.ai_client.error_occurred.connect(self._on_error)

        self.messages = []
        self._is_loading = False
        self._is_speaking = False

        self.speech_enabled = self.api._get_setting('ai_speech_enabled', 'false') == 'true'
        self.voice_code = self.api.get_ai_voice_name() or "ru-RU-DmitryNeural"
        self.current_sound = None
        self.current_generation_file = None
        self.tts = None

    @property
    def is_loading(self):
        return self._is_loading

    @is_loading.setter
    def is_loading(self, value):
        if self._is_loading != value:
            self._is_loading = value
            self.loading_changed.emit(value)

    @property
    def is_speaking(self):
        return self._is_speaking

    @is_speaking.setter
    def is_speaking(self, value):
        if self._is_speaking != value:
            self._is_speaking = value
            self.speaking_changed.emit(value)

    def set_history(self, messages):
        self.messages = messages

    def send_message(self, text):
        if self.is_loading:
            return
        self.is_loading = True
        prompt = self._build_prompt(text)
        self.ai_client.send_message(prompt)

    def cancel_request(self):
        if self.is_loading:
            logger.info("Cancelling AI request")
            self.ai_client.cancel()
            self.is_loading = False
            self.error_occurred.emit("Отменено пользователем")
        self.stop_speech()

    def _build_prompt(self, new_message):
        context = self._get_context_prompt(new_message)
        if context:
            return f"Ты — дружелюбный AI-ассистент. Отвечай на русском языке, продолжая диалог. Вот история:\n{context}"
        else:
            return f"Отвечай на русском языке кратко и дружелюбно. {new_message}"

    def _get_context_prompt(self, new_message):
        context_msgs = []
        for msg in reversed(self.messages):
            if len(context_msgs) >= CONTEXT_LIMIT:
                break
            if 'Ошибка' in msg['content'] or msg['content'].startswith('❌'):
                continue
            context_msgs.insert(0, msg)
        context_msgs.append({'role': 'user', 'content': new_message})
        context_str = ""
        for msg in context_msgs:
            if msg['role'] == 'user':
                context_str += f"Пользователь: {msg['content']}\n"
            else:
                context_str += f"AI: {msg['content']}\n"
        return context_str

    def _on_response(self, answer):
        self.reply_ready.emit(answer)
        self.is_loading = False

    def _on_error(self, error_msg):
        self.error_occurred.emit(error_msg)
        self.is_loading = False

    # ------------------------ Озвучивание ------------------------
    def stop_speech(self):
        logger.info("Stop speech requested")
        if self.current_sound:
            self.current_sound.stop()
            self.current_sound = None
        if self.tts:
            self.tts.stop()
            self.tts = None
        if self.current_generation_file and os.path.exists(self.current_generation_file):
            try:
                os.unlink(self.current_generation_file)
                logger.debug(f"Deleted generation file {self.current_generation_file}")
            except Exception as e:
                logger.error(f"Failed to delete {self.current_generation_file}: {e}")
        self.current_generation_file = None
        self.is_speaking = False

    def _speak_text_system(self, text, lang_code, on_start=None):
        """Fallback на системный TTS"""
        if self.tts is None:
            self.tts = QTextToSpeech()
        # Попробуем выбрать голос по языку (не обязательно)
        voices = self.tts.availableVoices()
        for voice in voices:
            if lang_code in voice.name().lower():
                self.tts.setVoice(voice)
                break
        if on_start:
            on_start()
        self.tts.say(text)
        # Подключаем сигнал окончания
        def on_finished():
            self.tts = None
            self.is_speaking = False
            if on_start:
                # дополнительно убираем индикацию
                pass
        self.tts.finished.connect(on_finished)

    def speak_text(self, text):
        if not self.speech_enabled:
            logger.debug("Speech disabled")
            return
        if self.is_speaking:
            logger.debug("Already speaking, stopping")
            self.stop_speech()

        clean_text = re.sub(r'\*\*', '', text)
        clean_text = re.sub(r'\*', '', clean_text)
        if not clean_text:
            logger.debug("No text to speak")
            return

        self.is_speaking = True
        logger.info(f"Speaking: {clean_text[:50]}...")

        def run():
            async def generate():
                mp3_path = None
                wav_path = None
                try:
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
                        mp3_path = tmp_mp3.name
                    self.current_generation_file = mp3_path
                    logger.debug(f"Generating MP3 to {mp3_path}")
                    communicate = edge_tts.Communicate(clean_text, self.voice_code)
                    await communicate.save(mp3_path)

                    if not self.is_speaking:
                        if os.path.exists(mp3_path):
                            os.unlink(mp3_path)
                        return

                    logger.debug("Converting MP3 to WAV...")
                    audio = AudioSegment.from_mp3(mp3_path)
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                        wav_path = tmp_wav.name
                    audio.export(wav_path, format="wav")
                    logger.info(f"Converted to WAV, size: {os.path.getsize(wav_path)} bytes")

                    if os.path.exists(mp3_path):
                        os.unlink(mp3_path)

                    if not self.is_speaking:
                        if os.path.exists(wav_path):
                            os.unlink(wav_path)
                        return

                    self.current_generation_file = wav_path
                    self.speech_ready.emit(wav_path)

                except Exception as e:
                    logger.error(f"Error in speech generation: {e}", exc_info=True)
                    self.is_speaking = False
                    # Удаляем временные файлы
                    for path in (mp3_path, wav_path):
                        if path and os.path.exists(path):
                            try:
                                os.unlink(path)
                            except:
                                pass
                    # Fallback на системный TTS
                    if self.speech_enabled:
                        # Определяем язык из voice_code
                        lang = self.voice_code.split('-')[0] if '-' in self.voice_code else 'ru'
                        # Вызываем fallback в основном потоке, т.к. QTextToSpeech должен работать в GUI
                        from PySide6.QtCore import QTimer
                        QTimer.singleShot(0, lambda: self._speak_text_system(clean_text, lang))
                finally:
                    if wav_path and not self.is_speaking:
                        self.current_generation_file = None

            asyncio.run(generate())

        threading.Thread(target=run, daemon=True).start()

    def toggle_speech(self, enabled):
        self.speech_enabled = enabled
        self.api._save_setting('ai_speech_enabled', 'true' if enabled else 'false')
        if not enabled:
            self.stop_speech()
        logger.info(f"Speech enabled set to {enabled}")

    def play_audio(self, file_path):
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return
        if self.current_sound:
            self.current_sound.stop()
            self.current_sound = None

        self.current_sound = QSoundEffect()
        self.current_sound.setSource(QUrl.fromLocalFile(file_path))
        self.current_sound.setVolume(1.0)
        self.current_sound.play()

        logger.info(f"Playing audio via QSoundEffect: {file_path}")

        def on_finished():
            logger.debug("Sound finished")
            self.current_sound = None
            self.is_speaking = False
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    logger.debug(f"Deleted temp speech file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete {file_path}: {e}")

        self.current_sound.playingChanged.connect(
            lambda: on_finished() if not self.current_sound.isPlaying() else None
        )
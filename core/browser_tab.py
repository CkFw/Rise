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

# core/browser_tab.py
"""
Класс для отдельной вкладки браузера (PySide6) - с обработкой ошибок рендера.
Перевод, озвучивание, блокировка медиа, кастомное выделение, F5.
WebChannel создаётся только для домашней страницы (для закладок).
"""
import logging
import tempfile
import os
import threading
import asyncio
from PySide6.QtCore import QUrl, Qt, QTimer, Slot, QEvent, QPoint, QObject, Signal
from PySide6.QtWidgets import (
    QMenu, QMessageBox, QApplication, QFrame, QVBoxLayout,
    QTextEdit, QPushButton, QLabel, QProgressBar
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEnginePage, QWebEngineSettings, QWebEngineUrlRequestInterceptor
)
from PySide6.QtGui import QContextMenuEvent, QDesktopServices, QKeyEvent
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtTextToSpeech import QTextToSpeech
from PySide6.QtWebChannel import QWebChannel

import edge_tts
from core.translator import Translator

logger = logging.getLogger(__name__)

# Расширенная карта голосов Edge-TTS (поддерживает большинство языков)
VOICE_MAP = {
    'ru': 'ru-RU-DmitryNeural',
    'en': 'en-US-AriaNeural',
    'de': 'de-DE-KatjaNeural',
    'fr': 'fr-FR-DeniseNeural',
    'es': 'es-ES-ElviraNeural',
    'it': 'it-IT-ElsaNeural',
    'pt': 'pt-PT-RaquelNeural',
    'zh-CN': 'zh-CN-XiaoxiaoNeural',
    'ja': 'ja-JP-NanamiNeural',
    'ko': 'ko-KR-SunHiNeural',
    'ar': 'ar-SA-ZariyahNeural',
    'tr': 'tr-TR-EmelNeural',
    'da': 'da-DK-ChristelNeural',
    'nl': 'nl-NL-ColetteNeural',
    'fi': 'fi-FI-NooraNeural',
    'el': 'el-GR-AthinaNeural',
    'he': 'he-IL-HilaNeural',
    'hi': 'hi-IN-SwaraNeural',
    'hu': 'hu-HU-NoemiNeural',
    'id': 'id-ID-GadisNeural',
    'ms': 'ms-MY-YasminNeural',
    'no': 'nb-NO-PernilleNeural',
    'pl': 'pl-PL-ZofiaNeural',
    'ro': 'ro-RO-AlinaNeural',
    'sk': 'sk-SK-ViktoriaNeural',
    'sv': 'sv-SE-SofieNeural',
    'th': 'th-TH-PremwadeeNeural',
    'uk': 'uk-UA-UlianaNeural',
    'vi': 'vi-VN-HoaiMyNeural',
    'bg': 'bg-BG-BorislavNeural',
    'cs': 'cs-CZ-VlastaNeural',
    'hr': 'hr-HR-GabrijelaNeural',
    'lt': 'lt-LT-OnaNeural',
    'lv': 'lv-LV-EveritaNeural',
    'et': 'et-EE-AnuNeural',
    'sl': 'sl-SI-PetraNeural',
    'cy': 'cy-GB-NiaNeural',
}


class BookmarkBridge(QObject):
    """Мост для JavaScript, позволяющий сохранять и удалять закладки из HTML-страницы."""
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
        import json
        all_bm = self.api.get_bookmarks()
        bookmarks = [bm for bm in all_bm if bm.get('type') == 'bookmark']
        return json.dumps(bookmarks)


class MediaBlockInterceptor(QWebEngineUrlRequestInterceptor):
    """Перехватчик, блокирующий медиа-запросы (видео/аудио) для предотвращения крашей."""
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}.MediaBlockInterceptor")

    def interceptRequest(self, info):
        resource_type = info.resourceType()
        if resource_type in (QWebEngineUrlRequestInterceptor.ResourceType.Media,
                             QWebEngineUrlRequestInterceptor.ResourceType.Object):
            self.logger.debug(f"Blocking media request: {info.requestUrl().toString()}")
            info.block(True)


class CompositeInterceptor(QWebEngineUrlRequestInterceptor):
    """Составной перехватчик, вызывающий несколько внутренних перехватчиков."""
    def __init__(self, interceptors):
        super().__init__()
        self.interceptors = interceptors
        self.logger = logging.getLogger(f"{__name__}.CompositeInterceptor")

    def interceptRequest(self, info):
        for interceptor in self.interceptors:
            interceptor.interceptRequest(info)
            if info.shouldBlockRequest():
                return


class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, view, browser_tab, parent=None):
        super().__init__(parent)
        self.view_ref = view
        self.browser_tab = browser_tab

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        url_str = url.toString()
        logger.debug(f"acceptNavigationRequest: {url_str}, type={_type}, isMainFrame={isMainFrame}")

        download_extensions = (
            '.mp3', '.mp4', '.zip', '.rar', '.7z', '.exe', '.dmg', '.apk',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico',
            '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4a', '.aac',
            '.ogg', '.wav', '.flac', '.csv', '.txt', '.rtf', '.psd', '.iso'
        )

        lower_url = url_str.lower()
        if any(lower_url.endswith(ext) for ext in download_extensions):
            logger.info(f"Обнаружена загрузка файла, запускаем download для {url_str}")
            self.download(url)
            return False

        return super().acceptNavigationRequest(url, _type, isMainFrame)

    def createWindow(self, _type):
        logger.debug(f"createWindow called with type: {_type}")
        main_window = self.browser_tab.main_window
        if main_window:
            new_tab = main_window.add_browser_tab(empty=True)
            if new_tab:
                logger.debug("New tab created, returning its page")
                return new_tab.page()
        return None

    def javaScriptConsoleMessage(self, level, message, line, source):
        if level == QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            logger.error(f"JS Error: {message} at {source}:{line}")
        else:
            logger.debug(f"JS: {message} at {source}:{line}")


class BrowserTab(QWebEngineView):
    speech_ready = Signal(str)

    def __init__(self, api, main_window, adblock_manager, is_home=False, parent=None):
        super().__init__(parent)
        self.api = api
        self.main_window = main_window
        self.adblock_manager = adblock_manager
        self.is_home = is_home
        self._discarded_url = None
        self._tts = None
        self._player = None
        self._audio_output = None
        self.bridge = None

        self._setup_page()
        self._setup_settings()
        self._setup_interceptor()
        self._connect_signals()
        self.speech_ready.connect(self._on_speech_ready)

        # Для домашней страницы создаём WebChannel с BookmarkBridge
        if self.is_home:
            self._setup_web_channel()

        # Подключаем внедрение стиля выделения после загрузки страницы
        self.loadFinished.connect(self.inject_selection_style)

        # Подключаем оптимизацию видео (удаление скрытых видео из DOM)
        self.loadFinished.connect(self._apply_video_optimizations)

        # Подключаем CSS content-visibility
        self.loadFinished.connect(self._apply_content_visibility)

    def _setup_web_channel(self):
        self.channel = QWebChannel(self.page())
        self.bridge = BookmarkBridge(self.api, self)
        self.channel.registerObject("bridge", self.bridge)
        self.page().setWebChannel(self.channel)
        logger.info("WebChannel with BookmarkBridge initialized")

    def _setup_page(self):
        custom_page = CustomWebEnginePage(self, self, self)
        self.setPage(custom_page)

    def _setup_settings(self):
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, self.api.get_plugins_enabled())
        settings.setAttribute(QWebEngineSettings.WebAttribute.HyperlinkAuditingEnabled, self.api.get_hyperlink_auditing_enabled())
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, self.api.get_scroll_animator_enabled())
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        try:
            settings.setAttribute(QWebEngineSettings.WebAttribute.StorageAccessApiEnabled, True)
        except AttributeError:
            pass
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)

        try:
            settings.setAttribute(QWebEngineSettings.WebAttribute.PictureInPictureEnabled, True)
        except AttributeError:
            pass

        profile = self.page().profile()
        # Размер кэша HTTP из настроек
        cache_mb = self.api.get_cache_size_mb()
        profile.setHttpCacheMaximumSize(cache_mb * 1024 * 1024)

    def _setup_interceptor(self):
        interceptors = []
        media_blocker = MediaBlockInterceptor()
        interceptors.append(media_blocker)

        try:
            adblock_interceptor = self.adblock_manager.get_interceptor()
            if adblock_interceptor:
                interceptors.append(adblock_interceptor)
                logger.info("AdBlock interceptor added")
        except Exception as e:
            logger.error(f"Error getting adblock interceptor: {e}")

        composite = CompositeInterceptor(interceptors)
        self.page().profile().setUrlRequestInterceptor(composite)
        logger.info(f"Composite interceptor set with {len(interceptors)} handlers")

    def _connect_signals(self):
        self.titleChanged.connect(self._on_title_changed)
        self.urlChanged.connect(self._on_url_changed)
        self.page().fullScreenRequested.connect(self._on_fullscreen_requested)
        self.page().renderProcessTerminated.connect(self._on_render_process_terminated)
        self.page().recommendedStateChanged.connect(self._on_recommended_state_changed)

    def _on_title_changed(self, title):
        pass

    def _on_url_changed(self, url):
        pass

    def _on_fullscreen_requested(self, request):
        logger.debug(f"BrowserTab: fullscreen request received, toggleOn={request.toggleOn()}")
        try:
            request.accept()
            if self.main_window and hasattr(self.main_window, '_handle_fullscreen_request'):
                self.main_window._handle_fullscreen_request(request.toggleOn())
        except Exception as e:
            logger.error(f"BrowserTab: error in fullscreen handler: {e}")

    def _on_render_process_terminated(self, status, exit_code):
        logger.error(f"Render process terminated: status={status}, exit_code={exit_code}")
        self.triggerPageAction(QWebEnginePage.WebAction.Reload)

    def _on_recommended_state_changed(self, state):
        current = self.page().lifecycleState()
        if current != state:
            logger.debug(f"Changing lifecycle state from {current} to {state}")
            self.page().setLifecycleState(state)

    # ----- Кастомное выделение -----
    def inject_selection_style(self):
        if not self.api.get_selection_custom_enabled():
            return
        color = self.api.get_selection_color1()
        css = f"::selection {{ background: {color}; color: #ffffff; }}"
        self.page().runJavaScript(f"""
            (function() {{
                var style = document.getElementById('rise-selection-style');
                if (style) style.remove();
                style = document.createElement('style');
                style.id = 'rise-selection-style';
                style.textContent = `{css}`;
                document.head.appendChild(style);
            }})();
        """)

    # ----- Видеооптимизация: удаление скрытых видео -----
    def _apply_video_optimizations(self):
        """Внедряет скрипт для удаления скрытых видео из DOM (если включено в настройках)."""
        if not self.api.get_video_optimizations_enabled():
            return

        js = """
        (function() {
            // Удаление скрытых видео из DOM (раз в 30 секунд)
            setInterval(() => {
                document.querySelectorAll('video').forEach(v => {
                    const rect = v.getBoundingClientRect();
                    // Если видео не видно (ширина или высота 0) и оно приостановлено
                    if ((rect.width === 0 || rect.height === 0) && v.paused && v.parentElement) {
                        v.remove();
                    }
                });
            }, 30000);
        })();
        """
        self.page().runJavaScript(js)

    # ----- CSS content-visibility -----
    def _apply_content_visibility(self):
        """Внедряет CSS-правило content-visibility: auto для всех элементов (если включено)."""
        if not self.api.get_content_visibility_enabled():
            return

        js = """
        (function() {
            // Внедряем CSS-правило для всех элементов
            const style = document.createElement('style');
            style.textContent = `
                * {
                    content-visibility: auto;
                    contain-intrinsic-size: 0 500px;
                }
                /* Исключаем критически важные элементы, чтобы не нарушать работу сайтов */
                body, html, head, script, style, link {
                    content-visibility: visible !important;
                }
            `;
            document.head.appendChild(style);
        })();
        """
        self.page().runJavaScript(js)

    # ----- Обработка клавиш (F5 обрабатываем напрямую) -----
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_F5:
            if self.main_window and hasattr(self.main_window, 'refresh_page'):
                self.main_window.refresh_page()
            event.accept()
            return
        super().keyPressEvent(event)

    # ----- Контекстное меню -----
    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = self.createStandardContextMenu()

        external_page_action = menu.addAction("🌐 Открыть страницу во внешнем браузере")
        external_page_action.triggered.connect(self._open_page_externally)
        menu.addSeparator()

        selected_text = self.selectedText().strip()
        if self.api.get_translate_enabled() and selected_text:
            menu.addSeparator()
            translate_menu = QMenu("Перевести и скопировать в буфер", menu)
            for lang_name in Translator.get_languages():
                act = translate_menu.addAction(lang_name)
                act.setData(lang_name)
            translate_menu.triggered.connect(self._on_translate_action)
            menu.addMenu(translate_menu)
            speak_action = menu.addAction("🔊 Озвучить выделенный текст")
            speak_action.triggered.connect(self._speak_selected)

        menu.exec_(event.globalPos())

    # ----- Внешний просмотр -----
    def _open_page_externally(self):
        url = self.url().toString()
        if url:
            logger.info(f"Opening page externally: {url}")
            QDesktopServices.openUrl(QUrl(url))

    # ----- Озвучивание выделенного текста -----
    def _speak_selected(self):
        text = self.selectedText().strip()
        if not text:
            return
        detected_lang = Translator.detect(text)
        if not detected_lang:
            detected_lang = 'en'
        logger.info(f"Detected language: {detected_lang} for selected text")
        self._speak_text(text, detected_lang)

    def _speak_text_system(self, text, lang_code, on_start=None):
        if self._tts is None:
            self._tts = QTextToSpeech()
        available_voices = self._tts.availableVoices()
        if available_voices:
            found = False
            for voice in available_voices:
                if lang_code in voice.name().lower():
                    self._tts.setVoice(voice)
                    found = True
                    break
            if not found:
                logger.warning(f"No system voice for language {lang_code}, using default")
        if on_start:
            on_start()
        self._tts.say(text)

    def _play_sound_file(self, file_path):
        logger.info(f"Playing sound file: {file_path}")
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)
        self._player.setSource(QUrl.fromLocalFile(file_path))
        self._player.play()

        def delete_file():
            if self._player and self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                QTimer.singleShot(1000, delete_file)
                return
            self._player = None
            self._audio_output = None
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                    logger.debug(f"Deleted temp file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete temp file {file_path}: {e}")

        QTimer.singleShot(5000, delete_file)

    def _on_speech_ready(self, file_path):
        if os.path.exists(file_path):
            logger.info(f"Speech file ready: {file_path} ({os.path.getsize(file_path)} bytes)")
            self._play_sound_file(file_path)
        else:
            logger.error(f"Speech file not found: {file_path}")

    def _speak_text_edge(self, text, voice_code, on_start=None):
        logger.info(f"Starting Edge-TTS for text: {text[:30]}... with voice {voice_code}")

        if on_start:
            def on_ready_once(file_path):
                on_start()
                self.speech_ready.disconnect(on_ready_once)

            self.speech_ready.connect(on_ready_once)

        def run_task():
            async def generate():
                try:
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                        tmp_path = tmp_file.name
                    logger.debug(f"Temp file: {tmp_path}")
                    communicate = edge_tts.Communicate(text, voice_code)
                    await communicate.save(tmp_path)
                    if os.path.exists(tmp_path):
                        logger.info(f"Edge-TTS file created: {tmp_path} ({os.path.getsize(tmp_path)} bytes)")
                        self.speech_ready.emit(tmp_path)
                    else:
                        logger.error("Edge-TTS file not created, falling back to system TTS")
                        lang = voice_code.split('-')[0] if '-' in voice_code else 'ru'
                        self._speak_text_system(text, lang, on_start)
                except Exception as e:
                    logger.error(f"Edge-TTS error: {e}", exc_info=True)
                    lang = voice_code.split('-')[0] if '-' in voice_code else 'ru'
                    self._speak_text_system(text, lang, on_start)

            asyncio.run(generate())

        thread = threading.Thread(target=run_task)
        thread.daemon = True
        thread.start()

    def _speak_text(self, text, lang_code, on_start=None):
        logger.info(f"_speak_text called: lang_code={lang_code}, text='{text[:30]}...'")
        voice_code = VOICE_MAP.get(lang_code)
        if voice_code:
            logger.info(f"Resolved voice_code: {voice_code}")
            self._speak_text_edge(text, voice_code, on_start)
        else:
            logger.warning(f"No Edge-TTS voice for language {lang_code}, falling back to system TTS")
            self._speak_text_system(text, lang_code, on_start)

    # ----- Перевод -----
    def _on_translate_action(self, action):
        lang_name = action.data()
        if not lang_name:
            return
        selected_text = self.selectedText().strip()
        if not selected_text:
            return
        target_code = Translator.get_lang_code(lang_name)
        translated = Translator.translate(selected_text, target_code)
        if translated.startswith("Ошибка"):
            QMessageBox.critical(self, "Ошибка перевода", translated)
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(translated)

        popup = QFrame(self.window())
        popup.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        popup.setFrameStyle(QFrame.Box)
        popup.setLineWidth(1)
        popup.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            }
            QLabel {
                color: #00a8ff;
                font-size: 13px;
                font-weight: bold;
                padding: 5px 10px 0 10px;
                background: transparent;
                border: none;
                text-shadow: 0 1px 2px rgba(0,0,0,0.5);
            }
            QTextEdit {
                background-color: #252525;
                color: #fff;
                border: 1px solid #444;
                border-radius: 8px;
                font-size: 14px;
                padding: 10px;
                margin: 5px 10px 10px 10px;
                selection-background-color: #00a8ff;
            }
            QTextEdit:focus {
                border-color: #00a8ff;
            }
            QPushButton {
                background-color: #00a8ff;
                color: #fff;
                border: none;
                padding: 8px 12px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
                margin: 2px 5px;
            }
            QPushButton:hover {
                background-color: #0097e6;
            }
            QPushButton.speak {
                background-color: #2a2a2a;
                color: #00a8ff;
                border: 1px solid #444;
            }
            QPushButton.speak:hover {
                background-color: #333;
            }
            QProgressBar {
                border: none;
                background-color: #333;
                border-radius: 2px;
                height: 4px;
                margin: 5px 10px;
            }
            QProgressBar::chunk {
                background-color: #00a8ff;
                border-radius: 2px;
            }
        """)

        popup.resize(600, 550)
        layout = QVBoxLayout(popup)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        orig_label = QLabel("Оригинал:")
        layout.addWidget(orig_label)
        orig_text = QTextEdit()
        orig_text.setPlainText(selected_text)
        orig_text.setReadOnly(True)
        layout.addWidget(orig_text)

        trans_label = QLabel("Перевод:")
        layout.addWidget(trans_label)
        trans_text = QTextEdit()
        trans_text.setPlainText(translated)
        trans_text.setReadOnly(True)
        layout.addWidget(trans_text)

        progress = QProgressBar()
        progress.setRange(0, 0)
        progress.setVisible(False)
        layout.addWidget(progress)

        speak_trans_btn = QPushButton("🔊 Озвучить перевод")
        speak_trans_btn.setProperty("class", "speak")
        layout.addWidget(speak_trans_btn)

        def hide_progress():
            progress.setVisible(False)
            speak_trans_btn.setEnabled(True)

        def on_speak_clicked():
            progress.setVisible(True)
            speak_trans_btn.setEnabled(False)
            self._speak_text(translated, target_code, on_start=hide_progress)

        speak_trans_btn.clicked.connect(on_speak_clicked)

        parent_rect = self.window().geometry()
        popup.move(parent_rect.center() - popup.rect().center())
        popup.show()

    # ----- Основные методы навигации -----
    def load_url(self, url):
        logger.info(f"BrowserTab.load_url: {url}")
        try:
            if isinstance(url, str):
                qurl = QUrl(url)
            else:
                qurl = url
            self.load(qurl)
        except Exception as e:
            logger.error(f"Exception in load_url: {e}", exc_info=True)

    def go_back(self):
        if self.page().history().canGoBack():
            self.back()

    def go_forward(self):
        if self.page().history().canGoForward():
            self.forward()

    def reload_page(self):
        self.reload()
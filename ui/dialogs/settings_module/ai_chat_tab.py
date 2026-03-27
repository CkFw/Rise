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

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, QLineEdit, QPushButton
from PySide6.QtCore import Qt
from core.config import DEFAULT_AI_API_KEY


def setup_ai_chat_tab(self):
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setSpacing(15)

    layout.addWidget(self._create_info_label(
        "🤖 Встроенный AI‑чат позволяет общаться с нейросетью прямо в браузере.\n"
        "Используется бесплатный API, не требующий регистрации и ключей.\n\n"
        "Вы можете включить озвучивание ответов и выбрать голос.\n"
        "Также вы можете указать свой API-ключ для использования других провайдеров."
    ))

    self.ai_chat_check = QCheckBox("Включить AI‑чат")
    self.ai_chat_check.setChecked(self.api.get_ai_chat_enabled())
    layout.addWidget(self.ai_chat_check)

    # Выбор языка для озвучивания
    lang_layout = QHBoxLayout()
    lang_layout.addWidget(QLabel("Язык озвучивания:"))
    self.ai_lang_combo = QComboBox()

    self.voice_map = {
        "Русский": {
            "code": "ru",
            "voices": {
                "Дмитрий (мужской)": "ru-RU-DmitryNeural",
                "Светлана (женский)": "ru-RU-SvetlanaNeural",
                "Дарья (женский)": "ru-RU-DariyaNeural"
            }
        },
        "Английский (США)": {
            "code": "en-US",
            "voices": {
                "Aria (женский)": "en-US-AriaNeural",
                "Guy (мужской)": "en-US-GuyNeural",
                "Jenny (женский)": "en-US-JennyNeural"
            }
        },
        "Английский (Великобритания)": {
            "code": "en-GB",
            "voices": {
                "Sonia (женский)": "en-GB-SoniaNeural",
                "Ryan (мужской)": "en-GB-RyanNeural"
            }
        },
        "Немецкий": {
            "code": "de",
            "voices": {
                "Katja (женский)": "de-DE-KatjaNeural",
                "Conrad (мужской)": "de-DE-ConradNeural"
            }
        },
        "Французский": {
            "code": "fr",
            "voices": {
                "Denise (женский)": "fr-FR-DeniseNeural",
                "Henri (мужской)": "fr-FR-HenriNeural"
            }
        },
        "Испанский": {
            "code": "es",
            "voices": {
                "Elvira (женский)": "es-ES-ElviraNeural",
                "Alvaro (мужской)": "es-ES-AlvaroNeural"
            }
        },
        "Итальянский": {
            "code": "it",
            "voices": {
                "Elsa (женский)": "it-IT-ElsaNeural",
                "Isabella (женский)": "it-IT-IsabellaNeural"
            }
        },
        "Китайский": {
            "code": "zh-CN",
            "voices": {
                "Xiaoxiao (женский)": "zh-CN-XiaoxiaoNeural",
                "Yunyang (мужской)": "zh-CN-YunyangNeural"
            }
        },
        "Японский": {
            "code": "ja",
            "voices": {
                "Nanami (женский)": "ja-JP-NanamiNeural",
                "Keita (мужской)": "ja-JP-KeitaNeural"
            }
        },
        "Корейский": {
            "code": "ko",
            "voices": {
                "SunHi (женский)": "ko-KR-SunHiNeural",
                "InJoon (мужской)": "ko-KR-InJoonNeural"
            }
        }
    }

    for lang_name in self.voice_map.keys():
        self.ai_lang_combo.addItem(lang_name)

    current_lang = self.api.get_ai_voice_language()
    current_lang_display = next(
        (name for name, data in self.voice_map.items() if data["code"] == current_lang),
        "Русский"
    )
    self.ai_lang_combo.setCurrentText(current_lang_display)
    self.ai_lang_combo.currentTextChanged.connect(self._update_ai_voices)

    lang_layout.addWidget(self.ai_lang_combo)
    lang_layout.addStretch()
    layout.addLayout(lang_layout)

    # Выбор голоса
    voice_layout = QHBoxLayout()
    voice_layout.addWidget(QLabel("Голос:"))
    self.ai_voice_combo = QComboBox()
    self._update_ai_voices(self.ai_lang_combo.currentText())
    saved_voice = self.api.get_ai_voice_name()
    index = self.ai_voice_combo.findData(saved_voice)
    if index >= 0:
        self.ai_voice_combo.setCurrentIndex(index)
    voice_layout.addWidget(self.ai_voice_combo)
    voice_layout.addStretch()
    layout.addLayout(voice_layout)

    # Выбор провайдера
    provider_layout = QHBoxLayout()
    provider_layout.addWidget(QLabel("Провайдер:"))
    self.ai_provider_combo = QComboBox()
    self.ai_provider_combo.addItems(["Бесплатный GPT (Free GPT API)"])
    self.ai_provider_combo.setCurrentText(
        {"free_gpt": "Бесплатный GPT (Free GPT API)"}.get(
            self.api.get_ai_provider(), "Бесплатный GPT (Free GPT API)"
        )
    )
    provider_layout.addWidget(self.ai_provider_combo)
    provider_layout.addStretch()
    layout.addLayout(provider_layout)

    # Поле API ключа (с дефолтным значением)
    key_layout = QHBoxLayout()
    key_layout.addWidget(QLabel("API ключ (для платных провайдеров):"))
    self.ai_api_key_edit = QLineEdit()
    current_key = self.api.get_ai_api_key()
    if not current_key:
        self.api.set_ai_api_key(DEFAULT_AI_API_KEY)
        current_key = DEFAULT_AI_API_KEY
    self.ai_api_key_edit.setText(current_key)
    self.ai_api_key_edit.setPlaceholderText("Не требуется для выбранного провайдера")
    key_layout.addWidget(self.ai_api_key_edit)
    layout.addLayout(key_layout)

    # Кнопка сохранения
    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    save_btn = QPushButton("💾 Сохранить настройки AI")
    save_btn.setProperty("class", "save-btn")
    save_btn.clicked.connect(self.save_ai_settings)
    btn_layout.addWidget(save_btn)
    btn_layout.addStretch()
    layout.addLayout(btn_layout)

    layout.addStretch()
    return tab
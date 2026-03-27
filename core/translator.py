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
Модуль для перевода текста через онлайн-сервисы (Google Translate) и определения языка.
Использует deep_translator для перевода и langdetect для определения языка.
"""
import logging
from deep_translator import GoogleTranslator

# langdetect для определения языка
try:
    from langdetect import detect as lang_detect, DetectorFactory
    # Фиксируем seed для воспроизводимости результатов
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.warning("langdetect not installed. Language detection will fallback to 'en'.")

logger = logging.getLogger(__name__)

# Словарь языков: отображаемое имя -> код для Google Translate
LANGUAGES = {
    "Русский": "ru",
    "Английский": "en",
    "Немецкий": "de",
    "Французский": "fr",
    "Испанский": "es",
    "Итальянский": "it",
    "Португальский": "pt",
    "Китайский (упрощ.)": "zh-CN",
    "Японский": "ja",
    "Корейский": "ko",
    "Арабский": "ar",
    "Турецкий": "tr"
}

class Translator:
    @staticmethod
    def translate(text, target_lang_code, source='auto'):
        """
        Переводит текст на указанный язык.
        :param text: исходный текст
        :param target_lang_code: код целевого языка (например, 'en', 'ru')
        :param source: исходный язык ('auto' для автоопределения)
        :return: переведённый текст или сообщение об ошибке
        """
        try:
            translator = GoogleTranslator(source=source, target=target_lang_code)
            result = translator.translate(text)
            logger.debug(f"Translated '{text[:30]}...' to {target_lang_code}")
            return result
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return f"Ошибка перевода: {str(e)}"

    @staticmethod
    def detect(text):
        """
        Определяет язык текста с помощью langdetect.
        :param text: текст для анализа
        :return: код языка (например, 'ru', 'en') или 'en' в случае ошибки
        """
        if not LANGDETECT_AVAILABLE:
            logger.warning("langdetect not available, falling back to 'en'")
            return 'en'
        try:
            detected = lang_detect(text)
            logger.debug(f"Detected language: {detected} for text '{text[:30]}...'")
            # Приводим к формату, который есть в VOICE_MAP
            if detected == 'zh-cn' or detected == 'zh-tw':
                return 'zh-CN'
            return detected
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return 'en'

    @staticmethod
    def get_languages():
        return list(LANGUAGES.keys())

    @staticmethod
    def get_lang_code(lang_name):
        return LANGUAGES.get(lang_name, 'en')
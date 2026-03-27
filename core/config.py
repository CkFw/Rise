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
Конфигурационный файл браузера Rise Browser.
Содержит пути к директориям, настройки по умолчанию, списки поисковых систем и стили.
"""

import os

# === Базовые пути ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'rise.db')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
ICONS_DIR = os.path.join(BASE_DIR, 'icons')
CONFIG_PATH = os.path.join(DATA_DIR, 'config.ini')
FILTERS_DIR = os.path.join(DATA_DIR, 'filters')

# Создаём необходимые директории
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ICONS_DIR, exist_ok=True)
os.makedirs(FILTERS_DIR, exist_ok=True)

# === Общие настройки окна ===
DEFAULT_SEARCH_ENGINE = "Google"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Rise Browser"

# === Настройки производительности и оптимизации ===
DEFAULT_PLUGINS_ENABLED = False
DEFAULT_HYPERLINK_AUDITING_ENABLED = False
DEFAULT_SCROLL_ANIMATOR_ENABLED = False
DEFAULT_PRINT_BACKGROUNDS_ENABLED = False
DEFAULT_PDF_SEPARATE_ENABLED = False
DEFAULT_BACKGROUND_MEDIA_ENABLED = True
DEFAULT_AGGRESSIVE_DISCARD = False
DEFAULT_CLEAR_CACHE_ON_EXIT = False
DEFAULT_RESTORE_SESSION = True  # Восстанавливать последнюю сессию при запуске
DEFAULT_HTTP_CACHE_SIZE_MB = 100  # Размер кэша HTTP по умолчанию (МБ)
DEFAULT_VIDEO_OPTIMIZATIONS_ENABLED = True  # Удалять скрытые видео из DOM
DEFAULT_CONTENT_VISIBILITY_ENABLED = False  # Использовать content-visibility: auto (экспериментально)

# === Настройки I2P ===
DEFAULT_I2P_ENABLED = False
DEFAULT_I2P_PORT = 4447  # SOCKS порт по умолчанию
DEFAULT_I2P_TYPE = "socks5"  # socks5 или http
DEFAULT_I2PD_PATH = ""  # путь к i2pd.exe, может быть пустым

# === Настройки блокировщика рекламы ===
DEFAULT_ADBLOCK_ENABLED = True
DEFAULT_ADBLOCK_MODE = "simple"  # simple, advanced, smart
ADBLOCK_MODES = ["simple", "advanced", "smart"]
ADBLOCK_MODE_NAMES = ["Простой", "Расширенный", "Интеллектуальный"]

# === Поисковые системы для обычного режима ===
SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q=",
    "Yandex": "https://yandex.ru/search/?text=",
    "Bing": "https://www.bing.com/search?q=",
    "DuckDuckGo": "https://duckduckgo.com/?q=",
    "Mail.ru": "https://go.mail.ru/search?q=",
    "YouTube": "https://www.youtube.com/results?search_query=",
    "Wikipedia": "https://ru.wikipedia.org/w/index.php?search=",
}

# === Поисковые системы для режима I2P ===
I2P_SEARCH_ENGINES = {
    "Legwork (I2P)": "http://legwork.i2p/?q=",
    "Ransack (I2P)": "http://ransack.i2p/search?q=",
    "Search (I2P)": "http://search.i2p/search?q=",
    "Ninja (I2P)": "http://ninja.i2p/?q=",
    "Identiguy (I2P)": "http://identiguy.i2p/",
    "Orion (I2P)": "http://orion.i2p/"
}

# === Базовые рекламные домены для простого режима ===
SIMPLE_AD_DOMAINS = [
    'doubleclick.net', 'adservice.google.com', 'googlesyndication.com',
    'ads.yahoo.com', 'adnxs.com', 'youtube.com/pagead',
    'an.yandex.ru', 'yandex.ru/ads', 'yandexadexchange.net',
    'adfox.ru', 'mytarget.ru', 'googleadservices.com'
]

# === Настройки VPN (общие) ===
DEFAULT_VPN_ENABLED = False
DEFAULT_VPN_PROTOCOL = "socks5"
DEFAULT_VPN_HOST = ""
DEFAULT_VPN_PORT = 1080
DEFAULT_VPN_USERNAME = ""
DEFAULT_VPN_PASSWORD = ""

# === Shadowsocks ===
DEFAULT_SS_METHOD = "aes-256-gcm"
DEFAULT_SS_PASSWORD = ""
DEFAULT_SS_LOCAL_PORT = 1081

# === Trojan ===
DEFAULT_TROJAN_PASSWORD = ""
DEFAULT_TROJAN_SNI = ""
DEFAULT_TROJAN_LOCAL_PORT = 1082

# === VMess ===
DEFAULT_VMESS_UUID = ""
DEFAULT_VMESS_ALTERID = 0
DEFAULT_VMESS_SECURITY = "auto"
DEFAULT_VMESS_LOCAL_PORT = 1083

# === VLESS ===
DEFAULT_VLESS_UUID = ""  # используем тот же, что и VMess
DEFAULT_VLESS_LOCAL_PORT = 1084

# === Tuic ===
DEFAULT_TUIC_TOKEN = ""
DEFAULT_TUIC_LOCAL_PORT = 1085

# === Hysteria ===
DEFAULT_HYSTERIA_AUTH = ""
DEFAULT_HYSTERIA_LOCAL_PORT = 1086

# === Juicity ===
DEFAULT_JUICITY_UUID = ""
DEFAULT_JUICITY_LOCAL_PORT = 1087

# === Настройки WebEngine (можно отключать для экономии памяти) ===
DEFAULT_JAVASCRIPT_CAN_OPEN_WINDOWS = True
DEFAULT_LOCAL_STORAGE_ENABLED = True
DEFAULT_ERROR_PAGE_ENABLED = False
DEFAULT_PDF_VIEWER_ENABLED = True
DEFAULT_PREDICTIVE_NETWORK_ACTIONS = False
DEFAULT_FULLSCREEN_SUPPORT_ENABLED = True

# === Настройка перевода выделенного текста ===
DEFAULT_TRANSLATE_ENABLED = False

# === Настройки AI чата ===
DEFAULT_AI_API_KEY = "sq-lRdAfPqeFRKKn18lYQgBmafeExBrD8Pr"
DEFAULT_AI_CHAT_ENABLED = False
DEFAULT_AI_PROVIDER = "free_gpt"
DEFAULT_AI_VOICE_LANGUAGE = "ru"
DEFAULT_AI_VOICE_NAME = "ru-RU-DmitryNeural"

# === Настройки предложения мобильной версии (устарело, оставлено для совместимости) ===
DEFAULT_MOBILE_SUGGESTION_ENABLED = True
DEFAULT_MOBILE_SUGGESTION_DOMAINS = [
    'google.com',
    'accounts.google.com',
    'mail.google.com',
    'drive.google.com',
    'docs.google.com',
    'youtube.com',
    'gmail.com'
]

# === Пользовательский User-Agent (по умолчанию мобильный) ===
DEFAULT_USER_AGENT = "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"

# === Стили для главного окна и диалогов ===
STYLES = {
    'main_window': """
QMainWindow {
    background-color: #0f0f0f;
    border: 1px solid #333;
}
QStackedWidget {
    background-color: #0f0f0f;
}
""",
    'dialog': """
QDialog { background-color: #1a1a1a; }
QLabel { color: #fff; font-size: 16px; font-weight: bold; }
QPushButton {
    background-color: #00a8ff;
    color: #fff;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-weight: bold;
}
QPushButton:hover { background-color: #0097e6; }
"""
}
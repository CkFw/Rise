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
Rise Browser - Современный браузер на PySide6 (Qt6)
Добавлена поддержка нескольких профилей.
"""
import sys
import os
import logging
import traceback
import configparser
import ctypes
import subprocess
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QIcon
from PySide6.QtWebEngineCore import QWebEngineProfile

from core.database import init_db
from core.config import DATA_DIR
from core.profile_manager import ProfileManager
from ui.main_window import BrowserWindow

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', encoding='utf-8')

def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    traceback.print_exception(exc_type, exc_value, exc_traceback)

sys.excepthook = global_exception_handler

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def add_to_defender_exclusion(folder_path):
    """
    Добавляет папку в исключения Windows Defender.
    Требует прав администратора. Возвращает True, если успешно.
    """
    if sys.platform != 'win32':
        return False
    if not os.path.exists(folder_path):
        logging.warning(f"Folder not found: {folder_path}")
        return False
    try:
        # Проверяем, запущен ли с правами администратора
        if ctypes.windll.shell32.IsUserAnAdmin():
            cmd = f'powershell -Command "Add-MpPreference -ExclusionPath \'{folder_path}\'"'
            result = subprocess.run(cmd, shell=True, capture_output=True)
            if result.returncode == 0:
                logging.info(f"Added {folder_path} to Windows Defender exclusions.")
                return True
            else:
                logging.error(f"Failed to add exclusion: {result.stderr.decode()}")
                return False
        else:
            # Запрашиваем повышение прав
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            return False
    except Exception as e:
        logging.error(f"Exception while adding exclusion: {e}")
        return False

def add_optimization_flags():
    from core.api import BrowserAPI
    temp_api = BrowserAPI()
    flags = []

    config_path = os.path.join(DATA_DIR, 'config.ini')
    config = configparser.ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path)
        if config.getboolean('Performance', 'background_media_enabled', fallback=True):
            flags.extend([
                '--disable-background-media-suspend',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows'
            ])
            logging.info("Background media playback enabled.")
    else:
        config['Performance'] = {
            'vulkan_enabled': 'false',
            'background_media_enabled': 'true',
            'aggressive_discard': 'false',
            'clear_cache_on_exit': 'false'
        }
        with open(config_path, 'w') as f:
            config.write(f)

    # Только проверенные флаги
    safe_flags = [
        '--ignore-gpu-blocklist',
        '--enable-software-rasterizer',
        '--enable-lazy-image-loading',
        '--enable-lazy-frame-loading',
        '--enable-async-dns',
        '--enable-parallel-downloading',
        '--enable-back-forward-cache',
        '--enable-fast-unload',
        '--smooth-scrolling',
    ]
    for flag in safe_flags:
        if temp_api.get_chromium_flag(flag, True):
            flags.append(flag)

    flags.extend([
        '--enable-features=CompressionDictionaryTransportBackend',
        '--enable-features=CompressionDictionaryTransport',
        '--enable-features=CompressionDictionaryTransportV3',
    ])

    if temp_api.get_doh_enabled():
        provider = temp_api.get_doh_provider()
        if provider == "google":
            flags.append('--enable-features="dns-over-https<DoHTrial" --force-fieldtrials="DoHTrial/Group1" --force-fieldtrial-params="DoHTrial.Group1:server/https%3A%2F%2Fdns.google%2Fdns-query/method/POST"')
        elif provider == "cloudflare":
            flags.append('--enable-features="dns-over-https<DoHTrial" --force-fieldtrials="DoHTrial/Group1" --force-fieldtrial-params="DoHTrial.Group1:server/https%3A%2F%2Fcloudflare-dns.com%2Fdns-query/method/POST"')
        elif provider == "quad9":
            flags.append('--enable-features="dns-over-https<DoHTrial" --force-fieldtrials="DoHTrial/Group1" --force-fieldtrial-params="DoHTrial.Group1:server/https%3A%2F%2Fdns.quad9.net%2Fdns-query/method/POST"')
    else:
        flags.append('--disable-features="dns-over-https"')

    if temp_api.get_quic_enabled():
        flags.append('--enable-quic')
    else:
        flags.append('--disable-quic')

    if not temp_api.get_webrtc_enabled():
        flags.append('--disable-features=WebRtc')

    if temp_api.get_ipv6_enabled():
        flags.append('--enable-ipv6')
    else:
        flags.append('--disable-ipv6')

    tcp_size = temp_api.get_tcp_buffer_size()
    if tcp_size > 0:
        flags.append(f'--tcp-receive-buffer-size={tcp_size * 1024}')

    # Устанавливаем флаги через переменную окружения
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = ' '.join(flags)
    logging.info(f"QtWebEngine flags set")

def setup_profile():
    profile_mgr = ProfileManager()
    current_profile = profile_mgr.get_current()
    profile_dir = profile_mgr.get_profile_path(current_profile)
    os.makedirs(profile_dir, exist_ok=True)
    os.makedirs(os.path.join(profile_dir, "Local Storage"), exist_ok=True)
    os.makedirs(os.path.join(profile_dir, "Cookies"), exist_ok=True)
    abs_profile_dir = os.path.abspath(profile_dir)

    os.environ['QTWEBENGINE_USER_DATA_DIR'] = abs_profile_dir

    profile = QWebEngineProfile.defaultProfile()
    profile.setPersistentStoragePath(abs_profile_dir)
    profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)

    logging.info(f"Profile '{current_profile}' storage path set to: {abs_profile_dir}")

    if os.path.exists(abs_profile_dir):
        files = os.listdir(abs_profile_dir)
        if files:
            logging.info(f"Profile directory contains {len(files)} items.")
        else:
            test_file = os.path.join(abs_profile_dir, "test_write.tmp")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                logging.warning("Profile directory is EMPTY, but write test passed.")
            except Exception as e:
                logging.error(f"Cannot write to profile directory: {e}")
    else:
        logging.error("Profile directory was not created!")

    return abs_profile_dir

def check_first_run():
    """Проверяет, был ли уже выполнен первый запуск, и выполняет действия при первом запуске."""
    first_run_flag = os.path.join(DATA_DIR, 'first_run.done')
    if os.path.exists(first_run_flag):
        return False
    # Первый запуск
    logging.info("First run detected. Performing initial setup...")
    # Добавляем папку I2P в исключения Defender
    i2p_folder = resource_path("I2P")
    if os.path.exists(i2p_folder):
        # Пробуем добавить
        if add_to_defender_exclusion(i2p_folder):
            logging.info("I2P folder added to Windows Defender exclusions.")
        else:
            logging.warning("Could not add I2P folder to exclusions. Please add manually if needed.")
    else:
        logging.warning(f"I2P folder not found at {i2p_folder}, skipping exclusion.")
    # Помечаем, что первый запуск выполнен
    try:
        with open(first_run_flag, 'w') as f:
            f.write('done')
    except Exception as e:
        logging.error(f"Failed to write first run flag: {e}")
    return True

def main():
    add_optimization_flags()
    app = QApplication(sys.argv)

    icon_path = resource_path("icons/icon.ico")
    if not os.path.exists(icon_path):
        icon_path = resource_path("icons/icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        logging.info(f"Icon set from {icon_path}")
    else:
        logging.warning("Icon file not found, using default")

    setup_profile()
    # Уже не нужно, так как флаги установлены через os.environ
    # os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = ' '.join(sys.argv[1:])
    QCoreApplication.setAttribute(Qt.AA_UseOpenGLES)
    init_db()

    # Проверяем первый запуск (добавление в исключения Defender)
    check_first_run()

    app.setStyleSheet("""
        QMenu {
            background-color: rgba(42, 42, 42, 250);
            color: #fff;
            border: 1px solid rgba(80, 80, 80, 200);
        }
        QMenu::item { padding: 8px 20px; }
        QMenu::item:selected { background-color: rgba(0, 168, 255, 220); }
    """)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
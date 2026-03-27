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

# core/api_module/customization.py
"""
Миксин для настроек кастомизации интерфейса.
Содержит методы для работы с видимостью элементов верхней панели, цветами, высотой,
кастомными иконками, настройками фона домашней страницы, настройками центральной области,
управлением флагами Chromium, умным буфером, сетевыми настройками (DoH, QUIC, WebRTC, IPv6, TCP),
а также для AI‑чата, автоскрытия панели, фона верхней панели, кастомизации выделения текста
и звуков клавиатуры.
"""
import configparser
import os
import json
import logging
from core.config import CONFIG_PATH

logger = logging.getLogger(__name__)


class CustomizationMixin:
    """Миксин для работы с настройками кастомизации."""

    def _get_custom_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_PATH):
            config.read(CONFIG_PATH)
        if 'Customization' not in config:
            config['Customization'] = {}
        return config

    def _save_custom_config(self, config):
        try:
            with open(CONFIG_PATH, 'w') as f:
                config.write(f)
        except Exception as e:
            logger.error(f"Error saving customization config: {e}")

    # --- Видимость элементов верхней панели ---
    def get_titlebar_button_visible(self, button_name, default=True):
        config = self._get_custom_config()
        val = config['Customization'].get(f'titlebar_show_{button_name}', str(default))
        return val.lower() == 'true'

    def set_titlebar_button_visible(self, button_name, visible):
        config = self._get_custom_config()
        config['Customization'][f'titlebar_show_{button_name}'] = str(visible)
        self._save_custom_config(config)

    # --- Включение/выключение кастомного фона панели (не используется, фон всегда кастомный) ---
    def get_titlebar_custom_bg_enabled(self, default=False):
        config = self._get_custom_config()
        val = config['Customization'].get('titlebar_custom_bg_enabled', str(default))
        return val.lower() == 'true'

    def set_titlebar_custom_bg_enabled(self, enabled):
        config = self._get_custom_config()
        config['Customization']['titlebar_custom_bg_enabled'] = str(enabled)
        self._save_custom_config(config)
        logger.info(f"Titlebar custom bg enabled set to {enabled}")

    # --- Цвета панели (только для сплошного цвета) ---
    def get_titlebar_bg_color(self, default='#1a1a1a'):
        config = self._get_custom_config()
        return config['Customization'].get('titlebar_bg_color', default)

    def set_titlebar_bg_color(self, color):
        config = self._get_custom_config()
        config['Customization']['titlebar_bg_color'] = color
        self._save_custom_config(config)
        logger.info(f"Titlebar bg color set to {color}")

    def get_titlebar_button_color(self, default='#ffffff'):
        config = self._get_custom_config()
        return config['Customization'].get('titlebar_button_color', default)

    def set_titlebar_button_color(self, color):
        config = self._get_custom_config()
        config['Customization']['titlebar_button_color'] = color
        self._save_custom_config(config)
        logger.info(f"Titlebar button color set to {color}")

    # --- Высота панели ---
    def get_titlebar_height(self, default=50):
        config = self._get_custom_config()
        try:
            return int(config['Customization'].get('titlebar_height', str(default)))
        except:
            return default

    def set_titlebar_height(self, height):
        config = self._get_custom_config()
        config['Customization']['titlebar_height'] = str(height)
        self._save_custom_config(config)
        logger.info(f"Titlebar height set to {height}")

    # --- Включение/выключение кастомных цветов вкладок ---
    def get_tab_custom_colors_enabled(self, default=False):
        config = self._get_custom_config()
        val = config['Customization'].get('tab_custom_colors_enabled', str(default))
        return val.lower() == 'true'

    def set_tab_custom_colors_enabled(self, enabled):
        config = self._get_custom_config()
        config['Customization']['tab_custom_colors_enabled'] = str(enabled)
        self._save_custom_config(config)
        logger.info(f"Tab custom colors enabled set to {enabled}")

    # --- Цвета вкладок ---
    def get_tab_bg_color(self, default='#323232'):
        config = self._get_custom_config()
        return config['Customization'].get('tab_bg_color', default)

    def set_tab_bg_color(self, color):
        config = self._get_custom_config()
        config['Customization']['tab_bg_color'] = color
        self._save_custom_config(config)

    def get_tab_text_color(self, default='#cccccc'):
        config = self._get_custom_config()
        return config['Customization'].get('tab_text_color', default)

    def set_tab_text_color(self, color):
        config = self._get_custom_config()
        config['Customization']['tab_text_color'] = color
        self._save_custom_config(config)

    def get_tab_active_bg_color(self, default='#00a8ff'):
        config = self._get_custom_config()
        return config['Customization'].get('tab_active_bg_color', default)

    def set_tab_active_bg_color(self, color):
        config = self._get_custom_config()
        config['Customization']['tab_active_bg_color'] = color
        self._save_custom_config(config)

    def get_tab_active_text_color(self, default='#ffffff'):
        config = self._get_custom_config()
        return config['Customization'].get('tab_active_text_color', default)

    def set_tab_active_text_color(self, color):
        config = self._get_custom_config()
        config['Customization']['tab_active_text_color'] = color
        self._save_custom_config(config)

    # --- Кастомные иконки для кнопок верхней панели ---
    def get_icon_custom_enabled(self, button_name, default=False):
        config = self._get_custom_config()
        val = config['Customization'].get(f'icon_custom_enabled_{button_name}', str(default))
        return val.lower() == 'true'

    def set_icon_custom_enabled(self, button_name, enabled):
        config = self._get_custom_config()
        config['Customization'][f'icon_custom_enabled_{button_name}'] = str(enabled)
        self._save_custom_config(config)

    def get_icon_custom_path(self, button_name, default=''):
        config = self._get_custom_config()
        return config['Customization'].get(f'icon_custom_path_{button_name}', default)

    def set_icon_custom_path(self, button_name, path):
        config = self._get_custom_config()
        config['Customization'][f'icon_custom_path_{button_name}'] = path
        self._save_custom_config(config)

    # --- Настройки фона домашней страницы ---
    def get_home_bg_type(self, default='Градиент'):
        config = self._get_custom_config()
        return config['Customization'].get('home_bg_type', default)

    def set_home_bg_type(self, bg_type):
        config = self._get_custom_config()
        config['Customization']['home_bg_type'] = bg_type
        self._save_custom_config(config)

    def get_home_bg_color1(self, default='#0a0a0a'):
        config = self._get_custom_config()
        return config['Customization'].get('home_bg_color1', default)

    def set_home_bg_color1(self, color):
        config = self._get_custom_config()
        config['Customization']['home_bg_color1'] = color
        self._save_custom_config(config)

    def get_home_bg_color2(self, default='#1a1a2e'):
        config = self._get_custom_config()
        return config['Customization'].get('home_bg_color2', default)

    def set_home_bg_color2(self, color):
        config = self._get_custom_config()
        config['Customization']['home_bg_color2'] = color
        self._save_custom_config(config)

    def get_home_bg_gradient_angle(self, default=135):
        config = self._get_custom_config()
        try:
            return int(config['Customization'].get('home_bg_gradient_angle', str(default)))
        except:
            return default

    def set_home_bg_gradient_angle(self, angle):
        config = self._get_custom_config()
        config['Customization']['home_bg_gradient_angle'] = str(angle)
        self._save_custom_config(config)

    def get_home_bg_image_path(self, default=''):
        config = self._get_custom_config()
        return config['Customization'].get('home_bg_image_path', default)

    def set_home_bg_image_path(self, path):
        config = self._get_custom_config()
        config['Customization']['home_bg_image_path'] = path
        self._save_custom_config(config)

    def get_home_bg_image_fit(self, default='cover'):
        config = self._get_custom_config()
        return config['Customization'].get('home_bg_image_fit', default)

    def set_home_bg_image_fit(self, fit):
        config = self._get_custom_config()
        config['Customization']['home_bg_image_fit'] = fit
        self._save_custom_config(config)

    def get_home_bg_animation_enabled(self, default=True):
        config = self._get_custom_config()
        val = config['Customization'].get('home_bg_animation_enabled', str(default))
        return val.lower() == 'true'

    def set_home_bg_animation_enabled(self, enabled):
        config = self._get_custom_config()
        config['Customization']['home_bg_animation_enabled'] = str(enabled)
        self._save_custom_config(config)

    def get_home_bg_animation_speed(self, default=20):
        config = self._get_custom_config()
        try:
            return int(config['Customization'].get('home_bg_animation_speed', str(default)))
        except:
            return default

    def set_home_bg_animation_speed(self, speed):
        config = self._get_custom_config()
        config['Customization']['home_bg_animation_speed'] = str(speed)
        self._save_custom_config(config)

    def get_home_bg_image_crop(self, default=None):
        config = self._get_custom_config()
        val = config['Customization'].get('home_bg_image_crop', 'null')
        try:
            return json.loads(val) if val != 'null' else {"x": 0, "y": 0, "width": 100, "height": 100, "scale": "cover"}
        except:
            return {"x": 0, "y": 0, "width": 100, "height": 100, "scale": "cover"}

    def set_home_bg_image_crop(self, crop_params):
        config = self._get_custom_config()
        config['Customization']['home_bg_image_crop'] = json.dumps(crop_params)
        self._save_custom_config(config)

    # --- Настройки центральной области домашней страницы ---
    def get_center_element_visible(self, element_name, default=True):
        config = self._get_custom_config()
        val = config['Customization'].get(f'center_visible_{element_name}', str(default))
        return val.lower() == 'true'

    def set_center_element_visible(self, element_name, visible):
        config = self._get_custom_config()
        config['Customization'][f'center_visible_{element_name}'] = str(visible)
        self._save_custom_config(config)

    def get_center_element_offset_x(self, element_name, default=0):
        config = self._get_custom_config()
        try:
            return int(config['Customization'].get(f'center_offset_x_{element_name}', str(default)))
        except:
            return default

    def set_center_element_offset_x(self, element_name, offset):
        config = self._get_custom_config()
        config['Customization'][f'center_offset_x_{element_name}'] = str(offset)
        self._save_custom_config(config)

    def get_center_element_offset_y(self, element_name, default=0):
        config = self._get_custom_config()
        try:
            return int(config['Customization'].get(f'center_offset_y_{element_name}', str(default)))
        except:
            return default

    def set_center_element_offset_y(self, element_name, offset):
        config = self._get_custom_config()
        config['Customization'][f'center_offset_y_{element_name}'] = str(offset)
        self._save_custom_config(config)

    # --- Управление флагами Chromium ---
    def _flag_to_key(self, flag):
        return flag.replace('=', '_').replace(' ', '_').replace('.', '_')

    def get_chromium_flags(self):
        config = self._get_custom_config()
        flags_dict = {}
        if 'Flags' in config:
            for key, value in config['Flags'].items():
                flags_dict[key] = value.lower() == 'true'
        return flags_dict

    def set_chromium_flag(self, flag, enabled):
        config = self._get_custom_config()
        if 'Flags' not in config:
            config['Flags'] = {}
        key = self._flag_to_key(flag)
        config['Flags'][key] = 'true' if enabled else 'false'
        self._save_custom_config(config)
        logger.info(f"Chromium flag {flag} set to {enabled}")

    def get_chromium_flag(self, flag, default=True):
        config = self._get_custom_config()
        if 'Flags' in config:
            key = self._flag_to_key(flag)
            val = config['Flags'].get(key, str(default))
            return val.lower() == 'true'
        return default

    def get_all_flags_with_descriptions(self):
        return [
            ('--process-per-tab', 'Запускать каждый таб в отдельном процессе', True),
            ('--ignore-gpu-blocklist', 'Игнорировать блокировку GPU', True),
            ('--enable-software-rasterizer', 'Использовать программный рендеринг', True),
            ('--max_old_space_size=4096', 'Максимальный размер кучи V8 (МБ)', True),
            ('--renderer-process-limit=10', 'Максимальное количество процессов рендера', True),
            ('--enable-lazy-image-loading', 'Ленивая загрузка изображений', True),
            ('--enable-lazy-frame-loading', 'Ленивая загрузка фреймов', True),
            ('--enable-async-dns', 'Асинхронный DNS', True),
            ('--enable-quic', 'Включить протокол QUIC', True),
            ('--enable-parallel-downloading', 'Параллельная загрузка', True),
            ('--enable-early-hints', 'Ранние подсказки HTTP (103)', True),
            ('--enable-back-forward-cache', 'Кэш навигации (быстрый переход назад/вперёд)', True),
            ('--enable-fast-unload', 'Быстрая выгрузка страниц', True),
            ('--disable-accelerated-video-decode', 'Отключить аппаратное декодирование видео', False),
            ('--disable-direct-composition-video-overlays', 'Отключить оверлеи видео DirectComposition', False),
            ('--enable-features=MemoryCacheIntelligentPruning', 'Умная обрезка кэша', False),
            ('--enable-features=ThrottleDisplayNoneAndVisibilityHiddenCrossOriginIframes', 'Оптимизация скрытых iframe', False),
            ('--enable-features=PartitionAllocEverywhere', 'Использовать PartitionAlloc везде', True),
            ('--enable-features=PartitionAlloc', 'Включить PartitionAlloc', True),
            ('--autoplay-policy=no-user-gesture-required', 'Разрешить автозапуск без жеста пользователя', True),
            ('--enable-media-stream', 'Включить медиа-потоки (WebRTC)', True),
            ('--smooth-scrolling', 'Плавная прокрутка', True),
            ('--enable-logging', 'Включить логирование', True),
            ('--log-level=3', 'Уровень логирования (3=INFO)', True),
            ('--disable-background-media-suspend', 'Не приостанавливать фоновое медиа', True),
            ('--disable-background-timer-throttling', 'Не замедлять фоновые таймеры', True),
            ('--disable-renderer-backgrounding', 'Не замедлять фоновые рендер-процессы', True),
            ('--disable-backgrounding-occluded-windows', 'Не приостанавливать скрытые окна', True),
        ]

    # --- Умный буфер ---
    def get_smart_buffer_enabled(self, default=False):
        config = self._get_custom_config()
        val = config['Customization'].get('smart_buffer_enabled', str(default))
        return val.lower() == 'true'

    def set_smart_buffer_enabled(self, enabled):
        config = self._get_custom_config()
        config['Customization']['smart_buffer_enabled'] = str(enabled)
        self._save_custom_config(config)
        logger.info(f"Smart buffer enabled set to {enabled}")

    def get_data_dir(self):
        from core.config import DATA_DIR
        return DATA_DIR

    # --- Сетевые настройки ---
    def get_doh_enabled(self, default=False):
        config = self._get_custom_config()
        val = config['Customization'].get('doh_enabled', str(default))
        return val.lower() == 'true'

    def set_doh_enabled(self, enabled):
        config = self._get_custom_config()
        config['Customization']['doh_enabled'] = str(enabled)
        self._save_custom_config(config)
        logger.info(f"DoH enabled set to {enabled}")

    def get_doh_provider(self, default='google'):
        config = self._get_custom_config()
        return config['Customization'].get('doh_provider', default)

    def set_doh_provider(self, provider):
        config = self._get_custom_config()
        config['Customization']['doh_provider'] = provider
        self._save_custom_config(config)

    def get_quic_enabled(self, default=True):
        config = self._get_custom_config()
        val = config['Customization'].get('quic_enabled', str(default))
        return val.lower() == 'true'

    def set_quic_enabled(self, enabled):
        config = self._get_custom_config()
        config['Customization']['quic_enabled'] = str(enabled)
        self._save_custom_config(config)
        logger.info(f"QUIC enabled set to {enabled}")

    def get_webrtc_enabled(self, default=True):
        config = self._get_custom_config()
        val = config['Customization'].get('webrtc_enabled', str(default))
        return val.lower() == 'true'

    def set_webrtc_enabled(self, enabled):
        config = self._get_custom_config()
        config['Customization']['webrtc_enabled'] = str(enabled)
        self._save_custom_config(config)
        logger.info(f"WebRTC enabled set to {enabled}")

    def get_ipv6_enabled(self, default=True):
        config = self._get_custom_config()
        val = config['Customization'].get('ipv6_enabled', str(default))
        return val.lower() == 'true'

    def set_ipv6_enabled(self, enabled):
        config = self._get_custom_config()
        config['Customization']['ipv6_enabled'] = str(enabled)
        self._save_custom_config(config)
        logger.info(f"IPv6 enabled set to {enabled}")

    def get_tcp_buffer_size(self, default=0):
        config = self._get_custom_config()
        try:
            return int(config['Customization'].get('tcp_buffer_size', str(default)))
        except:
            return default

    def set_tcp_buffer_size(self, size):
        config = self._get_custom_config()
        config['Customization']['tcp_buffer_size'] = str(size)
        self._save_custom_config(config)
        logger.info(f"TCP buffer size set to {size}")

    # --- Настройки AI чата ---
    def get_ai_chat_enabled(self, default=False):
        config = self._get_custom_config()
        val = config['Customization'].get('ai_chat_enabled', str(default))
        return val.lower() == 'true'

    def set_ai_chat_enabled(self, enabled):
        config = self._get_custom_config()
        config['Customization']['ai_chat_enabled'] = str(enabled)
        self._save_custom_config(config)
        logger.info(f"AI Chat enabled set to {enabled}")

    def get_ai_provider(self, default='free_gpt'):
        config = self._get_custom_config()
        return config['Customization'].get('ai_provider', default)

    def set_ai_provider(self, provider):
        config = self._get_custom_config()
        config['Customization']['ai_provider'] = provider
        self._save_custom_config(config)

    def get_ai_api_key(self, default=''):
        config = self._get_custom_config()
        return config['Customization'].get('ai_api_key', default)

    def set_ai_api_key(self, api_key):
        config = self._get_custom_config()
        config['Customization']['ai_api_key'] = api_key
        self._save_custom_config(config)

    def get_ai_voice_language(self, default='ru'):
        config = self._get_custom_config()
        return config['Customization'].get('ai_voice_language', default)

    def set_ai_voice_language(self, lang):
        config = self._get_custom_config()
        config['Customization']['ai_voice_language'] = lang
        self._save_custom_config(config)

    def get_ai_voice_name(self, default='ru-RU-DmitryNeural'):
        config = self._get_custom_config()
        return config['Customization'].get('ai_voice_name', default)

    def set_ai_voice_name(self, voice):
        config = self._get_custom_config()
        config['Customization']['ai_voice_name'] = voice
        self._save_custom_config(config)

    # --- Автоскрытие верхней панели ---
    def get_auto_hide_enabled(self, default=False):
        config = self._get_custom_config()
        val = config['Customization'].get('auto_hide_enabled', str(default))
        return val.lower() == 'true'

    def set_auto_hide_enabled(self, enabled):
        config = self._get_custom_config()
        config['Customization']['auto_hide_enabled'] = str(enabled)
        self._save_custom_config(config)
        logger.info(f"Auto hide enabled set to {enabled}")

    def get_auto_hide_delay(self, default=5):
        config = self._get_custom_config()
        try:
            return int(config['Customization'].get('auto_hide_delay', str(default)))
        except:
            return default

    def set_auto_hide_delay(self, delay):
        config = self._get_custom_config()
        config['Customization']['auto_hide_delay'] = str(delay)
        self._save_custom_config(config)
        logger.info(f"Auto hide delay set to {delay} seconds")

    # --- Фон верхней панели (цвет, градиент, изображение) ---
    def get_titlebar_bg_type(self, default='color'):
        config = self._get_custom_config()
        return config['Customization'].get('titlebar_bg_type', default)

    def set_titlebar_bg_type(self, bg_type):
        config = self._get_custom_config()
        config['Customization']['titlebar_bg_type'] = bg_type
        self._save_custom_config(config)

    def get_titlebar_gradient_color1(self, default='#00a8ff'):
        config = self._get_custom_config()
        return config['Customization'].get('titlebar_gradient_color1', default)

    def set_titlebar_gradient_color1(self, color):
        config = self._get_custom_config()
        config['Customization']['titlebar_gradient_color1'] = color
        self._save_custom_config(config)

    def get_titlebar_gradient_color2(self, default='#2a2a2a'):
        config = self._get_custom_config()
        return config['Customization'].get('titlebar_gradient_color2', default)

    def set_titlebar_gradient_color2(self, color):
        config = self._get_custom_config()
        config['Customization']['titlebar_gradient_color2'] = color
        self._save_custom_config(config)

    def get_titlebar_gradient_angle(self, default=135):
        config = self._get_custom_config()
        try:
            return int(config['Customization'].get('titlebar_gradient_angle', str(default)))
        except:
            return default

    def set_titlebar_gradient_angle(self, angle):
        config = self._get_custom_config()
        config['Customization']['titlebar_gradient_angle'] = str(angle)
        self._save_custom_config(config)

    def get_titlebar_bg_image_path(self, default=''):
        config = self._get_custom_config()
        return config['Customization'].get('titlebar_bg_image_path', default)

    def set_titlebar_bg_image_path(self, path):
        config = self._get_custom_config()
        config['Customization']['titlebar_bg_image_path'] = path
        self._save_custom_config(config)

    def get_titlebar_bg_image_crop(self, default=None):
        config = self._get_custom_config()
        val = config['Customization'].get('titlebar_bg_image_crop', 'null')
        try:
            return json.loads(val) if val != 'null' else {"x": 0, "y": 0, "width": 100, "height": 100, "scale": "cover"}
        except:
            return {"x": 0, "y": 0, "width": 100, "height": 100, "scale": "cover"}

    def set_titlebar_bg_image_crop(self, crop_params):
        config = self._get_custom_config()
        config['Customization']['titlebar_bg_image_crop'] = json.dumps(crop_params)
        self._save_custom_config(config)

    # --- Кастомизация выделения текста ---
    def get_selection_custom_enabled(self, default=False):
        config = self._get_custom_config()
        val = config['Customization'].get('selection_custom_enabled', str(default))
        return val.lower() == 'true'

    def set_selection_custom_enabled(self, enabled):
        config = self._get_custom_config()
        config['Customization']['selection_custom_enabled'] = str(enabled)
        self._save_custom_config(config)

    def get_selection_color1(self, default='#00a8ff'):
        config = self._get_custom_config()
        return config['Customization'].get('selection_color1', default)

    def set_selection_color1(self, color):
        config = self._get_custom_config()
        config['Customization']['selection_color1'] = color
        self._save_custom_config(config)

    def get_selection_type(self, default='solid'):
        config = self._get_custom_config()
        return config['Customization'].get('selection_type', default)

    def set_selection_type(self, sel_type):
        config = self._get_custom_config()
        config['Customization']['selection_type'] = sel_type
        self._save_custom_config(config)

    # ---------- Адресная строка ----------
    def get_urlbar_border_enabled(self, default=True):
        config = self._get_custom_config()
        val = config['Customization'].get('urlbar_border_enabled', str(default))
        return val.lower() == 'true'

    def set_urlbar_border_enabled(self, enabled):
        config = self._get_custom_config()
        config['Customization']['urlbar_border_enabled'] = str(enabled)
        self._save_custom_config(config)

    def get_urlbar_transparency(self, default=0):
        config = self._get_custom_config()
        try:
            return int(config['Customization'].get('urlbar_transparency', str(default)))
        except:
            return default

    def set_urlbar_transparency(self, transparency):
        config = self._get_custom_config()
        config['Customization']['urlbar_transparency'] = str(transparency)
        self._save_custom_config(config)

    def get_urlbar_bg_color(self, default='#0f0f0f'):
        config = self._get_custom_config()
        return config['Customization'].get('urlbar_bg_color', default)

    def set_urlbar_bg_color(self, color):
        config = self._get_custom_config()
        config['Customization']['urlbar_bg_color'] = color
        self._save_custom_config(config)

    # --- Настройки звуков клавиатуры ---
    def get_keyboard_sounds_enabled(self, default=False):
        config = self._get_custom_config()
        val = config['Customization'].get('keyboard_sounds_enabled', str(default))
        return val.lower() == 'true'

    def set_keyboard_sounds_enabled(self, enabled):
        config = self._get_custom_config()
        config['Customization']['keyboard_sounds_enabled'] = str(enabled)
        self._save_custom_config(config)
        logger.info(f"Keyboard sounds enabled set to {enabled}")

    def get_keyboard_sound_path(self, default=''):
        config = self._get_custom_config()
        return config['Customization'].get('keyboard_sound_path', default)

    def set_keyboard_sound_path(self, path):
        config = self._get_custom_config()
        config['Customization']['keyboard_sound_path'] = path
        self._save_custom_config(config)
        logger.info(f"Keyboard sound path set to {path}")

    def get_keyboard_sound_volume(self, default=50):
        config = self._get_custom_config()
        try:
            return int(config['Customization'].get('keyboard_sound_volume', str(default)))
        except:
            return default

    def set_keyboard_sound_volume(self, volume):
        config = self._get_custom_config()
        config['Customization']['keyboard_sound_volume'] = str(volume)
        self._save_custom_config(config)
        logger.info(f"Keyboard sound volume set to {volume}")
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
Объединённая верхняя панель с вкладками и кнопками управления (два уровня) - PySide6
Добавлена поддержка кастомизации (видимость кнопок, цвета, иконки, высота).
Фон панели вынесен в отдельный виджет для поддержки анимации GIF и кадрирования изображений.
ИСПРАВЛЕНО: автоскрытие теперь корректно обрабатывает наведение мыши на верхнюю границу окна.
"""
import os
import logging
import tempfile
import shutil
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QSizeGrip, QLabel, QApplication
from PySide6.QtCore import Qt, QRectF, QTimer, QPoint, QRect
from PySide6.QtGui import QIcon, QColor, QPalette, QMovie, QPixmap, QScreen

from core.utils import resource_path

logger = logging.getLogger(__name__)

class CustomTitleBar(QWidget):
    """Объединённая верхняя панель (два уровня)"""

    def __init__(self, parent_window, tab_bar, nav_bar):
        super().__init__()
        self.parent_window = parent_window
        self.tab_bar = tab_bar
        self.nav_bar = nav_bar
        self.api = parent_window.api
        self.setFixedHeight(90)
        self.dragging = False
        self.start_pos = None
        self.window_pos = None
        self.snap_threshold = 15        # пикселей до края экрана, чтобы сработал снэп
        self.snapped = False             # флаг, чтобы не вызывать снэп повторно в одном движении

        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.lower()
        self.background_label.setScaledContents(False)
        self.movie = None
        self.temp_gif_file = None

        self._setup_ui()
        self.apply_customization()
        logger.debug("CustomTitleBar initialized")

    def _get_icon(self, name, fallback_text):
        icon_path = resource_path(f"icons/{name}")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return None

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Верхний уровень
        self.top_level = QWidget()
        self.top_level.setObjectName("topLevel")
        self.top_level.setFixedHeight(38)
        self.top_level.setStyleSheet("background-color: transparent;")
        top_layout = QHBoxLayout(self.top_level)
        top_layout.setContentsMargins(10, 2, 15, 2)
        top_layout.setSpacing(15)

        # Логотип
        self.icon_btn = QPushButton()
        self.icon_btn.setObjectName("iconBtn")
        icon_path = resource_path("icons/icon.png")
        if os.path.exists(icon_path):
            self.icon_btn.setIcon(QIcon(icon_path))
            self.icon_btn.setIconSize(self.icon_btn.sizeHint())
        else:
            self.icon_btn.setText("🌐")
        self.icon_btn.setFixedWidth(32)
        self.icon_btn.setFixedHeight(32)
        self.icon_btn.clicked.connect(self.parent_window.go_home)
        top_layout.addWidget(self.icon_btn)

        self.tab_bar.setFixedHeight(38)
        top_layout.addWidget(self.tab_bar, 1)

        # Контейнер для кнопок управления окном
        window_controls = QWidget()
        window_controls.setObjectName("windowControls")
        controls_layout = QHBoxLayout(window_controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(10)

        self.min_btn = QPushButton("─")
        self.min_btn.setFixedSize(32, 32)
        self.min_btn.clicked.connect(self.parent_window.showMinimized)
        controls_layout.addWidget(self.min_btn)

        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(32, 32)
        self.max_btn.clicked.connect(self.toggle_maximize)
        controls_layout.addWidget(self.max_btn)

        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.clicked.connect(self.parent_window.close)
        controls_layout.addWidget(self.close_btn)

        top_layout.addWidget(window_controls)
        main_layout.addWidget(self.top_level)

        # Нижний уровень
        self.bottom_level = QWidget()
        self.bottom_level.setObjectName("bottomLevel")
        self.bottom_level.setFixedHeight(45)
        bottom_layout = QHBoxLayout(self.bottom_level)
        bottom_layout.setContentsMargins(15, 5, 15, 5)
        bottom_layout.setSpacing(12)

        # Блок навигации (назад, вперёд, обновить)
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(6)

        self.back_btn = QPushButton()
        self.back_btn.setObjectName("iconBtn")
        icon = self._get_icon('back.png', '◀')
        if icon:
            self.back_btn.setIcon(icon)
            self.back_btn.setIconSize(self.back_btn.sizeHint())
        else:
            self.back_btn.setText("◀")
        self.back_btn.setFixedSize(32, 32)
        self.back_btn.clicked.connect(self.nav_bar.on_back)
        nav_layout.addWidget(self.back_btn)

        self.forward_btn = QPushButton()
        self.forward_btn.setObjectName("iconBtn")
        icon = self._get_icon('forward.png', '▶')
        if icon:
            self.forward_btn.setIcon(icon)
            self.forward_btn.setIconSize(self.forward_btn.sizeHint())
        else:
            self.forward_btn.setText("▶")
        self.forward_btn.setFixedSize(32, 32)
        self.forward_btn.clicked.connect(self.nav_bar.on_forward)
        nav_layout.addWidget(self.forward_btn)

        self.refresh_btn = QPushButton()
        self.refresh_btn.setObjectName("iconBtn")
        icon = self._get_icon('refresh.png', '↻')
        if icon:
            self.refresh_btn.setIcon(icon)
            self.refresh_btn.setIconSize(self.refresh_btn.sizeHint())
        else:
            self.refresh_btn.setText("↻")
        self.refresh_btn.setFixedSize(32, 32)
        self.refresh_btn.setToolTip("Обновить страницу (F5)")
        self.refresh_btn.clicked.connect(self.nav_bar.on_refresh)
        nav_layout.addWidget(self.refresh_btn)

        bottom_layout.addWidget(nav_widget)

        # Адресная строка
        self.nav_bar.url_bar.setFixedHeight(32)
        bottom_layout.addWidget(self.nav_bar.url_bar, 1)

        # Растяжка, чтобы кнопки ушли вправо
        bottom_layout.addStretch()

        # Кнопки "Загрузки", "История", "Настройки"
        self.downloads_btn = QPushButton()
        self.downloads_btn.setObjectName("iconBtn")
        self.downloads_btn.setToolTip("Загрузки")
        icon = self._get_icon('downloads.png', '📥')
        if icon:
            self.downloads_btn.setIcon(icon)
            self.downloads_btn.setIconSize(self.downloads_btn.sizeHint())
        else:
            self.downloads_btn.setText("📥")
        self.downloads_btn.setFixedSize(32, 32)
        self.downloads_btn.clicked.connect(self.nav_bar.on_downloads)
        bottom_layout.addWidget(self.downloads_btn)

        self.history_btn = QPushButton()
        self.history_btn.setObjectName("iconBtn")
        self.history_btn.setToolTip("История")
        icon = self._get_icon('history.png', '📜')
        if icon:
            self.history_btn.setIcon(icon)
            self.history_btn.setIconSize(self.history_btn.sizeHint())
        else:
            self.history_btn.setText("📜")
        self.history_btn.setFixedSize(32, 32)
        self.history_btn.clicked.connect(self.nav_bar.on_history)
        bottom_layout.addWidget(self.history_btn)

        self.settings_btn = QPushButton()
        self.settings_btn.setObjectName("iconBtn")
        self.settings_btn.setToolTip("Настройки")
        icon = self._get_icon('settings.png', '⚙')
        if icon:
            self.settings_btn.setIcon(icon)
            self.settings_btn.setIconSize(self.settings_btn.sizeHint())
        else:
            self.settings_btn.setText("⚙")
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.clicked.connect(self.nav_bar.on_settings)
        bottom_layout.addWidget(self.settings_btn)

        # Размерный захват (для изменения размера окна) – самый правый элемент
        self.grip = QSizeGrip(self)
        self.grip.setFixedSize(16, 16)
        bottom_layout.addWidget(self.grip)

        main_layout.addWidget(self.bottom_level)

    # -------------------- Aero Snap логика (по курсору) --------------------
    def _get_current_screen_geometry(self, cursor_pos):
        screen = QApplication.screenAt(cursor_pos)
        if not screen:
            screen = QApplication.primaryScreen()
        return screen.availableGeometry()

    def _apply_snap_from_cursor(self, cursor_pos):
        if self.parent_window.isMaximized():
            return False
        screen_geom = self._get_current_screen_geometry(cursor_pos)
        x = cursor_pos.x() - screen_geom.x()
        y = cursor_pos.y() - screen_geom.y()
        left_edge = x <= self.snap_threshold
        right_edge = x >= screen_geom.width() - self.snap_threshold
        top_edge = y <= self.snap_threshold
        bottom_edge = y >= screen_geom.height() - self.snap_threshold

        if top_edge:
            self.parent_window.showMaximized()
            self.max_btn.setText("❐")
            return True
        elif left_edge and not right_edge:
            target_geom = QRect(screen_geom.left(), screen_geom.top(),
                                screen_geom.width() // 2, screen_geom.height())
            self.parent_window.setGeometry(target_geom)
            return True
        elif right_edge and not left_edge:
            target_geom = QRect(screen_geom.center().x(), screen_geom.top(),
                                screen_geom.width() // 2, screen_geom.height())
            self.parent_window.setGeometry(target_geom)
            return True
        elif bottom_edge:
            target_geom = QRect(screen_geom.left(), screen_geom.center().y(),
                                screen_geom.width(), screen_geom.height() // 2)
            self.parent_window.setGeometry(target_geom)
            return True
        return False

    # -------------------- Перетаскивание --------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.parent_window.isMaximized():
                self.parent_window.showNormal()
                self.max_btn.setText("□")
            self.start_pos = event.globalPos()
            self.window_pos = self.parent_window.pos()
            self.dragging = True
            self.snapped = False
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton and self.start_pos:
            delta = event.globalPos() - self.start_pos
            new_pos = self.window_pos + delta
            self.parent_window.move(new_pos)

            if not self.snapped:
                cursor_pos = event.globalPos()
                if self._apply_snap_from_cursor(cursor_pos):
                    self.dragging = False
                    self.snapped = True
                    self.start_pos = None
                    self.window_pos = None
                    event.accept()
                    return

            event.accept()

    def mouseReleaseEvent(self, event):
        if self.dragging and event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.snapped = False
            self.start_pos = None
            self.window_pos = None
            event.accept()

    # -------------------- Остальные методы --------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        if self.api.get_titlebar_bg_type() == 'image':
            self._apply_background()

    def apply_customization(self):
        logger.info("apply_customization called")

        self.back_btn.setVisible(self.api.get_titlebar_button_visible('back', True))
        self.forward_btn.setVisible(self.api.get_titlebar_button_visible('forward', True))
        self.refresh_btn.setVisible(self.api.get_titlebar_button_visible('refresh', True))
        self.downloads_btn.setVisible(self.api.get_titlebar_button_visible('downloads', True))
        self.history_btn.setVisible(self.api.get_titlebar_button_visible('history', True))
        self.settings_btn.setVisible(self.api.get_titlebar_button_visible('settings', True))
        self.nav_bar.url_bar.setVisible(self.api.get_titlebar_button_visible('url_bar', True))

        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
                border-radius: 5px;
            }
        """)

        btn_color = self.api.get_titlebar_button_color()
        for widget in self.findChildren(QPushButton):
            pal = widget.palette()
            pal.setColor(QPalette.ButtonText, QColor(btn_color))
            widget.setPalette(pal)

        icon_buttons = [
            ('back', self.back_btn),
            ('forward', self.forward_btn),
            ('refresh', self.refresh_btn),
            ('downloads', self.downloads_btn),
            ('history', self.history_btn),
            ('settings', self.settings_btn),
            ('icon', self.icon_btn),
        ]
        for name, btn in icon_buttons:
            if self.api.get_icon_custom_enabled(name):
                path = self.api.get_icon_custom_path(name)
                if path and os.path.exists(path):
                    btn.setIcon(QIcon(path))
                    btn.setIconSize(btn.sizeHint())
                    btn.setText("")
                else:
                    self._set_default_icon(name, btn)
            else:
                self._set_default_icon(name, btn)

        new_bottom_height = self.api.get_titlebar_height()
        if new_bottom_height < 40:
            new_bottom_height = 40
        elif new_bottom_height > 150:
            new_bottom_height = 150
        self.bottom_level.setFixedHeight(new_bottom_height)
        self.setFixedHeight(38 + new_bottom_height)

        self._apply_background()
        self.tab_bar.apply_customization()

        self.update()
        self.background_label.update()
        self.top_level.update()
        self.bottom_level.update()

    def _make_gradient(self, angle, color1, color2):
        if angle == 0:
            return f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:1 {color2})"
        elif angle == 45:
            return f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color1}, stop:1 {color2})"
        elif angle == 90:
            return f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {color1}, stop:1 {color2})"
        elif angle == 135:
            return f"qlineargradient(x1:0, y1:1, x2:1, y2:0, stop:0 {color1}, stop:1 {color2})"
        elif angle == 180:
            return f"qlineargradient(x1:1, y1:0, x2:0, y2:0, stop:0 {color1}, stop:1 {color2})"
        elif angle == 225:
            return f"qlineargradient(x1:1, y1:1, x2:0, y2:0, stop:0 {color1}, stop:1 {color2})"
        elif angle == 270:
            return f"qlineargradient(x1:0, y1:1, x2:0, y2:0, stop:0 {color1}, stop:1 {color2})"
        elif angle == 315:
            return f"qlineargradient(x1:0, y1:1, x2:1, y2:0, stop:0 {color1}, stop:1 {color2})"
        else:
            return f"qlineargradient(x1:0, y1:1, x2:1, y2:0, stop:0 {color1}, stop:1 {color2})"

    def _create_cropped_gif(self, original_path, crop_params, target_size):
        try:
            from PIL import Image, ImageSequence
        except ImportError:
            logger.error("Pillow not installed, cannot crop GIF. Falling back to full GIF.")
            return original_path

        x_p = crop_params.get('x', 0)
        y_p = crop_params.get('y', 0)
        w_p = crop_params.get('width', 100)
        h_p = crop_params.get('height', 100)

        with Image.open(original_path) as img:
            frames = []
            durations = []
            orig_w, orig_h = img.size
            crop_box = (
                int(x_p / 100.0 * orig_w),
                int(y_p / 100.0 * orig_h),
                int((x_p + w_p) / 100.0 * orig_w),
                int((y_p + h_p) / 100.0 * orig_h)
            )
            crop_box = (
                max(0, min(orig_w, crop_box[0])),
                max(0, min(orig_h, crop_box[1])),
                max(0, min(orig_w, crop_box[2])),
                max(0, min(orig_h, crop_box[3]))
            )
            if crop_box[2] <= crop_box[0] or crop_box[3] <= crop_box[1]:
                return original_path

            for frame in ImageSequence.Iterator(img):
                cropped = frame.crop(crop_box)
                scaled = cropped.resize((target_size.width(), target_size.height()), Image.Resampling.LANCZOS)
                frames.append(scaled)
                try:
                    duration = frame.info.get('duration', 100)
                except:
                    duration = 100
                durations.append(duration)

            fd, tmp_path = tempfile.mkstemp(suffix='.gif')
            os.close(fd)
            frames[0].save(
                tmp_path,
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                disposal=2
            )
            return tmp_path

    def _apply_background(self):
        bg_type = self.api.get_titlebar_bg_type()
        logger.info(f"Applying background type: {bg_type}")

        if self.temp_gif_file and os.path.exists(self.temp_gif_file):
            try:
                os.unlink(self.temp_gif_file)
            except:
                pass
            self.temp_gif_file = None

        if self.movie:
            self.movie.stop()
            self.movie.deleteLater()
            self.movie = None
        self.background_label.clear()
        self.background_label.setStyleSheet("")

        if bg_type == 'color':
            bg_color = self.api.get_titlebar_bg_color()
            self.background_label.setStyleSheet(f"background-color: {bg_color};")
            self.background_label.setPixmap(QPixmap())
            logger.info(f"Set solid color: {bg_color}")
        elif bg_type == 'gradient':
            color1 = self.api.get_titlebar_gradient_color1()
            color2 = self.api.get_titlebar_gradient_color2()
            angle = self.api.get_titlebar_gradient_angle()
            grad = self._make_gradient(angle, color1, color2)
            self.background_label.setStyleSheet(f"background: {grad};")
            self.background_label.setPixmap(QPixmap())
            logger.info(f"Set gradient: {color1} -> {color2}, angle {angle}")
        elif bg_type == 'image':
            image_path = self.api.get_titlebar_bg_image_path()
            if image_path and os.path.exists(image_path):
                crop = self.api.get_titlebar_bg_image_crop()
                if image_path.lower().endswith('.gif'):
                    try:
                        temp_gif = self._create_cropped_gif(image_path, crop, self.background_label.size())
                        if temp_gif != image_path:
                            self.temp_gif_file = temp_gif
                        self.movie = QMovie(temp_gif)
                        self.background_label.setScaledContents(True)
                        self.background_label.setMovie(self.movie)
                        self.movie.start()
                        logger.info(f"Started cropped GIF animation from {temp_gif}")
                    except Exception as e:
                        logger.error(f"Failed to process GIF: {e}, falling back to original")
                        self.movie = QMovie(image_path)
                        self.background_label.setScaledContents(True)
                        self.background_label.setMovie(self.movie)
                        self.movie.start()
                        logger.info(f"Started original GIF animation: {image_path}")
                else:
                    original = QPixmap(image_path)
                    if not original.isNull():
                        x_p = crop.get('x', 0)
                        y_p = crop.get('y', 0)
                        w_p = crop.get('width', 100)
                        h_p = crop.get('height', 100)

                        orig_w = original.width()
                        orig_h = original.height()
                        crop_x = int(x_p / 100.0 * orig_w)
                        crop_y = int(y_p / 100.0 * orig_h)
                        crop_w = int(w_p / 100.0 * orig_w)
                        crop_h = int(h_p / 100.0 * orig_h)

                        crop_x = max(0, min(orig_w - 1, crop_x))
                        crop_y = max(0, min(orig_h - 1, crop_y))
                        crop_w = min(orig_w - crop_x, max(1, crop_w))
                        crop_h = min(orig_h - crop_y, max(1, crop_h))

                        logger.info(f"Cropping: src={orig_w}x{orig_h}, crop={crop_x},{crop_y},{crop_w},{crop_h}")
                        cropped = original.copy(crop_x, crop_y, crop_w, crop_h)
                        scaled = cropped.scaled(self.background_label.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                        self.background_label.setPixmap(scaled)
                        self.background_label.setScaledContents(False)
                        logger.info(f"Set cropped image background: {image_path}")
                    else:
                        self.background_label.setStyleSheet("background-color: #252525;")
                        logger.warning(f"Failed to load image: {image_path}")
            else:
                self.background_label.setStyleSheet("background-color: #252525;")
                logger.warning("Image not found, using fallback")
        else:
            self.background_label.setStyleSheet("background-color: #252525;")

        self.background_label.update()

    def _set_default_icon(self, name, btn):
        if name == 'icon':
            icon_path = resource_path("icons/icon.png")
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(btn.sizeHint())
                btn.setText("")
            else:
                btn.setText("🌐")
                btn.setIcon(QIcon())
        else:
            icon = self._get_icon(f'{name}.png', None)
            if icon:
                btn.setIcon(icon)
                btn.setIconSize(btn.sizeHint())
                btn.setText("")
            else:
                fallback_map = {
                    'back': '◀', 'forward': '▶', 'refresh': '↻',
                    'downloads': '📥', 'history': '📜', 'settings': '⚙'
                }
                btn.setText(fallback_map.get(name, ''))
                btn.setIcon(QIcon())

    def toggle_maximize(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.max_btn.setText("□")
        else:
            self.parent_window.showMaximized()
            self.max_btn.setText("❐")
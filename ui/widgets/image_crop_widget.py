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

from PySide6.QtCore import Qt, QRect, QPoint, QRectF, Signal
from PySide6.QtGui import QPainter, QPixmap, QColor, QPen, QBrush
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
import logging

logger = logging.getLogger(__name__)

class ImageCropWidget(QWidget):
    cropChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 150)
        self.setStyleSheet("background-color: #252525; border: 1px solid #444; border-radius: 6px;")

        self.pixmap = None
        self.crop_rect = QRect()
        self.drag_mode = None
        self.drag_start = QPoint()
        self.resize_handle = None
        self.initial_crop_rect = QRect()

        self.view_area = QWidget(self)
        self.view_area.setStyleSheet("background-color: #1a1a1a; border: none;")

        btn_reset = QPushButton("Сбросить вид")
        btn_reset.clicked.connect(self.reset_crop)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(self.view_area, 1)
        layout.addWidget(btn_reset, 0, alignment=Qt.AlignCenter)

        self.view_area.mousePressEvent = self.on_mouse_press
        self.view_area.mouseMoveEvent = self.on_mouse_move
        self.view_area.mouseReleaseEvent = self.on_mouse_release
        self.view_area.paintEvent = self.on_paint

    def set_pixmap(self, pixmap: QPixmap):
        self.pixmap = pixmap
        self.reset_crop()
        self.update()

    def reset_crop(self):
        if not self.pixmap:
            return
        view_rect = self.view_area.rect()
        img_size = self.pixmap.size()
        scale = min(view_rect.width() / img_size.width(), view_rect.height() / img_size.height())
        scaled_width = img_size.width() * scale
        scaled_height = img_size.height() * scale
        x = (view_rect.width() - scaled_width) / 2
        y = (view_rect.height() - scaled_height) / 2
        self.crop_rect = QRect(int(x), int(y), int(scaled_width), int(scaled_height))
        self.cropChanged.emit()
        self.update()
        logger.debug(f"Crop rect reset to {self.crop_rect}")

    def on_paint(self, event):
        painter = QPainter(self.view_area)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        if self.pixmap:
            view_rect = self.view_area.rect()
            img_size = self.pixmap.size()

            scale = min(view_rect.width() / img_size.width(), view_rect.height() / img_size.height())
            scaled_width = img_size.width() * scale
            scaled_height = img_size.height() * scale
            img_x = (view_rect.width() - scaled_width) / 2
            img_y = (view_rect.height() - scaled_height) / 2
            target_rect = QRectF(img_x, img_y, scaled_width, scaled_height)
            source_rect = QRectF(0, 0, img_size.width(), img_size.height())
            painter.drawPixmap(target_rect, self.pixmap, source_rect)

            painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
            painter.setPen(Qt.NoPen)
            painter.drawRect(0, 0, view_rect.width(), self.crop_rect.top())
            painter.drawRect(0, self.crop_rect.bottom(), view_rect.width(), view_rect.height() - self.crop_rect.bottom())
            painter.drawRect(0, self.crop_rect.top(), self.crop_rect.left(), self.crop_rect.height())
            painter.drawRect(self.crop_rect.right(), self.crop_rect.top(), view_rect.width() - self.crop_rect.right(), self.crop_rect.height())

            painter.setPen(QPen(QColor(0, 168, 255), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.crop_rect)

            handle_size = 8
            for point in [
                self.crop_rect.topLeft(), self.crop_rect.topRight(),
                self.crop_rect.bottomLeft(), self.crop_rect.bottomRight(),
                self.crop_rect.center() + QPoint(-self.crop_rect.width()//2, 0),
                self.crop_rect.center() + QPoint(self.crop_rect.width()//2, 0),
                self.crop_rect.center() + QPoint(0, -self.crop_rect.height()//2),
                self.crop_rect.center() + QPoint(0, self.crop_rect.height()//2)
            ]:
                painter.fillRect(point.x() - handle_size//2, point.y() - handle_size//2, handle_size, handle_size, QColor(0, 168, 255))

    def get_handle_at(self, pos):
        handle_size = 8
        margin = handle_size // 2
        rect = self.crop_rect
        points = {
            'top-left': rect.topLeft(),
            'top': rect.center() + QPoint(-rect.width()//2, 0),
            'top-right': rect.topRight(),
            'right': rect.center() + QPoint(rect.width()//2, 0),
            'bottom-right': rect.bottomRight(),
            'bottom': rect.center() + QPoint(0, rect.height()//2),
            'bottom-left': rect.bottomLeft(),
            'left': rect.center() + QPoint(-rect.width()//2, 0),
        }
        for handle, point in points.items():
            if (pos - point).manhattanLength() <= margin:
                return handle
        return None

    def on_mouse_press(self, event):
        pos = event.pos()
        handle = self.get_handle_at(pos)
        if handle:
            self.drag_mode = 'resize'
            self.resize_handle = handle
            self.drag_start = pos
            self.initial_crop_rect = self.crop_rect
            event.accept()
            return
        if self.crop_rect.contains(pos):
            self.drag_mode = 'move'
            self.drag_start = pos
            self.initial_crop_rect = self.crop_rect
            event.accept()

    def on_mouse_move(self, event):
        if not self.drag_mode:
            return
        pos = event.pos()
        delta = pos - self.drag_start
        view_rect = self.view_area.rect()
        new_rect = self.initial_crop_rect

        if self.drag_mode == 'move':
            new_rect = new_rect.translated(delta)
            new_rect = new_rect.intersected(view_rect)
            if new_rect.width() >= 10 and new_rect.height() >= 10:
                self.crop_rect = new_rect

        elif self.drag_mode == 'resize':
            if self.resize_handle == 'top-left':
                new_rect.setTopLeft(new_rect.topLeft() + delta)
            elif self.resize_handle == 'top':
                new_rect.setTop(new_rect.top() + delta.y())
            elif self.resize_handle == 'top-right':
                new_rect.setTopRight(new_rect.topRight() + delta)
            elif self.resize_handle == 'right':
                new_rect.setRight(new_rect.right() + delta.x())
            elif self.resize_handle == 'bottom-right':
                new_rect.setBottomRight(new_rect.bottomRight() + delta)
            elif self.resize_handle == 'bottom':
                new_rect.setBottom(new_rect.bottom() + delta.y())
            elif self.resize_handle == 'bottom-left':
                new_rect.setBottomLeft(new_rect.bottomLeft() + delta)
            elif self.resize_handle == 'left':
                new_rect.setLeft(new_rect.left() + delta.x())
            new_rect = new_rect.intersected(view_rect)
            if new_rect.width() >= 10 and new_rect.height() >= 10:
                self.crop_rect = new_rect

        self.cropChanged.emit()
        self.update()

    def on_mouse_release(self, event):
        self.drag_mode = None
        self.resize_handle = None
        self.drag_start = QPoint()

    def get_crop_params(self):
        """Возвращает параметры кадрирования в процентах от исходного изображения."""
        if not self.pixmap:
            return {"x": 0, "y": 0, "width": 100, "height": 100}
        view_rect = self.view_area.rect()
        img_size = self.pixmap.size()
        scale = min(view_rect.width() / img_size.width(), view_rect.height() / img_size.height())
        img_x = (view_rect.width() - img_size.width() * scale) / 2
        img_y = (view_rect.height() - img_size.height() * scale) / 2

        # Координаты рамки в исходном изображении
        crop_rel_x = (self.crop_rect.left() - img_x) / scale
        crop_rel_y = (self.crop_rect.top() - img_y) / scale
        crop_rel_w = self.crop_rect.width() / scale
        crop_rel_h = self.crop_rect.height() / scale

        crop_rel_x = max(0, min(img_size.width(), crop_rel_x))
        crop_rel_y = max(0, min(img_size.height(), crop_rel_y))
        crop_rel_w = min(img_size.width() - crop_rel_x, crop_rel_w)
        crop_rel_h = min(img_size.height() - crop_rel_y, crop_rel_h)

        x_percent = (crop_rel_x / img_size.width()) * 100
        y_percent = (crop_rel_y / img_size.height()) * 100
        w_percent = (crop_rel_w / img_size.width()) * 100
        h_percent = (crop_rel_h / img_size.height()) * 100

        logger.debug(f"Crop params: x={x_percent:.2f}%, y={y_percent:.2f}%, w={w_percent:.2f}%, h={h_percent:.2f}%")
        return {"x": x_percent, "y": y_percent, "width": w_percent, "height": h_percent}

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.pixmap:
            self.reset_crop()
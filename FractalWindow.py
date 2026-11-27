# python
#
# This file is part of the qtFractals distribution
# (https://github.com/OdysseusLSe/qtFractals).
# Copyright (c) 2026 Lavrentios Servissoglou.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Apache 2.0 license as published.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# You should have received a copy of the Apache 2.0 license
# along with this program.
# If not, see <http://www.apache.org/licenses/LICENSE-2.0>.
#

import copy
import random

import pprint as pp

from PySide6.QtCore import QPoint, QRect, Qt, QThread, Signal
from PySide6.QtGui import (
    QBrush,
    QImage,
    QColor,
    QKeySequence,
    QPainter,
    QPen,
    QResizeEvent,
    QShortcut
)
from PySide6.QtWidgets import QMainWindow

from FractalWorker import FractalWorker
from Logging import Logging

#
# -----------------------------------------------
#


class FractalWindow(QMainWindow):

    # Signal for progress of frac calculation
    progress = Signal(int)

    # Signal finished calculation
    closing = Signal(QImage, float)

    # Signal this window is hidden
    hidden = Signal()

    #
    # -----------------------------------------------
    #

    def __init__(self, frac_area, draw_dim, iter_lim, col_pal, frac_set, julia_c):
        super().__init__()
        self.log = Logging("FractalWindow")
        self.log.entry("__init__")

        # Disable/hide the close button
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.hidden.connect(self.hidden.emit)

        self.calc_area = copy.copy(frac_area)
        self.frac_area = copy.copy(frac_area)
        self.draw_dim  = copy.copy(draw_dim)
        self.iter_lim  = iter_lim
        self.cp        = copy.copy(col_pal)
        self.frac_set  = frac_set
        self.julia_c   = julia_c

        self.image        = QImage()
        self.image_2_save = QImage()

        # Offset to centralize the calculated image.
        self.offset_x = 0
        self.offset_y = 0

        # Scaling factor in case calculated image is bigger than the window.
        self.scaling_factor = 1.00

        self.progress_in_percent = 0

        self.update_window_title()

        # First resize event should be ignored.
        self.starting = True

        # Mouse variables for Mandelbrot set selection.
        self.selecting = False
        self.sel_start = None
        self.sel_end   = None
        self.setMouseTracking(True)

        # Mouse variables for Julia set selection.
        self.sel_point = None

        # Create shortcut for ESC key (to stop calculation).
        self.esc_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.esc_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.esc_shortcut.activated.connect(self.stop_calculation)

        # Set start parameters for future thread check.
        self.thread = None
        self.worker = None

        self.start_calculation()

        self.log.exit("__init__")

    #
    # -----------------------------------------------
    #

    def build_history_element(self, thumbnail_name, calc_time):
        params = f"thumbnail_name={thumbnail_name},calc_time={calc_time}"
        self.log.entry(f"build_history_element({params})")

        history_element = {
            'frac_area'    : self.frac_area,
            'draw_dim'     : self.draw_dim,
            'iter_lim'     : self.iter_lim,
            'col_pal'      : self.cp,
            'real_julia_c' : self.julia_c.real,
            'imag_julia_c' : self.julia_c.imag,
            'frac_set'     : self.frac_set,
            'calc_time'    : calc_time,
            'thumbnail'    : thumbnail_name
        }

        self.log.exit("build_history_element")

        return history_element

    #
    # -----------------------------------------------
    # Calculate selection on fractal base
    # -----------------------------------------------
    #

    def calculate_selected_area(self, rect):
        self.log.entry(f"calculate_selected_area(rect={rect})")

        # Check if selected area is to small
        if rect.width() < 5 or rect.height() < 5:
            return False

        self.log.write(f"frac_area={self.frac_area}")

        # Size of the pixel in the complex plane
        xStep = self.frac_area['realWidth'] / self.draw_dim['width']
        yStep = self.frac_area['imagHeight'] / self.draw_dim['height']

        x_shift = (rect.left() - self.offset_x) * self.scaling_factor
        y_shift = (rect.top()  - self.offset_y) * self.scaling_factor
        real_orig = self.frac_area['realOrigin'] + x_shift * xStep
        imag_orig = self.frac_area['imagOrigin'] + y_shift * yStep

        real_width  = rect.width()  * xStep * self.scaling_factor
        imag_height = rect.height() * yStep * self.scaling_factor

        self.calc_area = {
            'realOrigin' : real_orig,
            'imagOrigin' : imag_orig,
            'realWidth'  : real_width,
            'imagHeight' : imag_height
        }
        self.log.write(f"self.calc_area={self.calc_area}")

        self.log.exit("calculate_selected_area")
        return True

    #
    # -----------------------------------------------
    #

    def calculation_finished(self, image, calc_time):
        self.log.entry(f"calculation_finished(image,{calc_time})")

        if image.isNull():
            self.log.error("Missing image!")
            self.log.exit("calculation_finished")
            return

        self.image_2_save = image

        iw = image.width()
        ih = image.height()
        sw = self.width()
        sh = self.height()
        self.log.write(f"iw,ih,sw,sh={iw},{ih},{sw},{sh}")

        self.image = image.scaled(
            sw,
            sh,
            Qt.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.scaling_factor = self.image_2_save.width() / self.image.width()
        self.log.write(f"self.scaling_factor={self.scaling_factor}")

        self.update_window_title()
        self.update()

        # Create thumbnail of the image for history
        self.thumbnail = self.image_2_save.scaledToWidth(
            150,
            Qt.TransformationMode.SmoothTransformation
        )
        self.closing.emit(self.thumbnail, calc_time)

        self.log.exit("calculation_finished")

    #
    # -----------------------------------------------
    #

    def closeEvent(self, event):
        self.log.entry("closeEvent(event)")

        # Inform parent window about closed/hidden window.
        self.hidden.emit()

        self.log.exit("closeEvent")

    #
    # -----------------------------------------------
    #

    def define_julia_parameter(self):
        self.log.entry("define_julia_parameter()")

        x = self.sel_point.x()
        y = self.sel_point.y()
        self.log.write(f"x,y={x},{y}")

        x = self.frac_area['realOrigin'] + x * self.frac_area['realWidth'] / self.draw_dim['width']
        y = self.frac_area['imagOrigin'] + y * self.frac_area['imagHeight'] / self.draw_dim['height']
        self.julia_c = complex(x, y)
        self.log.write(f"self.julia_c={self.julia_c}")

        self.log.exit("define_julia_parameter")

    #
    # -----------------------------------------------
    #

    def get_image(self):
        self.log.entry("get_image()")

        if self.image_2_save.isNull():
            self.log.error("Missing image!")
            self.log.exit("get_image")
            return

        self.log.exit("get_image")
        return self.image_2_save

    #
    # -----------------------------------------------
    #

    def get_parameters(self):
        self.log.entry("get_parameters()")

        self.log.exit("get_parameters")
        return self.frac_area, self.draw_dim, self.iter_lim, self.frac_set, self.julia_c

    #
    # -----------------------------------------------
    #

    # Auswahlquadrat erzeugen

    def get_selection_rect(self):
        self.log.entry("get_selection_rect()")

        x1, y1 = self.sel_start.x(), self.sel_start.y()
        x2, y2 = self.sel_end.x(), self.sel_end.y()
        self.log.write(f"x1,y1={x1},{y1} / x2,y2={x2},{y2}")

        dx = x2 - x1
        dy = y2 - y1

        if dx != 0 and dy != 0:
            delta_ratio = dx / dy
            self.log.write("delta_ratio=" + str(delta_ratio))

            draw_ratio = self.draw_dim['width'] / self.draw_dim['height']
            self.log.write("draw_ratio=" + str(draw_ratio))

            if dx < 0:
                dx = -abs(int(dy * draw_ratio))
            else:
                dx = abs(int(dy * draw_ratio))
            self.log.write(f"adapted dx,dy={dx},{dy}")

            delta_ratio = dx / dy
            self.log.write("adapted delta_ratio=" + str(delta_ratio))

        # Length/Width of the rectangle. Take the shorter one.
        size = min(abs(dx), abs(dy))
        if size <= 0:
            self.log.write("Selection area too small!")
            self.log.exit("get_selection_rect")
            return QRect(x1, y1, 0, 0)

        #
        # Determine the top-left corner of the rectangle based on the direction
        # of the drag.
        #

        if dx >= 0:
            x = x1
        else:
            x = x1 - abs(dx)

        if dy >= 0:
            y = y1
        else:
            y = y1 - abs(dy)

        # Rectangle should stay within drawing area

        max_bound_x = self.offset_x + self.draw_dim['width']
        max_bound_y = self.offset_y + self.draw_dim['height']

        if x < self.offset_x:
            x = self.offset_x

        if y < self.offset_y:
            y = self.offset_y

        if x + abs(dx) > max_bound_x:
            x = max_bound_x - abs(dx)

        if y + abs(dy) > max_bound_y:
            y = max_bound_y - abs(dy)

        if x < self.offset_x:
            x = self.offset_x
        if y < self.offset_y:
            y = self.offset_y

        self.log.write(f"x,y,dx,dy={x},{y},{abs(dx)},{abs(dy)}")

        self.calculate_selected_area(QRect(
            int(x),
            int(y),
            int(abs(dx)),
            int(abs(dy))
        ))
        self.log.write("frac_area=" + str(self.frac_area))
        self.log.write("calc_area=" + str(self.calc_area))

        ro = self.calc_area['realOrigin']
        io = self.calc_area['imagOrigin']
        rw = self.calc_area['realWidth']
        ih = self.calc_area['imagHeight']
        status = f"--- Rectangle: Real part: {ro:.15f}, Imag part: {io:.15f}, "
        status = status + f"Width: {rw:.15f}, Height: {ih:.15f}"

        self.log.exit("get_selection_rect")
        return QRect(int(x), int(y), int(abs(dx)), int(abs(dy)))

    #
    # -----------------------------------------------
    #

    # Mouse moved

    def mouseMoveEvent(self, event):
        self.log.entry("mouseMoveEvent")

        if self.selecting:
            self.sel_end = event.position().toPoint()
            self.update()

        super().mouseMoveEvent(event)

        self.log.exit("mouseMoveEvent")

    #
    # -----------------------------------------------
    #

    # Mouse pressed

    def mousePressEvent(self, event):
        self.log.entry("mousePressEvent")

        if event.button() == Qt.MouseButton.RightButton:
            self.log.write("RMB pressed.")
            if hasattr(self, 'thread') and self.thread is not None and self.thread.isRunning():
                self.log.write("Trying to stop running thread.")
                self.worker.stop()
                self.log.exit("mousePressEvent")
                return
            else:
                self.log.write("No running thread to stop.")
                self.log.exit("mousePressEvent")
                return


        if hasattr(self, 'thread') and self.thread is not None and self.thread.isRunning():
            self.log.write("Thread still working!")
            self.log.exit("mousePressEvent")
            return

        if event.button() == Qt.MouseButton.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                # Calculate Julia set at selected coordinations
                self.log.write("LMB and [CMD]/[Control] pressed.")
                self.frac_set = "Julia"
                self.sel_point = (event.position().toPoint())
                self.update()
                self.define_julia_parameter()
                self.start_calculation()
            else:
                # Start selection area to zoom in
                self.log.write("LMB pressed.")
                self.selecting = True
                self.sel_start = (event.position().toPoint())
                self.sel_end = self.sel_start
                self.update()

        super().mousePressEvent(event)

        self.log.exit("mousePressEvent")

    #
    # -----------------------------------------------
    #

    # Mouse released

    def mouseReleaseEvent(self, event):
        self.log.entry("mouseReleaseEvent")

        if event.button() == Qt.MouseButton.LeftButton:
            if self.selecting:
                self.sel_end = event.position().toPoint()
                rect = self.get_selection_rect()
                self.selecting = False
                self.update()
                # Calculate new fractal area
                if self.calculate_selected_area(rect):
                    # Selected area is not to small
                    self.log.write(f"frac_area={self.frac_area}")
                    self.frac_area = copy.copy(self.calc_area)
                    self.start_calculation()

        super().mouseReleaseEvent(event)

        self.log.exit("mouseReleaseEvent")

    #
    # -----------------------------------------------
    # Paint calculated image (called by default)
    # -----------------------------------------------
    #

    def paintEvent(self, event):
        self.log.entry("paintEvent(event)")

        if self.image.isNull():
            self.log.error("Missing image!")
            self.log.exit("paintEvent")
            return

        painter = QPainter(self)

        target_rect = QRect(QPoint(0, 0), self.image.size())
        target_rect.moveCenter(self.rect().center())

        self.offset_x = target_rect.x()
        self.offset_y = target_rect.y()

        painter.drawImage(target_rect, self.image)

        # Draw cursor of selection

        if (
            self.selecting
            and self.sel_start is not None
            and self.sel_end is not None
        ):

            rect = self.get_selection_rect()

            self.selection_color = QColor(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )

            pen = QPen(self.selection_color)
            pen.setWidth(2)
            pen.setStyle(Qt.PenStyle.DashLine)

            painter.setPen(pen)
            fill_color = QColor(
                self.selection_color.red(),
                self.selection_color.green(),
                self.selection_color.blue(),
                100,
            )
            painter.setBrush(QBrush(fill_color))
            painter.drawRect(rect)

            ro = self.calc_area['realOrigin']
            io = self.calc_area['imagOrigin']
            rw = self.calc_area['realWidth']
            ih = self.calc_area['imagHeight']
            self.log.write(f"ro,io,rw,ih={ro},{io},{rw},{ih}")

            window_title = "Selected coordinates: "
            window_title += f"Origin: {ro} , {io} || Size: {rw} x {ih}"
            self.setWindowTitle(window_title)

        self.log.exit("paintEvent")

    #
    # -----------------------------------------------
    #

    def realtime_update(self, image):
        self.log.entry("realtime_update(image)")

        if image.isNull():
            self.log.error("Missing image!")
            self.log.exit("realtime_update")
            return

        self.image_2_save = image

        iw = image.width()
        ih = image.height()
        sw = self.width()
        sh = self.height()
        self.log.write(f"iw,ih,ww,wh={iw},{ih},{sw},{sh}")

        self.image = image.scaled(
            sw,
            sh,
            Qt.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.scaling_factor = self.image_2_save.width() / self.image.width()
        self.log.write(f"self.scaling_factor={self.scaling_factor}")

        self.update_window_title()
        self.update()

        self.log.exit("realtime_update")

    #
    # -----------------------------------------------
    #

    def resizeEvent(self, event: QResizeEvent):
        self.log.entry("resizeEvent(event: QResizeEvent)")

        super().resizeEvent(event)

        if self.starting:
            self.starting = False
            self.log.exit("resizeEvent")
            return

        image = self.image_2_save

        iw = image.width()
        ih = image.height()
        sw = self.width()
        sh = self.height()
        self.log.write(f"iw,ih,sw,sh={iw},{ih},{sw},{sh}")

        self.image = image.scaled(
            sw,
            sh,
            Qt.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )

        self.scaling_factor = self.image_2_save.width() / self.image.width()
        self.log.write(f"self.scaling_factor={self.scaling_factor}")

        self.update_window_title()
        self.update()

        self.log.exit("resizeEvent")


    #
    # -----------------------------------------------
    #

    def set_parameters(self, frac_area, draw_dim, iter_lim, col_pal, frac_set, julia_c):
        self.log.entry("set_parameters")

        self.frac_area = copy.copy(frac_area)
        self.draw_dim  = copy.copy(draw_dim)
        self.iter_lim  = iter_lim
        self.cp        = copy.copy(col_pal)
        self.frac_set  = frac_set
        self.julia_c   = julia_c

        self.log.exit("set_parameters")

    #
    # -----------------------------------------------
    #

    def start_calculation(self):
        self.log.entry("start_calculation()")

        self.log.write(f"self.frac_area={pp.pformat(self.frac_area)}")
        self.log.write(f"self.draw_dim={pp.pformat(self.draw_dim)}")

        # Check if a thread is already running
        if hasattr(self, 'thread') and self.thread is not None and self.thread.isRunning():
            self.log.write("Thread still working!")
            self.log.exit("start_calculation")
            return

        # Create thread and worker
        self.thread = QThread()
        self.worker = FractalWorker(
            self.frac_area,
            self.draw_dim,
            self.iter_lim,
            self.cp,
            self.frac_set,
            self.julia_c
        )

        self.progress_in_percent = 0

        self.worker.moveToThread(self.thread)

        #
        # Connect signals and slots
        #

        if self.frac_set == "Mandelbrot":
            self.thread.started.connect(self.worker.calculate_mandelbrot)
        else:
            self.thread.started.connect(self.worker.calculate_julia)

        self.thread.finished.connect(self.thread_finished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.progress.emit)
        self.worker.progress.connect(self.update_progress)
        self.worker.drawing.connect(self.realtime_update)
        self.worker.finished.connect(self.calculation_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.thread.start()

        log_string = f"self.thread.isRunning()={self.thread.isRunning()}"
        self.log.write(log_string)

        self.log.exit("start_calculation")

    #
    # -----------------------------------------------
    #

    def stop_calculation(self):
        self.log.entry("stop_calculation")

        if hasattr(self, 'thread') and self.thread is not None and self.thread.isRunning():
            self.log.write("Trying to stop running thread.")
            self.worker.stop()
        else:
            self.log.write("No running thread to stop.")

        self.log.exit("stop_calculation")

    #
    # -----------------------------------------------
    #

    def thread_finished(self):
        self.log.entry("thread_finished")

        self.worker = None
        self.thread = None

        self.log.exit("thread_finished")

    #
    # -----------------------------------------------
    #

    def update_progress(self, value):
        self.log.entry(f"update_progress(value={value})")

        self.progress_in_percent = int(value / self.draw_dim['height'] * 100)
        self.update_window_title()

        self.log.exit("update_progress")

    #
    # -----------------------------------------------
    #

    def update_window_title(self):
        self.log.entry("update_window_title()")

        ro = self.frac_area['realOrigin']
        io = self.frac_area['imagOrigin']
        rw = self.frac_area['realWidth']
        ih = self.frac_area['imagHeight']

        w = self.draw_dim['width']
        h = self.draw_dim['height']

        window_title = "qtFractals"
        area = f"Origin: {ro},{io} || Size: {rw}x{ih}"
        area += f" || Resolution: {w}x{h}"
        area += f" || Scaling: 1:{self.scaling_factor:.2f}"
        area += f" || Progress: {self.progress_in_percent}%"
        self.setWindowTitle(f"{window_title} [{area}]")

        self.log.exit("update_window_title")

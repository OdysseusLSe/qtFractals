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
# along with this program. If not, see <http://www.apache.org/licenses/LICENSE-2.0>.
#

import copy

from PySide6.QtCore import Qt, QThread, Signal, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QImage, QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget

import FractalWorker
import Logging


class FractalWidget(QWidget):
    # Signal for progress
    progress = Signal(int)

    #
    # Constructor
    #

    def __init__(self, frac_area, draw_dim, iter_lim, col_pal, current_frac_set, julia_c):
        super().__init__()

        self.log = Logging.Logging("FractalWidget", True)
        self.log.entry("__init__", False)

        self.frac_area        = copy.deepcopy(frac_area)
        self.draw_dim         = copy.deepcopy(draw_dim)
        self.iter_lim         = iter_lim
        self.cp               = copy.deepcopy(col_pal)
        self.current_frac_set = current_frac_set
        self.julia_c          = julia_c

        self.log.write("self.frac_area=" + str(self.frac_area), False)
        self.log.write("self.draw_dim=" + str(self.draw_dim), False)
        self.log.write("self.iter_lim=" + str(self.iter_lim), False)
        self.log.write("self.cp=" + str(self.cp), False)
        self.log.write("self.julia_c=" + str(self.julia_c), False)
        self.log.write("self.current_frac_set=" + str(self.current_frac_set), False)

        self.image = QImage()

        # Mouse variables for mandelbrot selection
        self.selecting = False
        self.sel_start = None
        self.sel_end   = None
        self.setMouseTracking(True)

        # Mouse variables for mandelbrot selection
        self.sel_point = None

        # Create shortcut for ESC key (to stop calculation)
        self.esc_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.esc_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.esc_shortcut.activated.connect(self.stop_calculation)

        # Set start parameter for future thread check
        self.thread = None
        self.worker = None

        self.start_calculation()

        self.log.exit("__init__", False)

    #
    # -----------------------------------------------
    #

    def calculation_finished(self, image):
        self.log.entry("calculation_finished", False)

        self.image = image
        if self.image.isNull():
            self.log.error("Missing image!", False)

        self.setFixedSize(self.draw_dim['width'], self.draw_dim['height'])
        #self.setFixedSize(self.image.width(), self.image.height())

        self.update()

        self.log.exit("calculation_finished", False)

    #
    # -----------------------------------------------
    #

    # Calculate selection on fractal base

    def calculate_selected_area(self, rect):
        self.log.entry("calculate_selected_area", False)

        # Check if selected area is to small
        if rect.width() < 5 or rect.height() < 5:
            return

        # Size of the pixel in the complex plane
        xStep = self.frac_area['realWidth'] / self.draw_dim['width']
        yStep = self.frac_area['imagHeight'] / self.draw_dim['height']

        real_orig = self.frac_area['realOrigin'] + rect.left() * xStep
        imag_orig = self.frac_area['imagOrigin'] + rect.top() * yStep

        real_width  = rect.width()  * xStep
        imag_height = rect.height() * yStep

        newArea = {
            'realOrigin' : real_orig,
            'imagOrigin' : imag_orig,
            'realWidth'  : real_width,
            'imagHeight' : imag_height
        }
        self.log.write("newArea=" + str(newArea), False)

        self.set_parameters(
            newArea,
            self.draw_dim,
            self.iter_lim,
            self.cp,
            self.current_frac_set,
            self.julia_c
        )
        self.start_calculation()

        self.log.exit("calculate_selected_area", False)

    #
    # -----------------------------------------------
    #

    # Calculate selection on fractal base

    def change_col_pal(self, col_pal):
        self.log.entry("change_col_pal", False)

        self.cp = copy.deepcopy(col_pal)
        self.start_calculation()

        self.log.exit("change_col_pal", False)

    #
    # -----------------------------------------------
    #

    def define_julia_parameter(self):
        self.log.entry("define_julia_parameter", False)

        x = self.sel_point.x()
        y = self.sel_point.y()
        self.log.write("x=" + str(x) + " / y=" + str(y), False)

        x = self.frac_area['realOrigin'] + x * self.frac_area['realWidth'] / self.draw_dim['width']
        y = self.frac_area['imagOrigin'] + y * self.frac_area['imagHeight'] / self.draw_dim['height']
        self.julia_c = complex(x, y)
        self.log.write("self.julia_c=(" + str(x) + "," + str(y) + ")", False)

        self.log.exit("define_julia_parameter", False)

    #
    # -----------------------------------------------
    #

    def get_image(self):
        self.log.entry("get_image", False)

        if self.image.isNull():
            self.log.error("Missing image!", False)
            self.log.exit("get_image", False)
            return

        self.log.exit("get_image", False)

        return self.image

    #
    # -----------------------------------------------
    #

    def get_parameters(self):
        self.log.entry("get_parameters", False)

        self.log.exit("get_parameters", False)

        return self.frac_area, self.draw_dim, self.iter_lim, self.current_frac_set, self.julia_c

    #
    # -----------------------------------------------
    #

    # Auswahlquadrat erzeugen

    def get_selection_rect(self):
        self.log.entry("get_selection_rect", False)

        x1, y1 = self.sel_start.x(), self.sel_start.y()
        x2, y2 = self.sel_end.x(), self.sel_end.y()
        self.log.write("x1,y1=" + str(x1) + "," + str(y1) + " / x2,y2=" + str(x2) + "," + str(y2), False)

        dx = x2 - x1
        dy = y2 - y1

        if dx != 0 and dy != 0:
            delta_ratio = dx / dy
            self.log.write("delta_ratio=" + str(delta_ratio), False)

            draw_ratio = self.draw_dim['width'] / self.draw_dim['height']
            self.log.write("draw_ratio=" + str(draw_ratio), False)

            if dx < 0:
                dx = -abs(int(dy * draw_ratio))
            else:
                dx = abs(int(dy * draw_ratio))
            self.log.write("adapted dx=" + str(dx) + " / adapted dy=" + str(dy), False)

            delta_ratio = dx / dy
            self.log.write("adapted delta_ratio=" + str(delta_ratio), False)

        # Length/Width of the rectangle. Take the shorter one.
        size = min(abs(dx), abs(dy))
        if size <= 0:
            self.log.write("Selection area too small!", False)
            self.log.exit("get_selection_rect", False)
            return QRect(x1, y1, 0, 0)

        #
        # Determine the top-left corner of the rectangle based on the direction of the drag
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

        if x < 0:
            x = 0

        if y < 0:
            y = 0

        if x + abs(dx) > self.draw_dim['width']:
            x = self.draw_dim['width'] - abs(dx)

        if y + abs(dy) > self.draw_dim['height']:
            y = self.draw_dim['height'] - abs(dy)

        log_string = "x,y,dx,dy=" + str(x) + "," + str(y) + "," + str(abs(dx)) + "," + str(abs(dy))
        self.log.write(log_string, False)

        self.log.exit("get_selection_rect", False)
        return QRect(int(x), int(y), int(abs(dx)), int(abs(dy)))

    #
    # -----------------------------------------------
    #

    # Mouse moved

    def mouseMoveEvent(self, event):
        self.log.entry("mouseMoveEvent", False)

        if self.selecting:
            self.sel_end = event.position().toPoint()
            self.update()

        super().mouseMoveEvent(event)

        self.log.exit("mouseMoveEvent", False)

    #
    # -----------------------------------------------
    #

    # Mouse pressed

    def mousePressEvent(self, event):
        self.log.entry("mousePressEvent", False)

        if event.button() == Qt.MouseButton.RightButton:
            self.log.write("RMB pressed.", False)
            if hasattr(self, 'thread') and self.thread is not None and self.thread.isRunning():
                self.log.write("Trying to stop running thread.", False)
                self.worker.stop()
                self.log.exit("mousePressEvent", False)
                return
            else:
                self.log.write("No running thread to stop.", False)
                self.log.exit("mousePressEvent", False)
                return


        if hasattr(self, 'thread') and self.thread is not None and self.thread.isRunning():
            self.log.write("Thread still working!", False)
            self.log.exit("mousePressEvent", False)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                # Calculate Julia set at selected coordinations
                self.log.write("LMB and [CMD]/[Control] pressed.", False)
                self.current_frac_set = "Julia"
                self.sel_point = (event.position().toPoint())
                self.update()
                self.define_julia_parameter()
                self.start_calculation()
            else:
                # Start selection area to zoom in
                self.log.write("LMB pressed.", False)
                self.selecting = True
                self.sel_start = (event.position().toPoint())
                self.sel_end = self.sel_start
                self.update()

        super().mousePressEvent(event)

        self.log.exit("mousePressEvent", False)

    #
    # -----------------------------------------------
    #

    # Mouse released

    def mouseReleaseEvent(self, event):
        self.log.entry("mouseReleaseEvent", False)

        if event.button() == Qt.MouseButton.LeftButton:
            if self.selecting:
                self.sel_end = event.position().toPoint()
                rect = self.get_selection_rect()
                self.selecting = False
                self.update()
                # Neuen Fraktalbereich berechnen
                self.calculate_selected_area(rect)

        super().mouseReleaseEvent(event)

        self.log.exit("mouseReleaseEvent", False)

    #
    # Paint calculated image (called by default)
    #

    def paintEvent(self, event):
        self.log.entry("paintEvent", False)

        if self.image.isNull():
            self.log.error("Missing image!", False)
            self.log.exit("paintEvent", False)
            return

        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

        # Draw cursor of selection

        if (self.selecting and self.sel_start is not None and self.sel_end is not None):
            rect = self.get_selection_rect()

            pen = QPen(QColor(255, 255, 255))
            pen.setWidth(2)
            pen.setStyle(Qt.PenStyle.DashLine)

            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

        self.log.exit("paintEvent", False)

    #
    # -----------------------------------------------
    #

    def set_parameters(self, frac_area, draw_dim, iter_lim, col_pal, current_frac_set, julia_c):
        self.log.entry("set_parameters", False)

        self.frac_area        = copy.deepcopy(frac_area)
        self.draw_dim         = copy.deepcopy(draw_dim)
        self.iter_lim         = iter_lim
        self.cp               = copy.deepcopy(col_pal)
        self.current_frac_set = current_frac_set
        self.julia_c          = julia_c

        self.log.write(str(self.frac_area), False)
        self.log.write(str(self.draw_dim), False)
        self.log.write(str(self.iter_lim), False)
        self.log.write(str(self.current_frac_set), False)
        self.log.write(str(self.julia_c), False)

        self.log.exit("set_parameters", False)

    #
    # -----------------------------------------------
    #

    def start_calculation(self):
        self.log.entry("start_calculation", False)

        # Check if a thread is already running
        if hasattr(self, 'thread') and self.thread is not None and self.thread.isRunning():
            self.log.write("Thread still working!", False)
            self.log.exit("start_calculation", False)
            return

        # Create thread and worker
        self.thread = QThread()
        self.worker = FractalWorker.FractalWorker(
            self.frac_area,
            self.draw_dim,
            self.iter_lim,
            self.cp,
            self.current_frac_set,
            self.julia_c
        )
        self.worker.moveToThread(self.thread)

        #
        # Connect signals and slots
        #

        if self.current_frac_set == "Mandelbrot":
            self.thread.started.connect(self.worker.calculate_mandelbrot)
        else:
            self.thread.started.connect(self.worker.calculate_julia)

        self.thread.finished.connect(self.thread_finished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.progress.emit)
        self.worker.finished.connect(self.calculation_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.thread.start()

        self.log.write("self.thread.isRunning()=" + str(self.thread.isRunning()), False)
        self.log.exit("start_calculation", False)

    #
    # -----------------------------------------------
    #

    def stop_calculation(self):
        self.log.entry("stop_calculation", False)

        if hasattr(self, 'thread') and self.thread is not None and self.thread.isRunning():
            self.log.write("Trying to stop running thread.", False)
            self.worker.stop()
        else:
            self.log.write("No running thread to stop.", False)

        self.log.exit("stop_calculation", False)

    #
    # -----------------------------------------------
    #

    def thread_finished(self):
        self.log.entry("thread_finished", False)

        self.worker = None
        self.thread = None

        self.log.exit("thread_finished", False)

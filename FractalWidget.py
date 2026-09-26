import copy

from PySide6.QtCore import Qt, QThread, Signal, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QImage
from PySide6.QtWidgets import QWidget

import FractalWorker
import Logging


class FractalWidget(QWidget):
    # Signal for progress
    progress = Signal(int)

    #
    # Constructor
    #

    def __init__(self, frac_area, draw_dim, iter_lim, col_pal):
        super().__init__()

        self.log = Logging.Logging("FractalWidget", False)
        self.log.entry("init")

        self.frac_area = frac_area
        self.draw_dim = copy.deepcopy(draw_dim)
        self.iter_lim = iter_lim
        self.cp = copy.deepcopy(col_pal)

        self.log.write("frac_area=" + str(self.frac_area))
        self.log.write("draw_dim=" + str(self.draw_dim))

        self.image = QImage()

        # Mouse variables

        self.selecting = False
        self.sel_start = None
        self.sel_end = None
        self.setMouseTracking(True)

        self.start_calculation()

        self.log.exit("init")

    #
    # -----------------------------------------------
    #

    def calculation_finished(self, image):
        self.log.entry("calculation_finished")

        self.image = image
        if self.image.isNull():
            self.log.error("Missing image!")

        self.update()

        self.log.exit("calculation_finished")

    #
    # -----------------------------------------------
    #

    # Calculate selection on fractal base

    def calculate_selected_area(self, rect):
        self.log.entry("calculate_selected_area")

        # Check if selected area is to small
        if rect.width() < 2 or rect.height() < 2:
            return

        # Größe eines Pixels in der komplexen Ebene

        xStep = self.frac_area['realWidth'] / self.draw_dim['width']
        yStep = self.frac_area['imagHeight'] / self.draw_dim['height']

        real_orig = self.frac_area['realOrigin'] + rect.left() * xStep
        imag_orig = self.frac_area['imagOrigin'] + rect.top() * yStep

        real_width = rect.width() * xStep
        imag_height = rect.height() * yStep

        newArea = {
            'realOrigin' : real_orig,
            'imagOrigin' : imag_orig,
            'realWidth'  : real_width,
            'imagHeight' : imag_height
        }
        self.log.write("newArea=" + str(newArea))

        self.set_parameters(newArea, self.draw_dim, self.iter_lim, self.cp)
        self.start_calculation()

        self.log.exit("calculate_selected_area")

    #
    # -----------------------------------------------
    #

    # Calculate selection on fractal base

    def change_col_pal(self, col_pal):
        self.log.entry("change_col_pal")

        self.cp = copy.deepcopy(col_pal)

        self.log.exit("change_col_pal")

    #
    # -----------------------------------------------
    #

    def get_image(self):
        self.log.entry("get_image")

        if self.image.isNull():
            self.log.error("Missing image!")
            return

        self.log.exit("get_image")

        return self.image

    #
    # -----------------------------------------------
    #

    def get_parameters(self):
        self.log.entry("get_parameters")

        self.log.exit("get_parameters")

        return self.frac_area, self.draw_dim, self.iter_lim

    #
    # -----------------------------------------------
    #

    # Auswahlquadrat erzeugen

    def get_selection_rect(self):
        self.log.entry("get_selection_rect")

        x1 = self.sel_start.x()
        y1 = self.sel_start.y()
        self.log.write("x1=" + str(x1) + " / y1=" + str(y1))

        x2 = self.sel_end.x()
        y2 = self.sel_end.y()
        self.log.write("x2=" + str(x2) + " / y2=" + str(y2))

        dx = x2 - x1
        dy = y2 - y1
        self.log.write("dx=" + str(dx) + " / dy=" + str(dy))

        if dx != 0 and dy != 0:
            delta_ratio = dx / dy
            self.log.write("delta_ratio =" + str(delta_ratio))

            draw_ratio = self.draw_dim['width'] / self.draw_dim['height']
            self.log.write("draw_ratio =" + str(draw_ratio))

            if dx < 0:
                dx = -abs(int(dy * draw_ratio))
            else:
                dx = abs(int(dy * draw_ratio))
            delta_ratio = dx / dy
            self.log.write("adapted delta_ratio=" + str(delta_ratio))
            self.log.write("adapted dx=" + str(dx) + " / adapted dy=" + str(dy))

        # Length/Width of the rectangle. Take the shorter one.
        size = min(abs(dx), abs(dy))
        if size <= 0:
            return QRect(x1, y1, 0, 0)

        # Richtung bestimmen

        if dx >= 0:
            left = x1
        else:
            left = x1 - abs(dx)

        if dy >= 0:
            top = y1
        else:
            top = y1 - abs(dy)

        # Rectangle should stay within drawing area

        if left < 0:
            left = 0

        if top < 0:
            top = 0

        if left + abs(dx) > self.draw_dim['width']:
            left = self.draw_dim['width'] - abs(dx)

        if top + abs(dy) > self.draw_dim['height']:
            top = self.draw_dim['height'] - abs(dy)

        self.log.exit("get_selection_rect")

        return QRect(int(left), int(top), int(abs(dx)), int(abs(dy)))

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
        self.log.entry("mousePressEvent")

        if self.thread is not None:
            self.log.write("Thread still working!")
            return

        if event.button() == Qt.MouseButton.LeftButton:
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
                # Neuen Fraktalbereich berechnen
                self.calculate_selected_area(rect)

        super().mouseReleaseEvent(event)

        self.log.exit("mouseReleaseEvent")

    #
    # Paint calculated image (called by default)
    #

    def paintEvent(self, event):
        self.log.entry("paintEvent")

        if self.image.isNull():
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

        self.log.exit("paintEvent")

    #
    # -----------------------------------------------
    #

    def set_parameters(self, frac_area, draw_dim, iter_lim, col_pal):
        self.log.entry("set_parameters")

        self.frac_area = frac_area
        self.draw_dim = copy.deepcopy(draw_dim)
        self.iter_lim = iter_lim
        self.cp = copy.deepcopy(col_pal)

        self.log.write(str(self.frac_area))
        self.log.write(str(self.draw_dim))
        self.log.write(str(self.iter_lim))

        self.setFixedSize(self.draw_dim['width'], self.draw_dim['height'])

        self.log.exit("set_parameters")

    #
    # -----------------------------------------------
    #

    def start_calculation(self):
        self.log.entry("start_calculation")

        # Thread/Worker

        self.thread = QThread()
        self.worker = FractalWorker.FractalWorker(
            self.frac_area,
            self.draw_dim,
            self.iter_lim,
            self.cp
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.calculate)
        self.thread.finished.connect(self.thread_finished)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.progress.connect(self.progress)

        self.worker.finished.connect(self.calculation_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.thread.start()

        self.log.write("self.thread.isRunning()=" + str(self.thread.isRunning()))
        self.log.exit("start_calculation")

    #
    # -----------------------------------------------
    #

    def thread_finished(self):
        self.log.entry("thread_finished")

        self.worker = None
        self.thread = None

        self.log.exit("thread_finished")

import copy

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QImage
from PyQt6.QtWidgets import QWidget

import FractalWorker
import Logging

class FractalWidget(QWidget):
    # Signal for progress
    progress = pyqtSignal(int)

    #
    # Constructor
    #

    def __init__(self, fractalArea, drawDimensions, iterationLimit, colorPalette):
        super().__init__()

        self.log = Logging.Logging("FractalWidget", True)
        self.log.entry("init")

        self.fractalArea = fractalArea
        self.drawDimensions = copy.deepcopy(drawDimensions)
        self.iterationLimit = iterationLimit
        self.colorPalette = copy.deepcopy(colorPalette)

        self.log.write("fractalArea=" + str(self.fractalArea))
        self.log.write("drawDimensions=" + str(self.drawDimensions))

        self.image = QImage()

        # Mouse variables

        self.selecting = False
        self.selectionStart = None
        self.selectionEnd = None
        self.setMouseTracking(True)

        self.startCalculation()

        self.log.exit("init")

    #
    # -----------------------------------------------
    #

    def calculationFinished(self, image):
        self.log.entry("calculationFinished")

        self.image = image
        if self.image.isNull():
            self.log.error("Missing image!")

        self.update()

        self.log.exit("calculationFinished")

    #
    # -----------------------------------------------
    #

    # Calculate selection on fractal base

    def calculateSelectedArea(self, rect):
        self.log.entry("calculateSelectedArea")

        # Check if selected area is to small
        if rect.width() < 2 or rect.height() < 2:
            return

        # Größe eines Pixels in der komplexen Ebene

        xStep = self.fractalArea['realWidth'] / self.drawDimensions['width']
        yStep = self.fractalArea['imagHeight'] / self.drawDimensions['height']

        realOrigin = self.fractalArea['realOrigin'] + rect.left() * xStep
        imagOrigin = self.fractalArea['imagOrigin'] + rect.top() * yStep

        realWidth = rect.width() * xStep
        imagHeight = rect.height() * yStep

        newArea = {
            'realOrigin': realOrigin,
            'imagOrigin': imagOrigin,
            'realWidth': realWidth,
            'imagHeight': imagHeight
        }
        self.log.write("newArea=" + str(newArea))

        self.setParameters(newArea, self.drawDimensions, self.iterationLimit, self.colorPalette)
        self.startCalculation()

    #
    # -----------------------------------------------
    #

    # Calculate selection on fractal base

    def changeColorPalette(self, colorPalette):
        self.log.entry("changeColorPalette")

        self.colorPalette = copy.deepcopy(colorPalette)
        self.log.exit("changeColorPalette")

    #
    # -----------------------------------------------
    #

    def getImage(self):
        self.log.entry("getImage")

        if self.image.isNull():
            self.log.error("Missing image!")
            return

        self.log.exit("getImage")

        return self.image

    #
    # -----------------------------------------------
    #

    def getParameters(self):
        self.log.entry("getFractalArea")

        self.log.exit("getFractalArea")
        return self.fractalArea, self.drawDimensions, self.iterationLimit

    #
    # -----------------------------------------------
    #

    # Auswahlquadrat erzeugen

    def getSelectionRect(self):
        self.log.entry("getSelectionRect")

        x1 = self.selectionStart.x()
        y1 = self.selectionStart.y()
        self.log.write("x1=" + str(x1) + " / y1=" + str(y1))

        x2 = self.selectionEnd.x()
        y2 = self.selectionEnd.y()
        self.log.write("x2=" + str(x2) + " / y2=" + str(y2))

        dx = x2 - x1
        dy = y2 - y1
        self.log.write("dx=" + str(dx) + " / dy=" + str(dy))

        if dx != 0 and dy != 0:
            deltaRatio = dx / dy
            self.log.write("rectRatio     =" + str(deltaRatio))

            drawingRatio = self.drawDimensions['width'] / self.drawDimensions['height']
            self.log.write("drawingRatio  =" + str(drawingRatio))

            if dx < 0:
                dx = -abs(int(dy * drawingRatio))
            else:
                dx = abs(int(dy * drawingRatio))
            deltaRatio = dx / dy
            self.log.write("correctedRatio=" + str(deltaRatio))
            self.log.write("corrected dx=" + str(dx) + " / corrected dy=" + str(dy))

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

        if left + abs(dx) > self.drawDimensions['width']:
            left = self.drawDimensions['width'] - abs(dx)

        if top + abs(dy) > self.drawDimensions['height']:
            top = self.drawDimensions['height'] - abs(dy)

        self.log.exit("getSelectionRect")

        return QRect(int(left), int(top), int(abs(dx)), int(abs(dy)))

    #
    # -----------------------------------------------
    #

    # Mouse moved

    def mouseMoveEvent(self, event):
        self.log.entry("mouseMoveEvent")

        if self.selecting:
            self.selectionEnd = event.position().toPoint()
            self.update()

        super().mouseMoveEvent(event)

        self.log.exit("mouseMoveEvent")

    #
    # -----------------------------------------------
    #

    # Mouse pressed

    def mousePressEvent(self, event):
        self.log.entry("mousePressEvent")

        if self.thread != None:
            self.log.write("Thread still working!")
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.selecting = True
            self.selectionStart = (event.position().toPoint())
            self.selectionEnd = self.selectionStart
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
                self.selectionEnd = event.position().toPoint()
                rect = self.getSelectionRect()
                self.selecting = False
                self.update()
                # Neuen Fraktalbereich berechnen
                self.calculateSelectedArea(rect)

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

        if (self.selecting and self.selectionStart is not None and self.selectionEnd is not None):
            rect = self.getSelectionRect()

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

    def setParameters(self, fractalArea, drawDimensions, iterationLimit, colorPalette):
        self.log.entry("setFractalArea")

        self.fractalArea = fractalArea
        self.drawDimensions = copy.deepcopy(drawDimensions)
        self.iterationLimit = iterationLimit
        self.colorPalette = copy.deepcopy(colorPalette)

        self.log.write(str(self.fractalArea))
        self.log.write(str(self.drawDimensions))
        self.log.write(str(self.iterationLimit))

        self.setFixedSize(self.drawDimensions['width'], self.drawDimensions['height'])

        self.log.exit("setFractalArea")

    #
    # -----------------------------------------------
    #

    def startCalculation(self):
        self.log.entry("startCalculation")

        # Thread/Worker

        self.thread = QThread()
        self.worker = FractalWorker.FractalWorker(
            self.fractalArea,
            self.drawDimensions,
            self.iterationLimit,
            self.colorPalette
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.calculate)
        self.thread.finished.connect(self.threadFinished)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.progress.connect(self.progress)

        self.worker.finished.connect(self.calculationFinished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.thread.start()

        self.log.write("self.thread.isRunning()=" + str(self.thread.isRunning()))
        self.log.exit("startCalculation")

    #
    # -----------------------------------------------
    #

    def threadFinished(self):
        self.log.entry("threadFinished")

        self.worker = None
        self.thread = None

        self.log.exit("threadFinished")
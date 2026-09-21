import copy
import math

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QColor, QPainter
from PyQt6.QtWidgets import QWidget

import Logging

class FractalWorker(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(QImage)

    def __init__(self, fractalArea, drawDimensions, iterationLimit, colorPalette):
        super().__init__()

        self.log = Logging.Logging("FractalWorker", True)
        self.log.entry("init")

        self.fractalArea = fractalArea
        self.drawDimensions = copy.deepcopy(drawDimensions)
        self.iterationLimit = iterationLimit
        self.colorPalette = copy.deepcopy(colorPalette)
        # self.log.write("self.colorPalette=" + str(self.colorPalette))

    @pyqtSlot()
    def calculate(self):

        self.log.write("calculate")

        image = QImage(
            self.drawDimensions['width'],
            self.drawDimensions['height'],
            QImage.Format.Format_RGB32
        )
        color = QColor()

        x = y = 0

        image.fill(QColor(0, 0, 0))

        xStep = self.fractalArea['realWidth'] / self.drawDimensions['width']
        yStep = self.fractalArea['imagHeight'] / self.drawDimensions['height']

        realOrigin = self.fractalArea['realOrigin']
        imagOrigin = self.fractalArea['imagOrigin']

        valueLimitSquared = 4.0

        realPart = self.fractalArea['realOrigin']
        imagPart = self.fractalArea['imagOrigin']

        while y < self.drawDimensions['height']:

            while x < self.drawDimensions['width']:

                c = complex(realPart, imagPart)
                z = 0 + 0j
                loop = 0
                while loop < self.iterationLimit:
                    loop = loop + 1
                    z = z * z + c
                    valueSquared = z.real * z.real + z.imag * z.imag
                    if valueSquared > valueLimitSquared:
                        break

                if valueSquared > valueLimitSquared:

                    # c is not part of the mandelbrot set
                    r, g, b = self.getMandelbrotColor(loop, abs(math.sqrt(valueSquared)))
                    color.setRgb(r, g, b)
                    image.setPixelColor(x, y, color)

                else:
                    # c is part of the mandelbrot set
                    image.setPixelColor(x, y, QColor(0, 0, 0))

                x = x + 1
                realPart = realPart + xStep

            x = 0
            realPart = self.fractalArea['realOrigin']

            y = y + 1
            imagPart = imagPart + yStep

            self.progress.emit(y)

        self.log.exit("init")

        self.finished.emit(image)

    #
    # -----------------------------------------------
    #

    def getMandelbrotColor(self, loop, value):
        self.log.entry("getMandelbrotColor")

        # Calculate smoothed iteration value
        smoothed = loop + 1 - math.log(math.log(value)) / math.log(2.0)

        # Normed value between 0.0 and 1.0 (higher value = higher frequence of color change)
        velocity = smoothed / 40.0

        # self.log.write("smoothed=" + str(smoothed) + " / " + "velocity=" +str(velocity))

        #
        # Define cosinus palette (phase value defines time shifted increase of r,g,b):
        # color(velocity) = brightness + contrast * math.cos(2 * math.pi * (frequency * velocity + phase))
        #

        b = self.colorPalette['brightnessR']
        c = self.colorPalette['contrastR']
        f = self.colorPalette['frequencyR']
        p = self.colorPalette['phaseR']
        red = int(255 * (b + c * math.cos(2 * math.pi * (f * velocity + p))))

        b = self.colorPalette['brightnessG']
        c = self.colorPalette['contrastG']
        f = self.colorPalette['frequencyG']
        p = self.colorPalette['phaseG']
        green = int(255 * (b + c * math.cos(2 * math.pi * (f * velocity + p))))

        b = self.colorPalette['brightnessB']
        c = self.colorPalette['contrastB']
        f = self.colorPalette['frequencyB']
        p = self.colorPalette['phaseB']
        blue = int(255 * (b + c * math.cos(2 * math.pi * (f * velocity + p))))

        self.log.exit("getMandelbrotColor")

        return red, green, blue
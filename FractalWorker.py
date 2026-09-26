import copy
import math

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage, QColor

import Logging


class FractalWorker(QObject):
    progress = Signal(int)
    finished = Signal(QImage)

    def __init__(self, frac_area, draw_dim, iter_lim, col_pal):
        super().__init__()

        self.log = Logging.Logging("FractalWorker", False)
        self.log.entry("init")

        self.frac_area = frac_area
        self.draw_dim = copy.deepcopy(draw_dim)
        self.iter_lim = iter_lim
        self.cp = copy.deepcopy(col_pal)
        self.log.write("self.cp=" + str(self.cp), True)

    @Slot()
    def calculate(self):

        self.log.write("calculate")

        image = QImage(
            self.draw_dim['width'],
            self.draw_dim['height'],
            QImage.Format.Format_RGB32
        )
        color = QColor()

        x = y = 0

        image.fill(QColor(0, 0, 0))

        xStep = self.frac_area['realWidth'] / self.draw_dim['width']
        yStep = self.frac_area['imagHeight'] / self.draw_dim['height']

        #realOrigin = self.frac_area['realOrigin']
        #imagOrigin = self.frac_area['imagOrigin']

        valueLimitSquared = 4.0

        realPart = self.frac_area['realOrigin']
        imagPart = self.frac_area['imagOrigin']

        while y < self.draw_dim['height']:

            while x < self.draw_dim['width']:

                c = complex(realPart, imagPart)
                z = 0 + 0j
                loop = 0
                while loop < self.iter_lim:
                    loop = loop + 1
                    z = z * z + c
                    valueSquared = z.real * z.real + z.imag * z.imag
                    if valueSquared > valueLimitSquared:
                        break

                if valueSquared > valueLimitSquared:

                    # c is not part of the mandelbrot set
                    r, g, b = self.get_mandelbrot_color(loop, abs(math.sqrt(valueSquared)))
                    color.setRgb(r, g, b)
                    image.setPixelColor(x, y, color)

                else:
                    # c is part of the mandelbrot set
                    image.setPixelColor(x, y, QColor(0, 0, 0))

                x = x + 1
                realPart = realPart + xStep

            x = 0
            realPart = self.frac_area['realOrigin']

            y = y + 1
            imagPart = imagPart + yStep

            self.progress.emit(y)

        self.log.exit("init")

        self.finished.emit(image)

    #
    # -----------------------------------------------
    #

    def get_mandelbrot_color(self, loop, value):
        self.log.entry("get_mandelbrot_color", False)

        # Calculate smoothed iteration value
        smoothed = loop + 1 - math.log(math.log(value)) / math.log(2.0)

        # Normed value between 0.0 and 1.0 (higher value = higher frequence of color change)
        velocity = smoothed / 40.0

        self.log.write("smoothed=" + str(smoothed) + " / " + "velocity=" +str(velocity), False)

        #
        # Define cosinus palette (phase value defines time shifted increase of r,g,b):
        # color(velocity) = brightness + contrast * math.cos(2 * math.pi * (frequency * velocity + phase))
        #

        b = self.cp['brightnessR']
        c = self.cp['contrastR']
        f = self.cp['frequencyR']
        p = self.cp['phaseR']
        red = int(255 * (b + c * math.cos(2 * math.pi * (f * velocity + p))))

        b = self.cp['brightnessG']
        c = self.cp['contrastG']
        f = self.cp['frequencyG']
        p = self.cp['phaseG']
        green = int(255 * (b + c * math.cos(2 * math.pi * (f * velocity + p))))

        b = self.cp['brightnessB']
        c = self.cp['contrastB']
        f = self.cp['frequencyB']
        p = self.cp['phaseB']
        blue = int(255 * (b + c * math.cos(2 * math.pi * (f * velocity + p))))

        self.log.exit("get_mandelbrot_color", False)

        return red, green, blue

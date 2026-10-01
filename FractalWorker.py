import copy
import math
#import numpy as np

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage, QColor

import Logging


class FractalWorker(QObject):
    progress = Signal(int)
    finished = Signal(QImage)

    def __init__(self, frac_area, draw_dim, iter_lim, col_pal, julia_c):
        super().__init__()

        self.log = Logging.Logging("FractalWorker", True)
        self.log.entry("__init__", True)

        self.frac_area = copy.deepcopy(frac_area)
        self.draw_dim = copy.deepcopy(draw_dim)
        self.iter_lim = iter_lim
        self.cp = copy.deepcopy(col_pal)
        self.julia_c = julia_c

        self.log.write("self.frac_area=" + str(self.frac_area), True)
        self.log.write("self.draw_dim=" + str(self.draw_dim), True)
        self.log.write("self.iter_lim=" + str(self.iter_lim), True)
        self.log.write("self.cp=" + str(self.cp), True)
        self.log.write("self.julia_c=" + str(self.julia_c), True)

        self.log.exit("__init__", True)

    #
    # -----------------------------------------------
    #

    @Slot()
    def calculate_julia(self):

        self.log.entry("calculate_julia", True)

        image = QImage(
            self.draw_dim['width'],
            self.draw_dim['height'],
            QImage.Format.Format_RGB32
        )
        color = QColor()

        #self.julia_c = complex(-0.1, 0.65)

        x = y = 0

        image.fill(QColor(0, 0, 0))

        x_step = self.frac_area['realWidth'] / self.draw_dim['width']
        y_step = self.frac_area['imagHeight'] / self.draw_dim['height']

        val_lim_squared = 4.0

        real_part = self.frac_area['realOrigin']
        imag_part = self.frac_area['imagOrigin']

        while y < self.draw_dim['height']:

            while x < self.draw_dim['width']:

                self.log.write("x=" + str(x) + " / y=" + str(y), False)

                z = (x_step * x + real_part) + (y_step * y + imag_part) * 1j
                loop = 0
                while loop < self.iter_lim:
                    loop = loop + 1
                    z = z * z + self.julia_c
                    val_squared = z.real * z.real + z.imag * z.imag
                    if val_squared > val_lim_squared:
                        break

                if val_squared > val_lim_squared:

                    self.log.write("loop=" + str(loop), False)
                    # z is not part of the Julia set
                    r, g, b = self.get_color(loop, abs(math.sqrt(val_squared)))
                    color.setRgb(r, g, b)
                    image.setPixelColor(x, y, color)

                else:
                    self.log.write("NOT val_squared > val_lim_squared", False)
                    # z is part of the Julia set
                    image.setPixelColor(x, y, QColor(0, 0, 0))

                x = x + 1
                real_part = real_part + x_step

            x = 0
            real_part = self.frac_area['realOrigin']

            y = y + 1
            imag_part = imag_part + y_step

            self.progress.emit(y)

        self.log.exit("calculate_julia", True)

        self.finished.emit(image)

    #
    # -----------------------------------------------
    #

    @Slot()
    def calculate_mandelbrot(self):

        self.log.entry("calculate_mandelbrot", True)

        image = QImage(
            self.draw_dim['width'],
            self.draw_dim['height'],
            QImage.Format.Format_RGB32
        )
        color = QColor()

        x = y = 0

        image.fill(QColor(0, 0, 0))

        x_step = self.frac_area['realWidth'] / self.draw_dim['width']
        y_step = self.frac_area['imagHeight'] / self.draw_dim['height']

        val_lim_squared = 4.0

        real_part = self.frac_area['realOrigin']
        imag_part = self.frac_area['imagOrigin']

        while y < self.draw_dim['height']:

            while x < self.draw_dim['width']:

                c = complex(real_part, imag_part)
                z = 0 + 0j
                loop = 0
                while loop < self.iter_lim:
                    loop = loop + 1
                    z = z * z + c
                    val_squared = z.real * z.real + z.imag * z.imag
                    if val_squared > val_lim_squared:
                        break

                if val_squared > val_lim_squared:

                    # c is not part of the mandelbrot set
                    r, g, b = self.get_color(loop, abs(math.sqrt(val_squared)))
                    color.setRgb(r, g, b)
                    image.setPixelColor(x, y, color)

                else:
                    # c is part of the mandelbrot set
                    image.setPixelColor(x, y, QColor(0, 0, 0))

                x = x + 1
                real_part = real_part + x_step

            x = 0
            real_part = self.frac_area['realOrigin']

            y = y + 1
            imag_part = imag_part + y_step

            self.progress.emit(y)

        self.log.exit("calculate_mandelbrot", True)

        self.finished.emit(image)

    #
    # -----------------------------------------------
    #

    def get_color(self, loop, value):
        self.log.entry("get_color", False)

        # Calculate smoothed iteration value
        smoothed = loop + 1 - math.log(math.log(value)) / math.log(2.0)

        # Normed value between 0.0 and 1.0 (higher value = higher frequence of color change)
        velocity = smoothed / 40.0

        self.log.write("smoothed=" + str(smoothed) + " / " + "velocity=" + str(velocity), False)

        #
        # Cosine Palette-Method
        # (based on Inigo Quilez, phase value defines time shifted increase of r,g,b):
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

        self.log.exit("get_color", False)

        return red, green, blue

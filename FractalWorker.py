import copy
import math

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage, QColor

import Logging


class FractalWorker(QObject):
    progress = Signal(int)
    finished = Signal(QImage)

    def __init__(
            self,
            frac_area,
            draw_dim,
            iter_lim,
            col_pal,
            current_frac_set=None,
            julia_c=complex(0, 0)
        ):
        super().__init__()

        self.log = Logging.Logging("FractalWorker", True)
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

        self.log.exit("__init__", False)

    #
    # -----------------------------------------------
    #

    @Slot()
    def calculate_julia(self):

        self.log.entry("calculate_julia", False)

        image = QImage(self.draw_dim['width'], self.draw_dim['height'], QImage.Format.Format_RGB32)
        color = QColor()

        # Fill background with black color
        image.fill(QColor(0, 0, 0))

        x = y = 0

        x_step = self.frac_area['realWidth'] / self.draw_dim['width']
        y_step = self.frac_area['imagHeight'] / self.draw_dim['height']

        val_lim_squared = 4.0

        #real_part = self.frac_area['realOrigin']
        #imag_part = self.frac_area['imagOrigin']

        for y in range(self.draw_dim['height']):

            imag_part = self.frac_area['imagOrigin'] + y * y_step

            for x in range(self.draw_dim['width']):

                real_part = self.frac_area['realOrigin'] + x * x_step

                self.log.write("x=" + str(x) + " / y=" + str(y), False)

                z = complex(real_part, imag_part)
                loop = 0
                val_squared = 0.0
                
                while loop < self.iter_lim:
                    z = z * z + self.julia_c
                    val_squared = z.real * z.real + z.imag * z.imag
                    if val_squared > val_lim_squared:
                        break
                    loop = loop + 1

                if val_squared > val_lim_squared:
                    r, g, b = self.get_color(loop, math.sqrt(val_squared))
                    color.setRgb(r, g, b)
                    image.setPixelColor(x, y, color)
                else:
                    image.setPixelColor(x, y, QColor(0, 0, 0))

                loop = 0
                while loop < self.iter_lim:
                    loop = loop + 1
                    z = z * z + self.julia_c
                    val_squared = z.real * z.real + z.imag * z.imag
                    if val_squared > val_lim_squared:
                        break

            self.progress.emit(y)

        self.log.exit("calculate_julia", False)

        self.finished.emit(image)

    #
    # -----------------------------------------------
    #

    @Slot()
    def calculate_mandelbrot(self):

        self.log.entry("calculate_mandelbrot", False)

        image = QImage(self.draw_dim['width'], self.draw_dim['height'], QImage.Format.Format_RGB32)
        color = QColor()

        # Fill background with black color
        image.fill(QColor(0, 0, 0))

        x = y = 0

        x_step = self.frac_area['realWidth'] / self.draw_dim['width']
        y_step = self.frac_area['imagHeight'] / self.draw_dim['height']

        val_lim_squared = 4.0

        #real_part = self.frac_area['realOrigin']
        #imag_part = self.frac_area['imagOrigin']

        for y in range(self.draw_dim['height']):
            
            imag_part = self.frac_area['imagOrigin'] + y * y_step

            for x in range(self.draw_dim['width']):
                
                real_part = self.frac_area['realOrigin'] + x * x_step

                c = complex(real_part, imag_part)
                z = 0.0 + 0.0j
                loop = 0
                val_squared = 0.0

                while loop < self.iter_lim:
                    z = z * z + c
                    val_squared = z.real * z.real + z.imag * z.imag
                    if val_squared > val_lim_squared:
                        break
                    loop += 1

                if val_squared > val_lim_squared:
                    # c is not part of the mandelbrot set
                    r, g, b = self.get_color(loop, math.sqrt(val_squared))
                    color.setRgb(r, g, b)
                    image.setPixelColor(x, y, color)
                else:
                    image.setPixelColor(x, y, QColor(0, 0, 0))

            self.progress.emit(y)

        self.log.exit("calculate_mandelbrot", False)

        self.finished.emit(image)

    #
    # -----------------------------------------------
    #

    def get_color(self, loop, value):
        self.log.entry("get_color", False)

        # Safeguard against logarithm of values <= 1 or 0 (important for extreme close boundary values)
        if value <= 1.0:
            value = 1.0001

        # Calculate smoothed iteration value
        try:
            smoothed = loop + 1 - math.log(math.log(value)) / math.log(2.0)
        except ValueError:
            smoothed = loop

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

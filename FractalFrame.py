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
import math

from PySide6.QtCore import (
    QObject
)
from PySide6.QtGui import (
    QImage,
    QColor
)

from Logging import Logging


class FractalFrame(QObject):

    def __init__(self):
        super().__init__()

        self.log = Logging("FractalFrame", True)
        self.log.entry("__init__", False)

        self.is_running = True

        self.log.exit("__init__", False)

    #
    # -----------------------------------------------
    # Calculate Mandelbrot set
    # -----------------------------------------------
    #

    def mandelbrot_frame(self, frac_area, iter_lim, dd_width, dd_height, cp):
        self.log.entry("mandelbrot_frame", False)

        frac_area = copy.deepcopy(frac_area)

        self.log.write("frac_area=" + str(frac_area), False)
        self.log.write("iter_lim=" + str(iter_lim), False)
        self.log.write(f"dd_width,dd_height={dd_width},{dd_height}", False)
        self.log.write("cp=" + str(cp), False)

        image = QImage(dd_width, dd_height, QImage.Format.Format_RGB32)
        color = QColor()

        # Fill background with background color
        image.fill(QColor(cp['bg_R'], cp['bg_G'], cp['bg_B']))

        x = y = 0

        x_step = frac_area['realWidth'] / dd_width
        y_step = frac_area['imagHeight'] / dd_height

        real_origin = frac_area['realOrigin']
        imag_origin = frac_area['imagOrigin']

        val_lim_squared = 4.0

        log_2  = math.log(2.0)
        pi_x_2 = math.pi * 2

        # Build local lookups
        local_cos  = math.cos
        local_log  = math.log
        local_sqrt = math.sqrt

        for y in range(dd_height):

            if not self.is_running:
                # Boolean flag to stop the thread (initiated by the user)
                self.log.write("Thread stopped by user.", False)
                self.progress.emit(self.draw_dim['height'])
                self.log.exit("calculate_mandelbrot", False)
                break

            imag_part = imag_origin + y * y_step

            self.line = []

            for x in range(dd_width):

                real_part = real_origin + x * x_step

                c = complex(real_part, imag_part)
                z = complex(0.0, 0.0)

                loop = 0
                value_squared = 0.0

                while loop < iter_lim:
                    z = z * z + c
                    value_squared = z.real * z.real + z.imag * z.imag
                    if value_squared > val_lim_squared:

                        # Calculate color and smoothed color transfers.

                        value = local_sqrt(value_squared)

                        # Calculate smoothed iteration value
                        try:
                            smoothed = loop + 1 - local_log(local_log(value)) / log_2
                        except ValueError:
                            self.log.error(f"ValueError: loop,value={loop},{value}", True)
                            smoothed = loop

                        # Normed value between 0.0 and 1.0 (the higher value the
                        # higher frequency of color change)
                        velocity = smoothed / 40.0

                        # Cosine Palette-Method
                        rgb = {}
                        for channel in ['R', 'G', 'B']:
                            b = cp[f'brightness{channel}']
                            c = cp[f'contrast{channel}']
                            f = cp[f'frequency{channel}']
                            p = cp[f'phase{channel}']

                            # Calculate raw color value based on cosine palette
                            # method.
                            raw_val = int(255 * (b + c * local_cos(pi_x_2 * (f * velocity + p))))

                            # Implement safeguard to ensure that the color value
                            # is within the valid range of 0-255.
                            clipped_val  = max(0, min(255, raw_val))
                            rgb[channel] = clipped_val

                        color.setRgb(rgb['R'], rgb['G'], rgb['B'])
                        image.setPixelColor(x, y, color)

                        break

                    loop += 1

        self.log.exit("mandelbrot_frame", False)

        return image

    #
    # -----------------------------------------------
    # Parent widget informs the worker that calculation has to be stopped
    # -----------------------------------------------
    #

    def stop(self):
        self.log.entry("stop", False)
        self.is_running = False
        self.log.exit("stop", False)
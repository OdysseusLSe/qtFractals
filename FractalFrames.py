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

import Logging


class FractalFrames(QObject):

    def __init__(self):
        super().__init__()

        self.log = Logging.Logging("FractalFrames", True)
        self.log.entry("__init__", False)

        self.is_running = True

        self.log.exit("__init__", False)

    #
    # -----------------------------------------------
    # Calculate Mandelbrot set
    # -----------------------------------------------
    #

    def mandelbrot_frame(
            self,
            frac_area,
            iter_lim,
            dd_width,
            dd_height,
            cp
        ):
        self.log.entry("mandelbrot_frame", False)

        frac_area        = copy.deepcopy(frac_area)

        self.log.write("frac_area=" + str(frac_area), False)
        self.log.write("iter_lim=" + str(iter_lim), False)
        self.log.write(f"dd_width,dd_height={dd_width},{dd_height}", False)
        self.log.write("cp=" + str(cp), False)

        image = QImage(dd_width, dd_height, QImage.Format.Format_RGB32)
        color = QColor()

        # Fill background with black color
        image.fill(QColor(0, 0, 0))

        x = y = 0

        x_step = frac_area['realWidth'] / dd_width
        y_step = frac_area['imagHeight'] / dd_height

        real_origin = frac_area['realOrigin']
        imag_origin = frac_area['imagOrigin']

        val_lim_squared = 4.0

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
                val_squared = 0.0

                while loop < iter_lim:
                    z = z * z + c
                    val_squared = z.real * z.real + z.imag * z.imag
                    if val_squared > val_lim_squared:
                        item = {
                            'x'     : x,
                            'loop'  : loop,
                            'value' : math.sqrt(val_squared),
                            'R'     : 0,
                            'G'     : 0,
                            'B'     : 0,
                        }
                        self.line.append(item)
                        break
                    loop += 1

            self.get_color(cp)
            for item in self.line:
                color.setRgb(item['R'], item['G'], item['B'])
                image.setPixelColor(item['x'], y, color)

        self.log.exit("mandelbrot_frame", False)

        return image

    #
    # -----------------------------------------------
    # Calculate color and smoothed color transfers. Called by
    # calculate_mandelbrot and calculate_julia
    # -----------------------------------------------
    #

    def get_color(self, cp):
        self.log.entry("get_color", False)

        for item in self.line:

            loop  = item['loop']
            value = item['value']

            # Calculate smoothed iteration value
            try:
                smoothed = loop + 1 - math.log(math.log(value)) / math.log(2.0)
            except ValueError:
                self.log.error(f"ValueError: loop,value={loop},{value}", False)
                smoothed = loop

            # Normed value between 0.0 and 1.0
            # (the higher value = the higher frequency of color change)
            velocity = smoothed / 40.0

            #
            # Cosine Palette-Method
            # (based on Inigo Quilez, phase value defines time shifted increase
            # of r,g,b):
            # color = brightness + contrast * math.cos(2 * math.pi * (frequency * velocity + phase))
            #

            rgb = {}
            for channel in ['R', 'G', 'B']:
                b = cp[f'brightness{channel}']
                c = cp[f'contrast{channel}']
                f = cp[f'frequency{channel}']
                p = cp[f'phase{channel}']

                # Calculate raw color value based on cosine palette method
                raw_val = int(255 * (b + c * math.cos(2 * math.pi * (f * velocity + p))))

                # Implement safeguard to ensure that the color value is within
                # the valid range of 0-255
                clipped_val = max(0, min(255, raw_val))
                rgb[channel] = clipped_val

            item['R'] = rgb['R']
            item['G'] = rgb['G']
            item['B'] = rgb['B']

            self.log.exit("get_color", False)

    #
    # -----------------------------------------------
    # Super widget informs the worker that calculation has to be stopped
    # -----------------------------------------------
    #

    def stop(self):
        self.log.entry("stop", False)
        self.is_running = False
        self.log.exit("stop", False)
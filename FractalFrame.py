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

from PySide6.QtCore import QObject
from PySide6.QtGui import QImage, QColor

from Logging import Logging


class FractalFrame(QObject):

    def __init__(self):
        super().__init__()

        self.log = Logging("FractalFrame", True)
        self.log.entry("__init__", False)

        self.is_running = True

        self.log.exit("__init__", False)

    def mandelbrot_frame(self, frac_area, iter_lim, dd_width, dd_height, cp):
        self.log.entry("mandelbrot_frame", False)

        frac_area = copy.copy(frac_area)

        self.log.write("frac_area=" + str(frac_area), False)
        self.log.write("iter_lim=" + str(iter_lim), False)
        self.log.write(f"dd_width,dd_height={dd_width},{dd_height}", False)
        self.log.write("cp=" + str(cp), False)

        x_step = frac_area['realWidth'] / dd_width
        y_step = frac_area['imagHeight'] / dd_height

        real_origin = frac_area['realOrigin']
        imag_origin = frac_area['imagOrigin']

        pi_2  = 2.0 * math.pi
        log_2 = math.log(2.0)

        b_R, c_R = cp['brightnessR'], cp['contrastR']
        f_R, p_R = cp['frequencyR'], cp['phaseR']
        b_G, c_G = cp['brightnessG'], cp['contrastG']
        f_G, p_G = cp['frequencyG'], cp['phaseG']
        b_B, c_B = cp['brightnessB'], cp['contrastB']
        f_B, p_B = cp['frequencyB'], cp['phaseB']

        bg_R, bg_G, bg_B = cp['bg_R'], cp['bg_G'], cp['bg_B']

        img_buffer = bytearray([bg_B, bg_G, bg_R, 255] * (dd_width * dd_height))

        # Lokale Lookups von mathematischen Funktionen beschleunigen den Zugriff erheblich
        _cos = math.cos
        _log = math.log

        real_parts = [real_origin + x * x_step for x in range(dd_width)]

        idx = 0
        for y in range(dd_height):

            if not self.is_running:
                self.log.write("Thread stopped by user.", False)
                self.progress.emit(self.draw_dim['height'])
                self.log.exit("calculate_mandelbrot", False)
                break

            imag_part = imag_origin + y * y_step

            for x in range(dd_width):
                c_re = real_parts[x]
                c_im = imag_part

                z_re = 0.0
                z_im = 0.0
                loop = 0
                val_squared = 0.0

                while loop < iter_lim:
                    z_re_sq = z_re * z_re
                    z_im_sq = z_im * z_im
                    val_squared = z_re_sq + z_im_sq

                    if val_squared > 4.0:
                        break

                    z_im = 2.0 * z_re * z_im + c_im
                    z_re = z_re_sq - z_im_sq + c_re
                    loop += 1

                if loop < iter_lim:
                    value = math.sqrt(val_squared)
                    if value > 1.0:
                        smoothed = loop + 1 - _log(_log(value)) / log_2
                    else:
                        smoothed = loop

                    velocity = smoothed / 40.0
                    v_pi_2 = velocity * pi_2

                    # Format: BGRA
                    raw_B = int(255 * (b_B + c_B * _cos(f_B * v_pi_2 + p_B * pi_2)))
                    raw_G = int(255 * (b_G + c_G * _cos(f_G * v_pi_2 + p_G * pi_2)))
                    raw_R = int(255 * (b_R + c_R * _cos(f_R * v_pi_2 + p_R * pi_2)))
                    img_buffer[idx]     = 0 if raw_B < 0 else (255 if raw_B > 255 else raw_B)
                    img_buffer[idx + 1] = 0 if raw_G < 0 else (255 if raw_G > 255 else raw_G)
                    img_buffer[idx + 2] = 0 if raw_R < 0 else (255 if raw_R > 255 else raw_R)

                # Ignore Alpha value
                idx += 4

        image = QImage(
            img_buffer,
            dd_width,
            dd_height,
            QImage.Format.Format_RGB32
        )
        final_image = image.copy()

        self.log.exit("mandelbrot_frame", False)
        return final_image

    def stop(self):
        self.log.entry("stop", False)
        self.is_running = False
        self.log.exit("stop", False)

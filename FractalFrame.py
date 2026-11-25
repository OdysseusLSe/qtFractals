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

import numpy as np

from PySide6.QtCore import QObject
from PySide6.QtGui import QImage

from Logging import Logging

#
# -----------------------------------------------
#


class FractalFrame(QObject):

    def __init__(self):
        super().__init__()

        self.log = Logging("FractalFrame")
        self.log.entry("__init__")

        self.is_running = True

        self.log.exit("__init__")

    #
    # -----------------------------------------------
    # Calculate Mandelbrot set
    # -----------------------------------------------
    #

    def mandelbrot_frame(self, frac_area, iter_lim, dd_width, dd_height, cp):
        self.log.entry("mandelbrot_frame")

        frac_area = copy.copy(frac_area)

        x_step = frac_area['realWidth'] / dd_width
        y_step = frac_area['imagHeight'] / dd_height
        real_origin = frac_area['realOrigin']
        imag_origin = frac_area['imagOrigin']

        pixels = np.empty((dd_height, dd_width, 4), dtype=np.uint8)
        pixels[:, :, 0] = cp['bg_R']
        pixels[:, :, 1] = cp['bg_G']
        pixels[:, :, 2] = cp['bg_B']
        pixels[:, :, 3] = 255

        real_parts = real_origin + np.arange(dd_width) * x_step
        rows_per_chunk = min(16, dd_height)

        for row_start in range(0, dd_height, rows_per_chunk):
            if not self.is_running:
                self.log.write("Thread stopped by user.")
                break

            row_end = min(row_start + rows_per_chunk, dd_height)
            imag_parts = (
                imag_origin + np.arange(row_start, row_end) * y_step
            )[:, np.newaxis]
            shape = (row_end - row_start, dd_width)

            z_real = np.zeros(shape, dtype=np.float64)
            z_imag = np.zeros(shape, dtype=np.float64)
            active = np.ones(shape, dtype=bool)
            escape_iterations = np.zeros(shape, dtype=np.int32)
            escape_values = np.zeros(shape, dtype=np.float64)

            for iteration in range(iter_lim):
                real_squared = z_real * z_real
                imag_squared = z_imag * z_imag
                next_real = real_squared - imag_squared + real_parts
                next_imag = 2.0 * z_real * z_imag + imag_parts
                magnitude_squared = next_real * next_real + next_imag * next_imag

                escaped = active & (magnitude_squared > 4.0)
                escape_iterations[escaped] = iteration
                escape_values[escaped] = magnitude_squared[escaped]

                np.copyto(z_real, next_real, where=active)
                np.copyto(z_imag, next_imag, where=active)
                active &= ~escaped
                if not active.any():
                    break

            escaped = escape_values > 0.0
            if escaped.any():
                values = np.sqrt(escape_values[escaped])
                smoothed = (
                    escape_iterations[escaped] + 1
                    - np.log(np.log(values)) / math.log(2.0)
                )
                velocity = smoothed / 40.0

                for channel, pixel_channel in zip(('R', 'G', 'B'), range(3)):
                    brightness = cp[f'brightness{channel}']
                    contrast = cp[f'contrast{channel}']
                    frequency = cp[f'frequency{channel}']
                    phase = cp[f'phase{channel}']
                    raw_values = 255 * (
                        brightness
                        + contrast * np.cos(
                            2.0 * math.pi * (frequency * velocity + phase)
                        )
                    )
                    colors = np.clip(np.trunc(raw_values), 0, 255).astype(np.uint8)
                    chunk = pixels[row_start:row_end, :, pixel_channel]
                    chunk[escaped] = colors

        self.log.exit("mandelbrot_frame")

        image = QImage(
            pixels.data,
            dd_width,
            dd_height,
            pixels.strides[0],
            QImage.Format.Format_RGBA8888
        )
        return image.convertToFormat(QImage.Format.Format_RGB32)

    #
    # -----------------------------------------------
    # Parent widget informs the worker that calculation has to be stopped
    # -----------------------------------------------
    #

    def stop(self):
        self.log.entry("stop")
        self.is_running = False
        self.log.exit("stop")
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
import time

import numpy as np

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot
)
from PySide6.QtGui import (
    QImage
)

from Logging import Logging


class FractalWorker(QObject):

    # Signal for progress of frac calculation
    progress = Signal(int)

    # Signal to show calculation result until now
    drawing  = Signal(QImage)

    # Signal to show finished calculation result
    finished = Signal(QImage, float)

    def __init__(
            self,
            frac_area,
            draw_dim,
            iter_lim,
            col_pal,
            current_frac_set,
            julia_c
        ):
        super().__init__()

        self.log = Logging("FractalWorker")
        self.log.entry("__init__")

        self.frac_area        = copy.copy(frac_area)
        self.draw_dim         = copy.copy(draw_dim)
        self.iter_lim         = iter_lim
        self.cp               = copy.copy(col_pal)
        self.current_frac_set = current_frac_set
        self.julia_c          = julia_c

        self.log.write("self.frac_area=" + str(self.frac_area))
        self.log.write("self.draw_dim=" + str(self.draw_dim))
        self.log.write("self.iter_lim=" + str(self.iter_lim))
        self.log.write("self.cp=" + str(self.cp))
        self.log.write("self.julia_c=" + str(self.julia_c))

        self.is_running = True

        self.line = []

        self.log.exit("__init__")

    def _colorize_escaped(self, pixels, escaped, escape_iterations, escape_values):
        if not escaped.any():
            return

        values = np.sqrt(escape_values[escaped])
        smoothed = (
            escape_iterations[escaped] + 1
            - np.log(np.log(values)) / math.log(2.0)
        )
        velocity = smoothed / 40.0

        for pixel_channel, channel in enumerate(('R', 'G', 'B')):
            brightness = self.cp[f'brightness{channel}']
            contrast = self.cp[f'contrast{channel}']
            frequency = self.cp[f'frequency{channel}']
            phase = self.cp[f'phase{channel}']
            raw_values = 255 * (
                brightness
                + contrast * np.cos(
                    2.0 * math.pi * (frequency * velocity + phase)
                )
            )
            colors = np.clip(np.trunc(raw_values), 0, 255).astype(np.uint8)
            pixels[escaped, pixel_channel] = colors

    #
    # -----------------------------------------------
    # Calculate Julia set
    # -----------------------------------------------
    #

    @Slot()
    def calculate_julia(self):

        self.log.entry("calculate_julia")

        width = self.draw_dim['width']
        height = self.draw_dim['height']
        pixels = np.empty((height, width, 4), dtype=np.uint8)
        pixels[:, :, 0] = self.cp['bg_R']
        pixels[:, :, 1] = self.cp['bg_G']
        pixels[:, :, 2] = self.cp['bg_B']
        pixels[:, :, 3] = 255

        x_step = self.frac_area['realWidth'] / width
        y_step = self.frac_area['imagHeight'] / height
        real_origin = self.frac_area['realOrigin']
        imag_origin = self.frac_area['imagOrigin']
        real_parts = real_origin + np.arange(width) * x_step
        julia_real = self.julia_c.real
        julia_imag = self.julia_c.imag

        calc_time = 0.0

        image = QImage(
            pixels.data,
            width,
            height,
            pixels.strides[0],
            QImage.Format.Format_RGBA8888
        )

        for y in range(height):

            start_time = time.process_time()

            if not self.is_running:
                self.log.write("Thread stopped by user.")
                self.progress.emit(height)
                self.log.exit("calculate_julia")
                break

            imag_part = imag_origin + y * y_step
            self.line = []
            z_real = real_parts.copy()
            z_imag = np.full(width, imag_part, dtype=np.float64)
            active = np.ones(width, dtype=bool)
            escape_iterations = np.zeros(width, dtype=np.int32)
            escape_values = np.zeros(width, dtype=np.float64)

            for iteration in range(self.iter_lim):
                real_squared = z_real * z_real
                imag_squared = z_imag * z_imag
                next_real = real_squared - imag_squared + julia_real
                next_imag = 2.0 * z_real * z_imag + julia_imag
                magnitude_squared = next_real * next_real + next_imag * next_imag

                escaped = active & (magnitude_squared > 4.0)
                escape_iterations[escaped] = iteration
                escape_values[escaped] = magnitude_squared[escaped]

                np.copyto(z_real, next_real, where=active)
                np.copyto(z_imag, next_imag, where=active)
                active &= ~escaped
                if not active.any():
                    break

            self._colorize_escaped(
                pixels[y],
                escape_values > 0.0,
                escape_iterations,
                escape_values
            )

            calc_time = calc_time + time.process_time() - start_time
            self.progress.emit(y+1)
            self.drawing.emit(image.copy())

        calc_time = calc_time + time.process_time() - start_time

        self.log.exit("calculate_julia")
        self.finished.emit(
            image.convertToFormat(QImage.Format.Format_RGB32),
            calc_time
        )

    #
    # -----------------------------------------------
    # Calculate Mandelbrot set
    # -----------------------------------------------
    #

    @Slot()
    def calculate_mandelbrot(self):
        self.log.entry("calculate_mandelbrot")

        width = self.draw_dim['width']
        height = self.draw_dim['height']
        pixels = np.empty((height, width, 4), dtype=np.uint8)
        pixels[:, :, 0] = self.cp['bg_R']
        pixels[:, :, 1] = self.cp['bg_G']
        pixels[:, :, 2] = self.cp['bg_B']
        pixels[:, :, 3] = 255

        x_step = self.frac_area['realWidth'] / width
        y_step = self.frac_area['imagHeight'] / height
        real_origin = self.frac_area['realOrigin']
        imag_origin = self.frac_area['imagOrigin']
        real_parts = real_origin + np.arange(width) * x_step

        calc_time = 0.0

        image = QImage(
            pixels.data,
            width,
            height,
            pixels.strides[0],
            QImage.Format.Format_RGBA8888
        )

        for y in range(height):
            start_time = time.process_time()

            if not self.is_running:
                self.log.write("Thread stopped by user.")
                self.progress.emit(height)
                self.log.exit("calculate_mandelbrot")
                break

            imag_part = imag_origin + y * y_step
            self.line = []
            z_real = np.zeros(width, dtype=np.float64)
            z_imag = np.zeros(width, dtype=np.float64)
            active = np.ones(width, dtype=bool)
            escape_iterations = np.zeros(width, dtype=np.int32)
            escape_values = np.zeros(width, dtype=np.float64)

            for iteration in range(self.iter_lim):
                real_squared = z_real * z_real
                imag_squared = z_imag * z_imag
                next_real = real_squared - imag_squared + real_parts
                next_imag = 2.0 * z_real * z_imag + imag_part
                magnitude_squared = next_real * next_real + next_imag * next_imag

                escaped = active & (magnitude_squared > 4.0)
                escape_iterations[escaped] = iteration
                escape_values[escaped] = magnitude_squared[escaped]

                np.copyto(z_real, next_real, where=active)
                np.copyto(z_imag, next_imag, where=active)
                active &= ~escaped
                if not active.any():
                    break

            self._colorize_escaped(
                pixels[y],
                escape_values > 0.0,
                escape_iterations,
                escape_values
            )

            calc_time = calc_time + time.process_time() - start_time
            self.progress.emit(y+1)
            self.drawing.emit(image.copy())

        calc_time = calc_time + time.process_time() - start_time

        self.log.exit("calculate_mandelbrot")

        self.finished.emit(
            image.convertToFormat(QImage.Format.Format_RGB32),
            calc_time
        )
    #
    # -----------------------------------------------
    # Super widget informs the worker that calculation has to be stopped
    # -----------------------------------------------
    #

    def stop(self):
        self.log.entry("stop")
        self.is_running = False
        self.log.exit("stop")
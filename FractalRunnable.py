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

from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from PySide6.QtGui import QImage

#
# Custom signals can only be defined on objects derived from QObject. Since
# QRunnable is not derived from QObject I can’t define the signal there
# directly. A custom QObject to hold the signal is the simplest solution.
#


class FractalSignals(QObject):
    # When thread has finished send result (calculated image) back.
    finished = Signal(QImage)


class FractalRunnable(QRunnable):
    def __init__(self, ff, frac_area, iter_lim, dd_width, dd_height, cp, mw):
        super().__init__()

        self.ff          = ff
        self.frac_area   = frac_area
        self.iter_lim    = iter_lim
        self.dd_width    = dd_width
        self.dd_height   = dd_height
        self.cp          = cp
        self.main_window = mw
        self.signals     = FractalSignals()

    @Slot()
    def run(self):
        if self.main_window.stop_video_creation:
            self.signals.finished.emit(None)
            return

        image = self.ff.mandelbrot_frame(
            self.frac_area,
            self.iter_lim,
            self.dd_width,
            self.dd_height,
            self.cp
        )

        if self.main_window.stop_video_creation:
            self.signals.finished.emit(None)
        else:
            self.signals.finished.emit(image)

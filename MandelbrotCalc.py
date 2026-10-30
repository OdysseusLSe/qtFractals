from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from PySide6.QtGui import QImage


# Ein QObject, da QRunnable selbst keine Signale definieren kann
class MandelbrotSignals(QObject):
    finished = Signal(QImage)


class MandelbrotRunnable(QRunnable):
    def __init__(self, ff, frac_area, iter_lim, dd_width, dd_height, cp):
        super().__init__()
        self.ff = ff
        self.frac_area = frac_area
        self.iter_lim = iter_lim
        self.dd_width = dd_width
        self.dd_height = dd_height
        self.cp = cp
        self.signals = MandelbrotSignals()

    @Slot()
    def run(self):
        image = self.ff.mandelbrot_frame(
            self.frac_area,
            self.iter_lim,
            self.dd_width,
            self.dd_height,
            self.cp
        )
        self.signals.finished.emit(image)

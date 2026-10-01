import copy

from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget
)
from PySide6.QtGui import QDoubleValidator, QIcon
from PySide6.QtCore import Qt, QSize

import FractalWidget
import Logging


#
# Function to load the stylesheet from a file
#

def load_stylesheet(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("Warning: Stylesheet " + file_path + " not found.")
        return ""


#
#
#

class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        appName = "qtFractals"
        appVersion = "0.2"

        self.setWindowTitle(appName + " " + appVersion)

        self.log = Logging.Logging(appName + " " + appVersion, True)
        self.log.write("--- " + appName + " " + appVersion + " ---", False)
        self.log.entry("__init__", False)

        # Set default values for fractal area, drawing dimensions, iteration limit, and color palette
        self.set_default_values()

        # Build the main window with all the widgets
        self.build_main_window(appName, appVersion)

        self.log.exit("__init__", False)

    #
    # -----------------------------------------------
    #

    def build_main_window(self, appName, appVersion):

        self.log.entry("build_main_window", False)

        # Offset of the widgets from the main window frame
        xOffset = 10
        yOffset = 10

        # Title of the main window
        self.setWindowTitle(appName + " " + appVersion)

        # Build labels
        real_part_lbl = QLabel("<b>Origin of real part</b>:", self)
        imag_part_lbl = QLabel("<b>Origin of imag. part</b>:", self)
        width_lbl     = QLabel("<b>Width</b>:", self)
        height_lbl    = QLabel("<b>Height</b>:", self)
        xDim_lbl      = QLabel("<b>x-Dimension</b>:", self)
        yDim_lbl      = QLabel("<b>y-Dimension</b>:", self)
        iter_lim_lbl  = QLabel("<b>Iteration limit</b>:", self)

        #
        # Build line edits
        #

        self.real_part_edit = QLineEdit(self)
        self.real_part_edit.setPlaceholderText(str(self.frac_area['realOrigin']))
        self.real_part_edit.setValidator(QDoubleValidator(-2.0, 2.0, 4))
        self.real_part_edit.setFixedWidth(160)

        self.imag_part_edit = QLineEdit(self)
        self.imag_part_edit.setPlaceholderText(str(self.frac_area['imagOrigin']))
        self.imag_part_edit.setValidator(QDoubleValidator(-2.0, 2.0, 4))
        self.imag_part_edit.setFixedWidth(160)

        self.width_edit = QLineEdit(self)
        self.width_edit.setPlaceholderText(str(self.frac_area['realWidth']))
        self.width_edit.setValidator(QDoubleValidator(0.0001, 7.1, 4))
        self.width_edit.setFixedWidth(160)

        self.height_edit = QLineEdit(self)
        self.height_edit.setPlaceholderText(str(self.frac_area['imagHeight']))
        self.height_edit.setValidator(QDoubleValidator(0.0001, 4.0, 4))
        self.height_edit.setFixedWidth(160)

        self.x_dim_edit = QLineEdit(self)
        self.x_dim_edit.setPlaceholderText(str(self.draw_dim['width']))
        self.x_dim_edit.setValidator(QDoubleValidator(0.0001, 4.0, 4))
        self.x_dim_edit.setFixedWidth(50)

        self.y_dim_edit = QLineEdit(self)
        self.y_dim_edit.setPlaceholderText(str(self.draw_dim['height']))
        self.y_dim_edit.setValidator(QDoubleValidator(0.0001, 4.0, 4))
        self.y_dim_edit.setFixedWidth(50)

        self.iter_lim_edit = QLineEdit(self)
        self.iter_lim_edit.setPlaceholderText(str(self.iter_lim))
        self.iter_lim_edit.setValidator(QDoubleValidator(0.0001, 4.0, 4))
        self.iter_lim_edit.setFixedWidth(50)

        # Build combo box for drawing dimensions
        self.dd_combo = QComboBox()
        for value in self.sel_draw_dim.values():
            self.dd_combo.addItem(value)
        self.dd_combo.currentTextChanged.connect(self.dd_text_changed)

        #
        # Indicator if Mandelbrot set or Julia set is active (default: Mandelbrot set)
        #

        self.mandel_btn = QPushButton("Mandelbrot")
        self.mandel_btn.setIcon(QIcon("ui/LED_small_green.png"))
        self.mandel_btn.setIconSize(QSize(16, 16))
        self.mandel_btn.setObjectName("mandelJuliaButton")
        self.mandel_btn.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.julia_btn = QPushButton("Julia")
        self.julia_btn.setIcon(QIcon("ui/LED_small_red.png"))
        self.julia_btn.setIconSize(QSize(16, 16))
        self.julia_btn.setObjectName("mandelJuliaButton")
        self.julia_btn.setAttribute(Qt.WA_TransparentForMouseEvents)

        # "Reset" Button
        self.reset_btn = QPushButton('Reset', self)
        self.reset_btn.clicked.connect(self.reset)

        # "Start" Button
        self.start_btn = QPushButton('Start', self)
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.trigger_calculation)

        #
        # Build combo box for color palettes
        #

        cp_lbl = QLabel("<b>Color palettes: </b>:", self)
        self.cp_combo = QComboBox()
        for element in self.cp_list:
            self.cp_combo.addItem(element['name'])
            if element['name'] == self.cp['name']:
                self.cp_combo.setCurrentText(element['name'])
        self.cp_combo.currentTextChanged.connect(self.cp_text_changed)

        # "Save" Button
        save_btn = QPushButton('Save', self)
        save_btn.setStyleSheet(
            # "background-color: red; "
            # "color: white; "
            "font-style: bold; "
            "font-size: 18px"
        )
        save_btn.clicked.connect(self.save_image)

        # "Quit" Button
        quit_btn = QPushButton('Quit', self)
        quit_btn.setStyleSheet(
            "background-color : red; "
            "color            : white; "
            "font-style       : bold; "
            "font-size        : 18px"
        )
        quit_btn.clicked.connect(self.end_app)

        # All three buttons have the same width
        btn_width = self.reset_btn.sizeHint().width()
        self.reset_btn.setFixedWidth(btn_width)
        self.start_btn.setFixedWidth(btn_width)
        quit_btn.setFixedWidth(btn_width)

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setRange(0, self.draw_dim['height'])
        self.progress_bar.setValue(0)

        #
        # Layout labels, line edits, fractal window, progress bar, and buttons
        #

        layout_grid = QGridLayout()

        # First row

        layout_grid.addWidget(real_part_lbl, 0, 0)
        layout_grid.addWidget(self.real_part_edit, 0, 1)

        layout_grid.addWidget(width_lbl, 0, 3)
        layout_grid.addWidget(self.width_edit, 0, 4)

        layout_grid.addWidget(xDim_lbl, 0, 6)
        layout_grid.addWidget(self.x_dim_edit, 0, 7)

        layout_grid.addWidget(iter_lim_lbl, 0, 9)
        layout_grid.addWidget(self.iter_lim_edit, 0, 10)

        layout_grid.addWidget(self.mandel_btn, 0, 12)

        layout_grid.addWidget(self.reset_btn, 0, 14)

        # Second row

        layout_grid.addWidget(imag_part_lbl, 1, 0)
        layout_grid.addWidget(self.imag_part_edit, 1, 1)

        layout_grid.addWidget(height_lbl, 1, 3)
        layout_grid.addWidget(self.height_edit, 1, 4)

        layout_grid.addWidget(yDim_lbl, 1, 6)
        layout_grid.addWidget(self.y_dim_edit, 1, 7)

        layout_grid.addWidget(
            self.dd_combo, 1, 9, 1, 2,
            Qt.AlignmentFlag.AlignHCenter
        )

        layout_grid.addWidget(self.julia_btn, 1, 12)

        layout_grid.addWidget(self.start_btn, 1, 14)

        # Space within the grid layout

        layout_grid.setHorizontalSpacing(10)
        layout_grid.setVerticalSpacing(10)

        layout_grid.setColumnStretch(13, 1)
        layout_grid.setColumnMinimumWidth(2, 30)
        layout_grid.setColumnMinimumWidth(5, 30)
        layout_grid.setColumnMinimumWidth(8, 30)
        layout_grid.setColumnMinimumWidth(11, 30)

        # Create widget fractal ("third row") and connect it to the progress bar
        self.fw = FractalWidget.FractalWidget(
            self.frac_area,
            self.draw_dim,
            self.iter_lim,
            self.cp,
            self.current_frac_set,
            self.julia_c
        )
        self.fw.setFixedSize(self.draw_dim['width'], self.draw_dim['height'])
        self.fw.progress.connect(self.update_progress)

        # Buttons in the last row have their own layout
        last_row_layout = QHBoxLayout()
        # last_row_layout.setContentsMargins(0, 0, 0, 0)
        last_row_layout.addWidget(cp_lbl)
        last_row_layout.addWidget(self.cp_combo)
        last_row_layout.addStretch()
        last_row_layout.addWidget(save_btn)
        last_row_layout.addStretch()
        last_row_layout.addWidget(quit_btn)

        # Build the overall layout of the main window

        main_layout = QVBoxLayout()

        # 10 pixel distance from every window frame
        main_layout.setContentsMargins(xOffset, yOffset, xOffset, yOffset)
        main_layout.setSpacing(10)

        main_layout.addLayout(layout_grid)
        main_layout.addWidget(self.fw, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.progress_bar)
        main_layout.addLayout(last_row_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.adjustSize()
        self.setMinimumSize(self.sizeHint())

        self.log.exit("build_main_window", False)

    #
    # -----------------------------------------------
    #

    def cp_text_changed(self, text):
        self.log.entry("cp_text_changed", False)

        self.log.write(text)

        for element in self.cp_list:
            if text == element['name']:
                self.cp = element
        self.log.write(str(self.cp), False)

        self.fw.change_col_pal(self.cp)

        self.log.exit("cp_text_changed", False)

    #
    # -----------------------------------------------
    #

    def dd_text_changed(self, text):
        self.log.entry("dd_text_changed", False)

        self.log.write(text, False)

        if text == self.sel_draw_dim['HD']:
            self.x_dim_edit.setText("1280")
            self.y_dim_edit.setText("720")
        elif text == self.sel_draw_dim['Full HD']:
            self.x_dim_edit.setText("1920")
            self.y_dim_edit.setText("1080")
        elif text == self.sel_draw_dim['Full QHD']:
            self.x_dim_edit.setText("2560")
            self.y_dim_edit.setText("1440")
        elif text == self.sel_draw_dim['Ulra-Wide WQHD']:
            self.x_dim_edit.setText("3440")
            self.y_dim_edit.setText("1440")
        elif text == self.sel_draw_dim['4K Ultra HD']:
            self.x_dim_edit.setText("3840")
            self.y_dim_edit.setText("2160")
        elif text == self.sel_draw_dim['8K Ultra HD']:
            self.x_dim_edit.setText("7680")
            self.y_dim_edit.setText("4320")

        self.log.exit("dd_text_changed", False)

    #
    # -----------------------------------------------
    #

    def define_color_palettes(self):
        self.log.entry("define_color_palettes", False)

        #
        # Color palette (for more details see method "get_color" in FractalWorker.py):
        # (color = brightness + contrast * math.cos(2 * math.pi * (frequency * velocity + phase)))
        #

        self.cp_barrier_free = {
            'name'        : "Barrier-Free",
            'brightnessR' : 0.6,  'brightnessG' : 0.5,  'brightnessB' : 0.4,
            'contrastR'   : 0.4,  'contrastG'   : 0.5,  'contrastB'   : 0.6,
            'frequencyR'  : 1.0,  'frequencyG'  : 1.0,  'frequencyB'  : 1.0,
            'phaseR'      : 0.00, 'phaseG'      : 0.00, 'phaseB'      : 0.5
        }
        self.cp_list = [self.cp_barrier_free]

        self.cp_classic_rainbow = {
            'name'        : "Classic Rainbow",
            'brightnessR' : 0.5,  'brightnessG' : 0.5,  'brightnessB' : 0.5,
            'contrastR'   : 0.5,  'contrastG'   : 0.5,  'contrastB'   : 0.5,
            'frequencyR'  : 1.0,  'frequencyG'  : 1.0,  'frequencyB'  : 1.0,
            'phaseR'      : 0.00, 'phaseG'      : 0.33, 'phaseB'      : 0.67
        }
        self.cp_list.append(self.cp_classic_rainbow)

        self.cp_deep_forest = {
            'name'        : "Deep Forest",
            'brightnessR' : 0.3,  'brightnessG' : 0.6,  'brightnessB' : 0.2,
            'contrastR'   : 0.3,  'contrastG'   : 0.4,  'contrastB'   : 0.2,
            'frequencyR'  : 1.0,  'frequencyG'  : 1.0,  'frequencyB'  : 1.0,
            'phaseR'      : 0.00, 'phaseG'      : 0.05, 'phaseB'      : 0.33
        }
        self.cp_list.append(self.cp_deep_forest)

        self.cp_fire_and_ice = {
            'name'      : "Fire & Ice",
            'brightnessR' : 0.5,  'brightnessG' : 0.5,  'brightnessB' : 0.5,
            'contrastR'   : 0.5,  'contrastG'   : 0.5,  'contrastB'   : 0.5,
            'frequencyR'  : 1.0,  'frequencyG'  : 1.0,  'frequencyB'  : 1.0,
            'phaseR'      : 0.00, 'phaseG'      : 0.15, 'phaseB'      : 0.33
        }
        self.cp_list.append(self.cp_fire_and_ice)

        self.cp_grayscale = {
            'name'        : "Grayscale",
            'brightnessR' : 0.5,  'brightnessG' : 0.5,  'brightnessB' : 0.5,
            'contrastR'   : 0.5,  'contrastG'   : 0.5,  'contrastB'   : 0.5,
            'frequencyR'  : 1.0,  'frequencyG'  : 1.0,  'frequencyB'  : 1.0,
            'phaseR'      : 0.00, 'phaseG'      : 0.00, 'phaseB'      : 0.00
        }
        self.cp_list.append(self.cp_grayscale)

        self.cp_maximum_contrast = {
            'name'        : "Maximum Contrast",
            'brightnessR' : 0.5,  'brightnessG' : 0.5,  'brightnessB' : 0.5,
            'contrastR'   : 0.5,  'contrastG'   : 0.5,  'contrastB'   : 0.5,
            'frequencyR'  : 1.0,  'frequencyG'  : 1.0,  'frequencyB'  : 1.0,
            'phaseR'      : 0.00, 'phaseG'      : 0.00, 'phaseB'      : 0.00
        }
        self.cp_list.append(self.cp_maximum_contrast)

        self.cp_neon_electric = {
            'name'        : "Neon Electric",
            'brightnessR' : 0.8,  'brightnessG' : 0.5,  'brightnessB' : 0.4,
            'contrastR'   : 0.5,  'contrastG'   : 0.5,  'contrastB'   : 0.5,
            'frequencyR'  : 1.0,  'frequencyG'  : 1.0,  'frequencyB'  : 1.0,
            'phaseR'      : 0.00, 'phaseG'      : 0.33, 'phaseB'      : 0.67
        }
        self.cp_list.append(self.cp_neon_electric)

        self.cp_vintage_pastel = {
            'name'        : "Vintage Pastel",
            'brightnessR' : 0.5,  'brightnessG' : 0.5,  'brightnessB' : 0.5,
            'contrastR'   : 0.5,  'contrastG'   : 0.5,  'contrastB'   : 0.5,
            'frequencyR'  : 1.0,  'frequencyG'  : 1.0,  'frequencyB'  : 1.0,
            'phaseR'      : 0.30, 'phaseG'      : 0.20, 'phaseB'      : 0.20
        }
        self.cp_list.append(self.cp_vintage_pastel)

        self.log.exit("define_color_palettes", False)

        # return default color palette
        return self.cp_fire_and_ice

    #
    # -----------------------------------------------
    #

    def reset(self):
        self.log.entry("reset", False)

        self.real_part_edit.setText(str(self.const_frac_area['realOrigin']))
        self.imag_part_edit.setText(str(self.const_frac_area['imagOrigin']))
        self.width_edit.setText(str(self.const_frac_area['realWidth']))
        self.height_edit.setText(str(self.const_frac_area['imagHeight']))

        self.x_dim_edit.setText(str(self.const_draw_dim['width']))
        self.y_dim_edit.setText(str(self.const_draw_dim['height']))

        self.iter_lim_edit.setText(str(self.const_iter_lim))

        self.current_frac_set = self.default_frac_set
        self.julia_c = complex(10.0, 10.0)

        self.trigger_calculation()

        self.log.exit("reset", False)

    #
    # -----------------------------------------------
    #

    def save_image(self):
        self.log.entry("save_image", False)

        image = self.fw.get_image()

        file_filters = ["bmp", "jpg", "jpeg", "png"]
        self.log.write("file_filters=" + str(file_filters))
        initial_filter = file_filters[3]
        self.log.write("initial_filter=" + initial_filter, False)
        filters = ";;".join(file_filters)
        self.log.write("filters=" + filters, False)

        filename, selectedFilter = QFileDialog.getSaveFileName(
            self,
            "",
            "",
            # filters,
            # initial_filter,
            ";;",
            ""
        )
        self.log.write("filename=" + filename + " / selectedFilter=" + selectedFilter, False)
        if filename == "":
            self.log.exit("save_image", False)
            return

        result = image.save(filename, None, 100)
        if result:
            self.log.write("Image successful saved", False)
        else:
            self.log.error("Image not saved!", False)

        self.log.exit("save_image", False)

    #
    # -----------------------------------------------
    #

    def set_default_values(self):

        self.log.entry("set_default_values", False)

        # Default coordinates of the fractal (HD ratio)
        self.frac_area = {
            'realOrigin' : -2.6,
            'imagOrigin' : -1.2,
            'realWidth'  : 4.33,
            'imagHeight' : 2.43
        }
        self.const_frac_area = copy.deepcopy(self.frac_area)

        # c for Julia set
        self.julia_c = complex(10.0, 10.0)

        # Default dimensions of the fractal window (HD:)
        self.draw_dim = {'width': 1280, 'height': 720}
        self.const_draw_dim = copy.deepcopy(self.draw_dim)

        # Default iteration limit
        self.iter_lim = 100
        self.const_iter_lim = self.iter_lim

        # Default drawing dimensions to select
        self.sel_draw_dim = {
            'HD'              : "1280 x  720 (HD)",
            'Full HD'         : "1920 x 1080 (Full HD)",
            'Full QHD'        : "2560 × 1440 (Full QHD)",
            'Ultra-Wide WQHD' : "3440 x 1440 (Ultra-Wide WQHD)",
            '4K Ultra HD'     : "3840 × 2160 (4K Ultra HD)",
            '8K Ultra HD'     : "7680 × 4320 (8K Ultra HD)"
        }

        # Default fractal set to calculate
        self.default_frac_set = "Mandelbrot"
        self.current_frac_set = self.default_frac_set

        # Default color palette
        self.cp = copy.deepcopy(self.define_color_palettes())
        self.log.write("self.cp=" + str(self.cp), False)

        self.log.exit("set_default_values", False)

    #
    # -----------------------------------------------
    #

    def trigger_calculation(self):
        self.log.entry("trigger_calculation", False)

        if self.real_part_edit.text() != "" \
            and self.imag_part_edit.text() != "" \
            and self.width_edit.text() != "" \
            and self.height_edit.text() != "" \
            and self.iter_lim_edit.text() != "":

            self.progress_bar.setValue(0)
            self.reset_btn.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.frac_area = {
                'realOrigin': float(self.real_part_edit.text()),
                'imagOrigin': float(self.imag_part_edit.text()),
                'realWidth' : float(self.width_edit.text()),
                'imagHeight': float(self.height_edit.text())
            }
            self.log.write("self.frac_area=" + str(self.frac_area), False)

            self.draw_dim = {
                'width' : int(self.x_dim_edit.text()),
                'height': int(self.y_dim_edit.text())
            }
            self.log.write("self.draw_dim=" + str(self.draw_dim), False)

            self.iter_lim = int(self.iter_lim_edit.text())
            self.log.write("self.iter_lim=" + str(self.iter_lim), False)

            self.fw.set_parameters(
                self.frac_area,
                self.draw_dim,
                self.iter_lim,
                self.cp,
                self.current_frac_set,
                self.julia_c
            )

            self.fw.start_calculation()

        else:
            QMessageBox.about(self, "Error", "All fields need an input!")

        self.log.exit("trigger_calculation", False)

    #
    # -----------------------------------------------
    #

    def update_progress(self, value):
        self.log.entry("update_progress", False)

        if value == 1:

            self.log.write("Calculation just started.", False)

            frac_area, draw_dim, iter_lim, frac_set, julia_c = self.fw.get_parameters()

            self.frac_area        = copy.deepcopy(frac_area)
            self.draw_dim         = copy.deepcopy(draw_dim)
            self.iter_lim         = iter_lim
            self.current_frac_set = frac_set
            self.julia_c          = julia_c
            self.log.write("self.current_frac_set=" + self.current_frac_set, False)

            # Adapt text fields to current values

            self.real_part_edit.setText(str(self.frac_area['realOrigin']))
            self.imag_part_edit.setText(str(self.frac_area['imagOrigin']))
            self.width_edit.setText(str(self.frac_area['realWidth']))
            self.height_edit.setText(str(self.frac_area['imagHeight']))

            self.x_dim_edit.setText(str(self.draw_dim['width']))
            self.y_dim_edit.setText(str(self.draw_dim['height']))

            # Adapt range of progress bar to current y-dimension of drawing
            self.progress_bar.setRange(0, self.draw_dim['height'])

            self.iter_lim_edit.setText(str(self.iter_lim))

            if self.current_frac_set == "Mandelbrot":
                self.mandel_btn.setIcon(QIcon("ui/LED_small_green.png"))
                self.julia_btn.setIcon(QIcon("ui/LED_small_red.png"))
            else:
                self.mandel_btn.setIcon(QIcon("ui/LED_small_red.png"))
                self.julia_btn.setIcon(QIcon("ui/LED_small_green.png"))
            self.mandel_btn.update()
            self.julia_btn.update() 

        self.log.write("value=" + str(value) + " / " + str(self.fw.height()), False)

        self.progress_bar.setValue(value)
        if value >= self.progress_bar.maximum():
            self.reset_btn.setEnabled(True)
            self.start_btn.setEnabled(True)
        else:
            self.reset_btn.setEnabled(False)
            self.start_btn.setEnabled(False)

        self.log.exit("update_progress", False)

    #
    # -----------------------------------------------
    #

    def end_app(self):
        self.log.entry("end_app", False)

        app.quit()


#
# -----------------------------------------------
#

# The application runs until the window will be closed

app = QtWidgets.QApplication([])

stylesheet = load_stylesheet("ui/style.css")
app.setStyleSheet(stylesheet)

win = MainWindow()
win.show()

app.exec()

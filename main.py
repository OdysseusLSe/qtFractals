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
# along with this program. If not, see <http://www.apache.org/licenses/LICENSE-2.0>.
#

import copy
import time

from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStatusBar,
    QStyle,
    QVBoxLayout,
    QWidget
)
from PySide6.QtGui import (
    QAction,
    QDoubleValidator,
    QFont,
    QIntValidator,
    QKeySequence,
    QIcon
)
from PySide6.QtCore import (
    Qt,
    QFile,
    QSize,
    QTextStream
)

import FractalWidget
import Logging

import resources_rc


#
#
#

class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        appName = "qtFractals"
        appVersion = "0.4.0"

        self.setWindowTitle(appName + " " + appVersion)

        self.log = Logging.Logging(appName + " " + appVersion, True)
        self.log.write("--- " + appName + " " + appVersion + " ---", False)
        self.log.entry("__init__", False)

        # Load the stylesheet from a file
        style_file = QFile(":/ui/style.css")
        if style_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(style_file)
            self.setStyleSheet(stream.readAll())
        else:
            self.log.error("Warning: Stylesheet " + ":/ui/style.css" + " not found.")

        # Initiate status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setFont(QFont("Arial", 11))
        self.status_bar.showMessage("--- Ready ---")

        # Build the menu bar with all the menus and actions
        self.build_menu_bar()

        # Set default values for fractal area, drawing dimensions, iteration limit, and color palette
        self.set_default_values()

        # Build the main window with all the widgets
        self.build_main_window(appName, appVersion)

        self.start_time = time.process_time()

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

        self.setMinimumHeight(800)

        # Build labels
        real_part_lbl = QLabel("<b>Origin of real part</b>:", self)
        imag_part_lbl = QLabel("<b>Origin of imag. part</b>:", self)
        width_lbl     = QLabel("<b>Width</b>:", self)
        height_lbl    = QLabel("<b>Height</b>:", self)
        xDim_lbl      = QLabel("<b>x-Dim</b>:", self)
        yDim_lbl      = QLabel("<b>y-Dim</b>:", self)
        iter_lim_lbl  = QLabel("<b>Iteration limit</b>:", self)

        #
        # Build line edits
        #

        bottom = self.frac_area['realOrigin']
        top    = self.frac_area['realOrigin'] + self.frac_area['realWidth']
        self.real_part_edit = QLineEdit(self)
        self.real_part_edit.setText(str(self.const_frac_area['realOrigin']))
        self.real_part_edit.setValidator(QDoubleValidator(bottom, top, 15))
        self.real_part_edit.setFixedWidth(160)

        bottom = self.frac_area['imagOrigin']
        top    = self.frac_area['imagOrigin'] + self.frac_area['imagHeight']
        self.imag_part_edit = QLineEdit(self)
        self.imag_part_edit.setText(str(self.const_frac_area['imagOrigin']))
        self.imag_part_edit.setValidator(QDoubleValidator(bottom, top, 15))
        self.imag_part_edit.setFixedWidth(160)

        bottom = 0.00000000001
        top    = self.frac_area['realWidth']
        self.width_edit = QLineEdit(self)
        self.width_edit.setText(str(self.const_frac_area['realWidth']))
        self.width_edit.setValidator(QDoubleValidator(bottom, top, 15))
        self.width_edit.setFixedWidth(160)

        bottom = 0.00000000001
        top    = self.frac_area['imagHeight']
        self.height_edit = QLineEdit(self)
        self.height_edit.setText(str(self.const_frac_area['imagHeight']))
        self.height_edit.setValidator(QDoubleValidator(bottom, top, 15))
        self.height_edit.setFixedWidth(160)

        self.x_dim_edit = QLineEdit(self)
        self.x_dim_edit.setText(str(self.const_draw_dim['width']))
        self.x_dim_edit.setValidator(QIntValidator(500, 10000))
        self.x_dim_edit.setFixedWidth(50)

        self.y_dim_edit = QLineEdit(self)
        self.y_dim_edit.setText(str(self.const_draw_dim['height']))
        self.y_dim_edit.setValidator(QIntValidator(500, 10000))
        self.y_dim_edit.setFixedWidth(50)

        self.iter_lim_edit = QLineEdit(self)
        self.iter_lim_edit.setText(str(self.const_iter_lim))
        self.iter_lim_edit.setValidator(QIntValidator(100, 10000))
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
        self.mandel_btn.setIcon(QIcon(":/ui/LED_small_green.png"))
        self.mandel_btn.setIconSize(QSize(16, 16))
        self.mandel_btn.setObjectName("mandelJuliaButton")
        self.mandel_btn.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.julia_btn = QPushButton("Julia")
        self.julia_btn.setIcon(QIcon(":/ui/LED_small_red.png"))
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

        self.cp_combo = QComboBox()
        for element in self.cp_list:
            self.cp_combo.addItem(element['name'])
            if element['name'] == self.cp['name']:
                self.cp_combo.setCurrentText(element['name'])
        self.cp_combo.currentTextChanged.connect(self.cp_text_changed)

        # Both buttons have the same width
        btn_width = self.reset_btn.sizeHint().width()
        self.reset_btn.setFixedWidth(btn_width)
        self.start_btn.setFixedWidth(btn_width)

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setRange(0, self.const_draw_dim['height'])
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

        layout_grid.addWidget(yDim_lbl, 0, 9)
        layout_grid.addWidget(self.y_dim_edit, 0, 10)

        layout_grid.addWidget(iter_lim_lbl, 0, 12)
        layout_grid.addWidget(self.iter_lim_edit, 0, 13)

        layout_grid.addWidget(self.mandel_btn, 0, 15)

        layout_grid.addWidget(self.reset_btn, 0, 17)

        # Second row

        layout_grid.addWidget(imag_part_lbl, 1, 0)
        layout_grid.addWidget(self.imag_part_edit, 1, 1)

        layout_grid.addWidget(height_lbl, 1, 3)
        layout_grid.addWidget(self.height_edit, 1, 4)

        layout_grid.addWidget(
            self.dd_combo, 1, 6, 1, 5,
            Qt.AlignmentFlag.AlignHCenter
        )

        layout_grid.addWidget(
            self.cp_combo, 1, 12, 1, 2,
            Qt.AlignmentFlag.AlignHCenter
        )

        layout_grid.addWidget(self.julia_btn, 1, 15)

        layout_grid.addWidget(self.start_btn, 1, 17)

        # Space within the grid layout

        layout_grid.setHorizontalSpacing(10)
        layout_grid.setVerticalSpacing(10)

        layout_grid.setColumnStretch(16, 1)
        layout_grid.setColumnMinimumWidth(2, 30)
        layout_grid.setColumnMinimumWidth(5, 30)
        layout_grid.setColumnMinimumWidth(8, 1)
        layout_grid.setColumnMinimumWidth(11, 30)
        layout_grid.setColumnMinimumWidth(14, 30)
        layout_grid.setColumnMinimumWidth(16, 30)

        #
        # Create widget fractal ("third row") within a scrollable area
        #

        self.fw = FractalWidget.FractalWidget(
            self.const_frac_area,
            self.const_draw_dim,
            self.const_iter_lim,
            self.cp,
            self.current_frac_set,
            self.julia_c
        )
        self.fw.cur_rect.connect(self.status_bar_update_area)

        self.scroll_area = QScrollArea()

        sb_thickness = self.scroll_area.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        frame_margin = self.scroll_area.frameWidth() * 2
        min_width    = self.const_draw_dim['width'] + sb_thickness + frame_margin
        min_height   = self.const_draw_dim['height'] + sb_thickness + frame_margin
        self.scroll_area.setMinimumSize(min_width, min_height)

        log_string = "sb_thickness,frame_margin=" + str(sb_thickness) + "," + str(frame_margin)
        self.log.write(log_string, False)
        log_string = "min_width,min_height=" + str(min_width) + "," + str(min_height)
        self.log.write(log_string, False)

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.fw)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Connect the progress signal from the FractalWidget to the update_progress method
        self.fw.progress.connect(self.update_progress)

        # Build the overall layout of the main window

        main_layout = QVBoxLayout()

        # 10 pixel distance from every window frame
        main_layout.setContentsMargins(xOffset, yOffset, xOffset, yOffset)
        main_layout.setSpacing(10)

        main_layout.addLayout(layout_grid)
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.adjustSize()
        self.setMinimumSize(self.sizeHint())

        self.log.exit("build_main_window", False)

    #
    # -----------------------------------------------
    #

    def build_menu_bar(self):
        self.log.entry("build_menu_bar", False)

        self.status_bar.showMessage("--- Ready ---")

        # Create the menu bar
        menu_bar = self.menuBar()

        # Create the "File" menu
        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        # Create the "Save" action
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence("Ctrl+S"))
        self.save_action.setStatusTip("Save image")
        self.save_action.triggered.connect(self.save_image)
        file_menu.addAction(self.save_action)

        # Create the "Quit" action
        self.quit_action = QAction("&Quit", self)
        self.quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.quit_action.setStatusTip("Quit qtFractals")
        self.quit_action.triggered.connect(self.end_app)
        file_menu.addAction(self.quit_action)

        # Create the "Configuration" menu
        config_menu = QMenu("&Config", self)
        menu_bar.addMenu(config_menu)

        # MAC FIX: Connect the menu's hovered signal to a custom slots pipeline
        file_menu.hovered.connect(self.update_mac_status_bar)

        self.log.exit("build_menu_bar", False)

    #
    # -----------------------------------------------
    #

    def cp_text_changed(self, text):
        self.log.entry("cp_text_changed", False)

        self.log.write(text, False)

        for element in self.cp_list:
            if text == element['name']:
                self.cp = element
        self.log.write(str(self.cp), False)

        self.fw.set_parameters(
            self.frac_area,
            self.draw_dim,
            self.iter_lim,
            self.cp,
            self.current_frac_set,
            self.julia_c
        )

        self.trigger_calculation()

        self.log.exit("cp_text_changed", False)

    #
    # -----------------------------------------------
    #

    def dd_text_changed(self, text):
        self.log.entry("dd_text_changed", False)

        self.log.write("text=" + text, False)

        if text == self.sel_draw_dim['HD']:
            self.x_dim_edit.setText("1280")
            self.y_dim_edit.setText("720")
        elif text == self.sel_draw_dim['Full HD']:
            self.x_dim_edit.setText("1920")
            self.y_dim_edit.setText("1080")
        elif text == self.sel_draw_dim['Full QHD']:
            self.x_dim_edit.setText("2560")
            self.y_dim_edit.setText("1440")
        elif text == self.sel_draw_dim['Ultra-Wide WQHD']:
            self.x_dim_edit.setText("3440")
            self.y_dim_edit.setText("1440")
        elif text == self.sel_draw_dim['4K Ultra HD']:
            self.x_dim_edit.setText("3840")
            self.y_dim_edit.setText("2160")
        elif text == self.sel_draw_dim['8K Ultra HD']:
            self.x_dim_edit.setText("7680")
            self.y_dim_edit.setText("4320")

        self.trigger_calculation()

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

        file_filters   = ["*.bmp", "*.jpg", "*.jpeg", "*.png"]
        initial_filter = file_filters[3]
        filters        = ";;".join(file_filters)

        self.log.write("file_filters=" + str(file_filters), False)
        self.log.write("initial_filter=" + initial_filter, False)
        self.log.write("filters=" + filters, False)

        file_name, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save fractal image as...",
            "./qtFractals_image.png",
            filters,
            initial_filter
        )
        self.log.write("file_name,selected_filter=" + file_name + "," + selected_filter, False)
        if file_name == "":
            self.log.exit("save_image", False)
            return

        result = image.save(file_name, None, 100)
        if result:
            self.log.write("Image successful saved.", False)
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
            and self.iter_lim_edit.text() != "" \
            and self.x_dim_edit.text() != "" \
            and self.y_dim_edit.text() != "":

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

    def update_mac_status_bar(self, action):
        self.log.entry("update_mac_status_bar", False)

        if action and action.statusTip():
            self.log.write("action.statusTip()=" + str(action.statusTip()), False)
            self.status_bar.showMessage(action.statusTip())
        else:
            self.status_bar.clearMessage()

        self.log.exit("update_mac_status_bar", False)

    #
    # -----------------------------------------------
    #

    def update_progress(self, value):
        self.log.entry("update_progress", False)

        if value == 1:

            self.start_time = time.process_time()
            self.log.write("Calculation started (value=" + str(value) + ")", False)

            self.reset_btn.setEnabled(False)
            self.start_btn.setEnabled(False)

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
                self.mandel_btn.setIcon(QIcon(":/ui/LED_small_green.png"))
                self.julia_btn.setIcon(QIcon(":/ui/LED_small_red.png"))
            else:
                self.mandel_btn.setIcon(QIcon(":/ui/LED_small_red.png"))
                self.julia_btn.setIcon(QIcon(":/ui/LED_small_green.png"))

            self.mandel_btn.update()
            self.julia_btn.update()

        self.log.write("value=" + str(value) + " / " + str(self.draw_dim['height']), False)

        percent = int((value / self.progress_bar.maximum()) * 100)
        self.status_bar.showMessage("--- Progress: " + str(percent) + "%")

        self.progress_bar.setValue(value)

        if value >= self.progress_bar.maximum():

            end_time = time.process_time()
            delta_time = end_time - self.start_time
            status = "--- Progress: " + str(percent) + "% --- Process time: "
            status = status + str(delta_time) + " seconds ---"
            self.status_bar.showMessage(status)

            self.reset_btn.setEnabled(True)
            self.start_btn.setEnabled(True)
            self.log.write("Calculation finished (value=" + str(value) + ")", False)

        self.log.exit("update_progress", False)

    #
    # -----------------------------------------------
    #

    def status_bar_update_area(self, area):
        self.log.entry("status_bar_update_area", False)
        self.log.write("area=" + str(area), False)

        ro = area['realOrigin']
        io = area['imagOrigin']
        rw = area['realWidth']
        ih = area['imagHeight']
        status = f"--- Rectangle: Real part: {ro:.15f}, Imag part: {io:.15f}, "
        status = status + f"Width: {rw:.15f}, Height: {ih:.15f}"
        self.status_bar.showMessage(status)

        self.log.exit("status_bar_update_area", False)

    #
    # -----------------------------------------------
    #

    def end_app(self):
        self.log.entry("end_app", False)

        end_app_dlg = QMessageBox(self)
        end_app_dlg.setWindowTitle("Quit the application")
        end_app_dlg.setText("Quit the application?")
        end_app_dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        end_app_dlg.setIcon(QMessageBox.Question)
        button = end_app_dlg.exec()

        if button == QMessageBox.No:
            self.log.exit("end_app", False)
            return

        app.quit()


#
# -----------------------------------------------
#

# The application runs until the window will be closed

app = QtWidgets.QApplication([])

#load_stylesheet(":/ui/style.css")

win = MainWindow()
win.show()

app.exec()

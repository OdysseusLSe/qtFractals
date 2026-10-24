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

import cv2
import copy
import os
import shutil
import sys
import time

import numpy as np

from pathlib import Path
from platformdirs import user_data_dir, user_config_dir, user_cache_dir

from PySide6.QtCore import (
    Qt,
    QFile,
    QIODevice,
    QJsonDocument,
    QCoreApplication,
    QSize,
    QTextStream
)
from PySide6.QtGui import (
    QAction,
    QColor,
    QDoubleValidator,
    QFont,
    QIcon,
    QImage,
    QIntValidator,
    QKeySequence,
    QPixmap
)
from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QComboBox,
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStatusBar,
    QStyle,
    QTextEdit,
    QVBoxLayout,
    QWidget
)

from FractalFrame import FractalFrame
from FractalHistory import FractalHistory
from FractalWidget import FractalWidget
from Logging import Logging

import resources_rc


#
#
#

class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.app_name    = "qtFractals"
        self.app_version = "0.7.5"

        self.setWindowTitle(f"{self.app_name} {self.app_version}")

        self.log = Logging("main", True)
        self.log.write(f"--- {self.app_name} {self.app_version} ---", False)
        self.log.entry("__init__", False)

        # Load the stylesheet from a file
        style_file = QFile(":/ui/style.css")
        if style_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(style_file)
            self.setStyleSheet(stream.readAll())
        else:
            self.log.error('Stylesheet ":/ui/style.css" not found!', True)

        # Initiate status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setFont(QFont("Arial", 11))
        self.status_bar.showMessage("--- Ready ---")

        # Build the menu bar with all the menus and actions
        self.build_menu_bar()

        # Set default values for fractal area, drawing dimensions, iteration
        # limit, and color palette
        self.set_default_values()

        # Build the main window with all the widgets
        self.build_main_window()

        self.start_time = time.process_time()

        self.history_list = []
        self.fh = FractalHistory(self.app_name, "history.json")
        self.history_list = self.fh.load_history()
        self.log.write(f"history_list={self.history_list}", False)

        user_cp_list = []
        for item in self.history_list:
            cp_name = item['col_pal']['name']
            if "(*)" in cp_name:
                self.log.write(f"user defined cp={cp_name}", False)
                if cp_name not in user_cp_list:
                    self.cp_list.append(item['col_pal'])
                    user_cp_list.append(cp_name)
                    self.log.write(f"self.cp_list={self.cp_list}", False)
                    self.cp_combo.addItem(cp_name)

        self.log.exit("__init__", False)

    #
    # -----------------------------------------------
    #

    def build_main_window(self):

        self.log.entry("build_main_window", False)

        # Offset of the widgets from the main window frame
        xOffset = 10
        yOffset = 10

        # Title of the main window
        self.setWindowTitle(self.app_name + " " + self.app_version)

        self.setMinimumHeight(800)

        # Build labels
        rp_lbl       = QLabel("<b>Origin of real part</b>:", self)
        ip_lbl       = QLabel("<b>Origin of imag. part</b>:", self)
        width_lbl    = QLabel("<b>Width</b>:", self)
        height_lbl   = QLabel("<b>Height</b>:", self)
        xDim_lbl     = QLabel("<b>x-Dim</b>:", self)
        yDim_lbl     = QLabel("<b>y-Dim</b>:", self)
        iter_lim_lbl = QLabel("<b>Iteration limit</b>:", self)

        #
        # Build line edits
        #

        bottom = self.frac_area['realOrigin']
        top    = self.frac_area['realOrigin'] + self.frac_area['realWidth']
        self.rp_edit = QLineEdit(self)
        self.rp_edit.setText(str(self.const_frac_area['realOrigin']))
        self.rp_edit.setValidator(QDoubleValidator(bottom, top, 15))
        self.rp_edit.setFixedWidth(160)

        bottom = self.frac_area['imagOrigin']
        top    = self.frac_area['imagOrigin'] + self.frac_area['imagHeight']
        self.ip_edit = QLineEdit(self)
        self.ip_edit.setText(str(self.const_frac_area['imagOrigin']))
        self.ip_edit.setValidator(QDoubleValidator(bottom, top, 15))
        self.ip_edit.setFixedWidth(160)

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
        # Indicator if Mandelbrot set or Julia set is active
        # (default: Mandelbrot set).
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

        layout_grid.addWidget(rp_lbl, 0, 0)
        layout_grid.addWidget(self.rp_edit, 0, 1)

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

        layout_grid.addWidget(ip_lbl, 1, 0)
        layout_grid.addWidget(self.ip_edit, 1, 1)

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

        self.fw = FractalWidget(
            self.const_frac_area,
            self.const_draw_dim,
            self.const_iter_lim,
            self.cp,
            self.current_frac_set,
            self.julia_c
        )
        self.fw.cur_rect.connect(self.sb_update_area)
        self.fw.closing.connect(self.calculation_closing)

        self.scroll_area = QScrollArea()

        sb_thickness = self.scroll_area.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        frame_margin = self.scroll_area.frameWidth() * 2
        min_width    = self.const_draw_dim['width'] + sb_thickness + frame_margin
        min_height   = self.const_draw_dim['height'] + sb_thickness + frame_margin
        self.scroll_area.setMinimumSize(min_width, min_height)

        log_string = f"sb_thickness,frame_margin={sb_thickness},{frame_margin}"
        self.log.write(log_string, False)
        log_string = f"min_width,min_height={min_width},{min_height}"
        self.log.write(log_string, False)

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.fw)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Connect the progress signal from the FractalWidget to the
        # update_progress method.
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

        # Create the "Misc" menu
        misc_menu = QMenu("&Misc", self)
        menu_bar.addMenu(misc_menu)

        # Create the "Show history" action
        self.shis_action = QAction("Show his&tory", self)
        self.shis_action.setShortcut(QKeySequence("Ctrl+T"))
        self.shis_action.setStatusTip("Show history")
        self.shis_action.triggered.connect(self.show_history)
        misc_menu.addAction(self.shis_action)

        # Create the "New color palette" action
        self.ncop_action = QAction("&New color palette", self)
        self.ncop_action.setShortcut(QKeySequence("Ctrl+N"))
        self.ncop_action.setStatusTip("New color palette")
        self.ncop_action.triggered.connect(self.new_color_palette)
        misc_menu.addAction(self.ncop_action)

        # Create the "Zoom video" action
        self.zoom_action = QAction("Zoo&m video", self)
        self.zoom_action.setShortcut(QKeySequence("Ctrl+M"))
        self.zoom_action.setStatusTip("Create zoom video")
        self.zoom_action.triggered.connect(self.zoom_video)
        misc_menu.addAction(self.zoom_action)

        # Create the "Help" menu
        help_menu = QMenu("&Help", self)
        menu_bar.addMenu(help_menu)

        # Create the "Read me" action
        self.read_action = QAction("Show &Readme", self)
        self.read_action.setShortcut(QKeySequence("Ctrl+R"))
        self.read_action.setStatusTip("Show Readme")
        self.read_action.triggered.connect(self.show_readme)
        help_menu.addAction(self.read_action)

        # MAC FIX: Connect the menu's hovered signal to a custom slots pipeline
        file_menu.hovered.connect(self.update_mac_sb)
        misc_menu.hovered.connect(self.update_mac_sb)
        help_menu.hovered.connect(self.update_mac_sb)

        self.log.exit("build_menu_bar", False)

    #
    # -----------------------------------------------
    #

    def calculation_closing(self, thumbnail):
        self.log.entry("calculation_closing", False)

        end_time = time.process_time()
        calc_time = end_time - self.start_time
        status = f" --- Process time: {calc_time} seconds ---"
        self.status_bar.showMessage(status)

        self.reset_btn.setEnabled(True)
        self.start_btn.setEnabled(True)

        if self.is_interim_pic:
            # Do not store this calculation in the history, because it is
            # either a preview for a new color palette or a frame for a video.
            self.is_interim_pic = False
            self.log.exit("calculation_closing", False)
            return

        thumbnail_name = f"{time.time()}.png"

        new_history_element = self.fw.build_history_element(thumbnail_name, calc_time)
        self.log.write(f"new_history_element={new_history_element}", False)

        self.history_list.append(new_history_element)
        self.log.write(f"history_list={self.history_list}", False)
        self.fh.save_history(self.history_list, thumbnail, thumbnail_name)

        self.log.exit("calculation_closing", False)

    #
    # -----------------------------------------------
    # Preview of new color palette.
    # -----------------------------------------------
    #

    def cp_showroom(self):
        self.log.entry("cp_showroom", False)

        self.is_interim_pic = True

        self.frac_area = {
            'realOrigin' : -1.9,
            'imagOrigin' : -1.2,
            'realWidth'  : 2.43,
            'imagHeight' : 2.43
        }

        self.draw_dim = {'width': 360, 'height': 360}
        self.iter_lim = 100

        self.default_frac_set = "Mandelbrot"
        self.julia_c = complex(10.0, 10.0)

        self.fw.set_parameters(
            self.frac_area,
            self.draw_dim,
            self.iter_lim,
            self.cp,
            self.current_frac_set,
            self.julia_c
        )

        self.fw.start_calculation(self.is_interim_pic)

        self.log.exit("cp_showroom", False)

    #
    # -----------------------------------------------
    # User changed color palette. This triggers immediately a new calculation.
    # -----------------------------------------------
    #

    def cp_text_changed(self, text):
        self.log.entry("cp_text_changed", False)

        self.log.write(f"text={text}", False)

        if self.is_new_cp:
            self.is_new_cp = False
        else:
            for element in self.cp_list:
                if text == element['name']:
                    self.cp = element
            self.log.write(f"self.cp={self.cp}", False)
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

    def create_video(
            self,
            rp_edit,
            ip_edit,
            width_edit,
            height_edit,
            iter_lim,
            dd_width,
            dd_height,
            color_palette,
            fps = 10,
            sec = 1
        ):
        self.log.entry("create_video", False)

        self.is_stopped = False
        cp = copy.copy(color_palette)

        # From string to float

        real_part = []
        real_part.append(float(rp_edit[0].text()))
        real_part.append(float(rp_edit[1].text()))

        imag_part = []
        imag_part.append(float(ip_edit[0].text()))
        imag_part.append(float(ip_edit[1].text()))

        width = []
        width.append(float(width_edit[0].text()))
        width.append(float(width_edit[1].text()))

        height = []
        height.append(float(height_edit[0].text()))
        height.append(float(height_edit[1].text()))

        # Close zoom dialog of method "zoom_video"
        self.log.exit("ok_clicked", False)
        self.log.exit("zoom_video", False)
        self.zoom_dialog.close()

        # Center of the start area and end area
        cr_start = real_part[0] + width[0]  / 2
        cr_end   = real_part[1] + width[1]  / 2
        ci_start = imag_part[0] + height[0] / 2
        ci_end   = imag_part[1] + height[1] / 2

        # calculate steps between pics

        zoom_in = width[0] > width[1]
        num_of_frames = fps * sec
        if zoom_in:
            # For zoom-in I use an easing formula based on "Ease-Out"
            power = 4  # Higher value increases the slow down at the end
            ease_out = []
            for step in range(num_of_frames):
                t = step / (num_of_frames - 1)
                ease_out.append(1 - ((1 - t) ** power))
        else:
            # For zoom-out I use an easing formula based on "Ease-In"
            power = 4  # Higher value increases the accelaration at the end
            ease_in = []
            for step in range(num_of_frames):
                t = step / (num_of_frames - 1)
                ease_in.append(t ** power)

        # Build non-modal dialog to show progress

        cr_vid_dialog = QDialog(self)
        cr_vid_dialog.setWindowTitle("Creating video")

        main_layout = QVBoxLayout(cr_vid_dialog)

        thumbnail = QLabel()
        pixmap    = QPixmap()
        thumbnail.setMinimumSize(155, 155)
        thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumbnail.setPixmap(pixmap)
        main_layout.addWidget(thumbnail)

        frames_progress = QtWidgets.QProgressBar()
        frames_progress.setRange(0, num_of_frames)
        frames_progress.setValue(0)
        main_layout.addWidget(frames_progress)

        frames_per = QLabel("<b>Calculation: 0%</b>")
        frames_per.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(frames_per)

        frames_abs = QLabel(f"<b>Frames: 0/{num_of_frames}</b>")
        frames_abs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(frames_abs)

        button_box = QDialogButtonBox(QDialogButtonBox.Abort)
        main_layout.addWidget(button_box)

        cr_vid_dialog.setMinimumSize(cr_vid_dialog.sizeHint())
        cr_vid_dialog.show()
        cr_vid_dialog.raise_()
        cr_vid_dialog.activateWindow()

        def button_clicked(button):
            self.is_stopped = True

        button_box.clicked.connect(button_clicked)

        # Create directory for video frames
        dir_time = time.time()
        dir_name = f"{self.cache_dir}/{self.app_name}.video-{dir_time}"
        dir_path = Path(dir_name)
        try:
            dir_path.mkdir(exist_ok=True, parents=True)
        except BaseException as error:
            self.log.error(f"Directory for video frames ({error})!", True)

        # Define compression and file name for rendering
        video_name = f"{self.app_name}-{dir_time}.mp4"
        video_full_path = dir_path.joinpath(video_name)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(
            str(video_full_path),
            fourcc,
            fps,
            (dd_width, dd_height)
        )

        self.ff         = FractalFrame()
        image           = QImage()
        frame_name_list = []

        #
        # Start calculation of frames and rendering of video
        #

        for step in range(0, num_of_frames, 1):

            if self.is_stopped:
                break

            factor = ease_out[step] if zoom_in else ease_in[step]

            current_width  = width[0]  + (width[1]  - width[0])  * factor
            current_height = height[0] + (height[1] - height[0]) * factor

            current_cr = cr_start + (cr_end - cr_start) * factor
            current_ci = ci_start + (ci_end - ci_start) * factor

            frac_area = {
                'realOrigin': current_cr - current_width / 2,
                'imagOrigin': current_ci - current_height / 2,
                'realWidth' : current_width,
                'imagHeight': current_height
            }

            image = self.ff.mandelbrot_frame(
                frac_area,
                iter_lim,
                dd_width,
                dd_height,
                cp
            )

            """
            frame_name = f"{step:06d}.png"
            frame_name_list.append(frame_name)
            frame_full_path = dir_path.joinpath(frame_name)
            self.log.write(f"frame_full_path={frame_full_path}", False)
            """

            # Create thumbnail for progress window
            thumbnail.setPixmap(QPixmap.fromImage(image.scaledToWidth(
                150,
                Qt.TransformationMode.FastTransformation
            )))

            image = image.convertToFormat(QImage.Format.Format_RGB32)
            w     = image.width()
            h     = image.height()
            ptr   = image.bits()
            arr   = np.frombuffer(ptr, dtype=np.uint8).reshape((h, w, 4))
            video.write(cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR))

            frames_progress.setValue(step+1)
            percent = (step+1) / num_of_frames * 100
            frames_per.setText(f"<b>Calculation: {percent:.2f}%</b>")

            frames_abs.setText(f"<b>Frames: {step+1}/{num_of_frames}</b>")

            QCoreApplication.processEvents()

        if self.is_stopped:
            # User stopped calculation
            video.release()
            cv2.destroyAllWindows()

            cr_vid_dialog.close()

            msg = f"Aborted Video\n {video_name}\n in cache\n {str(dir_path)}"
            QMessageBox.warning(self, "Video in cache", msg)

            self.log.exit("create_video", False)
            return

        video.release()
        cv2.destroyAllWindows()

        current_dir = os.getcwd()
        os.chdir(dir_name)

        # Delete progress dialog for calculation and rendering
        cr_vid_dialog.close()

        # Select directory where to save the newly created video to
        folder_path = QFileDialog.getExistingDirectory(
            self,
            caption="Select folder to save video",
            dir=str(Path.home()),
            options=QFileDialog.ShowDirsOnly
        )
        if folder_path:

            video_full_path.copy_into(folder_path, preserve_metadata=True)
            os.chdir(current_dir)
            shutil.rmtree(dir_name)

            msg = f"Video\n {video_name}\n successful saved in\n {folder_path}"
            QMessageBox.information(self, "Video saved", msg)

        else:

            msg = f"Video\n {video_name}\n still in cache\n {str(dir_path)}"
            QMessageBox.warning(self, "Video in cache", msg)

        os.chdir(current_dir)

        self.log.exit("create_video", False)

    #
    # -----------------------------------------------
    #

    def dd_text_changed(self, text):
        self.log.entry("dd_text_changed", False)

        self.log.write(f"text={text}", False)

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
    # Load color palettes (for more details see FractalWorker.py)
    # -----------------------------------------------
    #

    def load_color_palettes(self):
        self.log.entry("load_color_palettes", False)

        self.cp_list = []
        file = QFile(":/ui/color_palettes.json")

        if file.open(QIODevice.ReadOnly | QIODevice.Text):
            cp_file_data = file.readAll()
            file.close()
            json_doc = QJsonDocument.fromJson(cp_file_data)
            self.cp_list = json_doc.toVariant()
        else:
            self.log.error(f"Loading color palettes:{file.errorString()}!", True)
            self.log.exit("load_color_palettes", False)
            return None

        # Filter default color palette
        for cp in self.cp_list:
            if cp['name'] == "Fire & Ice":
                self.log.exit("load_color_palettes", False)
                return cp

        self.log.exit("load_color_palettes", False)
        return None

    #
    # -----------------------------------------------
    #

    def new_color_palette(self):
        self.log.entry("new_color_palette", False)

        self.ncop_dialog = QDialog(self)
        self.ncop_dialog.setWindowTitle("New color palette")

        spin   = [[None for _ in range(3)] for _ in range(4)]
        vector = [[0.00 for _ in range(3)] for _ in range(4)]

        temp_cp       = copy.copy(self.cp)
        self.bg_color = QColor("black")

        def select_color():
            new_bg_color = QColorDialog.getColor(parent=self, title="Select color")
            if new_bg_color.isValid():
                self.bg_color = new_bg_color

        #
        # Build the user interface
        #

        main_layout = QVBoxLayout(self.ncop_dialog)

        name_lbl   = QLabel("<b>Name of new color palette: </b>", self)
        name_edit  = QLineEdit(self)
        name_edit.setText("New Color Palette")
        layout = QHBoxLayout()
        layout.addWidget(name_lbl)
        layout.addWidget(name_edit)
        main_layout.addLayout(layout)

        # Input for the 4 vectors

        vectors = ["Brightness", "Contrast", "Frequency", "Phase"]

        row = 0
        for item in vectors:
            layout = QHBoxLayout()
            desc = QLabel(f"<b>{item} (RGB):</b>", self)
            layout.addWidget(desc, 1)
            column = 0
            for color in ["R: ", "G: ", "B: "]:
                spin[row][column] = QDoubleSpinBox()
                spin[row][column].setRange(0.0, 1.0)
                spin[row][column].setSingleStep(0.01)
                spin[row][column].setPrefix(color)
                layout.addWidget(spin[row][column], 0)
                column = column + 1
            main_layout.addLayout(layout)
            row = row + 1
            self.log.write(f"spin={spin}", False)

        col_btn = QPushButton("Select background color", self)
        col_btn.clicked.connect(select_color)
        main_layout.addWidget(col_btn)

        QBtn = (
            QDialogButtonBox.Apply | QDialogButtonBox.Save | QDialogButtonBox.Close
        )
        button_box = QDialogButtonBox(QBtn)
        main_layout.addWidget(button_box)

        def vector_to_cp():
            self.cp['name'] = f"{name_edit.text()} (*)"
            for row in range(4):
                for column in range(3):
                    vector[row][column] = spin[row][column].value()
            self.cp['brightnessR'] = vector[0][0]
            self.cp['brightnessG'] = vector[0][1]
            self.cp['brightnessB'] = vector[0][2]
            self.cp['contrastR']   = vector[1][0]
            self.cp['contrastG']   = vector[1][1]
            self.cp['contrastB']   = vector[1][2]
            self.cp['frequencyR']  = vector[2][0]
            self.cp['frequencyG']  = vector[2][1]
            self.cp['frequencyB']  = vector[2][2]
            self.cp['phaseR']      = vector[3][0]
            self.cp['phaseG']      = vector[3][1]
            self.cp['phaseB']      = vector[3][2]

        def preview_cp():
            vector_to_cp()
            R, G, B, A = self.bg_color.getRgb()
            self.cp['bg_R'] = R
            self.cp['bg_G'] = G
            self.cp['bg_B'] = B
            self.cp_showroom()

        def save_cp():
            vector_to_cp()
            R, G, B , A = self.bg_color.getRgb()
            self.cp['bg_R'] = R
            self.cp['bg_G'] = G
            self.cp['bg_B'] = B
            self.cp_list.append(self.cp)
            self.log.write(f"self.cp_list={self.cp_list}", False)
            self.cp_combo.addItem(self.cp['name'])
            self.is_new_cp = True
            self.cp_combo.setCurrentText(self.cp['name'])
            self.log.write("calling self.reset()", False)
            self.reset()

        def button_clicked(button):
            role = button_box.buttonRole(button)
            if role == QDialogButtonBox.ApplyRole:
                # "Apply" maps to the preview method
                preview_cp()
            elif role == QDialogButtonBox.ButtonRole.AcceptRole:
                # "Save" maps to the save method
                save_cp()
            if role == QDialogButtonBox.ButtonRole.RejectRole:
                # "Close" maps to the reject role
                self.cp = copy.copy(temp_cp)
                self.ncop_dialog.reject()

        button_box.clicked.connect(button_clicked)

        # Exec dialog

        self.ncop_dialog.setMinimumSize(self.ncop_dialog.sizeHint())
        self.ncop_dialog.exec()

        self.log.exit("new_color_palette", False)

    #
    # -----------------------------------------------
    #

    def repeat_item(self, item):
        self.log.entry("repeat_item", False)

        history_item = self.history_list[item]

        fa = history_item['frac_area']
        dd = history_item['draw_dim']
        il = history_item['iter_lim']
        cp = history_item['col_pal']
        fs = history_item['frac_set']
        jc = complex(history_item['real_julia_c'], history_item['imag_julia_c'])

        self.fw.set_parameters(fa, dd, il, cp, fs, jc)

        self.fw.start_calculation()

        self.log.entry("repeat_item", False)

    #
    # -----------------------------------------------
    #

    def reset(self):
        self.log.entry("reset", False)

        self.rp_edit.setText(str(self.const_frac_area['realOrigin']))
        self.ip_edit.setText(str(self.const_frac_area['imagOrigin']))
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
        self.log.write(f"file_name={file_name}", False)
        self.log.write(f"selected_filter={selected_filter}", False)
        if file_name == "":
            self.log.exit("save_image", False)
            return

        result = image.save(file_name, None, 100)
        if result:
            self.log.write("Image successful saved.", False)
        else:
            self.log.error("Image not saved!", True)

        self.log.exit("save_image", False)

    #
    # -----------------------------------------------
    #

    def set_default_values(self):
        self.log.entry("set_default_values", False)

        self.cache_dir = user_cache_dir(self.app_name, "OdysseusLSe")

        self.is_interim_pic = False
        self.is_new_cp      = False

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
        self.cp = copy.copy(self.load_color_palettes())
        self.log.write(f"self.cp={self.cp}", False)

        self.log.exit("set_default_values", False)

    #
    # -----------------------------------------------
    #

    def show_history(self):
        self.log.entry("show_history", False)

        self.fh.show_history_list(self.history_list)
        if self.fh.repeat():
            item = self.fh.item_of_history()
            self.log.entry(f"item={item}", False)
            self.repeat_item(item)

        self.log.exit("show_history", False)

    #
    # -----------------------------------------------
    #

    def show_readme(self):
        self.log.entry("show_readme", False)

        self.read_dialog = QDialog(self)
        self.read_dialog.setWindowTitle("Readme")
        self.read_dialog.resize(1000, 600)
        # Makes the dialog modal without blocking the TSM subsystem
        self.read_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)

        layout = QVBoxLayout(self.read_dialog)

        self.text_edit = QTextEdit(self.read_dialog)
        self.text_edit.setReadOnly(True)

        layout.addWidget(self.text_edit)

        path = Path("README.md")
        if path.exists():
            content = path.read_text(encoding="utf-8")
            self.text_edit.setMarkdown(content)
        else:
            self.log.error("Readme file not found!", True)

        QBtn = (QDialogButtonBox.Ok)
        button_box = QDialogButtonBox(QBtn)
        layout.addWidget(button_box)
        button_box.accepted.connect(self.read_dialog.accept)

        # Show dialog

        self.read_dialog.setMinimumSize(self.read_dialog.sizeHint())
        self.read_dialog.exec()

        self.log.exit("show_readme", False)

    #
    # -----------------------------------------------
    #

    def sb_update_area(self, area):
        self.log.entry("sb_update_area", False)
        self.log.write(f"area={area}", False)

        ro = area['realOrigin']
        io = area['imagOrigin']
        rw = area['realWidth']
        ih = area['imagHeight']
        status = f"--- Rectangle: Real part: {ro:.15f}, Imag part: {io:.15f}, "
        status = status + f"Width: {rw:.15f}, Height: {ih:.15f}"
        self.status_bar.showMessage(status)

        self.log.exit("sb_update_area", False)

    #
    # -----------------------------------------------
    #

    def trigger_calculation(self):
        self.log.entry("trigger_calculation", False)

        if self.is_interim_pic:
            self.fw.start_calculation(self.is_interim_pic)
            self.is_interim_pic = False
            self.log.exit("trigger_calculation", False)
            return

        self.progress_bar.setValue(0)
        self.reset_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.frac_area = {
            'realOrigin': float(self.rp_edit.text()),
            'imagOrigin': float(self.ip_edit.text()),
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

        self.log.exit("trigger_calculation", False)

    #
    # -----------------------------------------------
    #

    def update_mac_sb(self, action):
        self.log.entry("update_mac_sb", False)

        if action and action.statusTip():
            self.log.write(f"action.statusTip()={action.statusTip()}", False)
            self.status_bar.showMessage(action.statusTip())
        else:
            self.status_bar.clearMessage()

        self.log.exit("update_mac_sb", False)

    #
    # -----------------------------------------------
    #

    def update_progress(self, value):
        self.log.entry("update_progress", False)

        if value == 1:

            self.start_time = time.process_time()
            self.log.write(f"Calculation started (value={value})", False)

            self.reset_btn.setEnabled(False)
            self.start_btn.setEnabled(False)

            frac_area, draw_dim, iter_lim, frac_set, julia_c = self.fw.get_parameters()

            self.frac_area        = copy.deepcopy(frac_area)
            self.draw_dim         = copy.deepcopy(draw_dim)
            self.iter_lim         = iter_lim
            self.current_frac_set = frac_set
            self.julia_c          = julia_c
            self.log.write(f"self.current_frac_set={self.current_frac_set}", False)

            # Adapt text fields to current values

            self.rp_edit.setText(str(self.frac_area['realOrigin']))
            self.ip_edit.setText(str(self.frac_area['imagOrigin']))
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
        self.status_bar.showMessage(f"--- Progress: {percent}%")

        self.progress_bar.setValue(value)

        self.log.exit("update_progress", False)

    #
    # -----------------------------------------------
    #

    def zoom_video(self):
        self.log.entry("zoom_video", False)

        self.zoom_dialog = QDialog(self)
        self.zoom_dialog.setWindowTitle("Zoom video")

        main_layout = QVBoxLayout(self.zoom_dialog)

        title       = []
        rp_edit     = []
        ip_edit     = []
        width_edit  = []
        height_edit = []
        grab_btn    = []

        def grab(item):
            frac_area, dd, iter_lim, fd, jc = self.fw.get_parameters()
            rp_edit[item].setText(str(frac_area['realOrigin']))
            ip_edit[item].setText(str(frac_area['imagOrigin']))
            width_edit[item].setText(str(frac_area['realWidth']))
            height_edit[item].setText(str(frac_area['imagHeight']))

            iter_lim_edit.setText(str(iter_lim))
            dd_width.setText(str(dd['width']))
            dd_height.setText(str(dd['height']))

        def input_area():

            title.append(QLabel("<b>First Mandelbrot set</b>", self))
            title.append(QLabel("<b>Last Mandelbrot set</b>", self))

            for loop in range(0, 2, 1):
                self.log.write(f"loop={loop}", False)

                grid = QGridLayout()

                title[loop].setAlignment(Qt.AlignmentFlag.AlignCenter)
                main_layout.addWidget(title[loop])

                label = QLabel("<b>Origin of real part</b>:", self)
                bottom = self.frac_area['realOrigin']
                top    = self.frac_area['realOrigin'] + self.frac_area['realWidth']
                rp_edit.append(QLineEdit(self))
                rp_edit[loop].setText(str(self.const_frac_area['realOrigin']))
                rp_edit[loop].setValidator(QDoubleValidator(bottom, top, 15))
                grid.addWidget(label, 0, 0)
                grid.addWidget(rp_edit[loop], 0, 1)

                label = QLabel("<b>Origin of imag. part</b>:", self)
                bottom = self.frac_area['imagOrigin']
                top    = self.frac_area['imagOrigin'] + self.frac_area['imagHeight']
                ip_edit.append(QLineEdit(self))
                ip_edit[loop].setText(str(self.const_frac_area['imagOrigin']))
                ip_edit[loop].setValidator(QDoubleValidator(bottom, top, 15))
                grid.addWidget(label, 1, 0)
                grid.addWidget(ip_edit[loop], 1, 1)

                label = QLabel("<b>Width</b>:", self)
                bottom = 0.00000000001
                top    = self.frac_area['realWidth']
                width_edit.append(QLineEdit(self))
                width_edit[loop].setText(str(self.const_frac_area['realWidth']))
                width_edit[loop].setValidator(QDoubleValidator(bottom, top, 15))
                grid.addWidget(label, 2, 0)
                grid.addWidget(width_edit[loop], 2, 1)

                label = QLabel("<b>Height</b>:", self)
                bottom = 0.00000000001
                top    = self.frac_area['imagHeight']
                height_edit.append(QLineEdit(self))
                height_edit[loop].setText(str(self.const_frac_area['imagHeight']))
                height_edit[loop].setValidator(QDoubleValidator(bottom, top, 15))
                grid.addWidget(label, 3, 0)
                grid.addWidget(height_edit[loop], 3, 1)

                main_layout.addLayout(grid)

                # "Grab" Button
                grab_btn.append(QPushButton('Grab current Mandelbrot set', self))
                grab_btn[loop].clicked.connect(lambda checked=False, item=loop: grab(item))
                main_layout.addWidget(grab_btn[loop])

                # Separation line
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFrameShadow(QFrame.Shadow.Sunken)
                line.setStyleSheet("background-color: #c0c0c0; max-height: 1px;")
                main_layout.addWidget(line)

        def cp_changed(text):
            for element in self.cp_list:
                if text == element['name']:
                    self.cp = copy.copy(element)

        input_area()

        row = QHBoxLayout()
        label  = QLabel("<b>Iterations</b>:", self)
        iter_lim_edit = QLineEdit(self)
        iter_lim_edit.setText(str(self.const_iter_lim))
        iter_lim_edit.setValidator(QIntValidator(100, 5000))
        iter_lim_edit.setFixedWidth(50)
        row.addWidget(label)
        row.addWidget(iter_lim_edit)

        label  = QLabel("<b>Width x Height</b>:", self)
        row.addWidget(label)

        dd_width = QLineEdit(self)
        dd_width.setText("1280")
        dd_width.setValidator(QIntValidator(100, 10000))
        dd_width.setFixedWidth(50)
        row.addWidget(dd_width)

        label  = QLabel("<b>x</b>", self)
        row.addWidget(label)

        dd_height = QLineEdit(self)
        dd_height.setText("720")
        dd_height.setValidator(QIntValidator(100, 10000))
        dd_height.setFixedWidth(50)
        row.addWidget(dd_height)

        main_layout.addLayout(row)

        temp_cp = copy.copy(self.cp)
        row = QHBoxLayout()
        label  = QLabel("<b>Choose color palette:</b>")
        row.addWidget(label)
        cp_combo = QComboBox()
        for element in self.cp_list:
            cp_combo.addItem(element['name'])
            if element['name'] == self.cp['name']:
                cp_combo.setCurrentText(element['name'])
        cp_combo.currentTextChanged.connect(cp_changed)
        row.addWidget(cp_combo)

        main_layout.addLayout(row)

        row = QHBoxLayout()

        label  = QLabel("<b>FPS</b>:", self)
        fps_edit = QLineEdit(self)
        fps_edit.setText("10")
        fps_edit.setValidator(QIntValidator(10, 90))
        fps_edit.setFixedWidth(50)
        row.addWidget(label)
        row.addWidget(fps_edit)

        label  = QLabel("<b>Seconds</b>:", self)
        sec_edit = QLineEdit(self)
        sec_edit.setText("1")
        sec_edit.setValidator(QIntValidator(1, 600))
        sec_edit.setFixedWidth(50)
        row.addWidget(label)
        row.addWidget(sec_edit)

        main_layout.addLayout(row)

        QBtn = (QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box = QDialogButtonBox(QBtn)
        main_layout.addWidget(button_box)

        def ok_clicked():
            self.log.entry("ok_clicked", False)
            self.create_video(
                rp_edit,
                ip_edit,
                width_edit,
                height_edit,
                int(iter_lim_edit.text()),
                int(dd_width.text()),
                int(dd_height.text()),
                self.cp,
                int(fps_edit.text()),
                int(sec_edit.text())
            )
            self.cp = copy.copy(temp_cp)

        def cancel_clicked():
            self.log.exit("zoom_video", False)
            self.zoom_dialog.close()

        button_box.accepted.connect(ok_clicked)
        button_box.rejected.connect(cancel_clicked)

        # Show dialog

        self.zoom_dialog.setMinimumSize(self.zoom_dialog.sizeHint())
        self.zoom_dialog.show()

        self.log.exit("zoom_video", False)

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

sys.exit(app.exec())

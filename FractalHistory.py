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

import json
import pprint
import time

from pathlib import Path
from platformdirs import user_data_dir, user_config_dir, user_cache_dir

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout
)

from Logging import Logging


class FractalHistory():

    #
    # Constructor
    #

    def __init__(self, app_name, file_name):
        super().__init__()

        self.log = Logging("FractalHistory", True)
        self.log.entry("__init__")

        # 1. Für Benutzerdaten (z. B. Datenbanken, Speicherstände)
        data_dir = user_data_dir(app_name, "OdysseusLSe")

        # 2. Für Konfigurationsdateien (z. B. settings.json, config.ini)
        config_dir = user_config_dir(app_name, "OdysseusLSe")

        # 3. Für temporäre Caches
        cache_dir = user_cache_dir(app_name, "OdysseusLSe")

        self.dir = Path(f"{data_dir}/{app_name}.history")
        self.file_name = self.dir.joinpath(file_name)
        self.log.write(f"file_name={self.file_name}")

        try:
            self.dir.mkdir(exist_ok=True, parents=True)
        except BaseException as error:
            self.log.error(f"Directory for history ({error})!", True)

        self.repeat_item = False
        self.history_clr = False
        self.item_to_repeat = -1

        self.log.exit("__init__")

    #
    # -----------------------------------------------
    #

    def build_history_item(self, history_item):
        self.log.entry("build_history_item(history_item)")
        self.log.write(f"history_item={history_item}")

        tn_path_name = self.dir.joinpath(history_item['thumbnail'])
        self.log.write(f"tn_path_name={tn_path_name}")

        ro = str(history_item['frac_area']['realOrigin'])
        io = str(history_item['frac_area']['imagOrigin'])
        rw = str(history_item['frac_area']['realWidth'])
        ih = str(history_item['frac_area']['imagHeight'])
        il = str(history_item['iter_lim'])
        dw = str(history_item['draw_dim']['width'])
        dh = str(history_item['draw_dim']['height'])
        ct = str(history_item['calc_time'])

        epoch_time = history_item['thumbnail'].rsplit('.', 1)[0]
        self.log.write(f"epoch_time={epoch_time}")

        et = float(epoch_time)
        ts = time.strftime("%Y.%m.%d-%H:%M:%S", time.gmtime(et))

        fs = history_item['frac_set']
        if fs == "Julia":
            text = f"Fractal set ({ts}): Julia\n"
            jr = str(history_item['real_julia_c'])
            ji = str(history_item['imag_julia_c'])
            text = text + f"c of Julia: {jr}, {ji}\n"
        else:
            text = f"Fractal set ({ts}): Mandelbrot\n"

        text = text + f"Origin: {ro}, {io}\n"
        text = text + f"Size: {rw}, {ih}\n"
        text = text + f"Iteration limit: {il}\n"
        text = text + f"Draw dimensions: {dw}x{dh}\n"
        text = text + f"Calculation time: {ct} seconds"

        item = QListWidgetItem(f"{text}")
        item.setIcon(QIcon(str(tn_path_name)))

        self.log.exit("build_history_item")
        return item

    #
    # -----------------------------------------------
    #

    def clear_history(self):
        self.log.entry("clear_history()")

        if self.history_clr:
            return

        self.file_name.unlink()
        for item in self.dir.iterdir():
            if item.is_file():
                item.unlink()

        self.history_clr = True

        self.log.exit("clear_history")

    #
    # -----------------------------------------------
    #

    def history_clear(self):
        return self.history_clr

    #
    # -----------------------------------------------
    #

    def item_of_history(self):
        return self.item_to_repeat

    #
    # -----------------------------------------------
    #

    def load_history(self):
        self.log.entry("load_history()")

        history_data = []
        try:
            with open(self.file_name, 'r', encoding="utf-8") as f:
                history_data = json.load(f)
        except BaseException as error:
            self.log.warning(f"Warning ({error}) with reading history!", True)

        self.log.exit("load_history")
        return history_data

    #
    # -----------------------------------------------
    #

    def repeat(self):
        return self.repeat_item

    #
    # -----------------------------------------------
    #

    def save_history(self, history_data, thumbnail=None, thumbnail_name=None):
        self.log.entry("save_history(history_data, thumbnail=None, thumbnail_name=None)")

        self.log.write(f"history_data={history_data}")

        if thumbnail is not None:
            tn_path_name = self.dir.joinpath(thumbnail_name)
            self.log.write(f"tn_path_name={tn_path_name}")

            result = thumbnail.save(str(tn_path_name), None, 100)
            if result:
                self.log.write("Thumbnail successful saved.")
            else:
                self.log.error("Thumbnail not saved!", True)

        try:
            with open(self.file_name, 'w', encoding="utf-8") as f:
                json.dump(history_data, f, ensure_ascii=False, indent=4)
        except BaseException as error:
            self.log.error(f"Error ({error}) with saving history!", True)

        self.history_clr = False

        self.log.exit("save_history")

    #
    # -----------------------------------------------
    #

    def show_history_list(self, history_data):
        self.log.entry("show_history_list(history_data)")

        log_string = pprint.pformat(history_data)
        self.log.write(f"history_data=\n{log_string}")

        self.repeat_item = False
        self.item_to_repeat = -1

        self.history_dialog = QDialog()
        self.history_dialog.setWindowTitle("History")
        self.history_dialog.resize(600, 400)

        main_layout = QHBoxLayout(self.history_dialog)

        list_widget = QListWidget(self.history_dialog)
        list_widget.setIconSize(QSize(150, 100))
        list_widget.setMinimumWidth(550)
        list_widget.setSpacing(5)

        for history_item in history_data:
            self.log.write(f"history_item={history_item}")
            item = self.build_history_item(history_item)
            list_widget.addItem(item)
        list_widget.clearSelection()

        main_layout.addWidget(list_widget)

        btn_layout = QVBoxLayout()

        btn_repeat = QPushButton("Repeat", self.history_dialog)
        btn_delete = QPushButton("Delete", self.history_dialog)
        btn_clear  = QPushButton("Clear\nhistory", self.history_dialog)
        btn_close  = QPushButton("Close", self.history_dialog)

        btn_clear.setStyleSheet("""
            QPushButton {
                border: 2px solid black;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton:hover {
                color: white;
                background-color: red;
            }
        """)

        # ------------------------------------------------------------

        def on_repeat_clicked():
            self.log.entry(f"on_repeat_clicked()")
            current_row = list_widget.currentRow()
            if current_row >= 0:
                self.log.write(f"current_row={current_row}")
                selected_item = history_data[current_row]
                self.log.write(f"Repeat of {current_row}: {selected_item}")
                self.history_dialog.accept()
                self.repeat_item = True
                self.item_to_repeat = current_row
            else:
                self.log.write("No item selected!")

        def on_delete_clicked():
            self.log.entry(f"on_delete_clicked()")
            current_row = list_widget.currentRow()
            if current_row >= 0:

                list_widget.setCurrentRow(current_row)

                dlg_text = "Delete selected history item?"

                warning_dlg = QMessageBox(self.history_dialog)
                warning_dlg.setIcon(QMessageBox.Icon.Warning)
                warning_dlg.setWindowTitle("Delete item?")
                warning_dlg.setText(dlg_text)
                warning_dlg.setStyleSheet("QLabel { text-align: center; }")
                warning_dlg.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                button = warning_dlg.exec()

                if button == QMessageBox.StandardButton.Yes:
                    self.log.write(f"current_row={current_row}")
                    list_widget.takeItem(current_row)

                    self.log.write(f"item to delete: {history_data[current_row]}")

                    # Delete appropriate thumbnail
                    tn_path_name = self.dir.joinpath(history_data[current_row]['thumbnail'])
                    self.log.write(f"tn_path_name={tn_path_name}")
                    p = Path(tn_path_name)
                    p.unlink()

                    # Delete item in history list
                    deleted_item = history_data.pop(current_row)
                    self.log.write(f"Item deleted: {deleted_item}")

                    self.save_history(history_data)

            else:

                self.log.write("No item for deletion selected.")

        def on_clear_clicked():
            self.log.entry(f"on_clear_clicked()")

            dlg_text = "Clear history?\n"
            dlg_text = dlg_text + "All entries and associated user defined\n"
            dlg_text = dlg_text + "color palettes will be deleted!"

            warning_dlg = QMessageBox(self.history_dialog)
            warning_dlg.setIcon(QMessageBox.Icon.Warning)
            warning_dlg.setWindowTitle("Clear history?")
            warning_dlg.setText(dlg_text)
            warning_dlg.setStyleSheet("QLabel { text-align: center; }")
            warning_dlg.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            button = warning_dlg.exec()
            if button == QMessageBox.StandardButton.Yes:
                self.clear_history()
                self.history_dialog.accept()

        # ------------------------------------------------------------

        # Connect buttons on actions
        btn_repeat.clicked.connect(on_repeat_clicked)
        btn_delete.clicked.connect(on_delete_clicked)
        btn_clear.clicked.connect(on_clear_clicked)
        btn_close.clicked.connect(self.history_dialog.accept)

        btn_layout.addWidget(btn_repeat)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_clear)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)

        main_layout.addLayout(btn_layout)

        self.history_dialog.exec()

        self.log.exit("show_history_list")

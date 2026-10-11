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

import json
import Logging

from pathlib import Path


class FractalHistory():

    #
    # Constructor
    #

    def __init__(self, directory, file_name):
        super().__init__()

        self.log = Logging.Logging("FractalHistory", True)
        self.log.entry("__init__", True)

        self.dir = Path(directory)
        self.file_name = self.dir.joinpath(file_name)
        self.log.write(f"file_name={self.file_name}", True)

        try:
            self.dir.mkdir(exist_ok=True, parents=True)
        except BaseException as error:
            self.log.error(f"Cannot create directory for history ({error})", True)

        self.log.exit("__init__", True)

    #
    # -----------------------------------------------
    #

    def load_history(self, history_data):
        self.log.entry("load_history", True)

        self.log.exit("load_history", True)

    #
    # -----------------------------------------------
    #

    def save_history(self, history_data, thumbnail, thumbnail_name):
        self.log.entry("save_history", True)

        self.log.write(f"history_data={history_data}", True)

        self.thumbnail_name = self.dir.joinpath(thumbnail_name)
        self.log.write(f"thumbnail_name={self.thumbnail_name}", True)
        result = thumbnail.save(str(self.thumbnail_name), None, 100)
        if result:
            self.log.write("Image successful saved.", True)
        else:
            self.log.error("Image not saved!", True)

        try:
            with open(self.file_name, 'w', encoding="utf-8") as f:
                json.dump(history_data, f, ensure_ascii=False, indent=4)
        except BaseException as error:
            self.log.error(f"Error ({error}) with opening history file!", True)

        self.log.exit("save_history", True)
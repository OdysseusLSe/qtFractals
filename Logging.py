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

from datetime import datetime


class Logging():

    def __init__(self, app_name, debug):
        self.app_name = app_name
        self.global_debug = debug
        self.n = 30

    def entry(self, info, local_debug=True):
        if self.global_debug and local_debug:
            current_time = datetime.now().strftime("%H:%M:%S")
            output_string = "[" + current_time + "]-" + self.app_name + ": "
            print(output_string.ljust(self.n) + ">" + info)

    def error(self, info, local_debug=True):
        if self.global_debug and local_debug:
            current_time = datetime.now().strftime("%H:%M:%S")
            output_string = "[" + current_time + "]-" + self.app_name + ": "
            print(output_string.ljust(self.n) + "*" + info)

    def exit(self, info, local_debug=True):
        if self.global_debug and local_debug:
            current_time = datetime.now().strftime("%H:%M:%S")
            output_string = "[" + current_time + "]-" + self.app_name + ": "
            print(output_string.ljust(self.n) + "<" + info)

    def write(self, info, local_debug=True):
        if self.global_debug and local_debug:
            current_time = datetime.now().strftime("%H:%M:%S")
            output_string = "[" + current_time + "]-" + self.app_name + ": "
            print(output_string.ljust(self.n) + "-" + info)

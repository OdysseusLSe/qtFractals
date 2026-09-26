from datetime import datetime

class Logging():

    def __init__(self, appName, debug):
        self.appName = appName
        self.global_debug = debug
        self.n = 28

    def entry(self, info, local_debug=True):
        if self.global_debug and local_debug:
            currentTime = datetime.now().strftime("%H:%M:%S")
            outputStr = "[" + currentTime + "]-" + self.appName + ": "
            print(outputStr.ljust(self.n) + ">" + info)

    def error(self, info, local_debug=True):
        if self.global_debug and local_debug:
            currentTime = datetime.now().strftime("%H:%M:%S")
            outputStr = "[" + currentTime + "]-" + self.appName + ": "
            print(outputStr.ljust(self.n) + "*" + info)

    def exit(self, info, local_debug=True):
        if self.global_debug and local_debug:
            currentTime = datetime.now().strftime("%H:%M:%S")
            outputStr = "[" + currentTime + "]-" + self.appName + ": "
            print(outputStr.ljust(self.n) + "<" + info)

    def write(self, info, local_debug=True):
        if self.global_debug and local_debug:
            currentTime = datetime.now().strftime("%H:%M:%S")
            outputStr = "[" + currentTime + "]-" + self.appName + ": "
            print(outputStr.ljust(self.n) + "-" + info)
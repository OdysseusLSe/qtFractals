from datetime import datetime

class Logging():

    def __init__(self, appName, debug):
        self.appName = appName
        self.debug = debug
        self.n = 28

    def entry(self, info):
        if self.debug:
            currentTime = datetime.now().strftime("%H:%M:%S")
            outputStr = "[" + currentTime + "]-" + self.appName + ": "
            print(outputStr.ljust(self.n) + ">" + info)

    def error(self, info):
        if self.debug:
            currentTime = datetime.now().strftime("%H:%M:%S")
            outputStr = "[" + currentTime + "]-" + self.appName + ": "
            print(outputStr.ljust(self.n) + "*" + info)

    def exit(self, info):
        if self.debug:
            currentTime = datetime.now().strftime("%H:%M:%S")
            outputStr = "[" + currentTime + "]-" + self.appName + ": "
            print(outputStr.ljust(self.n) + "<" + info)

    def write(self, info):
        if self.debug:
            currentTime = datetime.now().strftime("%H:%M:%S")
            outputStr = "[" + currentTime + "]-" + self.appName + ": "
            print(outputStr.ljust(self.n) + "-" + info)
#
# Copyright by Lavrentios Servissoglou under LGPL license
#
import copy

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget
)
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import Qt

import FractalWidget
import Logging

class MainWindow(QMainWindow):

    def __init__(self):
        # Konstruktor von QMainWindow aufrufen
        QMainWindow.__init__(self)

        appName = "qtFractals"
        appVersion = "0.2"

        self.setWindowTitle(appName + " " + appVersion)

        self.log = Logging.Logging(appName + " " + appVersion, True)
        self.log.write("--- " + appName + " " + appVersion + " ---")
        self.log.entry("init")

        # Default coordinates of the fractal (HD ratio)
        self.fractalArea = {
            'realOrigin': -4.0,
            'imagOrigin': -2.0,
            'realWidth': 7.1,
            'imagHeight': 4.0
        }
        self.constFractalArea = copy.deepcopy(self.fractalArea)

        # Default dimensions of the fractal window (HD:)
        self.drawDimensions = {'width': 1280, 'height': 720}
        self.constDrawDimensions = copy.deepcopy(self.drawDimensions)

        # Default iteration limit
        self.iterationLimit = 100
        self.constIterationLimit = self.iterationLimit

        # Default drawing dimensions to select
        self.selDrawDimensions = {
            'HD': "1280 x  720 (HD)",
            'Full HD': "1920 x 1080 (Full HD)",
            'Full QHD': "2560 × 1440 (Full QHD)",
            'Ultra-Wide WQHD': "3440 x 1440 (Ultra-Wide WQHD)",
            '4K Ultra HD': "3840 × 2160 (4K Ultra HD)",
            '8K Ultra HD': "7680 × 4320 (8K Ultra HD)"
        }

        # Default fractal set to calculate
        self.defaultFractalSet = "Mandelbrot"
        self.nextFractalSet = "Mandelbrot"

        # Default color palette
        cp = self.defineColorPalettes()
        self.colorPalette = copy.deepcopy(cp)
        self.log.write("self.colorPalette=" + str(self.colorPalette))

        #
        # Build the main window with all the widgets
        #

        # Offset of the widgets from the main window frame
        xOffset = 10
        yOffset = 10

        # Title of the main window
        self.setWindowTitle("qtFractals 0.2")

        # Build labels
        realPartLbl = QLabel("<b>Origin of real part</b>:", self)
        imagPartLbl = QLabel("<b>Origin of imag. part</b>:", self)
        widthLbl = QLabel("<b>Width</b>:", self)
        heightLbl = QLabel("<b>Height</b>:", self)
        xDimLbl = QLabel("<b>x-Dimension</b>:", self)
        yDimLbl = QLabel("<b>y-Dimension</b>:", self)
        iterLimitLbl = QLabel("<b>Iteration limit</b>:", self)

        #
        # Build line edits
        #

        self.realPartEdit = QLineEdit(self)
        self.realPartEdit.setPlaceholderText(str(self.fractalArea['realOrigin']))
        self.realPartEdit.setValidator(QDoubleValidator(-2.0, 2.0, 4))
        self.realPartEdit.setFixedWidth(160)

        self.imagPartEdit = QLineEdit(self)
        self.imagPartEdit.setPlaceholderText(str(self.fractalArea['imagOrigin']))
        self.imagPartEdit.setValidator(QDoubleValidator(-2.0, 2.0, 4))
        self.imagPartEdit.setFixedWidth(160)

        self.widthEdit = QLineEdit(self)
        self.widthEdit.setPlaceholderText(str(self.fractalArea['realWidth']))
        self.widthEdit.setValidator(QDoubleValidator(0.0001, 7.1, 4))
        self.widthEdit.setFixedWidth(160)

        self.heightEdit = QLineEdit(self)
        self.heightEdit.setPlaceholderText(str(self.fractalArea['imagHeight']))
        self.heightEdit.setValidator(QDoubleValidator(0.0001, 4.0, 4))
        self.heightEdit.setFixedWidth(160)

        self.xDimEdit = QLineEdit(self)
        self.xDimEdit.setPlaceholderText(str(self.drawDimensions['width']))
        self.xDimEdit.setValidator(QDoubleValidator(0.0001, 4.0, 4))
        self.xDimEdit.setFixedWidth(50)

        self.yDimEdit = QLineEdit(self)
        self.yDimEdit.setPlaceholderText(str(self.drawDimensions['height']))
        self.yDimEdit.setValidator(QDoubleValidator(0.0001, 4.0, 4))
        self.yDimEdit.setFixedWidth(50)

        self.iterLimitEdit = QLineEdit(self)
        self.iterLimitEdit.setPlaceholderText(str(self.iterationLimit))
        self.iterLimitEdit.setValidator(QDoubleValidator(0.0001, 4.0, 4))
        self.iterLimitEdit.setFixedWidth(50)

        #
        # Build combo box for drawing dimensions
        #

        self.ddCombo = QComboBox()
        self.ddCombo.addItems([
            "1280 x  720 (HD)",
            "1920 x 1080 (Full HD)",
            "2560 × 1440 (Full QHD)",
            "3440 x 1440 (Ulra-Wide WQHD)",
            "3840 × 2160 (4K Ultra HD)",
            "7680 × 4320 (8K Ultra HD)"
        ])
        self.ddCombo.currentTextChanged.connect(self.ddTextChanged)

        # Build radio buttons box        
        self.radBtnMandel = QRadioButton("Mandelbrot")
        self.radBtnMandel.setChecked(True)
        self.radBtnMandel.toggled.connect(self.toggledRadioBtn)
        self.radBtnJulia = QRadioButton("Julia")
        self.radBtnJulia.setEnabled(False)
        self.radBtnJulia.toggled.connect(self.toggledRadioBtn)

        # "Default" Button
        defaultBtn = QPushButton('Default', self)
        defaultBtn.clicked.connect(self.setDefaultValues)

        # "Start" Button
        self.startBtn = QPushButton('Start', self)
        self.startBtn.setEnabled(False)
        self.startBtn.clicked.connect(self.triggerCalculation)

        #
        # Build combo box for color palettes
        #

        cpLbl = QLabel("<b>Color palettes: </b>:", self)
        self.cpCombo = QComboBox()
        for element in self.cpList:
            self.cpCombo.addItem(element['name'])
            if element['name'] == self.colorPalette['name']:
                self.cpCombo.setCurrentText(element['name'])
        self.cpCombo.currentTextChanged.connect(self.cpTextChanged)

        # "Save" Button
        saveBtn = QPushButton('Save', self)
        saveBtn.setStyleSheet(
            # "background-color: red; "
            # "color: white; "
            "font-style: bold; "
            "font-size: 18px"
        )
        saveBtn.clicked.connect(self.saveImage)

        # "Quit" Button
        quitBtn = QPushButton('Quit', self)
        quitBtn.setStyleSheet(
            "background-color: red; "
            "color: white; "
            "font-style: bold; "
            "font-size: 18px"
        )
        quitBtn.clicked.connect(self.endApp)

        # All three buttons have the same width
        buttonWidth = defaultBtn.sizeHint().width()
        defaultBtn.setFixedWidth(buttonWidth)
        self.startBtn.setFixedWidth(buttonWidth)
        quitBtn.setFixedWidth(buttonWidth)

        # Progress bar
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setRange(0, self.drawDimensions['height'])
        self.progressBar.setValue(0)

        #
        # Layout labels, line edits, fractal window, progress bar, and buttons
        #

        layoutGrid = QGridLayout()

        # First row

        layoutGrid.addWidget(realPartLbl, 0, 0)
        layoutGrid.addWidget(self.realPartEdit, 0, 1)

        layoutGrid.addWidget(widthLbl, 0, 3)
        layoutGrid.addWidget(self.widthEdit, 0, 4)

        layoutGrid.addWidget(xDimLbl, 0, 6)
        layoutGrid.addWidget(self.xDimEdit, 0, 7)

        layoutGrid.addWidget(iterLimitLbl, 0, 9)
        layoutGrid.addWidget(self.iterLimitEdit, 0, 10)

        layoutGrid.addWidget(self.radBtnMandel, 0, 12)

        layoutGrid.addWidget(defaultBtn, 0, 14)

        # Second row

        layoutGrid.addWidget(imagPartLbl, 1, 0)
        layoutGrid.addWidget(self.imagPartEdit, 1, 1)

        layoutGrid.addWidget(heightLbl, 1, 3)
        layoutGrid.addWidget(self.heightEdit, 1, 4)

        layoutGrid.addWidget(yDimLbl, 1, 6)
        layoutGrid.addWidget(self.yDimEdit, 1, 7)

        layoutGrid.addWidget(self.ddCombo, 1, 9, 1, 2, Qt.AlignmentFlag.AlignHCenter)

        layoutGrid.addWidget(self.radBtnJulia, 1, 12)

        layoutGrid.addWidget(self.startBtn, 1, 14)

        # Space within the grid layout

        layoutGrid.setHorizontalSpacing(10)
        layoutGrid.setVerticalSpacing(10)

        layoutGrid.setColumnStretch(13, 1)
        layoutGrid.setColumnMinimumWidth(2, 30)
        layoutGrid.setColumnMinimumWidth(5, 30)
        layoutGrid.setColumnMinimumWidth(8, 30)
        layoutGrid.setColumnMinimumWidth(11, 30)

        # Create widget fractal
        self.fw = FractalWidget.FractalWidget(
            self.fractalArea,
            self.drawDimensions,
            self.iterationLimit,
            self.colorPalette
        )
        self.fw.setFixedSize(self.drawDimensions['width'], self.drawDimensions['height'])
        self.fw.progress.connect(self.updateProgress)

        # Buttons in the last row have their own layout
        lastRowLayout = QHBoxLayout()
        # lastRowLayout.setContentsMargins(0, 0, 0, 0)
        lastRowLayout.addWidget(cpLbl)
        lastRowLayout.addWidget(self.cpCombo)
        lastRowLayout.addStretch()
        lastRowLayout.addWidget(saveBtn)
        lastRowLayout.addStretch()
        lastRowLayout.addWidget(quitBtn)

        # Build the overall layout of the main window

        mainLayout = QVBoxLayout()

        # 10 pixel distance from every window frame
        mainLayout.setContentsMargins(xOffset, yOffset, xOffset, yOffset)
        mainLayout.setSpacing(10)

        mainLayout.addLayout(layoutGrid)
        mainLayout.addWidget(self.fw, 0, Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(self.progressBar)
        mainLayout.addLayout(lastRowLayout)

        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

        self.adjustSize()
        self.setMinimumSize(self.sizeHint())

        self.log.exit("init")

    #
    # -----------------------------------------------
    #

    def cpTextChanged(self, text):
        self.log.entry("cpTextChanged")

        self.log.write(text)

        for element in self.cpList:
            if text == element['name']:
                self.colorPalette = element
        self.log.write(str(self.colorPalette))

        self.fw.changeColorPalette(self.colorPalette)

        self.log.exit("cpTextChanged")

    #
    # -----------------------------------------------
    #

    def ddTextChanged(self, text):
        self.log.entry("ddTextChanged")

        self.log.write(text)

        if text == self.selDrawDimensions['HD']:
            self.xDimEdit.setText("1280")
            self.yDimEdit.setText("720")
        elif text == self.selDrawDimensions['Full HD']:
            self.xDimEdit.setText("1920")
            self.yDimEdit.setText("1080")
        elif text == self.selDrawDimensions['Full QHD']:
            self.xDimEdit.setText("2560")
            self.yDimEdit.setText("1440")
        elif text == self.selDrawDimensions['Ulra-Wide WQHD']:
            self.xDimEdit.setText("3440")
            self.yDimEdit.setText("1440")
        elif text == self.selDrawDimensions['4K Ultra HD']:
            self.xDimEdit.setText("3840")
            self.yDimEdit.setText("2160")
        elif text == self.selDrawDimensions['8K Ultra HD']:
            self.xDimEdit.setText("7680")
            self.yDimEdit.setText("4320")

        self.log.exit("ddTextChanged")

    #
    # -----------------------------------------------
    #       

    def defineColorPalettes(self):
        self.log.entry("defineColorPalettes")

        #
        # Color palette:
        # (color = brightness + contrast * math.cos(2 * math.pi * (frequency * velocity + phase)))
        #

        self.cpDeepForest = {
            'name': "Deep Forest",
            'brightnessR': 0.3,
            'brightnessG': 0.6,
            'brightnessB': 0.4,
            'contrastR': 0.3,
            'contrastG': 0.4,
            'contrastB': 0.2,
            'frequencyR': 1.0,
            'frequencyG': 1.0,
            'frequencyB': 1.0,
            'phaseR': 0.00,
            'phaseG': 0.05,
            'phaseB': 0.33
        }

        self.cpFireAndIce = {
            'name': "Fire & Ice",
            'brightnessR': 0.5,
            'brightnessG': 0.5,
            'brightnessB': 0.5,
            'contrastR': 0.5,
            'contrastG': 0.5,
            'contrastB': 0.5,
            'frequencyR': 1.0,
            'frequencyG': 1.0,
            'frequencyB': 1.0,
            'phaseR': 0.00,
            'phaseG': 0.15,
            'phaseB': 0.33
        }

        self.cpGreyscale = {
            'name': "Greyscale",
            'brightnessR': 0.5,
            'brightnessG': 0.5,
            'brightnessB': 0.5,
            'contrastR': 0.5,
            'contrastG': 0.5,
            'contrastB': 0.5,
            'frequencyR': 1.0,
            'frequencyG': 1.0,
            'frequencyB': 1.0,
            'phaseR': 0.00,
            'phaseG': 0.00,
            'phaseB': 0.00
        }

        self.cpList = [self.cpDeepForest, self.cpFireAndIce, self.cpGreyscale]

        self.log.exit("defineColorPalettes")

        # return default color palette
        return self.cpFireAndIce

    #
    # -----------------------------------------------
    #       

    def saveImage(self):
        self.log.entry("saveImage")

        image = self.fw.getImage()

        fileFilters = ["bmp", "jpg", "jpeg", "png"]
        self.log.write("fileFilters=" + str(fileFilters))
        initialFilter = fileFilters[3]
        self.log.write("initialFilter=" + initialFilter)
        filters = ";;".join(fileFilters)
        self.log.write("filters=" + filters)

        filename, selectedFilter = QFileDialog.getSaveFileName(
            self,
            "",
            "",
            # filters,
            # initialFilter,
            ";;",
            ""
        )
        self.log.write("filename=" + filename + " / selectedFilter=" + selectedFilter)
        if filename == "":
            self.log.exit("saveImage")
            return

        result = image.save(filename, None, 100)
        if result:
            self.log.write("Image successful saved")
        else:
            self.log.error("Image not saved!")

        self.log.exit("saveImage")

    #
    # -----------------------------------------------
    #       

    def setDefaultValues(self):
        self.log.entry("setDefaultValues")

        self.realPartEdit.setText(str(self.constFractalArea['realOrigin']))
        self.imagPartEdit.setText(str(self.constFractalArea['imagOrigin']))
        self.widthEdit.setText(str(self.constFractalArea['realWidth']))
        self.heightEdit.setText(str(self.constFractalArea['imagHeight']))

        self.xDimEdit.setText(str(self.constDrawDimensions['width']))
        self.yDimEdit.setText(str(self.constDrawDimensions['height']))

        self.iterLimitEdit.setText(str(self.constIterationLimit))

        self.log.exit("setDefaultValues")

    #
    # -----------------------------------------------
    #

    def toggledRadioBtn(self):
        self.log.entry("toggledRadioBtn")

        if self.sender().isChecked():
            self.nextFractalSet = self.sender().text()
            self.log.write(str(self.sender().isChecked()))
            self.log.write(self.sender().text())

        self.log.exit("toggledRadioBtn")

    #
    # -----------------------------------------------
    #       

    def triggerCalculation(self):
        self.log.entry("triggerCalculation")

        if self.realPartEdit.text() != "" and self.imagPartEdit.text() != "" \
                and self.widthEdit.text() != "" \
                and self.heightEdit.text() != "" \
                and self.iterLimitEdit.text() != "":

            self.progressBar.setValue(0)
            self.startBtn.setEnabled(False)
            self.fractalArea = {
                'realOrigin': float(self.realPartEdit.text()),
                'imagOrigin': float(self.imagPartEdit.text()),
                'realWidth': float(self.widthEdit.text()),
                'imagHeight': float(self.heightEdit.text())
            }
            self.log.write("self.fractalArea=" + str(self.fractalArea))

            self.drawDimensions = {
                'width': int(self.xDimEdit.text()),
                'height': int(self.yDimEdit.text())
            }
            self.log.write("self.drawDimensions=" + str(self.fractalArea))

            self.iterationLimit = int(self.iterLimitEdit.text())
            self.log.write("self.iterationLimit=" + str(self.iterationLimit))

            self.fw.setParameters(
                self.fractalArea,
                self.drawDimensions,
                self.iterationLimit,
                self.colorPalette
            )

            self.fw.startCalculation()

        else:
            QMessageBox.about(self, "Error", "All fields need an input!")

        self.log.exit("triggerCalculation")

    #
    # -----------------------------------------------
    #       

    def updateProgress(self, value):
        self.log.entry("updateProgress")

        #
        # 1st: adapt range of progress bar to current y-dimension of drawing
        # 2nd: adapt text fields to current values
        #

        if value == 1:
            self.progressBar.setRange(0, self.fw.height())

            self.fractalArea, self.drawDimensions, self.iterationLimit = self.fw.getParameters()

            self.realPartEdit.setText(str(self.fractalArea['realOrigin']))
            self.imagPartEdit.setText(str(self.fractalArea['imagOrigin']))
            self.widthEdit.setText(str(self.fractalArea['realWidth']))
            self.heightEdit.setText(str(self.fractalArea['imagHeight']))

            self.xDimEdit.setText(str(self.drawDimensions['width']))
            self.yDimEdit.setText(str(self.drawDimensions['height']))

            self.iterLimitEdit.setText(str(self.iterationLimit))

        # self.log.write("value: " + str(value) + "/" + str(self.fw.height()))

        self.progressBar.setValue(value)
        if value >= self.progressBar.maximum():
            self.startBtn.setEnabled(True)
        else:
            self.startBtn.setEnabled(False)

        self.log.exit("updateProgress")

    #
    # -----------------------------------------------
    #

    def endApp(self):
        self.log.entry("endApp")

        app.quit()


#
# -----------------------------------------------
#       

# The application runs until the window will be closed

app = QtWidgets.QApplication([])

win = MainWindow()
win.show()

app.exec()
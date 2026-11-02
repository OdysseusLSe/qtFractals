# qtFractals
App to calculate fractals with Python &amp; Qt (PySide6)

## Introduction
This app calculates fractal sets. It provides a few features like

- "zoom-in" in a fractal via cursor,
- "zoom-in" / "zoom-out" via specific input coordinates,
- define the area of the calculated set,
- define the value of iteration for the fractal formula,
- create zoom-in video
- history: every fractal calculation will be stored
- providing pre-defined drawing dimensions,
- switching from Mandelbrot set to Julia set,
- saving the calculated result in a file,
- change the color palette (providing pre-defined color palettes)
- ...

This program is free software: you can redistribute it and/or modify
it under the terms of the
[Apache 2.0 license](http://www.apache.org/licenses/LICENSE-2.0) as
published.

## "Main" window, "Drawing" window, and "New color palette" window

<!-- ![Main window](docs/main_window_legend.png) -->
<img src="docs/main_window_legend.png" alt="Main window" style="width:100%; height:auto;">

The left window with the application name as title is the "Main" window:

1.  **Origin coordinates of the complex area** separated by the real part
    and complex part and **Width and height of the complex area**.
2.  **Width and height of the drawing area (resolution)**. Additionally to the
    manual input you may select one of the predefined resolutions. Relevant for
    the next calculation are the values in the input/edit fields. Take care that
    the ratio of the complex area and the drawing area have the same value! As
    soon as you change the resolution, the fractal set will be recalculated.
    (Tip: defining areas to zoom in with the cursor takes into account the
    ratio by default.)
3.  **Itration limit** for the fractal formula. Good values are from 100 to
    2500. The bigger the value, the time consuming the calculation (more
    detailled results). Additionally a **Color palettes** provides a few
    predefined color palettes. As soon as you change the current color palette
    the current fractal set will be recalculated with the new selected colours.
4.  **Fractal indicator** that shows what kind of set (Mandelbrot or Julia)
    currently is active. Below you see three buttons: **"Reset", "Stop", and
    "Start"**: The "Reset" button resets all values to the values at the initial
    phase of the app. The "Stop" button stops any caclculation of the app,
    either of one set or the whole video creation prcess. The "Start" button
    starts a new calculation with the values in (1), (2), and (3).
5.  **The progress bar** indicates how much of the fractal has been calculated
    or how much of the video creation has been done. The **Status bar** below,
    shows progress in percentage, consumed process time to calculate the fractal
    set and other information.

The right window shows the "**New color palette**" window. With this window you
may define a new color palette. At the top of the window you can provide a name
for the new color palette. Pressing "Save" saves the new defined color palette
and adding it to the history list. Pressing "Close" closes the window.

For the theoretical background of this specific color palette calculation and
the meaning of these parameters you may follow these two links (the mastermind
of this is [Inigo Quilez](https://iquilezles.org/)):

- [Procedural Color Palette](https://iquilezles.org/articles/palettes/)
- [A simple formula to create beautiful color palettes](https://www.youtube.com/shorts/TH3OTy5fTog)

Additionally you are able to change the background color (default black). The
background color is the color of the origin fractal set!

**Attention**:
User defined color palettes are stored in the history list only. If you delete
the specific history item the user defined color palette will be lost!


## "History" window

<!-- ![History window](docs/app_screenshot_history.png) -->
<img src="docs/app_screenshot_history.png" alt="History window" style="width:100%; height:auto;">

The "History" window (the right window in the picture above) shows all past
calculations since starting the app the first time. The entries are sorted by
time. You can delete single entries (at the moment one by one only) or delete
the whole history. On the other side you may repeat a specific calculation. The
repeated one generates a new history entry!

**Attention**:

Deleting a history item deletes a possibly associated user defined color paette
defintion too! As long as this user defined color palette is associated with
another history item the color palete is safe.

## Create a zoom video

<!-- ![Zoom video parameters window](docs/app_screenshot_zoom.png) -->
<img src="docs/app_screenshot_zoom.png" alt="Zoom video parameters window" style="width:100%; height:auto;">

To build a zoom video you have to provide the parameters of two Mandelbrot
fractal sets: starting point and ending point. You may provide the data manually
or grab it from the current Mandelbrot fractal set (preferred method). Depending
which of the set is smaller or bigger the video will zoom-in or zoom-out.
Additionally you may select the resolution (width and height), frames per
second, and duration (seconds) of the video.

Of course you are able to select an existing color palette from a list.

At the end of the rendering process you may select the directory the video will
be stored. It replaces an existing file! During calculation and rendering the
"Main" window shows the progress (see item 5 of the first picture). The
"Drawing" window shows the current frame of calculation/rendering. You may abort
the whole video creation via the "Stop" button on the "Main" window!

**Attention**:

- Please take care, that the fractal set ratio (width x height) is the same as
  the ratio of the resolution (width x height)!

## Mouse and keyboard actions

### Julia set

You may switch from the Mandelbrot set to the Julia set by pressing [CTRL]+LMB
(Windows/Linux) or [Cmd(⌘)]+LMB (Apple) on any point of the calculated set.
Immediatly the calculation starts for the Julia set at this point. Of course
you may zoom-in in the Julia set, too. The fractal indicator (see item 5 above)
switches accordingly.

### Menu actions

- [CTRL]+[Q] (Windows/Linux) or [Cmd(⌘)]+[Q] (Apple): Quit the application
- [CTRL]+[S] (Windows/Linux) or [Cmd(⌘)]+[S] (Apple): Save the current image

- [CTRL]+[Shift]+[H] (Windows/Linux) or [Cmd(⌘)]+[Shift]+[T] (Apple):
  Show the "History" window
- [CTRL]+[Shift]+[N] (Windows/Linux) or [Cmd(⌘)]+[Shift]+[N] (Apple):
  Show "New color palette" window
- [CTRL]+[Shift]+[V] (Windows/Linux) or [Cmd(⌘)]+[Shift]+[N] (Apple):
  Show "Zoom video" window

- [CTRL]+[Shift]+[T] (Windows/Linux) or [Cmd(⌘)]+[Shift]+[T] (Apple):
  Toggle between light mode theme and dark mode theme of the OS.

### Stop running calculation

To stop a (long) running calculation you may press the key [ESC], RMB or the
"Stop" button on the "Main" window.

### Zoom-in

By pressing the LMB only you may draw an rectangle with the cursor (based on the
current ratio, see item 3) which defines the area you want to zoom in. As soon
as the calculation starts (immediately after release of the LMB), the new values
(see items 1, 2, and 3 of the "Main") will be adapted accordingly.

## Development recommendations

The app is written in Python3 (**version 3.14** and newer) and PySide6 (6.2 and
newer).

### Resources

To iclude all necessary resources you need the Qt resource system (`.qrc`)
provided by PySide6 from Qt: "pyside6-rcc" (included already in the "pyside6"
package):

`pyside6-rcc resources.qrc -o resources_rc.py`

This file contains all "styles" as text and the images as binary code.

### Build

To build a standalone app you need "pyinstaller". You have to install it first:

`pip install pyinstaller`

In the next step you have to change in the directory where "main.py" is and
execute the following line in a terminal:

macOS:\
`pyinstaller --noconsole --onefile --icon=ui/Mandelbrot.icns main.py`

Windows 11:\
`pyinstaller --noconsole --onefile --icon=ui/Mandelbrot.ico main.py`

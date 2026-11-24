#!/bin/zsh

# Compile Designer files (*.ui) to Python files

for f in *.ui(.N); do [[ $f -nt ${f:r}_ui.py ]] && pyside6-uic "$f" -o "${f:r}_ui.py"; done

# Build app icons mor macOS

if [[ -z "$1" ]]; then
  echo "Error: Please provide a filename (PNG file)!"
  echo "Call: $0 <filename>"
  exit 1
fi

PNG_FILE="$1"

cd ui

if [[ ! -f "$PNG_FILE" ]]; then
  echo "Error: File '$PNG_FILE' was not found!"
  cd ..
  exit 1
fi

rm -r icon.iconset
mkdir icon.iconset

sips -z 16 16     $PNG_FILE --out icon.iconset/icon_16x16.png
sips -z 32 32     $PNG_FILE --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     $PNG_FILE --out icon.iconset/icon_32x32.png
sips -z 64 64     $PNG_FILE --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   $PNG_FILE --out icon.iconset/icon_128x128.png
sips -z 256 256   $PNG_FILE --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   $PNG_FILE --out icon.iconset/icon_256x256.png
sips -z 512 512   $PNG_FILE --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   $PNG_FILE --out icon.iconset/icon_512x512.png
cp $PNG_FILE icon.iconset/icon_512x512@2x.png

rm icon.icns
iconutil -c icns icon.iconset
rm -r icon.iconset

cd ..

# Translate Markdown file to HtML file (README.md --> README.html)

python md2html.py

pyside6-rcc resources.qrc -o resources_rc.py
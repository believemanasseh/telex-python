#!/bin/sh

sudo rm -r build
pip install -r requirements.txt
meson setup --reconfigure build
meson compile --clean -C build
meson install -C build
cd ./build/src && ./telex
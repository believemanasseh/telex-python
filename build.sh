#!/bin/sh

sudo rm -r build
pip install -r requirements.txt
sudo meson setup --reconfigure build
sudo meson compile --clean -C build
sudo meson install -C build
cd /usr/local/bin && ./telex
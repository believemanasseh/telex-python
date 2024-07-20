#!/bin/sh

meson setup build
meson compile -C build
meson install -C build --destdir ~/telex_python
./usr/local/bin/telex
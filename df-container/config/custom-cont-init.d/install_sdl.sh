#!/bin/bash
echo "**** Verifying graphical dependencies for Dwarf Fortress ****"
if ! dpkg -s libsdl2-2.0-0 >/dev/null 2>&1; then
    echo "**** SDL2 not found. Installing... ****"
    apt-get update -qq
    apt-get install -y --no-install-recommends \
        wget tar bzip2 \
        libsdl2-2.0-0 \
        libsdl2-image-2.0-0 \
        libsdl2-ttf-2.0-0
    echo "**** SDL2 installed successfully ****"
else
    echo "**** SDL2 already present. Skipping installation ****"
fi

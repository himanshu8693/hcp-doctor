#!/bin/bash
# Build standalone binary for hcp-doctor using PyInstaller

set -e

if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
rm -rf dist build *.spec

# Build the binary
pyinstaller --onefile -n hcp-doctor -p hashicorp_doctor hashicorp_doctor/cli.py

echo "\nBinary built at dist/hcp-doctor"

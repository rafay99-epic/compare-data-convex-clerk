#!/bin/bash
# Build script for py2app to create macOS .app bundle

echo "Building Data Explorer application with py2app..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Clean previous builds
rm -rf build dist

# Install py2app if not already installed
pip install py2app > /dev/null 2>&1

# Run py2app
python setup.py py2app

if [ $? -eq 0 ]; then
    echo ""
    echo "Build successful! Application bundle created in dist/Data Explorer.app"
    echo "You can now move it to Applications folder or distribute it."
else
    echo ""
    echo "Build failed. Please check the error messages above."
    exit 1
fi

#!/bin/bash
# Build script for PyInstaller to create macOS .app bundle

echo "Building Data Explorer application with PyInstaller..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Clean previous builds
rm -rf build dist *.spec

# Create PyInstaller spec file
cat > DataExplorer.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'matplotlib',
        'pandas',
        'plotly',
        'numpy',
        'app',
        'app.modules',
        'app.tabs',
        'app.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DataExplorer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DataExplorer',
)

app = BUNDLE(
    coll,
    name='Data Explorer.app',
    icon=None,  # Add icon path if available
    bundle_identifier='com.dataexplorer.app',
)
EOF

# Run PyInstaller
pyinstaller DataExplorer.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "Build successful! Application bundle created in dist/Data Explorer.app"
    echo "You can now move it to Applications folder or distribute it."
else
    echo ""
    echo "Build failed. Please check the error messages above."
    exit 1
fi

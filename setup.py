"""Setup file for py2app to create macOS application bundle."""

from setuptools import setup

APP = ['app/main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tkinter', 'matplotlib', 'pandas', 'plotly', 'numpy'],
    'includes': ['app'],
    'iconfile': 'build/app_icon.icns',  # Add icon file if available
    'plist': {
        'CFBundleName': 'Data Explorer',
        'CFBundleDisplayName': 'Data Explorer',
        'CFBundleGetInfoString': "Data Explorer - Migration Tool & Data Visualization",
        'CFBundleIdentifier': "com.dataexplorer.app",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': "Copyright © 2024",
    }
}

setup(
    name='Data Explorer',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

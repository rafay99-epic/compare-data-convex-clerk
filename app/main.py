#!/usr/bin/env python3
"""Main entry point for Data Explorer application."""

import tkinter as tk
import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir.parent))

from app.main_window import MainWindow


def main():
    """Main entry point."""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()

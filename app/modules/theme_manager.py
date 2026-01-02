"""Theme Manager for handling theme switching between light and dark modes."""

import json
from pathlib import Path
from typing import Callable, Optional
from app.modules.theme import Theme


class ThemeManager:
    """Manages theme switching and persistence."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file) if config_file else Path.home() / ".data_explorer_theme.json"
        self.current_mode = "light"  # 'light' or 'dark'
        self.callbacks: list[Callable[[str], None]] = []  # Callbacks for theme changes
        
        # Load saved preference
        self.load_theme_preference()
    
    def load_theme_preference(self):
        """Load theme preference from config file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.current_mode = config.get('theme', 'light')
        except Exception:
            pass  # Use default if loading fails
    
    def save_theme_preference(self):
        """Save theme preference to config file."""
        try:
            config = {'theme': self.current_mode}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception:
            pass  # Continue if saving fails
    
    def get_current_theme(self) -> dict:
        """Get current theme colors."""
        if self.current_mode == "dark":
            return Theme.get_dark_theme()
        else:
            return Theme.get_light_theme()
    
    def toggle_theme(self):
        """Toggle between light and dark mode."""
        self.current_mode = "dark" if self.current_mode == "light" else "light"
        self.save_theme_preference()
        self.notify_callbacks()
    
    def set_theme(self, mode: str):
        """Set theme to specific mode."""
        if mode in ["light", "dark"]:
            self.current_mode = mode
            self.save_theme_preference()
            self.notify_callbacks()
    
    def register_callback(self, callback: Callable[[str], None]):
        """Register a callback to be called when theme changes."""
        self.callbacks.append(callback)
    
    def notify_callbacks(self):
        """Notify all registered callbacks of theme change."""
        for callback in self.callbacks:
            try:
                callback(self.current_mode)
            except Exception:
                pass  # Continue if callback fails

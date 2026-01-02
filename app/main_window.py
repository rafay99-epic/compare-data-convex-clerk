"""Main window for the Data Explorer application."""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from app.tabs.migration_tool.migration_tab import MigrationToolTab
from app.tabs.data_explorer.explorer_tab import DataExplorerTab
from app.modules.ui_components import StatusBar
from app.modules.theme import Theme
from app.modules.theme_manager import ThemeManager


class MainWindow:
    """Main application window with tabbed interface."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Data Explorer - Migration Tool & Data Visualization")
        self.root.geometry("1800x1100")
        self.root.minsize(1200, 800)
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.current_theme_colors = self.theme_manager.get_current_theme()
        
        # Configure theme
        self.style = ttk.Style()
        Theme.configure_theme(self.style, self.current_theme_colors)
        
        # Set window background
        self.root.configure(bg=self.current_theme_colors['BG_SECONDARY'])
        
        # Create main container
        self.create_widgets()
        
        # Register theme change callback
        self.theme_manager.register_callback(self.on_theme_changed)
        
        # Center window on screen
        self.center_window()
    
    def on_theme_changed(self, mode: str):
        """Handle theme change."""
        self.current_theme_colors = self.theme_manager.get_current_theme()
        
        # Reconfigure style
        Theme.configure_theme(self.style, self.current_theme_colors)
        
        # Update root background
        self.root.configure(bg=self.current_theme_colors['BG_SECONDARY'])
        
        # Update header
        self.title_label.config(foreground=self.current_theme_colors['PRIMARY'])
        
        # Update status bar
        if hasattr(self, 'status_bar'):
            self.status_bar.update_theme(self.current_theme_colors)
        
        # Notify tabs to update theme
        if hasattr(self, 'migration_tab'):
            self.migration_tab.update_theme(self.current_theme_colors)
        if hasattr(self, 'explorer_tab'):
            self.explorer_tab.update_theme(self.current_theme_colors)
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create main UI widgets."""
        # Main container with padding
        main_container = ttk.Frame(self.root, padding=15)
        main_container.pack(fill="both", expand=True)
        
        # Header section
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Title
        self.title_label = ttk.Label(
            header_frame,
            text="Data Explorer",
            font=('SF Pro Display', 28, 'bold'),
            foreground=self.current_theme_colors['PRIMARY']
        )
        self.title_label.pack(side='left')
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Migration Tool & Data Visualization",
            style='Subheading.TLabel'
        )
        subtitle_label.pack(side='left', padx=(15, 0), pady=(8, 0))
        
        # Theme toggle button
        theme_text = "🌙 Dark" if self.theme_manager.current_mode == "light" else "☀️ Light"
        self.theme_button = ttk.Button(
            header_frame,
            text=theme_text,
            command=self.toggle_theme,
            style='Secondary.TButton'
        )
        self.theme_button.pack(side='right')
        
        # Create notebook (tabbed interface) with custom styling
        notebook_frame = ttk.Frame(main_container)
        notebook_frame.pack(fill="both", expand=True)
        
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Create tabs (pass theme manager)
        self.migration_tab = MigrationToolTab(self.notebook, self.theme_manager)
        self.notebook.add(self.migration_tab.frame, text="  Migration Tool  ")
        
        self.explorer_tab = DataExplorerTab(self.notebook, self.theme_manager)
        self.notebook.add(self.explorer_tab.frame, text="  Data Explorer  ")
        
        # Status bar at bottom
        status_container = ttk.Frame(main_container)
        status_container.pack(fill="x", pady=(15, 0))
        
        self.status_bar = StatusBar(status_container, self.current_theme_colors)
        self.status_bar.pack()
        self.status_bar.set_status("Ready - Welcome to Data Explorer", self.current_theme_colors['INFO'])
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def toggle_theme(self):
        """Toggle between light and dark mode."""
        self.theme_manager.toggle_theme()
        theme_text = "🌙 Dark" if self.theme_manager.current_mode == "light" else "☀️ Light"
        self.theme_button.config(text=theme_text)
    
    def on_tab_changed(self, event=None):
        """Handle tab change event."""
        selected = self.notebook.index(self.notebook.select())
        if selected == 0:
            self.status_bar.set_status("Migration Tool - Load user data files to analyze migration patterns", self.current_theme_colors['INFO'])
        elif selected == 1:
            self.status_bar.set_status("Data Explorer - Upload CSV/JSON files to explore and visualize your data", self.current_theme_colors['INFO'])

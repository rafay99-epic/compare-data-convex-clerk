"""Reusable UI components for the application."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable


class Card(ttk.Frame):
    """A card component with shadow effect simulation."""
    
    def __init__(self, parent, title: Optional[str] = None, padding=15, theme_colors=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        if theme_colors is None:
            from app.modules.theme import Theme
            theme_colors = Theme.get_light_theme()
        
        # Configure card style
        style = ttk.Style()
        style.configure('Card.TFrame', 
                       background=theme_colors['BG_PRIMARY'],
                       relief='flat',
                       borderwidth=1)
        
        self.configure(style='Card.TFrame')
        
        if title:
            title_label = ttk.Label(self, text=title, style='Heading.TLabel')
            title_label.pack(anchor='w', pady=(0, padding//2))
        
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill='both', expand=True)


class StatCard(ttk.Frame):
    """A card for displaying statistics with icon and value."""
    
    def __init__(self, parent, title: str, value: str, color: str = None, theme_colors=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        if theme_colors is None:
            from app.modules.theme import Theme
            theme_colors = Theme.get_light_theme()
        
        if color is None:
            color = theme_colors['PRIMARY']
        
        style = ttk.Style()
        style.configure('StatCard.TFrame',
                       background=theme_colors['BG_PRIMARY'],
                       relief='flat')
        
        self.configure(style='StatCard.TFrame', padding=20)
        
        # Value
        value_label = ttk.Label(self, text=value, font=('SF Pro Display', 28, 'bold'), foreground=color)
        value_label.pack(anchor='w')
        
        # Title
        title_label = ttk.Label(self, text=title, style='Subheading.TLabel')
        title_label.pack(anchor='w', pady=(5, 0))


class LoadingIndicator:
    """A simple loading indicator widget."""
    
    def __init__(self, parent, text: str = "Loading..."):
        self.frame = ttk.Frame(parent)
        self.label = ttk.Label(self.frame, text=text, style='Subheading.TLabel')
        self.progress = ttk.Progressbar(
            self.frame,
            mode='indeterminate',
            length=200
        )
        self.label.pack(pady=5)
        self.progress.pack(pady=5)
    
    def pack(self, **kwargs):
        """Pack the loading indicator."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the loading indicator."""
        self.frame.grid(**kwargs)
    
    def start(self):
        """Start the loading animation."""
        self.progress.start(10)
    
    def stop(self):
        """Stop the loading animation."""
        self.progress.stop()
    
    def destroy(self):
        """Destroy the loading indicator."""
        self.frame.destroy()


class StatusBar:
    """A status bar widget for displaying status messages."""
    
    def __init__(self, parent, theme_colors=None):
        if theme_colors is None:
            from app.modules.theme import Theme
            theme_colors = Theme.get_light_theme()
        
        self.theme_colors = theme_colors
        self.frame = ttk.Frame(parent)
        
        # Create inner frame for padding
        self.inner_frame = tk.Frame(
            self.frame,
            background=theme_colors['BG_TERTIARY'],
            padx=10,
            pady=8
        )
        self.inner_frame.pack(fill=tk.X)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            self.inner_frame,
            textvariable=self.status_var,
            relief=tk.FLAT,
            anchor=tk.W,
            background=theme_colors['BG_TERTIARY'],
            foreground=theme_colors['TEXT_SECONDARY'],
            font=('SF Pro Display', 9)
        )
        self.status_label.pack(fill=tk.X)
    
    def pack(self, **kwargs):
        """Pack the status bar."""
        self.frame.pack(**kwargs, fill=tk.X, side='bottom')
    
    def set_status(self, message: str, color: str = None):
        """Set the status message."""
        if color is None:
            color = self.theme_colors['TEXT_SECONDARY']
        self.status_var.set(message)
        self.status_label.config(foreground=color)
    
    def update_theme(self, theme_colors):
        """Update theme colors."""
        self.theme_colors = theme_colors
        if hasattr(self, 'inner_frame'):
            self.inner_frame.config(background=theme_colors['BG_TERTIARY'])
        if hasattr(self, 'status_label'):
            self.status_label.config(
                background=theme_colors['BG_TERTIARY'],
                foreground=theme_colors['TEXT_SECONDARY']
            )
    
    def clear(self):
        """Clear the status message."""
        self.status_var.set("Ready")
        self.status_label.config(foreground=self.theme_colors['TEXT_SECONDARY'])


class ToolTip:
    """Create a tooltip for a given widget."""
    
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind('<Enter>', self.on_enter)
        self.widget.bind('<Leave>', self.on_leave)
    
    def on_enter(self, event=None):
        """Show tooltip on mouse enter."""
        self.show_tooltip()
    
    def on_leave(self, event=None):
        """Hide tooltip on mouse leave."""
        self.hide_tooltip()
    
    def show_tooltip(self):
        """Display the tooltip."""
        if self.tipwindow:
            return
        
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        
        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#2d3748",
            foreground="white",
            relief=tk.SOLID,
            borderwidth=1,
            font=('SF Pro Display', 9),
            wraplength=250,
            padx=8,
            pady=4
        )
        label.pack(ipadx=1)
    
    def hide_tooltip(self):
        """Hide the tooltip."""
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class SectionHeader(ttk.Frame):
    """A styled section header."""
    
    def __init__(self, parent, title: str, subtitle: Optional[str] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        title_label = ttk.Label(self, text=title, style='Heading.TLabel')
        title_label.pack(side='left')
        
        if subtitle:
            subtitle_label = ttk.Label(self, text=subtitle, style='Subheading.TLabel')
            subtitle_label.pack(side='left', padx=(10, 0))

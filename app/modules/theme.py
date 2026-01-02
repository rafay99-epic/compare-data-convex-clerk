"""Theme and styling configuration for the application."""

import tkinter as tk
from tkinter import ttk


class Theme:
    """Application theme and styling."""
    
    # Light mode colors
    LIGHT_PRIMARY = "#2563eb"
    LIGHT_PRIMARY_DARK = "#1e40af"
    LIGHT_PRIMARY_LIGHT = "#3b82f6"
    LIGHT_SECONDARY = "#10b981"
    LIGHT_SECONDARY_DARK = "#059669"
    LIGHT_ACCENT = "#f59e0b"
    LIGHT_SUCCESS = "#10b981"
    LIGHT_WARNING = "#f59e0b"
    LIGHT_ERROR = "#ef4444"
    LIGHT_INFO = "#3b82f6"
    
    LIGHT_BG_PRIMARY = "#ffffff"
    LIGHT_BG_SECONDARY = "#f8fafc"
    LIGHT_BG_TERTIARY = "#f1f5f9"
    LIGHT_BORDER = "#e2e8f0"
    LIGHT_TEXT_PRIMARY = "#1e293b"
    LIGHT_TEXT_SECONDARY = "#64748b"
    LIGHT_TEXT_MUTED = "#94a3b8"
    
    # Dark mode colors
    DARK_PRIMARY = "#3b82f6"
    DARK_PRIMARY_DARK = "#2563eb"
    DARK_PRIMARY_LIGHT = "#60a5fa"
    DARK_SECONDARY = "#10b981"
    DARK_SECONDARY_DARK = "#059669"
    DARK_ACCENT = "#f59e0b"
    DARK_SUCCESS = "#10b981"
    DARK_WARNING = "#f59e0b"
    DARK_ERROR = "#ef4444"
    DARK_INFO = "#60a5fa"
    
    DARK_BG_PRIMARY = "#0f172a"
    DARK_BG_SECONDARY = "#1e293b"
    DARK_BG_TERTIARY = "#334155"
    DARK_BORDER = "#475569"
    DARK_TEXT_PRIMARY = "#f1f5f9"
    DARK_TEXT_SECONDARY = "#cbd5e1"
    DARK_TEXT_MUTED = "#94a3b8"
    
    @staticmethod
    def get_light_theme() -> dict:
        """Get light theme color dictionary."""
        return {
            'PRIMARY': Theme.LIGHT_PRIMARY,
            'PRIMARY_DARK': Theme.LIGHT_PRIMARY_DARK,
            'PRIMARY_LIGHT': Theme.LIGHT_PRIMARY_LIGHT,
            'SECONDARY': Theme.LIGHT_SECONDARY,
            'SECONDARY_DARK': Theme.LIGHT_SECONDARY_DARK,
            'ACCENT': Theme.LIGHT_ACCENT,
            'SUCCESS': Theme.LIGHT_SUCCESS,
            'WARNING': Theme.LIGHT_WARNING,
            'ERROR': Theme.LIGHT_ERROR,
            'INFO': Theme.LIGHT_INFO,
            'BG_PRIMARY': Theme.LIGHT_BG_PRIMARY,
            'BG_SECONDARY': Theme.LIGHT_BG_SECONDARY,
            'BG_TERTIARY': Theme.LIGHT_BG_TERTIARY,
            'BORDER': Theme.LIGHT_BORDER,
            'TEXT_PRIMARY': Theme.LIGHT_TEXT_PRIMARY,
            'TEXT_SECONDARY': Theme.LIGHT_TEXT_SECONDARY,
            'TEXT_MUTED': Theme.LIGHT_TEXT_MUTED,
        }
    
    @staticmethod
    def get_dark_theme() -> dict:
        """Get dark theme color dictionary."""
        return {
            'PRIMARY': Theme.DARK_PRIMARY,
            'PRIMARY_DARK': Theme.DARK_PRIMARY_DARK,
            'PRIMARY_LIGHT': Theme.DARK_PRIMARY_LIGHT,
            'SECONDARY': Theme.DARK_SECONDARY,
            'SECONDARY_DARK': Theme.DARK_SECONDARY_DARK,
            'ACCENT': Theme.DARK_ACCENT,
            'SUCCESS': Theme.DARK_SUCCESS,
            'WARNING': Theme.DARK_WARNING,
            'ERROR': Theme.DARK_ERROR,
            'INFO': Theme.DARK_INFO,
            'BG_PRIMARY': Theme.DARK_BG_PRIMARY,
            'BG_SECONDARY': Theme.DARK_BG_SECONDARY,
            'BG_TERTIARY': Theme.DARK_BG_TERTIARY,
            'BORDER': Theme.DARK_BORDER,
            'TEXT_PRIMARY': Theme.DARK_TEXT_PRIMARY,
            'TEXT_SECONDARY': Theme.DARK_TEXT_SECONDARY,
            'TEXT_MUTED': Theme.DARK_TEXT_MUTED,
        }
    
    @staticmethod
    def configure_theme(style: ttk.Style, theme_colors: dict):
        """Configure ttk style with given theme colors."""
        # Use a modern theme as base
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=theme_colors['BG_SECONDARY'])
        style.configure('TLabelFrame', background=theme_colors['BG_SECONDARY'], borderwidth=2, relief='flat')
        style.configure('TLabelFrame.Label', background=theme_colors['BG_SECONDARY'], foreground=theme_colors['TEXT_PRIMARY'], font=('SF Pro Display', 11, 'bold'))
        
        # Buttons
        style.configure('TButton', 
                       background=theme_colors['PRIMARY'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8),
                       font=('SF Pro Display', 10))
        style.map('TButton',
                 background=[('active', theme_colors['PRIMARY_DARK']),
                           ('pressed', theme_colors['PRIMARY_DARK'])])
        
        # Primary button variant
        style.configure('Primary.TButton',
                       background=theme_colors['PRIMARY'],
                       foreground='white',
                       font=('SF Pro Display', 10, 'bold'))
        style.map('Primary.TButton',
                 background=[('active', theme_colors['PRIMARY_DARK'])])
        
        # Secondary button
        style.configure('Secondary.TButton',
                       background=theme_colors['BG_TERTIARY'],
                       foreground=theme_colors['TEXT_PRIMARY'],
                       font=('SF Pro Display', 10))
        style.map('Secondary.TButton',
                 background=[('active', theme_colors['BORDER'])])
        
        # Success button
        style.configure('Success.TButton',
                       background=theme_colors['SUCCESS'],
                       foreground='white')
        style.map('Success.TButton',
                 background=[('active', theme_colors['SECONDARY_DARK'])])
        
        # Entry
        style.configure('TEntry',
                       fieldbackground=theme_colors['BG_PRIMARY'],
                       borderwidth=2,
                       relief='solid',
                       padding=8,
                       font=('SF Pro Display', 10),
                       foreground=theme_colors['TEXT_PRIMARY'])
        style.map('TEntry',
                 bordercolor=[('focus', theme_colors['PRIMARY'])])
        
        # Notebook
        style.configure('TNotebook', background=theme_colors['BG_SECONDARY'], borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=theme_colors['BG_TERTIARY'],
                       foreground=theme_colors['TEXT_SECONDARY'],
                       padding=(20, 12),
                       font=('SF Pro Display', 11))
        style.map('TNotebook.Tab',
                 background=[('selected', theme_colors['BG_PRIMARY'])],
                 foreground=[('selected', theme_colors['PRIMARY'])],
                 expand=[('selected', [1, 1, 1, 0])])
        
        # Label
        style.configure('TLabel', background=theme_colors['BG_SECONDARY'], foreground=theme_colors['TEXT_PRIMARY'], font=('SF Pro Display', 10))
        style.configure('Heading.TLabel', font=('SF Pro Display', 12, 'bold'), foreground=theme_colors['TEXT_PRIMARY'])
        style.configure('Subheading.TLabel', font=('SF Pro Display', 10), foreground=theme_colors['TEXT_SECONDARY'])
        
        # Treeview
        style.configure('Treeview',
                       background=theme_colors['BG_PRIMARY'],
                       foreground=theme_colors['TEXT_PRIMARY'],
                       fieldbackground=theme_colors['BG_PRIMARY'],
                       borderwidth=1,
                       font=('SF Pro Display', 10))
        style.configure('Treeview.Heading',
                       background=theme_colors['BG_TERTIARY'],
                       foreground=theme_colors['TEXT_PRIMARY'],
                       font=('SF Pro Display', 10, 'bold'),
                       borderwidth=1,
                       relief='flat')
        style.map('Treeview',
                 background=[('selected', theme_colors['PRIMARY_LIGHT'])],
                 foreground=[('selected', 'white')])
        
        # Scrollbar
        style.configure('TScrollbar',
                       background=theme_colors['BORDER'],
                       troughcolor=theme_colors['BG_TERTIARY'],
                       borderwidth=0,
                       arrowcolor=theme_colors['TEXT_SECONDARY'],
                       darkcolor=theme_colors['BORDER'],
                       lightcolor=theme_colors['BORDER'])
        style.map('TScrollbar',
                 background=[('active', theme_colors['TEXT_MUTED'])])
        
        # Radiobutton
        style.configure('TRadiobutton',
                       background=theme_colors['BG_SECONDARY'],
                       foreground=theme_colors['TEXT_PRIMARY'],
                       font=('SF Pro Display', 10))
        
        # Combobox
        style.configure('TCombobox',
                       fieldbackground=theme_colors['BG_PRIMARY'],
                       borderwidth=2,
                       padding=8,
                       font=('SF Pro Display', 10),
                       foreground=theme_colors['TEXT_PRIMARY'])
        
        return style

"""Data Explorer Tab - General purpose CSV/JSON data visualization."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import pandas as pd

from app.utils.scrollable_frame import ScrollableFrame
from app.modules.file_loader import FileLoader
from app.modules.data_processor import DataProcessor
from app.modules.chart_engine import ChartEngine
from app.modules.ui_components import Card, StatCard
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import plotly.graph_objects as go
from plotly.offline import plot
import webbrowser
import tempfile
import os


class DataExplorerTab:
    """Tab for general purpose data exploration."""
    
    def __init__(self, parent, theme_manager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.theme_colors = theme_manager.get_current_theme()
        self.frame = ttk.Frame(parent, padding=20)
        
        # Data storage
        self.data: Optional[Union[pd.DataFrame, List[Dict], Dict]] = None
        self.data_info: Optional[Dict[str, Any]] = None
        self.file_path: str = ""
        self.file_type: Optional[str] = None
        
        # Build UI
        self.create_widgets()
    
    def update_theme(self, theme_colors: dict):
        """Update theme colors for all components."""
        self.theme_colors = theme_colors
        
        # Update text widget colors
        if hasattr(self, 'overview_text'):
            self.overview_text.config(bg=theme_colors['BG_PRIMARY'], fg=theme_colors['TEXT_PRIMARY'])
        
        # Update status label
        if hasattr(self, 'status_label'):
            current_text = self.status_label.cget('text')
            if '✓' in current_text:
                self.status_label.config(foreground=theme_colors['SUCCESS'])
            elif '✗' in current_text:
                self.status_label.config(foreground=theme_colors['ERROR'])
            else:
                self.status_label.config(foreground=theme_colors['TEXT_SECONDARY'])
    
    def create_widgets(self):
        """Create all UI widgets for the data explorer tab."""
        # File Upload Section - Modern card design
        upload_card = Card(self.frame, title="Load Data File", padding=20, theme_colors=self.theme_colors)
        upload_card.pack(fill="x", pady=(0, 20))
        
        # File input row
        file_row = ttk.Frame(upload_card.content_frame)
        file_row.pack(fill="x", pady=(0, 15))
        
        ttk.Label(file_row, text="Data File", width=15, anchor='w').pack(side='left', padx=(0, 10))
        self.file_entry = ttk.Entry(file_row, width=60)
        self.file_entry.pack(side='left', fill="x", expand=True, padx=(0, 10))
        ttk.Button(file_row, text="Browse", command=self.browse_file, style='Secondary.TButton').pack(side='left')
        
        # Load button and status
        button_row = ttk.Frame(upload_card.content_frame)
        button_row.pack(fill="x")
        ttk.Button(button_row, text="Load Data", command=self.load_data, style='Primary.TButton').pack(side='left')
        self.status_label = ttk.Label(button_row, text="No data loaded", style='Subheading.TLabel')
        self.status_label.pack(side='left', padx=(20, 0))
        
        # Main content area with notebook
        self.content_notebook = ttk.Notebook(self.frame)
        self.content_notebook.pack(fill="both", expand=True)
        
        # Overview tab
        overview_frame = ttk.Frame(self.content_notebook, padding=15)
        self.content_notebook.add(overview_frame, text="  Overview  ")
        self.create_overview_panel(overview_frame)
        
        # Charts tab
        charts_frame = ttk.Frame(self.content_notebook, padding=15)
        self.content_notebook.add(charts_frame, text="  Charts  ")
        self.create_charts_panel(charts_frame)
        
        # Data table tab
        table_frame = ttk.Frame(self.content_notebook, padding=15)
        self.content_notebook.add(table_frame, text="  Data Table  ")
        self.create_table_panel(table_frame)
    
    def create_overview_panel(self, parent):
        """Create overview panel with data statistics."""
        scroll_frame = ScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True)
        
        # Quick stats cards (will be populated when data loads)
        self.quick_stats_frame = ttk.Frame(scroll_frame.scrollable_frame)
        self.quick_stats_frame.pack(fill="x", pady=(0, 20))
        
        # Detailed info card
        info_card = Card(scroll_frame.scrollable_frame, title="Data Information", padding=15, theme_colors=self.theme_colors)
        info_card.pack(fill="x")
        
        text_frame = ttk.Frame(info_card.content_frame)
        text_frame.pack(fill="both", expand=True)
        
        self.overview_text = tk.Text(
            text_frame,
            wrap="word",
            width=80,
            height=30,
            font=("SF Mono", 11),
            bg=self.theme_colors['BG_PRIMARY'],
            fg=self.theme_colors['TEXT_PRIMARY'],
            relief='flat',
            padx=15,
            pady=15,
            borderwidth=0
        )
        overview_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.overview_text.yview)
        self.overview_text.configure(yscrollcommand=overview_scrollbar.set)
        
        self.overview_text.pack(side="left", fill="both", expand=True)
        overview_scrollbar.pack(side="right", fill="y")
    
    def create_charts_panel(self, parent):
        """Create charts panel with chart generation options."""
        # Controls card
        controls_card = Card(parent, title="Chart Configuration", padding=20, theme_colors=self.theme_colors)
        controls_card.pack(fill="x", pady=(0, 20))
        
        controls_grid = ttk.Frame(controls_card.content_frame)
        controls_grid.pack(fill="x")
        
        # Chart type selection
        type_row = ttk.Frame(controls_grid)
        type_row.pack(fill="x", pady=(0, 15))
        ttk.Label(type_row, text="Chart Type", width=15, anchor='w').pack(side='left', padx=(0, 10))
        self.chart_type_var = tk.StringVar(value="line")
        type_btn_frame = ttk.Frame(type_row)
        type_btn_frame.pack(side='left', fill="x", expand=True)
        chart_types = [
            ("Line", "line"),
            ("Bar", "bar"),
            ("Pie", "pie"),
            ("Histogram", "histogram"),
            ("Scatter", "scatter"),
            ("Heatmap", "heatmap")
        ]
        for text, value in chart_types:
            ttk.Radiobutton(type_btn_frame, text=text, variable=self.chart_type_var, value=value).pack(side='left', padx=(0, 15))
        
        # Library selection
        lib_row = ttk.Frame(controls_grid)
        lib_row.pack(fill="x", pady=(0, 15))
        ttk.Label(lib_row, text="Library", width=15, anchor='w').pack(side='left', padx=(0, 10))
        self.library_var = tk.StringVar(value="matplotlib")
        lib_btn_frame = ttk.Frame(lib_row)
        lib_btn_frame.pack(side='left', fill="x", expand=True)
        ttk.Radiobutton(lib_btn_frame, text="Matplotlib (Embedded)", variable=self.library_var, value="matplotlib").pack(side='left', padx=(0, 15))
        ttk.Radiobutton(lib_btn_frame, text="Plotly (Interactive)", variable=self.library_var, value="plotly").pack(side='left')
        
        # Column selection
        col_row = ttk.Frame(controls_grid)
        col_row.pack(fill="x")
        ttk.Label(col_row, text="X Column", width=15, anchor='w').pack(side='left', padx=(0, 10))
        self.x_column_var = tk.StringVar()
        self.x_column_combo = ttk.Combobox(col_row, textvariable=self.x_column_var, width=25, state="readonly")
        self.x_column_combo.pack(side='left', padx=(0, 20))
        
        ttk.Label(col_row, text="Y Column", width=12, anchor='w').pack(side='left', padx=(0, 10))
        self.y_column_var = tk.StringVar()
        self.y_column_combo = ttk.Combobox(col_row, textvariable=self.y_column_var, width=25, state="readonly")
        self.y_column_combo.pack(side='left')
        
        # Generate button
        button_row = ttk.Frame(controls_card.content_frame)
        button_row.pack(fill="x", pady=(20, 0))
        ttk.Button(button_row, text="Generate Chart", command=self.generate_chart, style='Primary.TButton').pack(side='left')
        
        # Charts display area (scrollable)
        charts_scroll = ScrollableFrame(parent)
        charts_scroll.pack(fill="both", expand=True)
        self.charts_container = charts_scroll.scrollable_frame
    
    def create_table_panel(self, parent):
        """Create data table viewer panel."""
        table_card = Card(parent, title="Data Table", padding=15, theme_colors=self.theme_colors)
        table_card.pack(fill="both", expand=True)
        
        # Search frame
        search_frame = ttk.Frame(table_card.content_frame)
        search_frame.pack(fill="x", pady=(0, 15))
        ttk.Label(search_frame, text="Search", width=10).pack(side='left', padx=(0, 10))
        self.table_search_entry = ttk.Entry(search_frame)
        self.table_search_entry.pack(side='left', fill="x", expand=True)
        self.table_search_entry.bind("<KeyRelease>", self.on_table_search)
        
        # Table frame with scrollbars
        table_frame = ttk.Frame(table_card.content_frame)
        table_frame.pack(fill="both", expand=True)
        
        self.data_tree = ttk.Treeview(table_frame, show="headings", height=35)
        
        # Scrollbars
        v_scrollbar_table = ttk.Scrollbar(table_frame, orient="vertical", command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=v_scrollbar_table.set)
        h_scrollbar_table = ttk.Scrollbar(table_frame, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(xscrollcommand=h_scrollbar_table.set)
        
        # Grid layout
        self.data_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar_table.grid(row=0, column=1, sticky="ns")
        h_scrollbar_table.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
    
    def browse_file(self):
        """Browse for data file."""
        filename = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("JSONL files", "*.jsonl"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            self.file_path = filename
    
    def load_data(self):
        """Load data from selected file."""
        try:
            if not self.file_path or not os.path.exists(self.file_path):
                messagebox.showerror("Error", "Please select a valid file")
                return
            
            self.file_type = FileLoader.detect_file_type(self.file_path)
            raw_data = FileLoader.load_file(self.file_path)
            
            if isinstance(raw_data, (dict, list)):
                self.data = DataProcessor.convert_to_dataframe(raw_data)
            else:
                self.data = raw_data
            
            self.data_info = DataProcessor.get_dataframe_info(self.data)
            
            self.update_overview()
            self.update_chart_controls()
            self.update_table()
            self.status_label.config(
                text=f"✓ Loaded: {len(self.data):,} rows, {len(self.data.columns)} columns",
                foreground=self.theme_colors['SUCCESS']
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.status_label.config(text="✗ Error loading data", foreground=self.theme_colors['ERROR'])
    
    def update_overview(self):
        """Update overview panel with data information."""
        # Clear quick stats
        for widget in self.quick_stats_frame.winfo_children():
            widget.destroy()
        
        # Create quick stat cards
        if self.data_info:
            info = self.data_info
            stats_row = ttk.Frame(self.quick_stats_frame)
            stats_row.pack(fill="x", pady=(0, 20))
            
            StatCard(stats_row, "Rows", f"{info['shape'][0]:,}", self.theme_colors['PRIMARY'], theme_colors=self.theme_colors).pack(side='left', padx=(0, 10), fill='x', expand=True)
            StatCard(stats_row, "Columns", f"{info['shape'][1]:,}", self.theme_colors['INFO'], theme_colors=self.theme_colors).pack(side='left', padx=(0, 10), fill='x', expand=True)
            StatCard(stats_row, "Numeric", f"{len(info['numeric_columns']):,}", self.theme_colors['SUCCESS'], theme_colors=self.theme_colors).pack(side='left', padx=(0, 10), fill='x', expand=True)
            StatCard(stats_row, "Categorical", f"{len(info['categorical_columns']):,}", self.theme_colors['WARNING'], theme_colors=self.theme_colors).pack(side='left', fill='x', expand=True)
        
        # Update text
        self.overview_text.delete(1.0, tk.END)
        if not self.data_info:
            return
        
        info = self.data_info
        text = f"""DATA OVERVIEW
{'='*80}

SHAPE: {info['shape'][0]:,} rows × {info['shape'][1]:,} columns

COLUMNS ({len(info['columns'])}):
{', '.join(info['columns'])}

DATA TYPES:
"""
        for col, dtype in info['dtypes'].items():
            text += f"  {col}: {dtype}\n"
        
        text += f"\nNULL VALUES:\n"
        for col, count in info['null_counts'].items():
            pct = info['null_percentages'][col]
            if count > 0:
                text += f"  {col}: {count:,} ({pct:.2f}%)\n"
        
        if info.get('numeric_stats'):
            text += f"\nNUMERIC STATISTICS:\n"
            for col in info['numeric_columns']:
                stats = info['numeric_stats'][col]
                text += f"\n  {col}:\n"
                text += f"    Mean: {stats.get('mean', 'N/A'):.2f}\n"
                text += f"    Std: {stats.get('std', 'N/A'):.2f}\n"
                text += f"    Min: {stats.get('min', 'N/A'):.2f}\n"
                text += f"    Max: {stats.get('max', 'N/A'):.2f}\n"
        
        if info.get('categorical_counts'):
            text += f"\nCATEGORICAL VALUE COUNTS (Top 10):\n"
            for col, counts in info['categorical_counts'].items():
                text += f"\n  {col}:\n"
                for value, count in list(counts.items())[:10]:
                    text += f"    {value}: {count:,}\n"
        
        self.overview_text.insert(1.0, text)
    
    def update_chart_controls(self):
        """Update chart control options based on loaded data."""
        if not isinstance(self.data, pd.DataFrame):
            return
        
        columns = self.data.columns.tolist()
        self.x_column_combo['values'] = columns
        self.y_column_combo['values'] = columns
        
        if columns:
            if self.x_column_var.get() not in columns:
                self.x_column_var.set(columns[0])
            numeric_cols = DataProcessor.detect_numeric_columns(self.data)
            if numeric_cols and self.y_column_var.get() not in columns:
                self.y_column_var.set(numeric_cols[0])
    
    def generate_chart(self):
        """Generate chart based on selected options."""
        if not isinstance(self.data, pd.DataFrame):
            messagebox.showerror("Error", "Please load data first")
            return
        
        chart_type = self.chart_type_var.get()
        library = self.library_var.get()
        x_col = self.x_column_var.get()
        y_col = self.y_column_var.get()
        
        try:
            if library == "matplotlib":
                self.generate_matplotlib_chart(chart_type, x_col, y_col)
            else:
                self.generate_plotly_chart(chart_type, x_col, y_col)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate chart: {str(e)}")
    
    def generate_matplotlib_chart(self, chart_type: str, x_col: str, y_col: str):
        """Generate matplotlib chart."""
        # Clear previous charts (keep last 3)
        widgets = self.charts_container.winfo_children()
        if len(widgets) > 3:
            for widget in widgets[:-3]:
                widget.destroy()
        
        chart_card = Card(self.charts_container, title=f"{chart_type.title()} Chart", padding=15, theme_colors=self.theme_colors)
        chart_card.pack(fill="x", pady=(0, 15))
        
        try:
            if chart_type == "line":
                fig = ChartEngine.create_line_chart_matplotlib(self.data, x_col, y_col, f"Line Chart: {y_col} over {x_col}")
            elif chart_type == "bar":
                value_counts = self.data[y_col].value_counts().head(20)
                fig = ChartEngine.create_bar_chart_matplotlib(value_counts, f"Bar Chart: {y_col}")
            elif chart_type == "pie":
                value_counts = self.data[y_col].value_counts().head(10)
                fig = ChartEngine.create_pie_chart_matplotlib(value_counts, f"Pie Chart: {y_col}")
            elif chart_type == "histogram":
                fig = ChartEngine.create_histogram_matplotlib(self.data[y_col], f"Histogram: {y_col}")
            elif chart_type == "scatter":
                fig = ChartEngine.create_scatter_plot_matplotlib(self.data, x_col, y_col, f"Scatter Plot: {y_col} vs {x_col}")
            else:
                messagebox.showerror("Error", "Chart type not supported with matplotlib")
                chart_card.destroy()
                return
            
            canvas = FigureCanvasTkAgg(fig, chart_card.content_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Chart generation failed: {str(e)}")
            chart_card.destroy()
    
    def generate_plotly_chart(self, chart_type: str, x_col: str, y_col: str):
        """Generate plotly chart and open in browser."""
        try:
            if chart_type == "line":
                fig = ChartEngine.create_line_chart_plotly(self.data, x_col, y_col, f"Line Chart: {y_col} over {x_col}")
            elif chart_type == "bar":
                value_counts = self.data[y_col].value_counts().head(20)
                fig = ChartEngine.create_bar_chart_plotly(value_counts, f"Bar Chart: {y_col}")
            elif chart_type == "pie":
                value_counts = self.data[y_col].value_counts().head(10)
                fig = ChartEngine.create_pie_chart_plotly(value_counts, f"Pie Chart: {y_col}")
            elif chart_type == "histogram":
                fig = ChartEngine.create_histogram_plotly(self.data[y_col], f"Histogram: {y_col}")
            elif chart_type == "scatter":
                fig = ChartEngine.create_scatter_plot_plotly(self.data, x_col, y_col, f"Scatter Plot: {y_col} vs {x_col}")
            elif chart_type == "heatmap":
                numeric_cols = DataProcessor.detect_numeric_columns(self.data)
                if len(numeric_cols) < 2:
                    messagebox.showerror("Error", "Need at least 2 numeric columns for heatmap")
                    return
                fig = ChartEngine.create_heatmap_plotly(self.data[numeric_cols], "Correlation Heatmap")
            else:
                messagebox.showerror("Error", "Chart type not supported")
                return
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
            temp_file.close()
            fig.write_html(temp_file.name)
            webbrowser.open(f'file://{temp_file.name}')
            messagebox.showinfo("Chart Generated", "Interactive chart opened in your browser")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plotly chart: {str(e)}")
    
    def update_table(self):
        """Update data table view."""
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        if not isinstance(self.data, pd.DataFrame):
            return
        
        columns = self.data.columns.tolist()
        self.data_tree['columns'] = columns
        
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=120, anchor='w')
        
        # Limit to first 1000 rows for performance
        display_data = self.data.head(1000)
        for idx, row in display_data.iterrows():
            values = [str(val)[:50] if pd.notna(val) else "" for val in row]
            self.data_tree.insert("", "end", values=values)
    
    def on_table_search(self, event=None):
        """Handle table search - placeholder for future implementation."""
        pass

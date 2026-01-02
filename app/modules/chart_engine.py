"""Chart engine for creating various types of charts using matplotlib and plotly."""

from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class ChartEngine:
    """Engine for creating charts with matplotlib and plotly."""
    
    @staticmethod
    def create_line_chart_matplotlib(
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "Line Chart",
        figsize: tuple = (8, 4)
    ) -> Figure:
        """Create a line chart using matplotlib."""
        fig = Figure(figsize=figsize, dpi=100)
        ax = fig.add_subplot(111)
        
        ax.plot(data[x_col], data[y_col], marker='o', linewidth=2)
        ax.set_title(title)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate()
        
        return fig
    
    @staticmethod
    def create_bar_chart_matplotlib(
        data: pd.Series,
        title: str = "Bar Chart",
        figsize: tuple = (8, 4)
    ) -> Figure:
        """Create a bar chart using matplotlib."""
        fig = Figure(figsize=figsize, dpi=100)
        ax = fig.add_subplot(111)
        
        data.plot(kind='bar', ax=ax)
        ax.set_title(title)
        ax.set_ylabel('Count')
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()
        
        return fig
    
    @staticmethod
    def create_pie_chart_matplotlib(
        data: pd.Series,
        title: str = "Pie Chart",
        figsize: tuple = (6, 6)
    ) -> Figure:
        """Create a pie chart using matplotlib."""
        fig = Figure(figsize=figsize, dpi=100)
        ax = fig.add_subplot(111)
        
        data.plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90)
        ax.set_title(title)
        ax.set_ylabel('')
        fig.tight_layout()
        
        return fig
    
    @staticmethod
    def create_histogram_matplotlib(
        data: pd.Series,
        title: str = "Histogram",
        bins: int = 30,
        figsize: tuple = (8, 4)
    ) -> Figure:
        """Create a histogram using matplotlib."""
        fig = Figure(figsize=figsize, dpi=100)
        ax = fig.add_subplot(111)
        
        ax.hist(data.dropna(), bins=bins, edgecolor='black', alpha=0.7)
        ax.set_title(title)
        ax.set_xlabel(data.name)
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        
        return fig
    
    @staticmethod
    def create_scatter_plot_matplotlib(
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "Scatter Plot",
        figsize: tuple = (8, 4)
    ) -> Figure:
        """Create a scatter plot using matplotlib."""
        fig = Figure(figsize=figsize, dpi=100)
        ax = fig.add_subplot(111)
        
        ax.scatter(data[x_col], data[y_col], alpha=0.6)
        ax.set_title(title)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        
        return fig
    
    @staticmethod
    def create_line_chart_plotly(
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "Line Chart"
    ) -> go.Figure:
        """Create an interactive line chart using plotly."""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='lines+markers',
            name=y_col,
            line=dict(width=2)
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def create_bar_chart_plotly(
        data: pd.Series,
        title: str = "Bar Chart"
    ) -> go.Figure:
        """Create an interactive bar chart using plotly."""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=data.index,
            y=data.values,
            name=title
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=data.index.name or 'Category',
            yaxis_title='Count',
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def create_pie_chart_plotly(
        data: pd.Series,
        title: str = "Pie Chart"
    ) -> go.Figure:
        """Create an interactive pie chart using plotly."""
        fig = go.Figure(data=[go.Pie(
            labels=data.index,
            values=data.values,
            hole=0.3  # Creates a donut chart
        )])
        
        fig.update_layout(
            title=title,
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def create_histogram_plotly(
        data: pd.Series,
        title: str = "Histogram",
        bins: int = 30
    ) -> go.Figure:
        """Create an interactive histogram using plotly."""
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=data.dropna(),
            nbinsx=bins,
            name=title
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=data.name,
            yaxis_title='Frequency',
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def create_scatter_plot_plotly(
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "Scatter Plot",
        color_col: Optional[str] = None
    ) -> go.Figure:
        """Create an interactive scatter plot using plotly."""
        if color_col:
            fig = px.scatter(data, x=x_col, y=y_col, color=color_col, title=title)
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data[x_col],
                y=data[y_col],
                mode='markers',
                name=title
            ))
            fig.update_layout(
                title=title,
                xaxis_title=x_col,
                yaxis_title=y_col,
                template='plotly_white'
            )
        
        return fig
    
    @staticmethod
    def create_heatmap_plotly(
        data: pd.DataFrame,
        title: str = "Correlation Heatmap"
    ) -> go.Figure:
        """Create a correlation heatmap using plotly."""
        corr = data.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            colorscale='RdBu',
            zmid=0,
            text=corr.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title=title,
            template='plotly_white'
        )
        
        return fig

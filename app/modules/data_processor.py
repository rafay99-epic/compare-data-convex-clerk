"""Data processing utilities for data analysis and transformation."""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union


class DataProcessor:
    """Utility class for data processing and analysis."""
    
    @staticmethod
    def get_dataframe_info(df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive information about a DataFrame."""
        info = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'null_counts': df.isnull().sum().to_dict(),
            'null_percentages': (df.isnull().sum() / len(df) * 100).to_dict(),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'datetime_columns': df.select_dtypes(include=['datetime64']).columns.tolist(),
        }
        
        # Add statistics for numeric columns
        if info['numeric_columns']:
            info['numeric_stats'] = df[info['numeric_columns']].describe().to_dict()
        
        # Add value counts for categorical columns (top 10)
        info['categorical_counts'] = {}
        for col in info['categorical_columns'][:10]:  # Limit to first 10 to avoid memory issues
            try:
                info['categorical_counts'][col] = df[col].value_counts().head(10).to_dict()
            except Exception:
                pass
        
        return info
    
    @staticmethod
    def detect_numeric_columns(df: pd.DataFrame) -> List[str]:
        """Detect columns that contain numeric data."""
        return df.select_dtypes(include=[np.number]).columns.tolist()
    
    @staticmethod
    def detect_categorical_columns(df: pd.DataFrame) -> List[str]:
        """Detect columns that contain categorical data."""
        return df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    @staticmethod
    def detect_datetime_columns(df: pd.DataFrame) -> List[str]:
        """Detect columns that might be datetime (will try to parse)."""
        datetime_cols = []
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to parse as datetime
                try:
                    pd.to_datetime(df[col].dropna().head(100))
                    datetime_cols.append(col)
                except:
                    pass
        return datetime_cols
    
    @staticmethod
    def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
        """Get correlation matrix for numeric columns."""
        numeric_cols = DataProcessor.detect_numeric_columns(df)
        if len(numeric_cols) < 2:
            return pd.DataFrame()
        return df[numeric_cols].corr()
    
    @staticmethod
    def convert_to_dataframe(data: Union[Dict, List[Dict]]) -> pd.DataFrame:
        """Convert JSON/JSONL data to DataFrame."""
        if isinstance(data, dict):
            # Single record - convert to list
            data = [data]
        return pd.DataFrame(data)

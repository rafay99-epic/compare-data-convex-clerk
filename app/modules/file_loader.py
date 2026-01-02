"""File loading utilities for JSON, JSONL, and CSV files."""

import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import pandas as pd


class FileLoader:
    """Utility class for loading various file formats."""
    
    @staticmethod
    def load_json(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Load a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Error loading JSON file {file_path}: {str(e)}")
    
    @staticmethod
    def load_jsonl(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Load a JSONL file (one JSON object per line)."""
        records = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        raise Exception(f"Malformed JSON on line {line_num} of {file_path}: {str(e)}")
            return records
        except Exception as e:
            raise Exception(f"Error loading JSONL file {file_path}: {str(e)}")
    
    @staticmethod
    def load_csv(file_path: Union[str, Path]) -> pd.DataFrame:
        """Load a CSV file into a pandas DataFrame."""
        try:
            return pd.read_csv(file_path, encoding='utf-8')
        except Exception as e:
            raise Exception(f"Error loading CSV file {file_path}: {str(e)}")
    
    @staticmethod
    def detect_file_type(file_path: Union[str, Path]) -> str:
        """Detect file type from extension."""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == '.json':
            return 'json'
        elif ext == '.jsonl':
            return 'jsonl'
        elif ext == '.csv':
            return 'csv'
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    @staticmethod
    def load_file(file_path: Union[str, Path]) -> Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]:
        """Load a file, automatically detecting the type."""
        file_type = FileLoader.detect_file_type(file_path)
        
        if file_type == 'json':
            return FileLoader.load_json(file_path)
        elif file_type == 'jsonl':
            return FileLoader.load_jsonl(file_path)
        elif file_type == 'csv':
            return FileLoader.load_csv(file_path)
        else:
            raise ValueError(f"Unknown file type: {file_type}")

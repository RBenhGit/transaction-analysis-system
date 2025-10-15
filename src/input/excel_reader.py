"""
Universal Excel file reader.

This module provides functionality to read Excel files regardless of their structure.
"""

import pandas as pd
from typing import Optional
from pathlib import Path


class ExcelReader:
    """Universal Excel file reader that works with any Excel structure."""
    
    def __init__(self, encoding: str = 'utf-8'):
        """
        Initialize Excel reader.
        
        Args:
            encoding: Character encoding for reading files
        """
        self.encoding = encoding
    
    def read(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Read an Excel file and return as DataFrame.
        
        Args:
            file_path: Path to the Excel file
            sheet_name: Optional sheet name to read (default: first sheet)
        
        Returns:
            pandas DataFrame with the Excel data
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a valid Excel file
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        if path.suffix not in ['.xlsx', '.xls']:
            raise ValueError(f"File is not an Excel file: {file_path}")
        
        try:
            # Read Excel file
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            else:
                df = pd.read_excel(file_path, engine='openpyxl')
            
            return df
        
        except Exception as e:
            raise ValueError(f"Error reading Excel file {file_path}: {str(e)}")
    
    def get_sheet_names(self, file_path: str) -> list:
        """
        Get list of sheet names in an Excel file.
        
        Args:
            file_path: Path to the Excel file
        
        Returns:
            List of sheet names
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        try:
            xl_file = pd.ExcelFile(file_path, engine='openpyxl')
            return xl_file.sheet_names
        except Exception as e:
            raise ValueError(f"Error reading sheet names from {file_path}: {str(e)}")
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get information about an Excel file.
        
        Args:
            file_path: Path to the Excel file
        
        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        df = self.read(file_path)
        
        return {
            'file_name': path.name,
            'file_path': str(path),
            'sheet_names': self.get_sheet_names(file_path),
            'rows': len(df),
            'columns': list(df.columns),
            'column_count': len(df.columns)
        }

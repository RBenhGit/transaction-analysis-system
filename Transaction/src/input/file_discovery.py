"""
Automatic file discovery for Excel transaction files.

This module scans directories and finds Excel files.
"""

from pathlib import Path
from typing import List, Dict


class FileDiscovery:
    """Automatic discovery of Excel transaction files."""
    
    def __init__(self, data_directory: str = "./Data_Files"):
        """
        Initialize file discovery.
        
        Args:
            data_directory: Directory to scan for Excel files
        """
        self.data_directory = Path(data_directory)
    
    def discover_excel_files(self) -> List[Path]:
        """
        Discover all Excel files in the data directory.
        
        Returns:
            List of Path objects for Excel files
        """
        if not self.data_directory.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_directory}")
        
        excel_files = []
        
        # Find all .xlsx and .xls files
        for pattern in ['*.xlsx', '*.xls']:
            excel_files.extend(self.data_directory.glob(pattern))
        
        # Sort by name
        excel_files.sort()
        
        return excel_files
    
    def get_file_list(self) -> List[Dict[str, str]]:
        """
        Get list of Excel files with metadata.
        
        Returns:
            List of dictionaries with file information
        """
        files = self.discover_excel_files()
        
        file_list = []
        for file in files:
            file_list.append({
                'name': file.name,
                'path': str(file),
                'size': file.stat().st_size,
                'modified': file.stat().st_mtime
            })
        
        return file_list
    
    def get_file_by_name(self, file_name: str) -> Path:
        """
        Get file path by file name.
        
        Args:
            file_name: Name of the file to find
        
        Returns:
            Path object for the file
        
        Raises:
            FileNotFoundError: If file is not found
        """
        files = self.discover_excel_files()
        
        for file in files:
            if file.name == file_name:
                return file
        
        raise FileNotFoundError(f"File not found: {file_name}")

"""
Excel Importer

This module handles the importing of Excel files containing transaction data.
It provides file discovery, loading, and basic validation capabilities.
"""

import os
import pandas as pd
from typing import List, Optional, Dict, Any
from pathlib import Path
import openpyxl

from .simple_models import ImportResult
from .config_manager import ConfigManager
from .json_adapter import JSONAdapter


class ExcelImporter:
    """
    Handles importing Excel transaction files from the Data_Files directory.

    This class provides:
    - File discovery in the configured data directory
    - Excel file loading with proper encoding handling
    - Integration with JSONAdapter for processing
    - Error handling and validation
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the Excel importer.

        Args:
            config_manager: ConfigManager instance, creates default if None
        """
        self.config_manager = config_manager or ConfigManager()
        self.json_adapter = JSONAdapter(self.config_manager)
        self.supported_extensions = self.config_manager.get_import_config().get(
            "supported_extensions", [".xlsx", ".xls"]
        )

    def discover_files(self, directory: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover Excel files in the specified directory.

        Args:
            directory: Directory to search, uses config default if None

        Returns:
            List of dictionaries containing file information
        """
        if not directory:
            directory = self.config_manager.get_data_files_path()

        files = []

        if not os.path.exists(directory):
            return files

        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)

                # Check if it's a file and has supported extension
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in self.supported_extensions:
                        # Get file information
                        stat = os.stat(file_path)
                        file_info = {
                            "filename": filename,
                            "path": file_path,
                            "size": stat.st_size,
                            "modified": stat.st_mtime,
                            "extension": ext.lower()
                        }
                        files.append(file_info)

        except OSError as e:
            print(f"Error accessing directory {directory}: {e}")

        # Sort by modification time (newest first)
        files.sort(key=lambda x: x["modified"], reverse=True)

        return files

    def load_excel_file(
        self,
        file_path: str,
        sheet_name: Optional[str] = None,
        encoding: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load an Excel file into a pandas DataFrame.

        Args:
            file_path: Path to the Excel file
            sheet_name: Specific sheet to load, first sheet if None
            encoding: File encoding, auto-detect if None

        Returns:
            pandas DataFrame containing the file data

        Raises:
            IOError: If file cannot be loaded
        """
        if not os.path.exists(file_path):
            raise IOError(f"File not found: {file_path}")

        try:
            # Determine file extension
            _, ext = os.path.splitext(file_path)

            if ext.lower() == '.xlsx':
                # For .xlsx files, use openpyxl engine
                df = pd.read_excel(
                    file_path,
                    sheet_name=sheet_name or 0,
                    engine='openpyxl',
                    header=None  # Don't assume first row is header
                )
            elif ext.lower() == '.xls':
                # For .xls files, use xlrd engine
                df = pd.read_excel(
                    file_path,
                    sheet_name=sheet_name or 0,
                    header=None
                )
            else:
                raise IOError(f"Unsupported file extension: {ext}")

            return df

        except Exception as e:
            raise IOError(f"Failed to load Excel file {file_path}: {e}")

    def get_sheet_names(self, file_path: str) -> List[str]:
        """
        Get list of sheet names in an Excel file.

        Args:
            file_path: Path to the Excel file

        Returns:
            List of sheet names

        Raises:
            IOError: If file cannot be accessed
        """
        if not os.path.exists(file_path):
            raise IOError(f"File not found: {file_path}")

        try:
            # Use openpyxl to get sheet names
            workbook = openpyxl.load_workbook(file_path, read_only=True)
            sheet_names = workbook.sheetnames
            workbook.close()
            return sheet_names

        except Exception as e:
            # Fallback to pandas
            try:
                excel_file = pd.ExcelFile(file_path)
                return excel_file.sheet_names
            except Exception:
                raise IOError(f"Failed to read sheet names from {file_path}: {e}")

    def preview_file(
        self,
        file_path: str,
        rows: int = 10,
        sheet_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Preview the first few rows of an Excel file.

        Args:
            file_path: Path to the Excel file
            rows: Number of rows to preview
            sheet_name: Specific sheet to preview

        Returns:
            Dictionary containing preview information
        """
        try:
            # Load the file
            df = self.load_excel_file(file_path, sheet_name)

            # Get basic information
            preview_info = {
                "filename": os.path.basename(file_path),
                "sheet_name": sheet_name or "First Sheet",
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "preview_rows": min(rows, len(df)),
                "data": df.head(rows).to_dict('records'),
                "columns": list(df.columns),
                "detected_bank": None
            }

            # Try to auto-detect bank
            detected_bank = self.json_adapter.auto_detect_bank(df)
            if detected_bank:
                preview_info["detected_bank"] = detected_bank

            return preview_info

        except Exception as e:
            return {
                "filename": os.path.basename(file_path),
                "error": str(e),
                "total_rows": 0,
                "total_columns": 0,
                "preview_rows": 0,
                "data": [],
                "columns": [],
                "detected_bank": None
            }

    def import_file(
        self,
        file_path: str,
        bank_name: Optional[str] = None,
        sheet_name: Optional[str] = None,
        save_json: bool = True
    ) -> ImportResult:
        """
        Import and process an Excel file.

        Args:
            file_path: Path to the Excel file
            bank_name: Specific bank adapter to use, auto-detect if None
            sheet_name: Specific sheet to import
            save_json: Whether to save processed data as JSON

        Returns:
            ImportResult containing processed transactions or errors
        """
        result = ImportResult(success=True)

        try:
            # Load the Excel file
            df = self.load_excel_file(file_path, sheet_name)

            if df.empty:
                result.add_error("File contains no data")
                return result

            # Process using JSON adapter
            process_result = self.json_adapter.process_dataframe(
                df, bank_name, file_path
            )

            # Copy results
            result.success = process_result.success
            result.transaction_set = process_result.transaction_set
            result.errors = process_result.errors
            result.warnings = process_result.warnings
            result.processing_time = process_result.processing_time

            # Save as JSON if requested and successful
            if save_json and result.success and result.transaction_set:
                try:
                    json_path = self.json_adapter.export_to_json(result.transaction_set)
                    result.add_warning(f"Data saved to: {json_path}")
                except Exception as e:
                    result.add_warning(f"Failed to save JSON: {e}")

        except Exception as e:
            result.add_error(f"Import failed: {e}")

        return result

    def batch_import(
        self,
        file_paths: List[str],
        bank_name: Optional[str] = None,
        save_json: bool = True
    ) -> List[ImportResult]:
        """
        Import multiple Excel files in batch.

        Args:
            file_paths: List of file paths to import
            bank_name: Specific bank adapter to use for all files
            save_json: Whether to save processed data as JSON

        Returns:
            List of ImportResult objects, one per file
        """
        results = []

        for file_path in file_paths:
            print(f"Processing: {os.path.basename(file_path)}")

            result = self.import_file(
                file_path,
                bank_name=bank_name,
                save_json=save_json
            )

            results.append(result)

            # Print summary
            if result.success:
                if result.transaction_set:
                    count = len(result.transaction_set.transactions)
                    print(f"✓ Imported {count} transactions")
                else:
                    print("✓ Processed successfully (no transactions)")
            else:
                print(f"✗ Failed: {'; '.join(result.errors)}")

        return results

    def validate_file_format(self, file_path: str) -> Dict[str, Any]:
        """
        Validate that a file can be processed.

        Args:
            file_path: Path to the file to validate

        Returns:
            Dictionary containing validation results
        """
        validation = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "file_info": {},
            "detected_bank": None
        }

        try:
            # Check file exists
            if not os.path.exists(file_path):
                validation["errors"].append("File does not exist")
                return validation

            # Check file extension
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in self.supported_extensions:
                validation["errors"].append(f"Unsupported file extension: {ext}")
                return validation

            # Get file info
            stat = os.stat(file_path)
            validation["file_info"] = {
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "extension": ext.lower()
            }

            # Try to load file
            df = self.load_excel_file(file_path)

            if df.empty:
                validation["errors"].append("File contains no data")
                return validation

            # Try to detect bank
            detected_bank = self.json_adapter.auto_detect_bank(df)
            if detected_bank:
                validation["detected_bank"] = detected_bank
                validation["valid"] = True
            else:
                validation["warnings"].append("Could not auto-detect bank format")
                validation["valid"] = True  # Still valid, just needs manual bank selection

        except Exception as e:
            validation["errors"].append(f"Validation failed: {e}")

        return validation

    def get_file_statistics(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed statistics about an Excel file.

        Args:
            file_path: Path to the Excel file

        Returns:
            Dictionary containing file statistics
        """
        stats = {
            "filename": os.path.basename(file_path),
            "file_size": 0,
            "sheets": [],
            "total_rows": 0,
            "total_columns": 0,
            "has_data": False,
            "detected_bank": None,
            "error": None
        }

        try:
            # File size
            stats["file_size"] = os.path.getsize(file_path)

            # Sheet names
            sheet_names = self.get_sheet_names(file_path)
            stats["sheets"] = sheet_names

            # Load first sheet for analysis
            df = self.load_excel_file(file_path)
            stats["total_rows"] = len(df)
            stats["total_columns"] = len(df.columns)
            stats["has_data"] = not df.empty

            # Detect bank
            if stats["has_data"]:
                stats["detected_bank"] = self.json_adapter.auto_detect_bank(df)

        except Exception as e:
            stats["error"] = str(e)

        return stats
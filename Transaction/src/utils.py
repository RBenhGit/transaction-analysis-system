"""
Utility functions for the Transaction Analysis system.

This module contains helper functions used across different components
of the transaction analysis system.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import pandas as pd


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory to create
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def get_timestamp() -> str:
    """
    Get current timestamp in YYYYMMDD_HHMMSS format.

    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def clean_column_name(column_name: str) -> str:
    """
    Clean and normalize column names for consistent processing.

    Args:
        column_name: Raw column name from Excel file

    Returns:
        Cleaned column name
    """
    if not isinstance(column_name, str):
        return str(column_name)

    # Remove extra whitespace
    cleaned = column_name.strip()

    # Handle Hebrew text encoding issues
    try:
        cleaned = cleaned.encode('utf-8').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    return cleaned


def safe_float_conversion(value: Any) -> Optional[float]:
    """
    Safely convert a value to float, handling various edge cases.

    Args:
        value: Value to convert

    Returns:
        Float value or None if conversion fails
    """
    if value is None or value == '':
        return None

    try:
        if isinstance(value, str):
            # Remove common formatting characters
            cleaned = value.replace(',', '').replace(' ', '')
            # Handle Hebrew/Arabic numerals if needed
            return float(cleaned)
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_date_conversion(value: Any, date_format: str = "%d/%m/%Y") -> Optional[str]:
    """
    Safely convert a value to ISO date format.

    Args:
        value: Date value to convert
        date_format: Expected input date format

    Returns:
        ISO formatted date string or None if conversion fails
    """
    if value is None or value == '':
        return None

    try:
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        elif isinstance(value, str):
            parsed_date = datetime.strptime(value, date_format)
            return parsed_date.strftime("%Y-%m-%d")
        else:
            # Handle pandas datetime
            return pd.to_datetime(value).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def validate_file_path(file_path: str, allowed_extensions: List[str] = None) -> bool:
    """
    Validate that a file path exists and has an allowed extension.

    Args:
        file_path: Path to validate
        allowed_extensions: List of allowed file extensions (e.g., ['.xlsx', '.xls'])

    Returns:
        True if file is valid, False otherwise
    """
    if not os.path.exists(file_path):
        return False

    if allowed_extensions:
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in [ext.lower() for ext in allowed_extensions]

    return True


def save_json_safely(data: Dict[str, Any], file_path: str) -> bool:
    """
    Safely save data to JSON file with error handling.

    Args:
        data: Data to save
        file_path: Path to save file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        ensure_directory_exists(directory)

        # Save with proper encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {str(e)}")
        return False


def load_json_safely(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Safely load JSON file with error handling.

    Args:
        file_path: Path to JSON file

    Returns:
        Loaded data or None if error occurs
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {str(e)}")
        return None


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.

    Args:
        file_path: Path to file

    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0


def format_currency(amount: float, currency_symbol: str = "₪") -> str:
    """
    Format amount as currency string.

    Args:
        amount: Amount to format
        currency_symbol: Currency symbol to use

    Returns:
        Formatted currency string
    """
    if amount is None:
        return "N/A"

    return f"{currency_symbol}{amount:,.2f}"


def truncate_string(text: str, max_length: int = 50) -> str:
    """
    Truncate string to maximum length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum allowed length

    Returns:
        Truncated string
    """
    if not isinstance(text, str):
        text = str(text)

    if len(text) <= max_length:
        return text

    return text[:max_length-3] + "..."
"""
Base adapter for bank/broker data transformation.

Defines the interface that all bank-specific adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd


class BaseAdapter(ABC):
    """
    Abstract base class for bank/broker adapters.

    All bank-specific adapters must inherit from this class and implement
    the required methods for column mapping and data transformation.
    """

    def __init__(self, config: Dict = None):
        """
        Initialize the adapter.

        Args:
            config: Optional configuration dictionary with bank-specific settings
        """
        self.config = config or {}
        self.bank_name = self.config.get('bank_name', 'Unknown')
        self.column_mapping = self.get_column_mapping()

    @abstractmethod
    def get_column_mapping(self) -> Dict[str, str]:
        """
        Get the column mapping from bank format to standard format.

        Returns:
            Dictionary mapping standard field names to bank-specific column names
            Example: {'date': 'תאריך', 'amount': 'סכום'}
        """
        pass

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform bank-specific DataFrame to standard format.

        Args:
            df: Raw DataFrame from bank Excel file

        Returns:
            Standardized DataFrame with consistent column names and data types
        """
        pass

    def validate_columns(self, df: pd.DataFrame) -> bool:
        """
        Validate that all required columns exist in the DataFrame.

        Args:
            df: DataFrame to validate

        Returns:
            True if all required columns exist, False otherwise
        """
        required_columns = set(self.column_mapping.values())
        actual_columns = set(df.columns)
        missing = required_columns - actual_columns

        if missing:
            print(f"Warning: Missing columns: {missing}")
            return False

        return True

    def rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename DataFrame columns from bank format to standard format.

        Args:
            df: DataFrame with bank-specific column names

        Returns:
            DataFrame with standardized column names
        """
        reverse_mapping = {v: k for k, v in self.column_mapping.items()}
        return df.rename(columns=reverse_mapping)

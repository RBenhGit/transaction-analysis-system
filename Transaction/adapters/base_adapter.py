"""
Base Adapter Class for Bank Transaction Processing

This module defines the abstract base class that all bank-specific adapters
must implement. It provides a standardized interface for processing different
bank transaction file formats.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import date, datetime
from decimal import Decimal

from src.simple_models import Transaction, AdapterConfig, ImportResult


class BaseAdapter(ABC):
    """
    Abstract base class for all bank adapters.

    Each bank adapter must inherit from this class and implement the required
    methods to handle that bank's specific file format and data structure.
    """

    def __init__(self, config: AdapterConfig):
        """
        Initialize the adapter with configuration.

        Args:
            config: AdapterConfig object containing bank-specific settings
        """
        self.config = config
        self.bank_name = config.bank_name
        self.column_mappings = config.column_mappings
        self.date_format = config.date_format
        self.encoding = config.encoding

    @abstractmethod
    def validate_data_format(self, df: pd.DataFrame) -> bool:
        """
        Validate that the DataFrame contains the expected format for this bank.

        Args:
            df: Pandas DataFrame containing the raw data

        Returns:
            bool: True if format is valid, False otherwise
        """
        pass

    @abstractmethod
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess the raw data.

        This method should handle bank-specific data cleaning such as:
        - Removing header/footer rows
        - Handling merged cells
        - Cleaning up data types
        - Removing empty rows

        Args:
            df: Raw DataFrame from Excel file

        Returns:
            Cleaned DataFrame ready for processing
        """
        pass

    @abstractmethod
    def parse_transaction(self, row: pd.Series) -> Optional[Transaction]:
        """
        Parse a single row into a Transaction object.

        Args:
            row: Pandas Series representing one transaction row

        Returns:
            Transaction object or None if row should be skipped
        """
        pass

    def process_dataframe(self, df: pd.DataFrame) -> ImportResult:
        """
        Process a complete DataFrame and convert to standardized transactions.

        This is the main entry point for processing bank data. It orchestrates
        the validation, cleaning, and parsing steps.

        Args:
            df: Raw DataFrame from Excel file

        Returns:
            ImportResult containing processed transactions or errors
        """
        result = ImportResult(success=True)
        start_time = datetime.now()

        try:
            # Step 1: Validate data format
            if not self.validate_data_format(df):
                result.add_error(f"Invalid data format for {self.bank_name}")
                return result

            # Step 2: Clean the data
            cleaned_df = self.clean_data(df)
            if cleaned_df.empty:
                result.add_error("No valid data found after cleaning")
                return result

            # Step 3: Process each row
            transactions = []
            errors = []

            for index, row in cleaned_df.iterrows():
                try:
                    transaction = self.parse_transaction(row)
                    if transaction:
                        transactions.append(transaction)
                except Exception as e:
                    error_msg = f"Error processing row {index + 1}: {str(e)}"
                    errors.append(error_msg)
                    result.add_warning(error_msg)

            if not transactions and errors:
                result.add_error("No transactions could be processed")
                return result

            # Step 4: Create transaction set with metadata
            from src.simple_models import TransactionSet, TransactionMetadata

            # Calculate date range
            dates = [t.date for t in transactions if t.date]
            date_range = {
                'start': min(dates) if dates else None,
                'end': max(dates) if dates else None
            }

            metadata = TransactionMetadata(
                source_file="",  # Will be set by caller
                import_date=datetime.now(),
                total_transactions=len(transactions),
                date_range=date_range,
                bank=self.bank_name,
                encoding=self.encoding
            )

            result.transaction_set = TransactionSet(
                transactions=transactions,
                metadata=metadata
            )

            # Add processing time
            end_time = datetime.now()
            result.processing_time = (end_time - start_time).total_seconds()

            if errors:
                result.add_warning(f"Processed {len(transactions)} transactions with {len(errors)} errors")

        except Exception as e:
            result.add_error(f"Failed to process data: {str(e)}")

        return result

    def parse_date(self, date_str: str) -> Optional[date]:
        """
        Parse a date string using the configured date format.

        Args:
            date_str: Date string from the file

        Returns:
            date object or None if parsing fails
        """
        if not date_str or pd.isna(date_str):
            return None

        try:
            # Handle different input types
            if isinstance(date_str, datetime):
                return date_str.date()
            elif isinstance(date_str, date):
                return date_str

            # Try to parse string
            date_str = str(date_str).strip()
            if not date_str:
                return None

            parsed_date = datetime.strptime(date_str, self.date_format)
            return parsed_date.date()

        except (ValueError, TypeError) as e:
            return None

    def parse_amount(self, amount_str: Any) -> Optional[Decimal]:
        """
        Parse an amount string/number into a Decimal.

        Args:
            amount_str: Amount value from the file

        Returns:
            Decimal object or None if parsing fails
        """
        if amount_str is None or pd.isna(amount_str):
            return None

        try:
            # Handle string amounts with commas and currency symbols
            if isinstance(amount_str, str):
                # Remove common currency symbols and whitespace
                cleaned = amount_str.strip()
                cleaned = cleaned.replace('₪', '').replace('$', '').replace('€', '')
                cleaned = cleaned.replace(',', '').replace(' ', '')

                # Handle empty string after cleaning
                if not cleaned:
                    return None

                # Handle parentheses for negative amounts
                if cleaned.startswith('(') and cleaned.endswith(')'):
                    cleaned = '-' + cleaned[1:-1]

                return Decimal(cleaned)
            else:
                # Handle numeric types
                return Decimal(str(amount_str))

        except (ValueError, TypeError, Exception):
            return None

    def clean_description(self, description: Any) -> str:
        """
        Clean and normalize transaction descriptions.

        Args:
            description: Description value from the file

        Returns:
            Cleaned description string
        """
        if description is None or pd.isna(description):
            return ""

        try:
            desc_str = str(description).strip()

            # Remove excessive whitespace
            desc_str = ' '.join(desc_str.split())

            # Handle Unicode issues by replacing problematic characters
            desc_str = desc_str.encode('ascii', 'ignore').decode('ascii')

            return desc_str
        except Exception:
            # If all else fails, return a safe placeholder
            return "Transaction"

    def get_column_value(self, row: pd.Series, column_key: str) -> Any:
        """
        Get a value from a row using the column mapping.

        Args:
            row: Pandas Series representing the row
            column_key: Key in the column_mappings dict

        Returns:
            Value from the specified column or None if not found
        """
        if column_key not in self.column_mappings:
            return None

        column_name = self.column_mappings[column_key]

        # Handle numeric column indices (for positional mapping)
        if column_name.isdigit():
            column_index = int(column_name)
            if 0 <= column_index < len(row):
                return row.iloc[column_index]
            else:
                return None

        # Handle named columns
        if column_name not in row.index:
            return None

        return row[column_name]

    def validate_required_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Check that all required columns are present in the DataFrame.

        Args:
            df: DataFrame to validate

        Returns:
            List of missing column names
        """
        required_columns = ['date', 'description', 'amount']
        missing_columns = []

        for column_key in required_columns:
            if column_key not in self.column_mappings:
                missing_columns.append(f"mapping for '{column_key}'")
                continue

            mapped_column = self.column_mappings[column_key]
            if mapped_column not in df.columns:
                missing_columns.append(f"column '{mapped_column}' (mapped from '{column_key}')")

        return missing_columns
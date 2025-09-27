"""
IBI Bank Adapter

This module provides the adapter for processing IBI (Israel Beinleumi Bank)
transaction files. It handles the specific format and quirks of IBI Excel exports.
"""

import pandas as pd
from typing import Optional, List
from datetime import date
from decimal import Decimal
import re

from .base_adapter import BaseAdapter
from src.simple_models import Transaction, AdapterConfig


class IBIAdapter(BaseAdapter):
    """
    Adapter for IBI Bank transaction files.

    IBI files typically have Hebrew column headers and may contain:
    - Header rows with account information
    - Footer rows with summary information
    - Date format: DD/MM/YYYY
    - Amount columns that may be split into debit/credit
    """

    def __init__(self, config: Optional[AdapterConfig] = None):
        """
        Initialize IBI adapter with default configuration if none provided.
        """
        if config is None:
            config = AdapterConfig(
                bank_name="IBI",
                column_mappings={
                    "date": "0",        # First column
                    "description": "1", # Second column
                    "amount": "4",      # Fifth column
                    "balance": "5",     # Sixth column (if exists)
                    "reference": "3"    # Fourth column
                },
                date_format="%d/%m/%Y",
                encoding="utf-8",
                skip_rows=1  # Skip header row
            )
        super().__init__(config)

    def validate_data_format(self, df: pd.DataFrame) -> bool:
        """
        Validate that this is an IBI transaction file.

        Checks for expected patterns in the data structure.
        """
        if df.empty or len(df) < 2:
            return False

        # Check if we have the expected structure:
        # - At least 5 columns (date, description, details, reference, amount)
        # - First column looks like dates (DD/MM/YYYY format)
        # - First row might be headers (different from data rows)

        if df.shape[1] < 5:
            return False

        # Check if first column in data rows (row 1+) contains date-like patterns
        date_like_count = 0
        for i in range(1, min(10, len(df))):  # Check first 9 data rows
            first_col_val = str(df.iloc[i, 0])
            # Look for DD/MM/YYYY pattern
            if re.match(r'\d{1,2}/\d{1,2}/\d{4}', first_col_val):
                date_like_count += 1

        # If most rows in first column look like dates, this is likely IBI format
        return date_like_count >= 3

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean IBI-specific data issues.

        IBI files often have:
        - Header row (skip it)
        - Footer rows with totals
        - Empty rows
        """
        # Make a copy to avoid modifying original
        cleaned_df = df.copy()

        # Step 1: Skip header row if skip_rows is configured
        if self.config.skip_rows > 0:
            cleaned_df = cleaned_df.iloc[self.config.skip_rows:].reset_index(drop=True)

        # Step 2: Remove completely empty rows
        cleaned_df = cleaned_df.dropna(how='all')

        # Step 3: Remove footer rows (usually contain totals or summaries)
        cleaned_df = self._remove_footer_rows(cleaned_df)

        # Step 4: Remove rows where date column (first column) is empty
        if len(cleaned_df) > 0:
            cleaned_df = cleaned_df.dropna(subset=[0])  # Remove rows with no date

        # Step 5: Keep only rows where first column looks like a date
        if len(cleaned_df) > 0:
            date_mask = cleaned_df[0].astype(str).str.match(r'\d{1,2}/\d{1,2}/\d{4}')
            cleaned_df = cleaned_df[date_mask]

        return cleaned_df

    def parse_transaction(self, row: pd.Series) -> Optional[Transaction]:
        """
        Parse a single IBI transaction row.
        """
        try:
            # Extract date
            transaction_date = self._parse_ibi_date(row)
            if not transaction_date:
                return None

            # Extract description
            description = self._parse_ibi_description(row)
            # Allow empty descriptions, just make sure it's not None
            if description is None:
                description = ""

            # Extract amount
            amount = self._parse_ibi_amount(row)
            if amount is None:
                return None

            # Extract balance (optional)
            balance = self._parse_ibi_balance(row)

            # Extract reference (optional)
            reference = self._parse_ibi_reference(row)

            # Create transaction
            transaction = Transaction(
                date=transaction_date,
                description=description,
                amount=amount,
                balance=balance,
                category=None,  # IBI files don't include category info
                reference=reference,
                bank=self.bank_name,
                account=None  # IBI files don't typically include account number in data rows
            )

            return transaction

        except Exception as e:
            # Print actual error for debugging
            print(f"Parse error: {e}")
            return None

    def _parse_ibi_date(self, row: pd.Series) -> Optional[date]:
        """Parse date from IBI format."""
        date_value = self.get_column_value(row, 'date')
        return self.parse_date(date_value)

    def _parse_ibi_description(self, row: pd.Series) -> str:
        """Parse description from IBI format."""
        description = self.get_column_value(row, 'description')
        return self.clean_description(description)

    def _parse_ibi_amount(self, row: pd.Series) -> Optional[Decimal]:
        """
        Parse amount from IBI format.

        IBI files may have separate debit/credit columns or a single amount column.
        """
        # Try single amount column first
        amount = self.get_column_value(row, 'amount')
        if amount is not None:
            parsed_amount = self.parse_amount(amount)
            if parsed_amount is not None:
                return parsed_amount

        # Try separate debit/credit columns if configured
        if hasattr(self.config, 'amount_columns') and self.config.amount_columns:
            debit_col = self.config.amount_columns.get('debit')
            credit_col = self.config.amount_columns.get('credit')

            debit_amount = Decimal('0')
            credit_amount = Decimal('0')

            if debit_col and debit_col in row.index:
                debit_value = self.parse_amount(row[debit_col])
                if debit_value:
                    debit_amount = debit_value

            if credit_col and credit_col in row.index:
                credit_value = self.parse_amount(row[credit_col])
                if credit_value:
                    credit_amount = credit_value

            # Calculate net amount (credit - debit)
            if debit_amount != 0 or credit_amount != 0:
                return credit_amount - debit_amount

        return None

    def _parse_ibi_balance(self, row: pd.Series) -> Optional[Decimal]:
        """Parse balance from IBI format."""
        balance = self.get_column_value(row, 'balance')
        return self.parse_amount(balance)

    def _parse_ibi_reference(self, row: pd.Series) -> Optional[str]:
        """Parse reference number from IBI format."""
        reference = self.get_column_value(row, 'reference')
        if reference and not pd.isna(reference):
            return str(reference).strip()
        return None

    def _is_valid_date_cell(self, cell_value) -> bool:
        """Check if a cell contains a valid date."""
        if cell_value is None or pd.isna(cell_value):
            return False

        # Try to parse as date
        parsed_date = self.parse_date(cell_value)
        return parsed_date is not None

    def _remove_footer_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove footer rows that contain summaries or totals.

        IBI files often have footer rows with Hebrew text like "סה״כ" (total).
        """
        if df.empty:
            return df

        # Look for rows that contain summary keywords
        summary_keywords = ['סה״כ', 'סהכ', 'סך הכל', 'Total', 'סיכום']

        # Check each row from the bottom up
        rows_to_remove = []
        for idx in reversed(df.index):
            row_text = ' '.join(str(val) for val in df.loc[idx] if pd.notna(val))

            # If row contains summary keywords, mark for removal
            if any(keyword in row_text for keyword in summary_keywords):
                rows_to_remove.append(idx)
            # If we find a row with a valid date after summary rows, stop
            elif self._is_valid_date_cell(df.loc[idx].get(self.column_mappings.get('date', ''), None)):
                break

        # Remove identified footer rows
        if rows_to_remove:
            df = df.drop(rows_to_remove)

        return df

    def get_account_info(self, df: pd.DataFrame) -> dict:
        """
        Extract account information from IBI file headers.

        IBI files often contain account information in the first few rows.
        """
        account_info = {
            'account_number': None,
            'account_name': None,
            'branch': None,
            'currency': 'ILS'  # Default for IBI
        }

        if df.empty:
            return account_info

        # Look in the first 10 rows for account information
        header_rows = df.head(10)

        # Patterns to look for
        patterns = {
            'account_number': [r'חשבון.*?(\d{6,})', r'מס.*?חשבון.*?(\d{6,})'],
            'branch': [r'סניף.*?(\d{3,})', r'מס.*?סניף.*?(\d{3,})']
        }

        for idx, row in header_rows.iterrows():
            row_text = ' '.join(str(val) for val in row if pd.notna(val))

            for field, field_patterns in patterns.items():
                if account_info[field] is None:
                    for pattern in field_patterns:
                        match = re.search(pattern, row_text)
                        if match:
                            account_info[field] = match.group(1)
                            break

        return account_info
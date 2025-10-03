"""
IBI Broker Adapter

Handles transformation of IBI securities trading Excel files to standard format.
Supports all 13 IBI fields including stock names, transaction types, fees, etc.
"""

from typing import Dict
import pandas as pd
from datetime import datetime
from .base_adapter import BaseAdapter


class IBIAdapter(BaseAdapter):
    """
    Adapter for IBI broker securities trading format.

    Supports complete 13-field IBI format:
    - Date and transaction type
    - Security information (name, symbol)
    - Trade execution (quantity, price, currency)
    - Fees and costs
    - Multi-currency amounts
    - Balance and tax estimates
    """

    def __init__(self, config: Dict = None):
        """Initialize IBI adapter with configuration."""
        super().__init__(config)
        self.bank_name = 'IBI'
        self.account_type = 'securities_trading'
        self.date_format = '%d/%m/%Y'

    def get_column_mapping(self) -> Dict[str, str]:
        """
        Get IBI-specific column mapping.

        Maps standard field names to Hebrew column names in IBI Excel files.

        Returns:
            Complete mapping for all 13 IBI fields
        """
        return {
            'date': 'תאריך',
            'transaction_type': 'סוג פעולה',
            'security_name': 'שם נייר',
            'security_symbol': 'מס\' נייר / סימבול',
            'quantity': 'כמות',
            'execution_price': 'שער ביצוע',
            'currency': 'מטבע',
            'transaction_fee': 'עמלת פעולה',
            'additional_fees': 'עמלות נלוות',
            'amount_foreign_currency': 'תמורה במט"ח',
            'amount_local_currency': 'תמורה בשקלים',
            'balance': 'יתרה שקלית',
            'capital_gains_tax_estimate': 'אומדן מס רווחי הון'
        }

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform IBI DataFrame to standard format.

        Steps:
        1. Validate columns exist
        2. Rename columns to standard names
        3. Parse and convert data types
        4. Clean and normalize data

        Args:
            df: Raw IBI Excel DataFrame

        Returns:
            Standardized DataFrame ready for Transaction model
        """
        # Validate columns
        if not self.validate_columns(df):
            raise ValueError("IBI Excel file is missing required columns")

        # Rename columns
        df_transformed = self.rename_columns(df.copy())

        # Parse date column
        df_transformed['date'] = self._parse_dates(df_transformed['date'])

        # Ensure numeric columns are float
        numeric_columns = [
            'quantity', 'execution_price', 'transaction_fee', 'additional_fees',
            'amount_foreign_currency', 'amount_local_currency', 'balance',
            'capital_gains_tax_estimate'
        ]

        for col in numeric_columns:
            if col in df_transformed.columns:
                df_transformed[col] = pd.to_numeric(df_transformed[col], errors='coerce').fillna(0.0)

        # Clean string columns
        string_columns = ['transaction_type', 'security_name', 'security_symbol', 'currency']
        for col in string_columns:
            if col in df_transformed.columns:
                df_transformed[col] = df_transformed[col].astype(str).str.strip()

        # Add metadata
        df_transformed['bank'] = self.bank_name
        df_transformed['account_type'] = self.account_type

        # Generate unique IDs
        df_transformed['id'] = df_transformed.apply(
            lambda row: self._generate_transaction_id(row), axis=1
        )

        return df_transformed

    def _parse_dates(self, date_series: pd.Series) -> pd.Series:
        """
        Parse dates from IBI format (DD/MM/YYYY).

        Args:
            date_series: Series with date strings

        Returns:
            Series with parsed datetime objects
        """
        try:
            # Try parsing with IBI format
            return pd.to_datetime(date_series, format=self.date_format, errors='coerce')
        except Exception as e:
            print(f"Warning: Error parsing dates: {e}")
            return pd.to_datetime(date_series, errors='coerce')

    def _generate_transaction_id(self, row: pd.Series) -> str:
        """
        Generate unique transaction ID.

        Combines date, transaction type, and security symbol to create
        a unique identifier.

        Args:
            row: DataFrame row

        Returns:
            Unique transaction ID string
        """
        date_str = row['date'].strftime('%Y%m%d') if isinstance(row['date'], datetime) else str(row['date'])
        trans_type = str(row.get('transaction_type', ''))[:5]
        symbol = str(row.get('security_symbol', ''))[:10]
        amount = str(abs(row.get('amount_local_currency', 0)))[:8]

        return f"IBI_{date_str}_{trans_type}_{symbol}_{amount}".replace(' ', '_')

    def categorize_transaction(self, transaction_type: str) -> str:
        """
        Categorize transaction based on type.

        Args:
            transaction_type: Hebrew transaction type from IBI

        Returns:
            Standard category (stocks, etf, dividend, fee, tax, other)
        """
        transaction_type = transaction_type.lower()

        if 'קניה' in transaction_type or 'מכירה' in transaction_type:
            return 'stocks'
        elif 'דיבידנד' in transaction_type or 'דיב' in transaction_type:
            return 'dividend'
        elif 'עמלה' in transaction_type or 'דמי' in transaction_type:
            return 'fee'
        elif 'מס' in transaction_type:
            return 'tax'
        elif 'העברה' in transaction_type:
            return 'transfer'
        elif 'ריבית' in transaction_type:
            return 'interest'
        else:
            return 'other'

    def get_transaction_direction(self, row: pd.Series) -> str:
        """
        Determine if transaction is buy, sell, or other.

        Args:
            row: DataFrame row with transaction data

        Returns:
            'buy', 'sell', or 'other'
        """
        trans_type = str(row.get('transaction_type', '')).lower()

        if 'קניה' in trans_type:
            return 'buy'
        elif 'מכירה' in trans_type:
            return 'sell'
        else:
            return 'other'

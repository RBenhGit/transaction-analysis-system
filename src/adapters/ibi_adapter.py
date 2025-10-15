"""
IBI Broker Adapter

Handles transformation of IBI securities trading Excel files to standard format.
Supports all 13 IBI fields including stock names, transaction types, fees, etc.
"""

import logging
from typing import Dict, List
import pandas as pd
from datetime import datetime
from .base_adapter import BaseAdapter
from src.models.transaction_classifier import IBITransactionClassifier

# Configure logging
logger = logging.getLogger(__name__)


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
        self.classifier = IBITransactionClassifier()

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

        Raises:
            ValueError: If required columns are missing or data is invalid
        """
        try:
            # Validate input
            if df is None or df.empty:
                raise ValueError("DataFrame is empty or None")

            logger.info(f"Transforming IBI data: {len(df)} rows")

            # Validate columns
            if not self.validate_columns(df):
                missing_cols = self._get_missing_columns(df)
                raise ValueError(
                    f"IBI Excel file is missing required columns: {', '.join(missing_cols)}"
                )

            # Rename columns
            df_transformed = self.rename_columns(df.copy())

            # Parse date column with error handling
            try:
                df_transformed['date'] = self._parse_dates(df_transformed['date'])

                # Check for invalid dates
                null_dates = df_transformed['date'].isnull().sum()
                if null_dates > 0:
                    logger.warning(f"{null_dates} rows have invalid dates and will be skipped")
                    # Remove rows with invalid dates
                    df_transformed = df_transformed.dropna(subset=['date'])

            except Exception as e:
                logger.error(f"Date parsing failed: {e}")
                raise ValueError(f"Failed to parse dates: {e}")

            # Ensure numeric columns are float with validation
            numeric_columns = [
                'quantity', 'execution_price', 'transaction_fee', 'additional_fees',
                'amount_foreign_currency', 'amount_local_currency', 'balance',
                'capital_gains_tax_estimate'
            ]

            for col in numeric_columns:
                if col in df_transformed.columns:
                    try:
                        # Convert to numeric, coercing errors
                        df_transformed[col] = pd.to_numeric(
                            df_transformed[col],
                            errors='coerce'
                        ).fillna(0.0)

                        # Check for infinite values
                        inf_count = (df_transformed[col] == float('inf')).sum()
                        if inf_count > 0:
                            logger.warning(f"{col} has {inf_count} infinite values, replacing with 0")
                            df_transformed[col] = df_transformed[col].replace([float('inf'), float('-inf')], 0.0)

                    except Exception as e:
                        logger.error(f"Error converting {col} to numeric: {e}")
                        # Set to 0.0 as fallback
                        df_transformed[col] = 0.0

            # Clean string columns with validation
            string_columns = ['transaction_type', 'security_name', 'security_symbol', 'currency']
            for col in string_columns:
                if col in df_transformed.columns:
                    try:
                        df_transformed[col] = df_transformed[col].astype(str).str.strip()

                        # Replace 'nan' strings with empty strings
                        df_transformed[col] = df_transformed[col].replace('nan', '')

                    except Exception as e:
                        logger.error(f"Error cleaning {col}: {e}")
                        df_transformed[col] = ''

            # Validate required fields are not empty
            required_fields = ['security_symbol', 'security_name']
            for field in required_fields:
                if field in df_transformed.columns:
                    empty_count = (df_transformed[field] == '').sum()
                    if empty_count > 0:
                        logger.warning(f"{empty_count} rows have empty {field}, removing these rows")
                        df_transformed = df_transformed[df_transformed[field] != '']

            # Add classifier metadata columns
            logger.info("Adding classifier metadata columns...")
            try:
                # Apply classifier to each row and add metadata
                df_transformed['transaction_effect'] = df_transformed.apply(
                    lambda row: self.classifier.classify_transaction(row).value, axis=1
                )
                df_transformed['is_phantom'] = df_transformed.apply(
                    lambda row: self.classifier.is_phantom_position(row), axis=1
                )

                # Calculate share direction and quantity
                share_effects = df_transformed.apply(
                    lambda row: self.classifier.get_share_effect(row), axis=1
                )
                df_transformed['share_direction'] = share_effects.apply(lambda x: x[0])
                df_transformed['share_quantity_abs'] = share_effects.apply(lambda x: x[1])

                # Calculate cost basis
                df_transformed['cost_basis'] = df_transformed.apply(
                    lambda row: self.classifier.get_cost_basis(row), axis=1
                )

                logger.info("Successfully added all classifier metadata columns")
            except Exception as e:
                logger.error(f"Error adding classifier metadata: {e}", exc_info=True)
                # Add empty columns if classification fails
                df_transformed['transaction_effect'] = 'other'
                df_transformed['is_phantom'] = False
                df_transformed['share_direction'] = 'none'
                df_transformed['share_quantity_abs'] = 0.0
                df_transformed['cost_basis'] = 0.0

            # Add metadata
            df_transformed['bank'] = self.bank_name
            df_transformed['account_type'] = self.account_type

            # Generate unique IDs with error handling
            try:
                df_transformed['id'] = df_transformed.apply(
                    lambda row: self._generate_transaction_id(row), axis=1
                )
            except Exception as e:
                logger.error(f"Error generating transaction IDs: {e}")
                # Fallback: simple sequential IDs
                df_transformed['id'] = [f"IBI_{i}" for i in range(len(df_transformed))]

            logger.info(f"Successfully transformed {len(df_transformed)} transactions")
            return df_transformed

        except Exception as e:
            logger.error(f"IBI adapter transform failed: {e}", exc_info=True)
            raise

    def _get_missing_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of missing required columns.

        Args:
            df: DataFrame to check

        Returns:
            List of missing column names
        """
        mapping = self.get_column_mapping()
        required_columns = [
            'date', 'transaction_type', 'security_name', 'security_symbol',
            'quantity', 'currency', 'balance'
        ]

        missing = []
        for req_col in required_columns:
            hebrew_col = mapping.get(req_col)
            if hebrew_col and hebrew_col not in df.columns:
                missing.append(f"{req_col} ({hebrew_col})")

        return missing

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
            parsed = pd.to_datetime(date_series, format=self.date_format, errors='coerce')

            # Count how many dates failed to parse
            failed_count = parsed.isnull().sum()
            if failed_count > 0:
                logger.warning(
                    f"Failed to parse {failed_count} dates out of {len(date_series)}. "
                    "These rows will be excluded."
                )

            return parsed

        except Exception as e:
            logger.error(f"Critical error parsing dates: {e}")
            # Fallback: try auto-detection
            try:
                logger.info("Attempting automatic date format detection")
                return pd.to_datetime(date_series, errors='coerce')
            except Exception as e2:
                logger.error(f"Date auto-detection failed: {e2}")
                raise ValueError(f"Cannot parse dates: {e}")

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

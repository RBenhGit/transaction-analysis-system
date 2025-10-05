"""
Actual Portfolio Adapter.

Reads IBI's current portfolio file (actual positions with market values).
This represents the broker's real-time holdings data.
"""

import pandas as pd
from typing import List, Dict
from pathlib import Path


class ActualPortfolioAdapter:
    """
    Adapter for reading IBI's actual portfolio positions file.

    Parses the current holdings Excel file which contains:
    - Current quantities held
    - Cost basis (actual money invested)
    - Current market prices
    - Current market values
    - Unrealized P&L
    """

    def __init__(self, file_path: str = None):
        """
        Initialize adapter.

        Args:
            file_path: Path to IBI portfolio Excel file
        """
        self.file_path = file_path

    def get_column_mapping(self) -> Dict[str, str]:
        """
        Get column mapping from Hebrew to English.

        Returns:
            Dictionary mapping English field names to Hebrew column names
        """
        return {
            'security_name': 'שם נייר',
            'security_number': 'מספר נייר',
            'security_symbol': 'סימבול',
            'security_type': 'סוג נייר',
            'currency': 'מטבע',
            'quantity': 'כמות נוכחית',
            'current_price': 'שער',
            'price_change_pct': '% שינוי',
            'market_value': 'שווי נוכחי',
            'daily_pnl': 'רווח/הפסד יומי',
            'total_pnl': 'שינוי מעלות',
            'total_pnl_pct': 'שינוי מעלות ב%',
            'cost_basis': 'עלות',
            'holding_pct': 'אחוז אחזקה',
        }

    def read(self, file_path: str = None) -> pd.DataFrame:
        """
        Read actual portfolio Excel file.

        Args:
            file_path: Path to Excel file (overrides init path)

        Returns:
            Raw DataFrame with Hebrew columns
        """
        path = file_path or self.file_path

        if not path:
            raise ValueError("No file path provided")

        if not Path(path).exists():
            raise FileNotFoundError(f"Portfolio file not found: {path}")

        # Read Excel file
        df = pd.read_excel(path)

        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform IBI portfolio to standard format.

        Steps:
        1. Rename columns to English
        2. Filter out non-stock entries
        3. Clean and normalize data
        4. Add calculated fields

        Args:
            df: Raw DataFrame from IBI portfolio file

        Returns:
            Standardized DataFrame with actual positions
        """
        # Get reverse mapping (Hebrew -> English)
        mapping = self.get_column_mapping()
        reverse_mapping = {v: k for k, v in mapping.items()}

        # Rename columns
        df_transformed = df.rename(columns=reverse_mapping).copy()

        # Filter out non-stock positions:
        # 1. Remove negative quantities (short positions, tax liabilities)
        # 2. Remove options and derivatives (אופציה, תפ"ס)
        # 3. Remove tax entries (מס לשלם, מס תקבולים)
        # 4. Keep only positive quantity stock positions

        if 'quantity' in df_transformed.columns:
            df_transformed = df_transformed[df_transformed['quantity'] > 0].copy()

        if 'security_type' in df_transformed.columns:
            # Filter out derivatives and tax entries
            exclude_types = ['אופציית', 'תפ"ס', 'פח"ק']
            for exclude_type in exclude_types:
                df_transformed = df_transformed[
                    ~df_transformed['security_type'].str.contains(exclude_type, na=False)
                ].copy()

        if 'security_name' in df_transformed.columns:
            # Exclude tax-related entries
            exclude_names = ['מס לשלם', 'מס תקבולים', 'מס ששולם']
            df_transformed = df_transformed[
                ~df_transformed['security_name'].str.contains('|'.join(exclude_names), na=False)
            ].copy()

        # Clean numeric columns
        numeric_columns = [
            'quantity', 'current_price', 'market_value', 'cost_basis',
            'total_pnl', 'daily_pnl'
        ]

        for col in numeric_columns:
            if col in df_transformed.columns:
                df_transformed[col] = pd.to_numeric(
                    df_transformed[col],
                    errors='coerce'
                ).fillna(0.0)

        # Clean string columns
        string_columns = ['security_name', 'security_symbol', 'currency', 'security_type']
        for col in string_columns:
            if col in df_transformed.columns:
                df_transformed[col] = df_transformed[col].astype(str).str.strip()

        # Normalize currency names
        if 'currency' in df_transformed.columns:
            df_transformed['currency'] = df_transformed['currency'].apply(
                self._normalize_currency
            )

        # Use symbol if available, otherwise use security number or name
        if 'security_symbol' in df_transformed.columns:
            df_transformed['symbol_clean'] = df_transformed.apply(
                lambda row: (
                    row['security_symbol'] if pd.notna(row['security_symbol']) and row['security_symbol'].strip()
                    else row.get('security_number', row.get('security_name', ''))
                ),
                axis=1
            )

        # Calculate average cost per share
        if 'cost_basis' in df_transformed.columns and 'quantity' in df_transformed.columns:
            df_transformed['avg_cost'] = df_transformed.apply(
                lambda row: row['cost_basis'] / row['quantity'] if row['quantity'] > 0 else 0,
                axis=1
            )

        # Add source identifier
        df_transformed['source'] = 'actual'

        return df_transformed

    def _normalize_currency(self, currency_str: str) -> str:
        """
        Normalize currency string to symbol.

        Args:
            currency_str: Currency name from Excel (e.g., "שקל חדש", "דולר אמריקאי")

        Returns:
            Currency symbol ("₪" or "$")
        """
        if pd.isna(currency_str):
            return "₪"

        currency_str = str(currency_str).strip().lower()

        if 'שקל' in currency_str or 'nis' in currency_str:
            return "₪"
        elif 'דולר' in currency_str or 'usd' in currency_str or 'dollar' in currency_str:
            return "$"
        else:
            return "₪"  # Default to NIS

    def load_positions(self, file_path: str = None) -> List[Dict]:
        """
        Load actual positions from file.

        Convenience method that reads and transforms in one step.

        Args:
            file_path: Path to portfolio Excel file

        Returns:
            List of position dictionaries
        """
        df_raw = self.read(file_path)
        df_transformed = self.transform(df_raw)

        # Convert to list of dictionaries
        positions = df_transformed.to_dict('records')

        return positions

    def get_summary_stats(self, df: pd.DataFrame) -> Dict:
        """
        Calculate summary statistics for portfolio.

        Args:
            df: Transformed DataFrame

        Returns:
            Dictionary with summary statistics
        """
        # Group by currency
        by_currency = {}

        for currency in df['currency'].unique():
            currency_df = df[df['currency'] == currency]

            by_currency[currency] = {
                'total_positions': len(currency_df),
                'total_market_value': currency_df['market_value'].sum(),
                'total_cost_basis': currency_df['cost_basis'].sum(),
                'total_unrealized_pnl': currency_df['total_pnl'].sum(),
                'total_daily_pnl': currency_df['daily_pnl'].sum(),
            }

        # Overall stats
        return {
            'by_currency': by_currency,
            'total_positions': len(df),
            'currencies': list(df['currency'].unique()),
        }

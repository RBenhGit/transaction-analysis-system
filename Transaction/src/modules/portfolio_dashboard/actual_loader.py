"""
Actual Portfolio Loader.

Converts data from actual portfolio adapter to Position objects.
"""

from typing import List, Dict
import pandas as pd
from .position import Position
from src.adapters.actual_portfolio_adapter import ActualPortfolioAdapter


class ActualPortfolioLoader:
    """
    Load actual portfolio positions from IBI portfolio file.

    Converts raw portfolio data to Position objects with market values.
    """

    def __init__(self, file_path: str = None):
        """
        Initialize loader.

        Args:
            file_path: Path to IBI portfolio Excel file
        """
        self.file_path = file_path
        self.adapter = ActualPortfolioAdapter(file_path)

    def load(self, file_path: str = None) -> List[Position]:
        """
        Load positions from actual portfolio file.

        Args:
            file_path: Path to portfolio file (overrides init path)

        Returns:
            List of Position objects with market data
        """
        # Read and transform data
        df_raw = self.adapter.read(file_path)
        df_transformed = self.adapter.transform(df_raw)

        # Convert to Position objects
        positions = self._dataframe_to_positions(df_transformed)

        return positions

    def load_by_currency(self, file_path: str = None) -> Dict[str, List[Position]]:
        """
        Load positions grouped by currency.

        Args:
            file_path: Path to portfolio file

        Returns:
            Dictionary mapping currency to positions
            Example: {"₪": [pos1, pos2], "$": [pos3, pos4]}
        """
        positions = self.load(file_path)

        # Group by currency
        by_currency = {}
        for pos in positions:
            currency = pos.currency
            if currency not in by_currency:
                by_currency[currency] = []
            by_currency[currency].append(pos)

        return by_currency

    def _dataframe_to_positions(self, df: pd.DataFrame) -> List[Position]:
        """
        Convert DataFrame to Position objects.

        Args:
            df: Transformed DataFrame from adapter

        Returns:
            List of Position objects
        """
        positions = []

        for _, row in df.iterrows():
            # Get symbol (use cleaned symbol or fallback)
            symbol = row.get('symbol_clean', row.get('security_symbol', ''))
            if not symbol or pd.isna(symbol):
                symbol = str(row.get('security_number', row.get('security_name', 'UNKNOWN')))

            # Create position
            position = Position(
                security_name=str(row.get('security_name', 'Unknown')),
                security_symbol=str(symbol),
                quantity=float(row.get('quantity', 0)),
                average_cost=float(row.get('avg_cost', 0)),
                total_invested=float(row.get('cost_basis', 0)),
                currency=str(row.get('currency', '₪')),
                current_price=float(row.get('current_price', 0)) if pd.notna(row.get('current_price')) else None,
                market_value=float(row.get('market_value', 0)) if pd.notna(row.get('market_value')) else None,
                source='actual'
            )

            positions.append(position)

        return positions

    def get_summary(self, file_path: str = None) -> Dict:
        """
        Get portfolio summary statistics.

        Args:
            file_path: Path to portfolio file

        Returns:
            Summary statistics dictionary
        """
        df_raw = self.adapter.read(file_path)
        df_transformed = self.adapter.transform(df_raw)

        return self.adapter.get_summary_stats(df_transformed)

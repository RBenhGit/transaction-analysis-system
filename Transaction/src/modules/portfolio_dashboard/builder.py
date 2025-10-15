"""
Portfolio Builder.

Builds current portfolio by processing actual transactions chronologically.
Uses REAL transaction data to calculate actual holdings.
"""

from typing import List, Dict
from src.models.transaction import Transaction
from .position import Position


class PortfolioBuilder:
    """
    Builds portfolio by processing transactions in chronological order.

    Process:
    1. Sort all transactions by date (oldest first)
    2. Process each transaction sequentially
    3. Update positions as we go (buy adds, sell removes)
    4. Calculate weighted average cost
    5. Return current positions
    """

    def __init__(self):
        self.positions: Dict[str, Position] = {}  # symbol -> position

    def build(self, transactions: List[Transaction]) -> List[Position]:
        """
        Build current portfolio from actual transaction history.

        Args:
            transactions: List of REAL Transaction objects from loaded Excel files

        Returns:
            List of current Position objects (quantity > 0 only)
        """
        # Reset positions
        self.positions = {}

        # 1. Sort transactions by date (oldest first) - CRITICAL for correct calculations
        sorted_txs = sorted(transactions, key=lambda t: t.date)

        # 2. Process each transaction chronologically
        for tx in sorted_txs:
            self._process_transaction(tx)

        # 3. Return only positions with quantity > 0 (filter out closed positions)
        return [p for p in self.positions.values() if p.quantity > 0]

    def build_by_currency(self, transactions: List[Transaction]) -> Dict[str, List[Position]]:
        """
        Build portfolio grouped by currency (NIS vs USD).

        Args:
            transactions: List of REAL Transaction objects

        Returns:
            Dictionary: currency -> List of Position objects
            Example: {"₪": [pos1, pos2], "$": [pos3, pos4]}
        """
        # Build all positions
        all_positions = self.build(transactions)

        # Group by currency
        by_currency = {}
        for pos in all_positions:
            currency = pos.currency
            if currency not in by_currency:
                by_currency[currency] = []
            by_currency[currency].append(pos)

        return by_currency

    def _process_transaction(self, tx: Transaction):
        """
        Process one actual transaction and update position.

        Args:
            tx: Real Transaction object with actual quantities and prices
        """
        symbol = tx.security_symbol

        # Get existing position or create new one
        if symbol not in self.positions:
            self.positions[symbol] = Position(
                security_name=tx.security_name,
                security_symbol=symbol,
                quantity=0.0,
                average_cost=0.0,
                total_invested=0.0,
                currency=tx.currency
            )

        position = self.positions[symbol]

        # Update position based on actual transaction type
        if tx.is_buy:
            self._process_buy(position, tx)
        elif tx.is_sell:
            self._process_sell(position, tx)
        # Ignore dividends, fees, taxes for now (don't affect holdings)

    def _process_buy(self, position: Position, tx: Transaction):
        """
        Add shares to position from actual buy transaction.

        Calculates weighted average cost based on actual prices paid.

        Args:
            position: Current position to update
            tx: Actual buy transaction
        """
        # Calculate new total quantity
        new_quantity = position.quantity + tx.quantity

        # Calculate new total invested (add actual money paid for these shares)
        new_total_invested = position.total_invested + (tx.quantity * tx.execution_price)

        # Update position with actual values
        position.quantity = new_quantity
        position.total_invested = new_total_invested

        # Calculate weighted average cost
        position.average_cost = new_total_invested / new_quantity if new_quantity > 0 else 0.0

    def _process_sell(self, position: Position, tx: Transaction):
        """
        Remove shares from position from actual sell transaction.

        Reduces quantity and invested amount. Average cost stays the same
        (we're reducing at our cost basis, not sale price).

        Args:
            position: Current position to update
            tx: Actual sell transaction
        """
        # Calculate value to remove (at our average cost, not sale price)
        sold_value = tx.quantity * position.average_cost

        # Update position - reduce by actual shares sold
        position.quantity -= tx.quantity
        position.total_invested -= sold_value

        # Average cost stays the same (it's our cost basis)
        # If position is fully closed, quantity and invested will both be 0
        # and will be filtered out in build()

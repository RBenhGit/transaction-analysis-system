"""
Position data model.

Represents current holdings for a single security.
Can include both calculated (from transactions) and actual (from broker) data.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Position:
    """
    Current holding position for one security.

    Core fields (always present):
    - quantity: Shares currently owned
    - average_cost: Weighted average price paid per share
    - total_invested: Money invested in this position (cost basis)
    - currency: Currency symbol (₪ or $)

    Market data fields (from actual portfolio):
    - current_price: Current market price per share
    - market_value: Current market value (quantity * current_price)
    - source: Data source ('calculated' | 'actual' | 'merged')
    """

    security_name: str
    security_symbol: str
    quantity: float
    average_cost: float
    total_invested: float
    currency: str
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    source: str = 'calculated'

    @property
    def unrealized_pnl(self) -> Optional[float]:
        """
        Calculate unrealized profit/loss.

        Returns:
            Market value minus cost basis, or None if market value not available
        """
        if self.market_value is not None and self.total_invested != 0:
            return self.market_value - self.total_invested
        return None

    @property
    def unrealized_pnl_pct(self) -> Optional[float]:
        """
        Calculate unrealized profit/loss percentage.

        Returns:
            P&L as percentage of cost basis, or None if not calculable
        """
        pnl = self.unrealized_pnl
        if pnl is not None and self.total_invested != 0:
            return (pnl / self.total_invested) * 100
        return None

    @property
    def has_market_data(self) -> bool:
        """Check if position has current market data."""
        return self.current_price is not None and self.market_value is not None

    def __str__(self) -> str:
        """String representation of position."""
        base = f"{self.security_name}: {self.quantity:.2f} shares @ {self.currency}{self.average_cost:.2f}"
        if self.has_market_data:
            pnl = self.unrealized_pnl
            pnl_pct = self.unrealized_pnl_pct
            return f"{base} | Market: {self.currency}{self.market_value:,.2f} | P&L: {self.currency}{pnl:+,.2f} ({pnl_pct:+.1f}%)"
        return base

    def __repr__(self) -> str:
        """Developer representation."""
        return (f"Position(security_name='{self.security_name}', "
                f"symbol='{self.security_symbol}', qty={self.quantity:.2f}, "
                f"avg_cost={self.average_cost:.2f}, invested={self.total_invested:.2f}, "
                f"source='{self.source}')")

    def to_dict(self) -> dict:
        """Convert position to dictionary for export/display."""
        data = {
            'security_name': self.security_name,
            'security_symbol': self.security_symbol,
            'quantity': self.quantity,
            'average_cost': self.average_cost,
            'total_invested': self.total_invested,
            'currency': self.currency,
            'source': self.source,
        }

        # Add market data if available
        if self.has_market_data:
            data.update({
                'current_price': self.current_price,
                'market_value': self.market_value,
                'unrealized_pnl': self.unrealized_pnl,
                'unrealized_pnl_pct': self.unrealized_pnl_pct,
            })

        return data

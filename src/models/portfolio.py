"""
Portfolio data model.

This module defines the Portfolio model that contains a collection of transactions.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from src.models.transaction import Transaction


class PortfolioMetadata(BaseModel):
    """Metadata for the portfolio."""
    source_file: str
    bank: str
    import_timestamp: datetime
    total_transactions: int
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None


class Portfolio(BaseModel):
    """
    Represents a portfolio of transactions.
    
    Attributes:
        metadata: Portfolio metadata
        transactions: List of transactions
    """
    metadata: PortfolioMetadata
    transactions: List[Transaction]
    
    def to_dict(self) -> dict:
        """Convert portfolio to dictionary."""
        return {
            "metadata": {
                "source_file": self.metadata.source_file,
                "bank": self.metadata.bank,
                "import_timestamp": self.metadata.import_timestamp.isoformat(),
                "total_transactions": self.metadata.total_transactions,
                "date_range": {
                    "start": self.metadata.date_range_start.strftime('%Y-%m-%d') if self.metadata.date_range_start else None,
                    "end": self.metadata.date_range_end.strftime('%Y-%m-%d') if self.metadata.date_range_end else None
                }
            },
            "transactions": [t.to_dict() for t in self.transactions]
        }
    
    def get_total_income(self) -> float:
        """Calculate total income."""
        return sum(t.amount for t in self.transactions if t.is_income)
    
    def get_total_expenses(self) -> float:
        """Calculate total expenses."""
        return sum(t.amount for t in self.transactions if t.is_expense)
    
    def get_net_balance(self) -> float:
        """Calculate net balance."""
        return self.get_total_income() + self.get_total_expenses()
    
    def filter_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Transaction]:
        """Filter transactions by date range."""
        return [t for t in self.transactions if start_date <= t.date <= end_date]
    
    def filter_by_category(self, category: str) -> List[Transaction]:
        """Filter transactions by category."""
        return [t for t in self.transactions if t.category == category]

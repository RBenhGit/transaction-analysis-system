"""
Simple Data Models for Transaction Analysis System

Simplified version without Pydantic for initial testing.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class Transaction:
    """Standard transaction model."""
    date: Optional[date]
    description: str
    amount: Optional[Decimal]
    balance: Optional[Decimal]
    category: Optional[str]
    reference: Optional[str]
    bank: str
    account: Optional[str]


@dataclass
class TransactionMetadata:
    """Metadata about a set of transactions."""
    source_file: str
    import_date: datetime
    total_transactions: int
    date_range: Dict[str, Optional[date]]
    bank: str
    encoding: Optional[str] = None


@dataclass
class TransactionSet:
    """Complete set of transactions with metadata."""
    transactions: List[Transaction]
    metadata: TransactionMetadata

    def get_date_range(self) -> Dict[str, Optional[date]]:
        """Calculate actual date range from transactions."""
        if not self.transactions:
            return {'start': None, 'end': None}

        dates = [t.date for t in self.transactions if t.date]
        if not dates:
            return {'start': None, 'end': None}

        return {
            'start': min(dates),
            'end': max(dates)
        }

    def get_total_amount(self) -> Decimal:
        """Calculate total amount of all transactions."""
        return sum(t.amount for t in self.transactions if t.amount) or Decimal('0')


@dataclass
class ImportResult:
    """Result of an import operation."""
    success: bool
    transaction_set: Optional[TransactionSet] = None
    errors: List[str] = None
    warnings: List[str] = None
    processing_time: Optional[float] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)


@dataclass
class AdapterConfig:
    """Configuration for bank adapters."""
    bank_name: str
    column_mappings: Dict[str, str]
    date_format: str = "%d/%m/%Y"
    encoding: str = "utf-8"
    skip_rows: int = 0
    amount_columns: Optional[Dict[str, str]] = None
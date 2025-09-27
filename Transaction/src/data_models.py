"""
Data Models for Transaction Analysis System

This module defines the data models and schemas used throughout the transaction
analysis system using Pydantic for validation and type safety.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from decimal import Decimal

try:
    from pydantic import BaseModel, Field, field_validator, ConfigDict
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseModel, Field, validator as field_validator, Config as ConfigDict


class Transaction(BaseModel):
    """
    Standard transaction model used across all bank adapters.

    All transaction data is normalized to this format regardless of
    the source bank or file format.
    """
    date: date = Field(..., description="Transaction date")
    description: str = Field(..., description="Transaction description")
    amount: Decimal = Field(..., description="Transaction amount")
    balance: Optional[Decimal] = Field(None, description="Account balance after transaction")
    category: Optional[str] = Field(None, description="Transaction category")
    reference: Optional[str] = Field(None, description="Transaction reference number")
    bank: str = Field(..., description="Bank name/identifier")
    account: Optional[str] = Field(None, description="Account identifier")

    @field_validator('amount', 'balance', mode='before')
    @classmethod
    def convert_to_decimal(cls, v):
        """Convert numeric values to Decimal for precise financial calculations."""
        if v is None:
            return v
        try:
            return Decimal(str(v))
        except (ValueError, TypeError):
            raise ValueError(f"Invalid numeric value: {v}")

    @field_validator('description')
    @classmethod
    def clean_description(cls, v):
        """Clean and normalize transaction descriptions."""
        if v:
            return v.strip()
        return v

    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(v) if v is not None else None,
            date: lambda v: v.isoformat() if v is not None else None
        }
    )


class TransactionMetadata(BaseModel):
    """
    Metadata about a set of transactions imported from a file.
    """
    source_file: str = Field(..., description="Source file path")
    import_date: datetime = Field(default_factory=datetime.now, description="Import timestamp")
    total_transactions: int = Field(..., description="Total number of transactions")
    date_range: Dict[str, Optional[date]] = Field(..., description="Date range of transactions")
    bank: str = Field(..., description="Bank identifier")
    encoding: Optional[str] = Field(None, description="File encoding used")

    @field_validator('date_range')
    @classmethod
    def validate_date_range(cls, v):
        """Ensure date range has valid start and end dates."""
        if not isinstance(v, dict):
            raise ValueError("Date range must be a dictionary")

        required_keys = ['start', 'end']
        for key in required_keys:
            if key not in v:
                raise ValueError(f"Date range must contain '{key}' key")

        start_date = v.get('start')
        end_date = v.get('end')

        if start_date and end_date and start_date > end_date:
            raise ValueError("Start date cannot be after end date")

        return v


class TransactionSet(BaseModel):
    """
    Complete set of transactions with metadata.

    This is the main data structure returned by the import and processing system.
    """
    transactions: List[Transaction] = Field(..., description="List of transactions")
    metadata: TransactionMetadata = Field(..., description="Import metadata")

    @field_validator('transactions')
    @classmethod
    def validate_transactions(cls, v):
        """Validate transactions list."""
        # Simple validation - just ensure it's a list
        if not isinstance(v, list):
            raise ValueError("Transactions must be a list")
        return v

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
        return sum(t.amount for t in self.transactions)

    def get_transactions_by_date_range(self, start_date: date, end_date: date) -> List[Transaction]:
        """Filter transactions by date range."""
        return [
            t for t in self.transactions
            if t.date and start_date <= t.date <= end_date
        ]

    def get_transactions_by_amount_range(
        self,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None
    ) -> List[Transaction]:
        """Filter transactions by amount range."""
        filtered = self.transactions

        if min_amount is not None:
            filtered = [t for t in filtered if t.amount >= min_amount]

        if max_amount is not None:
            filtered = [t for t in filtered if t.amount <= max_amount]

        return filtered


class ImportResult(BaseModel):
    """
    Result of an import operation, including success status and any errors.
    """
    success: bool = Field(..., description="Whether import was successful")
    transaction_set: Optional[TransactionSet] = Field(None, description="Imported transactions")
    errors: List[str] = Field(default_factory=list, description="Import errors")
    warnings: List[str] = Field(default_factory=list, description="Import warnings")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)


class AdapterConfig(BaseModel):
    """
    Configuration for bank adapters.
    """
    bank_name: str = Field(..., description="Bank identifier")
    column_mappings: Dict[str, str] = Field(..., description="Column name mappings")
    date_format: str = Field(default="%d/%m/%Y", description="Date format string")
    encoding: str = Field(default="utf-8", description="File encoding")
    skip_rows: int = Field(default=0, description="Number of rows to skip")
    amount_columns: Optional[Dict[str, str]] = Field(None, description="Debit/credit column mapping")

    @field_validator('column_mappings')
    @classmethod
    def validate_required_columns(cls, v):
        """Ensure all required columns are mapped."""
        required_columns = ['date', 'description', 'amount']
        missing = [col for col in required_columns if col not in v]
        if missing:
            raise ValueError(f"Missing required column mappings: {missing}")
        return v
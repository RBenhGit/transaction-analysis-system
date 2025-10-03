"""
Transaction data model.

This module defines the Transaction model for securities trading transactions.
Supports complete IBI broker format with all 13 fields.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Transaction(BaseModel):
    """
    Represents a single securities trading transaction.

    Complete IBI broker format with 13 fields:
    - Date and transaction type
    - Security information (name, symbol)
    - Trade details (quantity, price, currency)
    - Fees and costs
    - Amounts in multiple currencies
    - Balance and tax estimates
    """
    # Core identification
    id: str = Field(default="", description="Unique transaction identifier")
    date: datetime = Field(description="Transaction date")

    # Transaction details
    transaction_type: str = Field(description="Type: Buy/Sell/Dividend/Tax/Fee")
    security_name: str = Field(description="Stock/Asset name")
    security_symbol: str = Field(description="Stock symbol or security number")

    # Trade execution
    quantity: float = Field(default=0.0, description="Number of shares/units")
    execution_price: float = Field(default=0.0, description="Price per share/unit")
    currency: str = Field(default="₪", description="Currency symbol")

    # Fees and costs
    transaction_fee: float = Field(default=0.0, description="Transaction commission")
    additional_fees: float = Field(default=0.0, description="Additional charges")

    # Amounts
    amount_foreign_currency: float = Field(default=0.0, description="Total in foreign currency")
    amount_local_currency: float = Field(default=0.0, description="Total in NIS")

    # Account status
    balance: float = Field(description="Account balance after transaction")
    capital_gains_tax_estimate: float = Field(default=0.0, description="Estimated capital gains tax")

    # Metadata
    bank: str = Field(default="IBI", description="Bank/Broker name")
    account: Optional[str] = Field(default="", description="Account number")
    category: Optional[str] = Field(default="other", description="Transaction category")

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d')
        }

    def to_dict(self) -> dict:
        """Convert transaction to dictionary with all fields."""
        return {
            "id": self.id,
            "date": self.date.strftime('%Y-%m-%d') if isinstance(self.date, datetime) else str(self.date),
            "transaction_type": self.transaction_type,
            "security_name": self.security_name,
            "security_symbol": self.security_symbol,
            "quantity": self.quantity,
            "execution_price": self.execution_price,
            "currency": self.currency,
            "transaction_fee": self.transaction_fee,
            "additional_fees": self.additional_fees,
            "amount_foreign_currency": self.amount_foreign_currency,
            "amount_local_currency": self.amount_local_currency,
            "balance": self.balance,
            "capital_gains_tax_estimate": self.capital_gains_tax_estimate,
            "bank": self.bank,
            "account": self.account,
            "category": self.category
        }

    @property
    def is_buy(self) -> bool:
        """Check if transaction is a buy order."""
        buy_types = ['קניה שח', 'קניה מטח', 'קניה חול מטח', 'קניה רצף', 'קניה מעוף', 'Buy']
        return any(buy_type in self.transaction_type for buy_type in buy_types)

    @property
    def is_sell(self) -> bool:
        """Check if transaction is a sell order."""
        sell_types = ['מכירה שח', 'מכירה מטח', 'מכירה חול מטח', 'מכירה רצף', 'מכירה מעוף', 'Sell']
        return any(sell_type in self.transaction_type for sell_type in sell_types)

    @property
    def is_dividend(self) -> bool:
        """Check if transaction is a dividend."""
        return 'דיבידנד' in self.transaction_type or 'Dividend' in self.transaction_type

    @property
    def is_fee(self) -> bool:
        """Check if transaction is a fee."""
        return 'עמלה' in self.transaction_type or 'Fee' in self.transaction_type or 'דמי' in self.transaction_type

    @property
    def is_tax(self) -> bool:
        """Check if transaction is tax-related."""
        return 'מס' in self.transaction_type or 'Tax' in self.transaction_type

    @property
    def total_cost(self) -> float:
        """Calculate total transaction cost including fees."""
        return abs(self.amount_local_currency) + self.transaction_fee + self.additional_fees

"""
Transaction data model.

This module defines the Transaction model for securities trading transactions.
Supports complete IBI broker format with all 13 fields.
"""

import logging
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from .transaction_classifier import ClassifierFactory, TransactionCategory

# Configure logging for transaction classification
logger = logging.getLogger(__name__)


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
    # Note: quantity can be negative in raw IBI data to represent sells (negative = selling)
    # The portfolio builder will use abs() when needed
    quantity: float = Field(default=0.0, description="Number of shares/units (can be negative for sells in IBI format)")
    execution_price: float = Field(default=0.0, ge=0.0, description="Price per share/unit (must be >= 0)")
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

    # Classifier Metadata (added by adapter)
    transaction_effect: Optional[str] = Field(default=None, description="Transaction effect from classifier (buy/sell/dividend/etc)")
    is_phantom: Optional[bool] = Field(default=False, description="Whether this is a phantom/accounting position")
    share_direction: Optional[str] = Field(default=None, description="Share movement direction (add/remove/none)")
    share_quantity_abs: Optional[float] = Field(default=None, description="Absolute share quantity")
    cost_basis: Optional[float] = Field(default=None, description="Calculated cost basis")

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d')
        }

    # ==================== VALIDATORS ====================

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """
        Validate currency is from allowed list.

        Allowed currencies:
        - '₪' (NIS shekel symbol)
        - '$' (USD dollar symbol)
        - 'USD' (explicit USD)
        - 'NIS' (explicit NIS)
        - 'ILS' (explicit ILS - Israeli shekel)

        Args:
            v: Currency string to validate

        Returns:
            Validated currency string

        Raises:
            ValueError: If currency not in allowed list
        """
        allowed_currencies = {'₪', '$', 'USD', 'NIS', 'ILS', ''}
        if v not in allowed_currencies:
            raise ValueError(
                f"Invalid currency '{v}'. Must be one of: {', '.join(sorted(allowed_currencies))}"
            )
        return v

    @field_validator('transaction_fee', 'additional_fees')
    @classmethod
    def validate_fees_non_negative(cls, v: float) -> float:
        """
        Validate that fees are non-negative.

        Fees should always be >= 0. Negative fees don't make sense.

        Args:
            v: Fee amount to validate

        Returns:
            Validated fee amount

        Raises:
            ValueError: If fee is negative
        """
        if v < 0:
            raise ValueError(f"Fee must be non-negative, got {v}")
        return v

    @field_validator('security_symbol')
    @classmethod
    def validate_security_symbol(cls, v: str) -> str:
        """
        Validate security symbol is not empty and reasonable length.

        Args:
            v: Security symbol to validate

        Returns:
            Validated and stripped security symbol

        Raises:
            ValueError: If symbol is empty or too long
        """
        v = v.strip()
        if not v:
            raise ValueError("Security symbol cannot be empty")
        if len(v) > 20:
            raise ValueError(f"Security symbol too long (max 20 chars): {v}")
        return v

    @field_validator('security_name')
    @classmethod
    def validate_security_name(cls, v: str) -> str:
        """
        Validate security name is not empty.

        Args:
            v: Security name to validate

        Returns:
            Validated and stripped security name

        Raises:
            ValueError: If name is empty
        """
        v = v.strip()
        if not v:
            raise ValueError("Security name cannot be empty")
        return v

    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v: str) -> str:
        """
        Validate transaction type is not empty.

        Args:
            v: Transaction type to validate

        Returns:
            Validated and stripped transaction type

        Raises:
            ValueError: If transaction type is empty
        """
        v = v.strip()
        if not v:
            raise ValueError("Transaction type cannot be empty")
        return v

    @model_validator(mode='after')
    def validate_transaction_logic(self) -> 'Transaction':
        """
        Cross-field validation for transaction logic.

        Validates:
        1. Buy transactions should have non-negative quantity (IBI format can have negative for sells)
        2. Buy/sell transactions should have positive execution price (with some exceptions)

        Returns:
            Validated transaction

        Note:
            This is a warning-level validator - logs issues but doesn't fail
            to maintain backwards compatibility with existing data.

            IBI data format uses:
            - Positive quantity for buys/deposits
            - Negative quantity for sells/withdrawals
            This is acceptable and expected behavior.
        """
        # Get classifier to check transaction type
        try:
            classifier = ClassifierFactory.get_classifier(self.bank)

            # Buy transactions should have positive quantity
            if classifier.is_buy(self.transaction_type):
                if self.quantity < 0:
                    logger.warning(
                        f"Buy transaction has negative quantity: {self.quantity} "
                        f"for {self.security_symbol} ({self.transaction_type})"
                    )

            # Sell transactions can have negative quantity in IBI format (that's normal)
            # No warning needed for negative quantity on sells

            # Buy/sell should typically have execution_price > 0
            # (except for some special cases like gifts, splits)
            if classifier.is_buy(self.transaction_type) or classifier.is_sell(self.transaction_type):
                if self.execution_price == 0:
                    logger.debug(
                        f"Buy/sell transaction has zero execution price for {self.security_symbol} "
                        f"({self.transaction_type}) - may be gift, split, or data issue"
                    )

        except Exception as e:
            # Don't fail validation if classifier fails
            logger.debug(f"Could not validate transaction logic: {e}")

        return self

    # ==================== END VALIDATORS ====================

    def _get_classifier(self):
        """Get appropriate classifier for this transaction's broker."""
        try:
            return ClassifierFactory.get_classifier(self.bank)
        except ValueError:
            # Fallback to IBI classifier if broker not found
            logger.warning(f"No classifier found for broker '{self.bank}', using IBI classifier")
            return ClassifierFactory.get_classifier('IBI')

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
        """
        Check if transaction is a buy order or deposit (adds to position).

        Uses broker-specific classifier for classification logic.

        Returns:
            True if transaction adds shares to position
        """
        classifier = self._get_classifier()
        return classifier.is_buy(self.transaction_type)

    @property
    def is_sell(self) -> bool:
        """
        Check if transaction is a sell order or withdrawal (reduces position).

        Uses broker-specific classifier for classification logic.

        Returns:
            True if transaction removes shares from position
        """
        classifier = self._get_classifier()
        return classifier.is_sell(self.transaction_type)

    @property
    def is_dividend(self) -> bool:
        """Check if transaction is a dividend payment."""
        classifier = self._get_classifier()
        return classifier.is_dividend(self.transaction_type)

    @property
    def is_fee(self) -> bool:
        """Check if transaction is a fee or handling charge."""
        classifier = self._get_classifier()
        return classifier.is_fee(self.transaction_type)

    @property
    def is_tax(self) -> bool:
        """Check if transaction is tax-related."""
        classifier = self._get_classifier()
        return classifier.is_tax(self.transaction_type)

    @property
    def is_interest(self) -> bool:
        """Check if transaction is interest payment."""
        classifier = self._get_classifier()
        return classifier.is_interest(self.transaction_type)

    @property
    def is_cash_transfer(self) -> bool:
        """Check if transaction is a cash transfer."""
        classifier = self._get_classifier()
        return classifier.is_cash_transfer(self.transaction_type)

    @property
    def transaction_category(self) -> str:
        """
        Categorize transaction into standard category.

        Returns one of:
        - 'buy': Purchase or deposit of shares
        - 'sell': Sale or withdrawal of shares
        - 'dividend': Dividend payment
        - 'tax': Tax payment
        - 'fee': Fee or commission
        - 'interest': Interest payment
        - 'transfer': Cash transfer
        - 'other': Unclassified transaction type
        """
        classifier = self._get_classifier()
        category = classifier.categorize(self.transaction_type)
        return category.value

    def get_classification_info(self) -> dict:
        """
        Get comprehensive classification information for debugging.

        Returns:
            Dictionary with all classification flags and category
        """
        classifier = self._get_classifier()
        return classifier.get_classification_info(self.transaction_type)

    def log_if_unclassified(self):
        """
        Log warning if transaction type is not properly classified.

        This helps identify transaction types that may need to be added
        to the classification logic.
        """
        category = self.transaction_category

        if category == 'other':
            logger.warning(
                f"Unclassified transaction type: '{self.transaction_type}' | "
                f"Security: {self.security_name} ({self.security_symbol}) | "
                f"Date: {self.date.strftime('%Y-%m-%d')} | "
                f"Quantity: {self.quantity} | "
                f"Amount (NIS): {self.amount_local_currency}"
            )
            return True
        return False

    @property
    def total_cost(self) -> float:
        """Calculate total transaction cost including fees."""
        return abs(self.amount_local_currency) + self.transaction_fee + self.additional_fees

"""
Portfolio Dashboard Error Handling Module.

Defines custom exception classes and error handling utilities for the portfolio
building process, providing clear error messages and error recovery strategies.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime


class PortfolioError(Exception):
    """Base exception for all portfolio-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/display."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class DataValidationError(PortfolioError):
    """Raised when transaction data fails validation checks."""
    pass


class TransactionProcessingError(PortfolioError):
    """Raised when a transaction cannot be processed."""
    pass


class PositionCalculationError(PortfolioError):
    """Raised when position calculations fail."""
    pass


class InsufficientSharesError(PortfolioError):
    """Raised when attempting to sell more shares than owned."""

    def __init__(
        self,
        symbol: str,
        available: float,
        requested: float,
        transaction_date: datetime
    ):
        message = (
            f"Cannot sell {requested} shares of {symbol}. "
            f"Only {available} shares available in position."
        )
        details = {
            "symbol": symbol,
            "available_shares": available,
            "requested_shares": requested,
            "transaction_date": transaction_date.strftime("%Y-%m-%d"),
            "shortfall": requested - available
        }
        super().__init__(message, details)


class NegativeQuantityError(DataValidationError):
    """Raised when a transaction has a negative quantity."""

    def __init__(self, transaction_id: str, quantity: float, transaction_type: str):
        message = (
            f"Transaction {transaction_id} has negative quantity: {quantity}. "
            f"Transaction type: {transaction_type}"
        )
        details = {
            "transaction_id": transaction_id,
            "quantity": quantity,
            "transaction_type": transaction_type
        }
        super().__init__(message, details)


class MissingRequiredFieldError(DataValidationError):
    """Raised when a required field is missing from transaction."""

    def __init__(self, transaction_id: str, field_name: str):
        message = f"Transaction {transaction_id} is missing required field: {field_name}"
        details = {
            "transaction_id": transaction_id,
            "missing_field": field_name
        }
        super().__init__(message, details)


class InvalidDateError(DataValidationError):
    """Raised when a transaction has an invalid date."""

    def __init__(self, transaction_id: str, date_value: Any):
        message = f"Transaction {transaction_id} has invalid date: {date_value}"
        details = {
            "transaction_id": transaction_id,
            "date_value": str(date_value)
        }
        super().__init__(message, details)


class CurrencyMismatchError(DataValidationError):
    """Raised when currency is inconsistent within a position."""

    def __init__(
        self,
        symbol: str,
        existing_currency: str,
        new_currency: str
    ):
        message = (
            f"Currency mismatch for {symbol}: "
            f"Position currency is {existing_currency}, "
            f"but transaction uses {new_currency}"
        )
        details = {
            "symbol": symbol,
            "existing_currency": existing_currency,
            "new_currency": new_currency
        }
        super().__init__(message, details)


class ErrorCollector:
    """
    Collects errors during portfolio building for batch reporting.

    Allows the portfolio builder to continue processing valid transactions
    while collecting errors for later review.
    """

    def __init__(self, fail_fast: bool = False):
        """
        Initialize error collector.

        Args:
            fail_fast: If True, raise first error immediately.
                      If False, collect all errors and continue processing.
        """
        self.fail_fast = fail_fast
        self.errors: List[PortfolioError] = []
        self.warnings: List[str] = []

    def add_error(self, error: PortfolioError):
        """
        Add an error to the collection.

        Args:
            error: The error to add

        Raises:
            PortfolioError: If fail_fast is True
        """
        if self.fail_fast:
            raise error
        self.errors.append(error)

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)

    def has_errors(self) -> bool:
        """Check if any errors were collected."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if any warnings were collected."""
        return len(self.warnings) > 0

    def get_error_count(self) -> int:
        """Get total number of errors."""
        return len(self.errors)

    def get_warning_count(self) -> int:
        """Get total number of warnings."""
        return len(self.warnings)

    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of all collected errors and warnings.

        Returns:
            Dictionary with error statistics and details
        """
        error_types = {}
        for error in self.errors:
            error_type = error.__class__.__name__
            error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            "total_errors": self.get_error_count(),
            "total_warnings": self.get_warning_count(),
            "error_types": error_types,
            "errors": [error.to_dict() for error in self.errors],
            "warnings": self.warnings
        }

    def clear(self):
        """Clear all collected errors and warnings."""
        self.errors.clear()
        self.warnings.clear()

    def raise_if_errors(self):
        """
        Raise an exception if any errors were collected.

        Raises:
            PortfolioError: If errors were collected
        """
        if self.has_errors():
            summary = self.get_error_summary()
            raise PortfolioError(
                f"Portfolio building failed with {summary['total_errors']} error(s)",
                details=summary
            )


def validate_transaction_data(transaction) -> List[str]:
    """
    Validate transaction data quality.

    Args:
        transaction: Transaction object to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check for negative quantities (should be positive for both buy/sell)
    if transaction.quantity < 0:
        errors.append(f"Negative quantity: {transaction.quantity}")

    # Check for missing required fields
    if not transaction.security_symbol:
        errors.append("Missing security symbol")

    if not transaction.security_name:
        errors.append("Missing security name")

    # Check date validity
    if not isinstance(transaction.date, datetime):
        errors.append(f"Invalid date type: {type(transaction.date)}")

    # Check currency validity
    valid_currencies = ["₪", "$", "€", "£"]
    if transaction.currency not in valid_currencies:
        errors.append(f"Invalid currency: {transaction.currency}")

    # Check for NaN or infinite values in numeric fields
    numeric_fields = [
        'quantity', 'execution_price', 'transaction_fee',
        'additional_fees', 'amount_foreign_currency',
        'amount_local_currency', 'balance'
    ]

    for field in numeric_fields:
        value = getattr(transaction, field, 0)
        if value is None or (isinstance(value, float) and (value != value or abs(value) == float('inf'))):
            errors.append(f"Invalid value for {field}: {value}")

    return errors

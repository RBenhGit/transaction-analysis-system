"""
Transaction Classification System.

Provides broker-specific transaction classification logic using strategy pattern.
Extracts classification logic from Transaction model for better separation of concerns.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum


class TransactionCategory(Enum):
    """Standard transaction categories."""
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    TAX = "tax"
    FEE = "fee"
    INTEREST = "interest"
    TRANSFER = "transfer"
    OTHER = "other"


class TransactionClassifier(ABC):
    """
    Abstract base class for transaction classification.

    Defines interface for broker-specific transaction type classification.
    Each broker (IBI, etc.) implements their own classification logic.
    """

    @abstractmethod
    def is_buy(self, transaction_type: str, **kwargs) -> bool:
        """Check if transaction is a buy/purchase."""
        pass

    @abstractmethod
    def is_sell(self, transaction_type: str, **kwargs) -> bool:
        """Check if transaction is a sell."""
        pass

    @abstractmethod
    def is_dividend(self, transaction_type: str, **kwargs) -> bool:
        """Check if transaction is a dividend payment."""
        pass

    @abstractmethod
    def is_fee(self, transaction_type: str, **kwargs) -> bool:
        """Check if transaction is a fee or commission."""
        pass

    @abstractmethod
    def is_tax(self, transaction_type: str, **kwargs) -> bool:
        """Check if transaction is tax-related."""
        pass

    @abstractmethod
    def is_interest(self, transaction_type: str, **kwargs) -> bool:
        """Check if transaction is interest payment."""
        pass

    @abstractmethod
    def is_cash_transfer(self, transaction_type: str, **kwargs) -> bool:
        """Check if transaction is a cash transfer."""
        pass

    def categorize(self, transaction_type: str, **kwargs) -> TransactionCategory:
        """
        Categorize transaction into standard category.

        Args:
            transaction_type: Transaction type string
            **kwargs: Additional context (e.g., security_symbol, quantity)

        Returns:
            TransactionCategory enum value
        """
        if self.is_buy(transaction_type, **kwargs):
            return TransactionCategory.BUY
        elif self.is_sell(transaction_type, **kwargs):
            return TransactionCategory.SELL
        elif self.is_dividend(transaction_type, **kwargs):
            return TransactionCategory.DIVIDEND
        elif self.is_tax(transaction_type, **kwargs):
            return TransactionCategory.TAX
        elif self.is_fee(transaction_type, **kwargs):
            return TransactionCategory.FEE
        elif self.is_interest(transaction_type, **kwargs):
            return TransactionCategory.INTEREST
        elif self.is_cash_transfer(transaction_type, **kwargs):
            return TransactionCategory.TRANSFER
        else:
            return TransactionCategory.OTHER

    def get_classification_info(self, transaction_type: str, **kwargs) -> Dict[str, Any]:
        """
        Get comprehensive classification information.

        Args:
            transaction_type: Transaction type string
            **kwargs: Additional context

        Returns:
            Dictionary with all classification flags and category
        """
        return {
            'transaction_type': transaction_type,
            'category': self.categorize(transaction_type, **kwargs).value,
            'is_buy': self.is_buy(transaction_type, **kwargs),
            'is_sell': self.is_sell(transaction_type, **kwargs),
            'is_dividend': self.is_dividend(transaction_type, **kwargs),
            'is_tax': self.is_tax(transaction_type, **kwargs),
            'is_fee': self.is_fee(transaction_type, **kwargs),
            'is_interest': self.is_interest(transaction_type, **kwargs),
            'is_cash_transfer': self.is_cash_transfer(transaction_type, **kwargs)
        }


class IBITransactionClassifier(TransactionClassifier):
    """
    IBI Broker transaction classification logic.

    Implements classification for IBI securities trading account transactions.
    Handles Hebrew transaction types and IBI-specific patterns.
    """

    def is_buy(self, transaction_type: str, **kwargs) -> bool:
        """
        Check if transaction is a buy order or deposit (adds to position).

        Handles all IBI transaction types that add shares to portfolio:
        - Regular purchases (קניה)
        - Deposits (הפקדה) - shares transferred in
        - Benefits/bonuses (הטבה)
        - Stock splits (if implemented)

        Excludes:
        - Dividend deposits (cash, not shares)
        - Tax withdrawals (cash only)
        - Interest payments (cash only)
        """
        trans_type = transaction_type.strip()

        # Explicitly exclude dividend deposits and cash transactions
        # These are cash flows, not share additions
        exclude_types = [
            'דיבידנד',        # Dividend (cash)
            'דיב',             # Dividend abbreviation
            'משיכת מס',       # Tax withdrawal (cash)
            'ריבית',          # Interest (cash)
            'העברה מזומן',    # Cash transfer
            'דמי טפול'        # Handling fee
        ]

        if any(exclude in trans_type for exclude in exclude_types):
            return False

        # Buy transactions - add shares to position
        buy_types = [
            # Regular purchases (all variations)
            'קניה שח',        # NIS buy
            'קניה מטח',       # Foreign currency buy
            'קניה חול מטח',   # Foreign currency buy (abroad)
            'קניה רצף',       # Continuous buy
            'קניה מעוף',      # Immediate execution buy

            # Deposits - shares transferred into account
            'הפקדה',          # Deposit (general)
            'הפקדה פקיעה',    # Expiration deposit (e.g., option exercise)

            # Benefits/bonuses - shares received as benefit
            'הטבה',           # Benefit/bonus shares

            # Stock splits and dividends (if they add shares, not cash)
            'פיצול',          # Stock split
            'דיבידנד מניות',  # Stock dividend (shares, not cash)

            # English equivalents
            'Buy', 'Deposit', 'Benefit', 'Split'
        ]

        return any(buy_type in trans_type for buy_type in buy_types)

    def is_sell(self, transaction_type: str, **kwargs) -> bool:
        """
        Check if transaction is a sell order or withdrawal (reduces position).

        Handles all IBI transaction types that remove shares from portfolio:
        - Regular sales (מכירה)
        - Withdrawals (משיכה) - shares transferred out
        - Expiration withdrawals (option expiration, etc.)

        Excludes:
        - Tax withdrawals (cash, not shares)
        - Dividend payments (cash only)
        - Interest withdrawals (cash only)
        - Cash transfers and fees
        """
        trans_type = transaction_type.strip()

        # Explicitly exclude cash-only transactions
        # These withdraw cash but don't remove shares
        exclude_types = [
            'דיבידנד',        # Dividend (cash)
            'דיב',             # Dividend abbreviation
            'משיכת מס',       # Tax withdrawal (cash only)
            'משיכת ריבית',    # Interest withdrawal (cash)
            'העברה מזומן',    # Cash transfer
            'דמי טפול',       # Handling fee
            'ריבית מזומן'     # Cash interest
        ]

        if any(exclude in trans_type for exclude in exclude_types):
            return False

        # Sell transactions - remove shares from position
        sell_types = [
            # Regular sales (all variations)
            'מכירה שח',       # NIS sell
            'מכירה מטח',      # Foreign currency sell
            'מכירה חול מטח',  # Foreign currency sell (abroad)
            'מכירה רצף',      # Continuous sell
            'מכירה מעוף',     # Immediate execution sell

            # Withdrawals - shares transferred out of account
            'משיכה',          # Withdrawal (general)
            'משיכה פקיעה',    # Expiration withdrawal

            # English equivalents
            'Sell', 'Withdrawal'
        ]

        return any(sell_type in trans_type for sell_type in sell_types)

    def is_dividend(self, transaction_type: str, **kwargs) -> bool:
        """
        Check if transaction is a dividend payment (cash).

        Includes:
        - Regular dividends
        - Dividend deposits in foreign currency
        """
        trans_type = transaction_type.strip()
        dividend_types = [
            'דיבידנד',                 # Dividend (general)
            'דיב',                      # Dividend abbreviation
            'הפקדה דיבידנד',          # Dividend deposit
            'Dividend'                  # English
        ]
        return any(div_type in trans_type for div_type in dividend_types)

    def is_fee(self, transaction_type: str, **kwargs) -> bool:
        """
        Check if transaction is a fee or handling charge.

        Includes:
        - Transaction fees (עמלה)
        - Handling fees (דמי טפול)
        """
        trans_type = transaction_type.strip()
        fee_types = [
            'עמלה',            # Fee/commission
            'דמי טפול',        # Handling fee
            'דמי ניהול',       # Management fee
            'Fee'              # English
        ]
        return any(fee_type in trans_type for fee_type in fee_types)

    def is_tax(self, transaction_type: str, **kwargs) -> bool:
        """
        Check if transaction is tax-related.

        Includes:
        - Tax withdrawals (משיכת מס)
        - Tax payments
        - Capital gains tax
        """
        trans_type = transaction_type.strip()
        tax_types = [
            'משיכת מס',       # Tax withdrawal (check this first - more specific)
            'Tax'              # English
        ]
        # Check for tax patterns
        return any(tax_type in trans_type for tax_type in tax_types)

    def is_interest(self, transaction_type: str, **kwargs) -> bool:
        """
        Check if transaction is interest payment.

        Includes:
        - Interest on cash balances
        - Interest withdrawals
        """
        trans_type = transaction_type.strip()
        interest_types = [
            'ריבית',           # Interest
            'משיכת ריבית',    # Interest withdrawal
            'Interest'         # English
        ]
        return any(int_type in trans_type for int_type in interest_types)

    def is_cash_transfer(self, transaction_type: str, **kwargs) -> bool:
        """
        Check if transaction is a cash transfer.

        Includes:
        - Cash deposits
        - Cash withdrawals
        - Internal transfers
        """
        trans_type = transaction_type.strip()
        transfer_types = [
            'העברה מזומן',     # Cash transfer
            'העברה',           # Transfer (general)
            'Transfer'         # English
        ]
        return any(transfer_type in trans_type for transfer_type in transfer_types)


class ClassifierFactory:
    """
    Factory for creating appropriate transaction classifier based on broker.
    """

    _classifiers: Dict[str, type] = {
        'IBI': IBITransactionClassifier,
        'ibi': IBITransactionClassifier,
    }

    @classmethod
    def get_classifier(cls, broker: str) -> TransactionClassifier:
        """
        Get classifier instance for specified broker.

        Args:
            broker: Broker name (e.g., 'IBI', 'ibi')

        Returns:
            TransactionClassifier instance

        Raises:
            ValueError: If broker not supported
        """
        classifier_class = cls._classifiers.get(broker)

        if not classifier_class:
            raise ValueError(
                f"No classifier found for broker: {broker}. "
                f"Supported brokers: {list(cls._classifiers.keys())}"
            )

        return classifier_class()

    @classmethod
    def register_classifier(cls, broker: str, classifier_class: type):
        """
        Register a new classifier for a broker.

        Args:
            broker: Broker name
            classifier_class: Classifier class (must inherit from TransactionClassifier)
        """
        if not issubclass(classifier_class, TransactionClassifier):
            raise TypeError(
                f"Classifier must inherit from TransactionClassifier, "
                f"got {classifier_class}"
            )

        cls._classifiers[broker] = classifier_class

    @classmethod
    def get_supported_brokers(cls) -> list:
        """Get list of supported broker names."""
        return list(cls._classifiers.keys())

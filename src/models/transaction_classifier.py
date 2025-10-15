"""
Transaction Classification System.

Provides broker-specific transaction classification logic using strategy pattern.
Extracts classification logic from Transaction model for better separation of concerns.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
from enum import Enum
import pandas as pd


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


class TransactionEffect(Enum):
    """
    Standard transaction effects across all brokers.

    Each broker's transaction types map to these standardized effects.
    Used for portfolio calculation and position management.
    """
    # Share transactions
    BUY = "buy"                    # Adds shares, money out
    SELL = "sell"                  # Removes shares, money in

    # Share transfers
    DEPOSIT = "deposit"            # Adds shares, no money (transfer in)
    WITHDRAWAL = "withdrawal"      # Removes shares, no money (transfer out)

    # Income
    DIVIDEND = "dividend"          # No shares, money in
    INTEREST = "interest"          # No shares, money out/in

    # Costs
    TAX = "tax"                    # Creates liability, money out
    FEE = "fee"                    # No shares, money out

    # Cash operations
    TRANSFER = "transfer"          # Cash only movement

    # Special events
    BONUS = "bonus"                # Free shares (stock bonus, RSUs)
    OPTION_EXERCISE = "option_exercise"
    STOCK_SPLIT = "stock_split"
    MERGER = "merger"

    # Unknown
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

    @abstractmethod
    def get_transaction_mapping(self) -> Dict[str, TransactionEffect]:
        """
        Return mapping of broker transaction types to standardized effects.

        Returns:
            Dict[broker_transaction_type, TransactionEffect]

        Example:
            {
                'קניה שח': TransactionEffect.BUY,
                'מכירה שח': TransactionEffect.SELL,
                'דיבידנד': TransactionEffect.DIVIDEND,
            }
        """
        pass

    @abstractmethod
    def is_phantom_position(self, row: pd.Series) -> bool:
        """
        Determine if transaction creates a phantom (non-real) position.

        Phantom positions are broker internal tracking entries that should
        NOT be counted as actual holdings.

        Examples:
        - IBI tax entries (symbols starting with "999", names like "מס לשלם")
        - Broker internal accounting entries
        - Future tax liabilities

        Args:
            row: Transaction row with all fields

        Returns:
            True if this is a phantom position (exclude from portfolio)
            False if this is a real holding
        """
        pass

    @abstractmethod
    def get_share_effect(self, row: pd.Series) -> Tuple[str, float]:
        """
        Calculate net share effect considering broker quirks.

        This method handles broker-specific quirks like:
        - IBI: Sells show positive quantities (need to reverse)
        - Other brokers: Sells show negative quantities (use as-is)

        Args:
            row: Transaction row with all fields

        Returns:
            Tuple of (direction: "add"|"remove"|"none", quantity: float)

        Example - IBI sell quirk:
            - Transaction type = "מכירה שח"
            - Quantity = +10.5 (positive in IBI!)
            - Returns: ("remove", 10.5)

        Example - Normal broker:
            - Transaction type = "Sell"
            - Quantity = -10.5 (negative normally)
            - Returns: ("remove", 10.5)
        """
        pass

    @abstractmethod
    def get_cost_basis(self, row: pd.Series) -> float:
        """
        Calculate cost basis for this transaction.

        Handles special cases:
        - Regular purchases: use amount_local_currency or amount_foreign_currency
        - Deposits (no cash): use execution_price × quantity
        - Bonuses (free): return 0.0

        Args:
            row: Transaction row with all fields

        Returns:
            Cost basis in the transaction's currency
        """
        pass

    def classify_transaction(self, row: pd.Series) -> TransactionEffect:
        """
        Classify transaction based on type string.

        Default implementation using mapping, can be overridden for complex logic.

        Args:
            row: Transaction row with all fields

        Returns:
            TransactionEffect enum value
        """
        txn_type = row.get('transaction_type', '')
        mapping = self.get_transaction_mapping()

        # Try direct match
        if txn_type in mapping:
            return mapping[txn_type]

        # Try partial match
        for broker_type, effect in mapping.items():
            if broker_type in txn_type:
                return effect

        return TransactionEffect.OTHER


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

    def get_transaction_mapping(self) -> Dict[str, TransactionEffect]:
        """
        Complete IBI transaction type mapping.

        Based on analysis of 1,931 transactions (2022-2025).
        All 21 transaction types mapped.
        """
        return {
            # Purchases (קניות) - 442 transactions
            'קניה שח': TransactionEffect.BUY,
            'קניה רצף': TransactionEffect.BUY,
            'קניה חול מטח': TransactionEffect.BUY,
            'קניה מעוף': TransactionEffect.BUY,

            # Sales (מכירות) - 253 transactions
            # ⚠️ IBI QUIRK: Positive quantities!
            'מכירה שח': TransactionEffect.SELL,
            'מכירה רצף': TransactionEffect.SELL,
            'מכירה חול מטח': TransactionEffect.SELL,
            'מכירה מעוף': TransactionEffect.SELL,

            # Deposits (הפקדות) - 627 transactions
            'הפקדה': TransactionEffect.DEPOSIT,
            'הפקדה דיבידנד מטח': TransactionEffect.DIVIDEND,  # Special: dividend reinvested as shares
            'הפקדה פקיעה': TransactionEffect.DEPOSIT,

            # Withdrawals (משיכות) - 211 transactions
            # ⚠️ IBI QUIRK: Positive quantities, many are tax entries!
            'משיכה': TransactionEffect.WITHDRAWAL,
            'משיכה פקיעה': TransactionEffect.WITHDRAWAL,

            # Income (הכנסות) - 83 transactions
            'דיבדנד': TransactionEffect.DIVIDEND,
            'ריבית מזומן בשח': TransactionEffect.INTEREST,

            # Taxes (מסים) - 254 transactions
            # ⚠️ PHANTOM POSITIONS: Should be excluded from portfolio
            'משיכת מס חול מטח': TransactionEffect.TAX,
            'משיכת מס מטח': TransactionEffect.TAX,
            'משיכת ריבית מטח': TransactionEffect.TAX,

            # Transfers & Fees (העברות ודמי ניהול) - 61 transactions
            'העברה מזומן בשח': TransactionEffect.TRANSFER,
            'הטבה': TransactionEffect.BONUS,
            'דמי טפול מזומן בשח': TransactionEffect.FEE,
        }

    def is_phantom_position(self, row: pd.Series) -> bool:
        """
        Identify IBI phantom positions (tax tracking entries).

        IBI creates fake positions for:
        1. Tax withholding: symbol starts with "999"
        2. Future tax liability: security_name = "מס עתידי", "מס לשלם"
        3. Tax credits: security_name = "זיכוי מס", "מס תקבולים"
        4. Interest charges: security_name = "ריבית חובה מט\"ח"

        Found in data:
        - 216 transactions: משיכת מס חול מטח (foreign dividend tax)
        - 28 transactions: משיכת מס מטח (foreign capital gains tax)
        - 10 transactions: משיכת ריבית מטח (foreign interest charges)
        - Many משיכה transactions with tax-related names

        Returns:
            True if this should be excluded from portfolio calculations
        """
        symbol = str(row.get('security_symbol', '')).strip()
        name = str(row.get('security_name', '')).strip()
        txn_type = str(row.get('transaction_type', '')).strip()

        # Check 1: Symbol prefix (IBI standard for tax entries)
        if symbol.startswith('999'):
            return True

        # Check 2: Security name contains tax keywords
        tax_keywords = [
            'מס לשלם',      # Tax to be paid
            'מס עתידי',     # Future tax
            'מס ששולם',     # Tax paid
            'זיכוי מס',     # Tax credit
            'מס תקבולים',   # Tax receivable
            'ריבית חובה',   # Interest debt
            'מסח/',          # Tax prefix (e.g., "מסח/ QYLD US")
            'מס/',           # Tax prefix (e.g., "מס/ GOGL US")
        ]

        for keyword in tax_keywords:
            if keyword in name:
                return True

        # Check 3: Transaction type is tax-related
        # These ALWAYS create phantom positions
        if txn_type in ['משיכת מס חול מטח', 'משיכת מס מטח', 'משיכת ריבית מטח']:
            return True

        return False

    def get_share_effect(self, row: pd.Series) -> Tuple[str, float]:
        """
        Calculate share effect handling IBI's positive-quantity-on-sell quirk.

        IBI QUIRK: Sells and withdrawals show POSITIVE quantities!

        Evidence from 1,931 transactions:
        - מכירה חול מטח: 82 transactions, ALL positive (avg +28.52)
        - מכירה רצף: 22 transactions, ALL positive (avg +714.59)
        - מכירה שח: 44 transactions, ALL positive (avg +647.88)
        - מכירה מעוף: 105 transactions, ALL positive (avg +2.47)
        - משיכה: 209 transactions, ALL positive (avg +217.06)

        We need to reverse the sign based on transaction effect.
        """
        quantity = float(row.get('quantity', 0))
        effect = self.classify_transaction(row)

        # Determine direction based on effect
        if effect in [TransactionEffect.BUY, TransactionEffect.DEPOSIT, TransactionEffect.BONUS]:
            direction = "add"
            # Quantity is already positive and correct

        elif effect in [TransactionEffect.SELL, TransactionEffect.WITHDRAWAL]:
            direction = "remove"
            # ⚠️ IBI QUIRK: Quantity is POSITIVE but should remove shares!
            # We return positive quantity, and builder.py will handle removal

        else:
            # No share impact (dividends, fees, taxes, transfers)
            direction = "none"
            quantity = 0

        return (direction, abs(quantity))

    def get_cost_basis(self, row: pd.Series) -> float:
        """
        Calculate cost basis for IBI transaction.

        IBI has special cases:
        1. Regular purchases: use amount_local_currency or amount_foreign_currency
        2. Deposits (הפקדה): amount is 0.00, use execution_price × quantity
        3. Foreign transactions: use amount_foreign_currency (amount_local is 0.00)
        4. Bonuses: return 0.0 (free shares)

        Evidence from data:
        - הפקדה: 337 transactions, ALL show amount = 0.00
        - קניה חול מטח: 234 transactions, amount_local = 0.00, amount_foreign ≠ 0
        - הטבה: 6 transactions, both amounts = 0.00
        """
        txn_type = row.get('transaction_type', '')
        currency = row.get('currency', '₪')
        quantity = float(row.get('quantity', 0))
        execution_price = float(row.get('execution_price', 0))
        amount_local = float(row.get('amount_local_currency', 0))
        amount_foreign = float(row.get('amount_foreign_currency', 0))

        # Case 1: Bonuses (free shares)
        if 'הטבה' in txn_type:
            return 0.0

        # Case 2: Deposits (no cash, use market price)
        # IBI methodology: deposits are valued at execution_price at transfer time
        if 'הפקדה' in txn_type and 'דיבידנד' not in txn_type:
            if currency == "₪":
                # NIS: execution_price is in agorot, convert to shekels
                return quantity * (execution_price / 100.0)
            else:
                # USD: execution_price is in dollars
                return quantity * execution_price

        # Case 3: Regular transactions - use actual amounts
        if currency == "₪":
            # NIS transactions: use amount_local_currency
            return abs(amount_local)
        else:
            # Foreign transactions: use amount_foreign_currency
            # (amount_local will be 0.00 for these)
            return abs(amount_foreign)


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

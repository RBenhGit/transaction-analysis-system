"""
Unit tests for Transaction classification logic.

Tests all IBI transaction types to ensure proper classification
for portfolio calculations.
"""

import pytest
from datetime import datetime
from src.models.transaction import Transaction


class TestBuyClassification:
    """Test buy transaction classification."""

    def test_regular_buy_nis(self):
        """Test regular NIS stock purchase."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="קניה שח",
            security_name="Apple Inc",
            security_symbol="AAPL",
            quantity=10.0,
            execution_price=150.0,
            currency="$",
            amount_local_currency=-5500.0,
            balance=45000.0
        )
        assert tx.is_buy is True
        assert tx.is_sell is False
        assert tx.transaction_category == 'buy'

    def test_foreign_currency_buy(self):
        """Test foreign currency stock purchase."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="קניה חול מטח",
            security_name="Microsoft Corp",
            security_symbol="MSFT",
            quantity=5.0,
            execution_price=300.0,
            currency="$",
            amount_foreign_currency=-1500.0,
            balance=43500.0
        )
        assert tx.is_buy is True
        assert tx.transaction_category == 'buy'

    def test_continuous_buy(self):
        """Test continuous trading buy."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="קניה רצף",
            security_name="Tesla Inc",
            security_symbol="TSLA",
            quantity=3.0,
            execution_price=250.0,
            currency="$",
            amount_foreign_currency=-750.0,
            balance=42750.0
        )
        assert tx.is_buy is True
        assert tx.transaction_category == 'buy'

    def test_immediate_buy(self):
        """Test immediate execution buy (מעוף)."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="קניה מעוף",
            security_name="NVIDIA Corp",
            security_symbol="NVDA",
            quantity=2.0,
            execution_price=450.0,
            currency="$",
            amount_foreign_currency=-900.0,
            balance=41850.0
        )
        assert tx.is_buy is True
        assert tx.transaction_category == 'buy'

    def test_deposit(self):
        """Test share deposit (shares transferred in)."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="הפקדה",
            security_name="Bank Hapoalim",
            security_symbol="POLI",
            quantity=100.0,
            execution_price=950.0,
            currency="₪",
            amount_local_currency=0.0,
            balance=41850.0
        )
        assert tx.is_buy is True
        assert tx.transaction_category == 'buy'

    def test_expiration_deposit(self):
        """Test expiration deposit (e.g., option exercise)."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="הפקדה פקיעה",
            security_name="Some Stock",
            security_symbol="SOME",
            quantity=50.0,
            execution_price=100.0,
            currency="₪",
            amount_local_currency=0.0,
            balance=41850.0
        )
        assert tx.is_buy is True
        assert tx.transaction_category == 'buy'

    def test_benefit_shares(self):
        """Test benefit/bonus shares."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="הטבה",
            security_name="Employee Stock",
            security_symbol="EMPL",
            quantity=10.0,
            execution_price=50.0,
            currency="₪",
            amount_local_currency=0.0,
            balance=41850.0
        )
        assert tx.is_buy is True
        assert tx.transaction_category == 'buy'

    def test_dividend_deposit_not_buy(self):
        """Test that dividend deposits are NOT classified as buy."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="הפקדה דיבידנד מטח",
            security_name="Apple Inc",
            security_symbol="AAPL",
            quantity=0.0,
            execution_price=0.0,
            currency="$",
            amount_foreign_currency=50.0,
            balance=42000.0
        )
        assert tx.is_buy is False
        assert tx.is_dividend is True
        assert tx.transaction_category == 'dividend'


class TestSellClassification:
    """Test sell transaction classification."""

    def test_regular_sell_nis(self):
        """Test regular NIS stock sale."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="מכירה שח",
            security_name="Bank Leumi",
            security_symbol="LUMI",
            quantity=50.0,
            execution_price=800.0,
            currency="₪",
            amount_local_currency=40000.0,
            balance=82000.0
        )
        assert tx.is_sell is True
        assert tx.is_buy is False
        assert tx.transaction_category == 'sell'

    def test_foreign_currency_sell(self):
        """Test foreign currency stock sale."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="מכירה חול מטח",
            security_name="Tesla Inc",
            security_symbol="TSLA",
            quantity=3.0,
            execution_price=260.0,
            currency="$",
            amount_foreign_currency=780.0,
            balance=85000.0
        )
        assert tx.is_sell is True
        assert tx.transaction_category == 'sell'

    def test_continuous_sell(self):
        """Test continuous trading sell."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="מכירה רצף",
            security_name="Microsoft Corp",
            security_symbol="MSFT",
            quantity=5.0,
            execution_price=310.0,
            currency="$",
            amount_foreign_currency=1550.0,
            balance=90000.0
        )
        assert tx.is_sell is True
        assert tx.transaction_category == 'sell'

    def test_immediate_sell(self):
        """Test immediate execution sell (מעוף)."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="מכירה מעוף",
            security_name="Apple Inc",
            security_symbol="AAPL",
            quantity=10.0,
            execution_price=160.0,
            currency="$",
            amount_foreign_currency=1600.0,
            balance=96000.0
        )
        assert tx.is_sell is True
        assert tx.transaction_category == 'sell'

    def test_withdrawal(self):
        """Test share withdrawal (shares transferred out)."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="משיכה",
            security_name="Some Stock",
            security_symbol="SOME",
            quantity=25.0,
            execution_price=100.0,
            currency="₪",
            amount_local_currency=0.0,
            balance=96000.0
        )
        assert tx.is_sell is True
        assert tx.transaction_category == 'sell'

    def test_expiration_withdrawal(self):
        """Test expiration withdrawal."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="משיכה פקיעה",
            security_name="Option Stock",
            security_symbol="OPT",
            quantity=10.0,
            execution_price=50.0,
            currency="₪",
            amount_local_currency=0.0,
            balance=96000.0
        )
        assert tx.is_sell is True
        assert tx.transaction_category == 'sell'

    def test_tax_withdrawal_not_sell(self):
        """Test that tax withdrawals are NOT classified as sell."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="משיכת מס חול מטח",
            security_name="מס ששולם",
            security_symbol="9993983",
            quantity=0.0,
            execution_price=0.0,
            currency="$",
            amount_foreign_currency=-50.0,
            balance=95800.0
        )
        assert tx.is_sell is False
        assert tx.is_tax is True
        assert tx.transaction_category == 'tax'


class TestDividendClassification:
    """Test dividend transaction classification."""

    def test_dividend(self):
        """Test regular dividend."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="דיבדנד",
            security_name="Apple Inc",
            security_symbol="AAPL",
            quantity=0.0,
            execution_price=0.0,
            currency="$",
            amount_foreign_currency=25.0,
            balance=95900.0
        )
        assert tx.is_dividend is True
        assert tx.is_buy is False
        assert tx.is_sell is False
        assert tx.transaction_category == 'dividend'

    def test_foreign_currency_dividend_deposit(self):
        """Test foreign currency dividend deposit."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="הפקדה דיבידנד מטח",
            security_name="Microsoft Corp",
            security_symbol="MSFT",
            quantity=0.0,
            execution_price=0.0,
            currency="$",
            amount_foreign_currency=30.0,
            balance=96000.0
        )
        assert tx.is_dividend is True
        assert tx.is_buy is False
        assert tx.transaction_category == 'dividend'


class TestTaxClassification:
    """Test tax transaction classification."""

    def test_foreign_currency_tax_withdrawal(self):
        """Test foreign currency tax withdrawal."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="משיכת מס חול מטח",
            security_name="מס ששולם",
            security_symbol="9993983",
            quantity=0.0,
            execution_price=0.0,
            currency="$",
            amount_foreign_currency=-50.0,
            balance=95800.0
        )
        assert tx.is_tax is True
        assert tx.is_sell is False
        assert tx.transaction_category == 'tax'

    def test_tax_withdrawal(self):
        """Test general tax withdrawal."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="משיכת מס מטח",
            security_name="מס ששולם",
            security_symbol="9993984",
            quantity=0.0,
            execution_price=0.0,
            currency="$",
            amount_foreign_currency=-25.0,
            balance=95700.0
        )
        assert tx.is_tax is True
        assert tx.transaction_category == 'tax'


class TestInterestClassification:
    """Test interest transaction classification."""

    def test_cash_interest_nis(self):
        """Test NIS cash interest."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="ריבית מזומן בשח",
            security_name="ריבית",
            security_symbol="INTEREST",
            quantity=0.0,
            execution_price=0.0,
            currency="₪",
            amount_local_currency=15.0,
            balance=95715.0
        )
        assert tx.is_interest is True
        assert tx.is_buy is False
        assert tx.transaction_category == 'interest'

    def test_interest_withdrawal(self):
        """Test interest withdrawal."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="משיכת ריבית מטח",
            security_name="Interest",
            security_symbol="INT",
            quantity=0.0,
            execution_price=0.0,
            currency="$",
            amount_foreign_currency=-10.0,
            balance=95680.0
        )
        assert tx.is_interest is True
        assert tx.transaction_category == 'interest'


class TestCashTransferClassification:
    """Test cash transfer classification."""

    def test_cash_transfer_nis(self):
        """Test NIS cash transfer."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="העברה מזומן בשח",
            security_name="העברה",
            security_symbol="TRANSFER",
            quantity=0.0,
            execution_price=0.0,
            currency="₪",
            amount_local_currency=1000.0,
            balance=96680.0
        )
        assert tx.is_cash_transfer is True
        assert tx.is_buy is False
        assert tx.transaction_category == 'transfer'


class TestFeeClassification:
    """Test fee transaction classification."""

    def test_handling_fee(self):
        """Test handling fee."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="דמי טפול מזומן בשח",
            security_name="דמי טפול",
            security_symbol="FEE",
            quantity=0.0,
            execution_price=0.0,
            currency="₪",
            amount_local_currency=-10.0,
            balance=96670.0
        )
        assert tx.is_fee is True
        assert tx.is_buy is False
        assert tx.transaction_category == 'fee'


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_zero_quantity_transaction(self):
        """Test transaction with zero quantity (cash-only)."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="העברה מזומן בשח",
            security_name="Cash",
            security_symbol="CASH",
            quantity=0.0,
            execution_price=0.0,
            currency="₪",
            amount_local_currency=500.0,
            balance=97170.0
        )
        assert tx.is_buy is False
        assert tx.is_sell is False
        assert tx.is_cash_transfer is True

    def test_phantom_security_number(self):
        """Test transaction with phantom security (999xxxx series)."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="משיכת מס חול מטח",
            security_name="מס ששולם",
            security_symbol="9993983",
            quantity=0.0,
            execution_price=0.0,
            currency="$",
            amount_foreign_currency=-50.0,
            balance=95800.0
        )
        # Should be classified as tax, not buy/sell
        assert tx.is_tax is True
        assert tx.is_buy is False
        assert tx.is_sell is False

    def test_classification_info(self):
        """Test get_classification_info method."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="קניה שח",
            security_name="Apple Inc",
            security_symbol="AAPL",
            quantity=10.0,
            execution_price=150.0,
            currency="$",
            amount_local_currency=-5500.0,
            balance=45000.0
        )

        info = tx.get_classification_info()

        assert info['transaction_type'] == 'קניה שח'
        assert info['category'] == 'buy'
        assert info['is_buy'] is True
        assert info['is_sell'] is False
        assert info['is_dividend'] is False
        assert info['is_tax'] is False
        assert info['is_fee'] is False
        assert info['is_interest'] is False
        assert info['is_cash_transfer'] is False

    def test_unclassified_transaction_logging(self, caplog):
        """Test that unclassified transactions are logged."""
        import logging
        caplog.set_level(logging.WARNING)

        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="סוג פעולה לא ידוע",  # Unknown transaction type
            security_name="Unknown Security",
            security_symbol="UNKN",
            quantity=5.0,
            execution_price=100.0,
            currency="₪",
            amount_local_currency=-500.0,
            balance=44500.0
        )

        # Call log_if_unclassified
        result = tx.log_if_unclassified()

        # Should return True (was unclassified)
        assert result is True

        # Should be categorized as 'other'
        assert tx.transaction_category == 'other'

        # Should have logged a warning
        assert "Unclassified transaction type" in caplog.text
        assert "סוג פעולה לא ידוע" in caplog.text

    def test_all_known_types_classified(self):
        """Test that all known IBI transaction types are classified."""
        known_types = [
            # Buy types
            ('קניה שח', 'buy'),
            ('קניה חול מטח', 'buy'),
            ('קניה רצף', 'buy'),
            ('קניה מעוף', 'buy'),
            ('הפקדה', 'buy'),
            ('הפקדה פקיעה', 'buy'),
            ('הטבה', 'buy'),

            # Sell types
            ('מכירה שח', 'sell'),
            ('מכירה חול מטח', 'sell'),
            ('מכירה רצף', 'sell'),
            ('מכירה מעוף', 'sell'),
            ('משיכה', 'sell'),
            ('משיכה פקיעה', 'sell'),

            # Dividend types
            ('דיבדנד', 'dividend'),
            ('הפקדה דיבידנד מטח', 'dividend'),

            # Tax types
            ('משיכת מס חול מטח', 'tax'),
            ('משיכת מס מטח', 'tax'),

            # Interest types
            ('ריבית מזומן בשח', 'interest'),
            ('משיכת ריבית מטח', 'interest'),

            # Transfer types
            ('העברה מזומן בשח', 'transfer'),

            # Fee types
            ('דמי טפול מזומן בשח', 'fee'),
        ]

        for trans_type, expected_category in known_types:
            tx = Transaction(
                date=datetime(2024, 1, 15),
                transaction_type=trans_type,
                security_name="Test Security",
                security_symbol="TEST",
                quantity=1.0,
                execution_price=100.0,
                currency="₪",
                amount_local_currency=100.0,
                balance=100000.0
            )

            assert tx.transaction_category == expected_category, \
                f"Transaction type '{trans_type}' was classified as '{tx.transaction_category}', expected '{expected_category}'"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

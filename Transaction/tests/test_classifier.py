"""
Unit tests for TransactionClassifier system.

Tests the classification system independently from Transaction model.
"""

import pytest
from src.models.transaction_classifier import (
    TransactionClassifier,
    IBITransactionClassifier,
    ClassifierFactory,
    TransactionCategory
)


class TestIBITransactionClassifier:
    """Test IBI-specific transaction classifier."""

    @pytest.fixture
    def classifier(self):
        """Get IBI classifier instance."""
        return IBITransactionClassifier()

    def test_buy_classification(self, classifier):
        """Test various buy transaction types."""
        buy_types = [
            'קניה שח',
            'קניה חול מטח',
            'קניה רצף',
            'קניה מעוף',
            'הפקדה',
            'הפקדה פקיעה',
            'הטבה',
            'Buy'
        ]

        for trans_type in buy_types:
            assert classifier.is_buy(trans_type), \
                f"'{trans_type}' should be classified as buy"

    def test_sell_classification(self, classifier):
        """Test various sell transaction types."""
        sell_types = [
            'מכירה שח',
            'מכירה חול מטח',
            'מכירה רצף',
            'מכירה מעוף',
            'משיכה',
            'משיכה פקיעה',
            'Sell'
        ]

        for trans_type in sell_types:
            assert classifier.is_sell(trans_type), \
                f"'{trans_type}' should be classified as sell"

    def test_dividend_not_buy(self, classifier):
        """Test that dividend deposits are not classified as buy."""
        dividend_types = [
            'דיבידנד',
            'דיב',
            'הפקדה דיבידנד',
            'Dividend'
        ]

        for trans_type in dividend_types:
            assert not classifier.is_buy(trans_type), \
                f"'{trans_type}' should NOT be classified as buy"
            assert classifier.is_dividend(trans_type), \
                f"'{trans_type}' should be classified as dividend"

    def test_tax_not_sell(self, classifier):
        """Test that tax withdrawals are not classified as sell."""
        tax_types = [
            'משיכת מס',
            'משיכת מס חול מטח',
            'Tax'
        ]

        for trans_type in tax_types:
            assert not classifier.is_sell(trans_type), \
                f"'{trans_type}' should NOT be classified as sell"
            assert classifier.is_tax(trans_type), \
                f"'{trans_type}' should be classified as tax"

    def test_categorize_buy(self, classifier):
        """Test categorization of buy transactions."""
        result = classifier.categorize('קניה שח')
        assert result == TransactionCategory.BUY
        assert result.value == 'buy'

    def test_categorize_sell(self, classifier):
        """Test categorization of sell transactions."""
        result = classifier.categorize('מכירה שח')
        assert result == TransactionCategory.SELL
        assert result.value == 'sell'

    def test_categorize_dividend(self, classifier):
        """Test categorization of dividend transactions."""
        result = classifier.categorize('דיבידנד')
        assert result == TransactionCategory.DIVIDEND
        assert result.value == 'dividend'

    def test_categorize_tax(self, classifier):
        """Test categorization of tax transactions."""
        result = classifier.categorize('משיכת מס')
        assert result == TransactionCategory.TAX
        assert result.value == 'tax'

    def test_categorize_fee(self, classifier):
        """Test categorization of fee transactions."""
        result = classifier.categorize('דמי טפול')
        assert result == TransactionCategory.FEE
        assert result.value == 'fee'

    def test_categorize_interest(self, classifier):
        """Test categorization of interest transactions."""
        result = classifier.categorize('ריבית')
        assert result == TransactionCategory.INTEREST
        assert result.value == 'interest'

    def test_categorize_transfer(self, classifier):
        """Test categorization of cash transfer transactions."""
        result = classifier.categorize('העברה מזומן')
        assert result == TransactionCategory.TRANSFER
        assert result.value == 'transfer'

    def test_categorize_unknown(self, classifier):
        """Test categorization of unknown transaction types."""
        result = classifier.categorize('סוג לא ידוע')
        assert result == TransactionCategory.OTHER
        assert result.value == 'other'

    def test_get_classification_info(self, classifier):
        """Test comprehensive classification info."""
        info = classifier.get_classification_info('קניה שח')

        assert info['transaction_type'] == 'קניה שח'
        assert info['category'] == 'buy'
        assert info['is_buy'] is True
        assert info['is_sell'] is False
        assert info['is_dividend'] is False
        assert info['is_tax'] is False
        assert info['is_fee'] is False
        assert info['is_interest'] is False
        assert info['is_cash_transfer'] is False

    def test_exclusion_patterns(self, classifier):
        """Test that exclusion patterns work correctly."""
        # Dividend deposits should not be buy
        assert not classifier.is_buy('הפקדה דיבידנד')

        # Tax withdrawals should not be sell
        assert not classifier.is_sell('משיכת מס')

        # Interest withdrawals should not be sell
        assert not classifier.is_sell('משיכת ריבית')

        # Handling fees should not be buy
        assert not classifier.is_buy('דמי טפול')

    def test_mixed_transaction_types(self, classifier):
        """Test transaction types with multiple keywords."""
        # Should be classified as tax, not sell
        assert classifier.is_tax('משיכת מס חול מטח')
        assert not classifier.is_sell('משיכת מס חול מטח')

        # Should be classified as dividend, not buy
        assert classifier.is_dividend('הפקדה דיבידנד מטח')
        assert not classifier.is_buy('הפקדה דיבידנד מטח')


class TestClassifierFactory:
    """Test ClassifierFactory."""

    def test_get_ibi_classifier(self):
        """Test getting IBI classifier."""
        classifier = ClassifierFactory.get_classifier('IBI')
        assert isinstance(classifier, IBITransactionClassifier)

    def test_get_ibi_classifier_lowercase(self):
        """Test getting IBI classifier with lowercase name."""
        classifier = ClassifierFactory.get_classifier('ibi')
        assert isinstance(classifier, IBITransactionClassifier)

    def test_unsupported_broker_raises_error(self):
        """Test that unsupported broker raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ClassifierFactory.get_classifier('UNKNOWN_BROKER')

        assert 'No classifier found for broker' in str(exc_info.value)
        assert 'UNKNOWN_BROKER' in str(exc_info.value)

    def test_register_new_classifier(self):
        """Test registering a new classifier."""

        class CustomClassifier(TransactionClassifier):
            def is_buy(self, transaction_type: str, **kwargs) -> bool:
                return 'BUY' in transaction_type.upper()

            def is_sell(self, transaction_type: str, **kwargs) -> bool:
                return 'SELL' in transaction_type.upper()

            def is_dividend(self, transaction_type: str, **kwargs) -> bool:
                return 'DIV' in transaction_type.upper()

            def is_fee(self, transaction_type: str, **kwargs) -> bool:
                return 'FEE' in transaction_type.upper()

            def is_tax(self, transaction_type: str, **kwargs) -> bool:
                return 'TAX' in transaction_type.upper()

            def is_interest(self, transaction_type: str, **kwargs) -> bool:
                return 'INT' in transaction_type.upper()

            def is_cash_transfer(self, transaction_type: str, **kwargs) -> bool:
                return 'TRANSFER' in transaction_type.upper()

        # Register custom classifier
        ClassifierFactory.register_classifier('CUSTOM', CustomClassifier)

        # Should be in supported brokers
        assert 'CUSTOM' in ClassifierFactory.get_supported_brokers()

        # Should be able to get it
        classifier = ClassifierFactory.get_classifier('CUSTOM')
        assert isinstance(classifier, CustomClassifier)

        # Should work correctly
        assert classifier.is_buy('buy stock')
        assert classifier.is_sell('sell stock')

    def test_register_invalid_classifier_raises_error(self):
        """Test that registering non-classifier class raises TypeError."""

        class NotAClassifier:
            pass

        with pytest.raises(TypeError) as exc_info:
            ClassifierFactory.register_classifier('INVALID', NotAClassifier)

        assert 'must inherit from TransactionClassifier' in str(exc_info.value)

    def test_get_supported_brokers(self):
        """Test getting list of supported brokers."""
        brokers = ClassifierFactory.get_supported_brokers()

        assert isinstance(brokers, list)
        assert 'IBI' in brokers
        assert 'ibi' in brokers


class TestTransactionCategoryEnum:
    """Test TransactionCategory enum."""

    def test_category_values(self):
        """Test category enum values."""
        assert TransactionCategory.BUY.value == 'buy'
        assert TransactionCategory.SELL.value == 'sell'
        assert TransactionCategory.DIVIDEND.value == 'dividend'
        assert TransactionCategory.TAX.value == 'tax'
        assert TransactionCategory.FEE.value == 'fee'
        assert TransactionCategory.INTEREST.value == 'interest'
        assert TransactionCategory.TRANSFER.value == 'transfer'
        assert TransactionCategory.OTHER.value == 'other'

    def test_category_comparison(self):
        """Test category enum comparison."""
        assert TransactionCategory.BUY == TransactionCategory.BUY
        assert TransactionCategory.BUY != TransactionCategory.SELL


class TestAbstractClassifier:
    """Test abstract classifier behavior."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that abstract TransactionClassifier cannot be instantiated."""
        with pytest.raises(TypeError):
            TransactionClassifier()

    def test_must_implement_all_methods(self):
        """Test that subclass must implement all abstract methods."""

        # Missing is_sell method
        class IncompleteClassifier(TransactionClassifier):
            def is_buy(self, transaction_type: str, **kwargs) -> bool:
                return True

            # Missing other methods...

        with pytest.raises(TypeError):
            IncompleteClassifier()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
Portfolio Builder.

Builds current portfolio by processing actual transactions chronologically.
Uses REAL transaction data to calculate actual holdings.
"""

import logging
from typing import List, Dict, Optional
from src.models.transaction import Transaction
from .position import Position
from .errors import (
    ErrorCollector,
    TransactionProcessingError,
    PositionCalculationError,
    InsufficientSharesError,
    CurrencyMismatchError,
    NegativeQuantityError,
    validate_transaction_data
)

# Configure logging
logger = logging.getLogger(__name__)


class PortfolioBuilder:
    """
    Builds portfolio by processing transactions in chronological order.

    Process:
    1. Sort all transactions by date (oldest first)
    2. Process each transaction sequentially
    3. Update positions as we go (buy adds, sell removes)
    4. Calculate weighted average cost
    5. Return current positions
    """

    def __init__(self, fail_fast: bool = False):
        """
        Initialize PortfolioBuilder.

        Args:
            fail_fast: If True, raise errors immediately when encountered.
                      If False, collect errors and continue processing valid transactions.
        """
        self.positions: Dict[str, Position] = {}  # symbol -> position
        self.error_collector = ErrorCollector(fail_fast=fail_fast)

    def build(self, transactions: List[Transaction]) -> List[Position]:
        """
        Build current portfolio from actual transaction history.

        Args:
            transactions: List of REAL Transaction objects from loaded Excel files

        Returns:
            List of current Position objects (quantity > 0 only)

        Raises:
            PortfolioError: If fail_fast is True and errors are encountered
        """
        # Reset positions and error collector
        self.positions = {}
        self.error_collector.clear()

        # Validate input
        if not transactions:
            logger.warning("No transactions provided to build portfolio")
            return []

        try:
            # 1. Sort transactions by date (oldest first) - CRITICAL for correct calculations
            sorted_txs = sorted(transactions, key=lambda t: t.date)
        except (AttributeError, TypeError) as e:
            error = TransactionProcessingError(
                "Failed to sort transactions by date. Check date fields.",
                details={"error": str(e)}
            )
            self.error_collector.add_error(error)
            logger.error(f"Transaction sorting failed: {e}")
            return []

        # 2. Process each transaction chronologically
        processed_count = 0
        skipped_count = 0

        for idx, tx in enumerate(sorted_txs):
            try:
                # Validate transaction data quality
                validation_errors = validate_transaction_data(tx)
                if validation_errors:
                    error_msg = f"Transaction validation failed: {'; '.join(validation_errors)}"
                    error = TransactionProcessingError(
                        error_msg,
                        details={
                            "transaction_id": tx.id,
                            "transaction_index": idx,
                            "validation_errors": validation_errors,
                            "transaction_type": tx.transaction_type,
                            "security": f"{tx.security_name} ({tx.security_symbol})"
                        }
                    )
                    self.error_collector.add_error(error)
                    logger.warning(f"Skipping invalid transaction: {error_msg}")
                    skipped_count += 1
                    continue

                # Log if transaction type is unclassified (helps identify gaps)
                if tx.log_if_unclassified():
                    self.error_collector.add_warning(
                        f"Unclassified transaction type: {tx.transaction_type} for {tx.security_symbol}"
                    )

                # Process the transaction
                self._process_transaction(tx)
                processed_count += 1

            except Exception as e:
                # Catch any unexpected errors during processing
                error = TransactionProcessingError(
                    f"Unexpected error processing transaction: {str(e)}",
                    details={
                        "transaction_id": tx.id,
                        "transaction_index": idx,
                        "transaction_type": tx.transaction_type,
                        "security": f"{tx.security_name} ({tx.security_symbol})",
                        "error_type": type(e).__name__
                    }
                )
                self.error_collector.add_error(error)
                logger.error(f"Error processing transaction {idx}: {e}", exc_info=True)
                skipped_count += 1

        # Log processing summary
        logger.info(
            f"Portfolio build complete: {processed_count} transactions processed, "
            f"{skipped_count} skipped, {self.error_collector.get_error_count()} errors, "
            f"{self.error_collector.get_warning_count()} warnings"
        )

        # 3. Return only positions with quantity > 0 (filter out closed positions)
        return [p for p in self.positions.values() if p.quantity > 0]

    def build_by_currency(self, transactions: List[Transaction], fetch_prices: bool = True) -> Dict[str, List[Position]]:
        """
        Build portfolio grouped by currency (NIS vs USD).

        Args:
            transactions: List of REAL Transaction objects
            fetch_prices: If True, fetch current prices for all positions

        Returns:
            Dictionary: currency -> List of Position objects
            Example: {"₪": [pos1, pos2], "$": [pos3, pos4]}
        """
        # Build all positions
        all_positions = self.build(transactions)

        # Group by currency
        by_currency = {}
        for pos in all_positions:
            currency = pos.currency
            if currency not in by_currency:
                by_currency[currency] = []
            by_currency[currency].append(pos)

        # Fetch current prices if requested
        if fetch_prices:
            try:
                from .price_fetcher import update_positions_with_prices
                for currency, positions in by_currency.items():
                    update_positions_with_prices(positions)
            except Exception as e:
                # Silently fail if price fetching fails
                pass

        return by_currency

    def _is_phantom_security(self, tx: Transaction) -> bool:
        """
        Check if transaction represents a phantom/accounting security.

        Now uses classifier metadata when available, with fallback to legacy logic.

        Args:
            tx: Transaction to check

        Returns:
            True if transaction is a phantom security, False otherwise
        """
        # Use classifier metadata if available (from enhanced adapters)
        if tx.is_phantom is not None:
            return tx.is_phantom

        # Fallback to legacy logic for backward compatibility
        symbol = tx.security_symbol.strip()
        security_name = tx.security_name.strip()

        # Check symbol patterns
        phantom_symbol_patterns = [
            symbol.startswith('999'),  # IBI tax tracking series
            symbol.upper() == 'FEE',   # Fee placeholder
            symbol.upper() == 'TAX',   # Tax placeholder
        ]

        if any(phantom_symbol_patterns):
            return True

        # Check security name patterns (Hebrew)
        phantom_name_patterns = [
            'מס ששולם',      # Tax paid (exact match)
            'דמי טפול',       # Handling fees
            'עמלת',           # Commission/fee (partial match for variations)
        ]

        # Case-insensitive partial match for Hebrew patterns
        security_name_lower = security_name.lower()
        for pattern in phantom_name_patterns:
            if pattern in security_name_lower:
                return True

        return False

    def _process_transaction(self, tx: Transaction):
        """
        Process one actual transaction and update position.

        Now uses classifier metadata when available for improved accuracy.

        Args:
            tx: Real Transaction object with actual quantities and prices
        """
        symbol = tx.security_symbol

        # Skip phantom/tax tracking securities
        # These are IBI internal accounting entries, not actual holdings
        if self._is_phantom_security(tx):
            return

        # Get existing position or create new one
        if symbol not in self.positions:
            self.positions[symbol] = Position(
                security_name=tx.security_name,
                security_symbol=symbol,
                quantity=0.0,
                average_cost=0.0,
                total_invested=0.0,
                currency=tx.currency
            )

        position = self.positions[symbol]

        # Use classifier metadata if available
        if tx.share_direction is not None:
            if tx.share_direction == "add":
                self._process_buy(position, tx)
            elif tx.share_direction == "remove":
                self._process_sell(position, tx)
            # else: share_direction == "none" (dividends, fees, taxes - ignore)
        else:
            # Fallback to legacy logic for backward compatibility
            if tx.is_buy:
                self._process_buy(position, tx)
            elif tx.is_sell:
                self._process_sell(position, tx)
            # Ignore dividends, fees, taxes for now (don't affect holdings)

    def _process_buy(self, position: Position, tx: Transaction):
        """
        Add shares to position from actual buy transaction.

        Now uses classifier metadata when available for improved accuracy.

        Args:
            position: Current position to update
            tx: Actual buy transaction

        Raises:
            CurrencyMismatchError: If transaction currency doesn't match position currency
            PositionCalculationError: If calculation fails
        """
        try:
            # Validate currency consistency
            if position.currency != tx.currency:
                error = CurrencyMismatchError(
                    tx.security_symbol,
                    position.currency,
                    tx.currency
                )
                self.error_collector.add_error(error)
                logger.error(f"Currency mismatch for {tx.security_symbol}: {error.message}")
                return

            # Use classifier metadata for quantity if available
            if tx.share_quantity_abs is not None:
                add_quantity = tx.share_quantity_abs
            else:
                # Fallback: use transaction quantity
                add_quantity = abs(tx.quantity)

            # Validate positive quantity
            if add_quantity <= 0:
                error = NegativeQuantityError(tx.id, add_quantity, tx.transaction_type)
                self.error_collector.add_error(error)
                logger.warning(f"Buy transaction has non-positive quantity: {add_quantity}")
                return

            # Calculate new total quantity
            new_quantity = position.quantity + add_quantity

            # Use classifier metadata for cost basis if available
            if tx.cost_basis is not None:
                actual_cost = abs(tx.cost_basis)
            else:
                # Fallback to legacy cost calculation
                is_deposit = 'הפקדה' in tx.transaction_type

                if is_deposit:
                    # Deposits: use market price at time of deposit
                    if tx.currency == "₪":
                        # NIS: execution_price is in agorot, convert to shekels
                        actual_cost = add_quantity * (tx.execution_price / 100.0)
                    else:
                        # USD: execution_price is in dollars
                        actual_cost = add_quantity * tx.execution_price
                else:
                    # Purchases: use actual money paid from IBI data
                    if tx.currency == "₪":
                        # For NIS stocks: use amount_local_currency (negative means money out)
                        actual_cost = abs(tx.amount_local_currency)
                    else:
                        # For USD stocks: use amount_foreign_currency (negative means money out)
                        actual_cost = abs(tx.amount_foreign_currency)

            # Validate cost is reasonable
            if actual_cost < 0:
                self.error_collector.add_warning(
                    f"Negative cost calculated for buy transaction: {tx.id} ({tx.security_symbol})"
                )
                actual_cost = abs(actual_cost)

            # Calculate new total invested
            new_total_invested = position.total_invested + actual_cost

            # Update position with actual values
            position.quantity = new_quantity
            position.total_invested = new_total_invested

            # Calculate weighted average cost
            if new_quantity > 0:
                position.average_cost = new_total_invested / new_quantity
            else:
                position.average_cost = 0.0
                self.error_collector.add_warning(
                    f"Zero quantity after buy transaction for {tx.security_symbol}"
                )

        except ZeroDivisionError as e:
            error = PositionCalculationError(
                f"Division by zero in buy calculation for {tx.security_symbol}",
                details={
                    "transaction_id": tx.id,
                    "quantity": tx.quantity,
                    "error": str(e)
                }
            )
            self.error_collector.add_error(error)
            logger.error(f"Calculation error in _process_buy: {e}")

        except Exception as e:
            error = PositionCalculationError(
                f"Unexpected error in buy calculation for {tx.security_symbol}",
                details={
                    "transaction_id": tx.id,
                    "error_type": type(e).__name__,
                    "error": str(e)
                }
            )
            self.error_collector.add_error(error)
            logger.error(f"Unexpected error in _process_buy: {e}", exc_info=True)

    def _process_sell(self, position: Position, tx: Transaction):
        """
        Remove shares from position from actual sell transaction.

        Now uses classifier metadata when available for improved accuracy.

        Args:
            position: Current position to update
            tx: Actual sell transaction

        Raises:
            InsufficientSharesError: If trying to sell more shares than owned
            CurrencyMismatchError: If transaction currency doesn't match position currency
            PositionCalculationError: If calculation fails
        """
        try:
            # Validate currency consistency
            if position.currency != tx.currency:
                error = CurrencyMismatchError(
                    tx.security_symbol,
                    position.currency,
                    tx.currency
                )
                self.error_collector.add_error(error)
                logger.error(f"Currency mismatch for {tx.security_symbol}: {error.message}")
                return

            # Use classifier metadata for quantity if available
            if tx.share_quantity_abs is not None:
                sell_quantity = tx.share_quantity_abs
            else:
                # Fallback: use transaction quantity
                sell_quantity = abs(tx.quantity)

            # Validate positive quantity
            if sell_quantity <= 0:
                error = NegativeQuantityError(tx.id, sell_quantity, tx.transaction_type)
                self.error_collector.add_error(error)
                logger.warning(f"Sell transaction has non-positive quantity: {sell_quantity}")
                return

            # Check for sufficient shares (with small tolerance for rounding)
            TOLERANCE = 0.01
            if sell_quantity > position.quantity + TOLERANCE:
                error = InsufficientSharesError(
                    tx.security_symbol,
                    position.quantity,
                    sell_quantity,
                    tx.date
                )
                self.error_collector.add_error(error)
                logger.error(
                    f"Insufficient shares to sell: {tx.security_symbol} "
                    f"(have: {position.quantity}, need: {sell_quantity})"
                )
                return

            # Calculate value to remove from cost basis (at our average cost, not sale price)
            # This maintains accurate cost basis for remaining shares
            sold_value = sell_quantity * position.average_cost

            # Update position - reduce quantity and cost basis
            position.quantity -= sell_quantity
            position.total_invested -= sold_value

            # Handle potential rounding errors (if quantity is very close to zero, set to zero)
            if abs(position.quantity) < TOLERANCE:
                position.quantity = 0.0
                position.total_invested = 0.0
                position.average_cost = 0.0
            # Average cost per share stays the same (it's our original cost basis)
            # If position is fully closed, quantity and invested will both be ~0
            # and will be filtered out in build()

        except Exception as e:
            error = PositionCalculationError(
                f"Unexpected error in sell calculation for {tx.security_symbol}",
                details={
                    "transaction_id": tx.id,
                    "available_quantity": position.quantity,
                    "sell_quantity": tx.quantity,
                    "error_type": type(e).__name__,
                    "error": str(e)
                }
            )
            self.error_collector.add_error(error)
            logger.error(f"Unexpected error in _process_sell: {e}", exc_info=True)

    def get_error_summary(self) -> Dict:
        """
        Get summary of all errors and warnings from last build.

        Returns:
            Dictionary with error statistics and details
        """
        return self.error_collector.get_error_summary()

    def has_errors(self) -> bool:
        """Check if any errors occurred during last build."""
        return self.error_collector.has_errors()

    def has_warnings(self) -> bool:
        """Check if any warnings occurred during last build."""
        return self.error_collector.has_warnings()

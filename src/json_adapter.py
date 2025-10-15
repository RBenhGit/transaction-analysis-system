"""
JSON Adapter for standardizing transaction data.

Converts bank/broker-specific data to standardized JSON format and
creates Transaction model instances.
"""

from typing import List, Dict
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

from .models.transaction import Transaction
from src.adapters.base_adapter import BaseAdapter


class JSONAdapter:
    """
    Adapter for converting bank data to standardized JSON format.

    Handles:
    - DataFrame to Transaction model conversion
    - JSON export with metadata
    - Data validation and cleaning
    """

    def __init__(self):
        """Initialize JSON adapter."""
        pass

    def dataframe_to_transactions(
        self,
        df: pd.DataFrame,
        adapter: BaseAdapter
    ) -> List[Transaction]:
        """
        Convert DataFrame to list of Transaction objects.

        Args:
            df: Standardized DataFrame from bank adapter
            adapter: The bank adapter used for transformation

        Returns:
            List of Transaction model instances
        """
        transactions = []

        for idx, row in df.iterrows():
            try:
                # Create Transaction object
                trans = Transaction(
                    id=row.get('id', ''),
                    date=row.get('date'),
                    transaction_type=row.get('transaction_type', ''),
                    security_name=row.get('security_name', ''),
                    security_symbol=row.get('security_symbol', ''),
                    quantity=float(row.get('quantity', 0.0)),
                    execution_price=float(row.get('execution_price', 0.0)),
                    currency=row.get('currency', '₪'),
                    transaction_fee=float(row.get('transaction_fee', 0.0)),
                    additional_fees=float(row.get('additional_fees', 0.0)),
                    amount_foreign_currency=float(row.get('amount_foreign_currency', 0.0)),
                    amount_local_currency=float(row.get('amount_local_currency', 0.0)),
                    balance=float(row.get('balance', 0.0)),
                    capital_gains_tax_estimate=float(row.get('capital_gains_tax_estimate', 0.0)),
                    bank=row.get('bank', adapter.bank_name),
                    account=row.get('account', ''),
                    category=row.get('category', adapter.categorize_transaction(row.get('transaction_type', '')))
                    if hasattr(adapter, 'categorize_transaction') else 'other',
                    # Classifier metadata (optional, added by enhanced adapters)
                    transaction_effect=row.get('transaction_effect'),
                    is_phantom=row.get('is_phantom', False),
                    share_direction=row.get('share_direction'),
                    share_quantity_abs=float(row.get('share_quantity_abs')) if row.get('share_quantity_abs') is not None else None,
                    cost_basis=float(row.get('cost_basis')) if row.get('cost_basis') is not None else None
                )
                transactions.append(trans)

            except Exception as e:
                print(f"Warning: Error creating transaction at row {idx}: {e}")
                continue

        return transactions

    def transactions_to_json(
        self,
        transactions: List[Transaction],
        output_path: str = None,
        include_metadata: bool = True
    ) -> Dict:
        """
        Convert transactions to JSON format with metadata.

        Args:
            transactions: List of Transaction objects
            output_path: Optional path to save JSON file
            include_metadata: Whether to include metadata section

        Returns:
            Dictionary with transactions and metadata
        """
        # Convert transactions to dictionaries
        trans_dicts = [t.to_dict() for t in transactions]

        # Prepare output structure
        output = {}

        if include_metadata:
            # Calculate metadata
            dates = [t.date for t in transactions]
            output['metadata'] = {
                'bank': transactions[0].bank if transactions else 'Unknown',
                'import_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_transactions': len(transactions),
                'date_range': {
                    'start': min(dates).strftime('%Y-%m-%d') if dates else None,
                    'end': max(dates).strftime('%Y-%m-%d') if dates else None
                },
                'statistics': self._calculate_statistics(transactions)
            }

        output['transactions'] = trans_dicts

        # Save to file if path provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"✅ Exported {len(transactions)} transactions to {output_path}")

        return output

    def _calculate_statistics(self, transactions: List[Transaction]) -> Dict:
        """
        Calculate summary statistics for transactions.

        Args:
            transactions: List of Transaction objects

        Returns:
            Dictionary with statistics
        """
        if not transactions:
            return {}

        # Count transaction types
        type_counts = {}
        for t in transactions:
            type_counts[t.transaction_type] = type_counts.get(t.transaction_type, 0) + 1

        # Count unique securities
        unique_securities = len(set(t.security_name for t in transactions))

        # Calculate totals
        total_fees = sum(t.transaction_fee + t.additional_fees for t in transactions)
        total_buys = sum(1 for t in transactions if t.is_buy)
        total_sells = sum(1 for t in transactions if t.is_sell)
        total_dividends = sum(1 for t in transactions if t.is_dividend)

        # Final balance
        final_balance = transactions[-1].balance if transactions else 0.0

        return {
            'transaction_type_counts': type_counts,
            'unique_securities': unique_securities,
            'total_fees': round(total_fees, 2),
            'total_buys': total_buys,
            'total_sells': total_sells,
            'total_dividends': total_dividends,
            'final_balance': round(final_balance, 2)
        }

    def import_from_json(self, json_path: str) -> List[Transaction]:
        """
        Import transactions from JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            List of Transaction objects
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        transactions = []
        trans_data = data.get('transactions', [])

        for t_dict in trans_data:
            try:
                # Parse date if it's a string
                if isinstance(t_dict.get('date'), str):
                    t_dict['date'] = datetime.strptime(t_dict['date'], '%Y-%m-%d')

                trans = Transaction(**t_dict)
                transactions.append(trans)

            except Exception as e:
                print(f"Warning: Error importing transaction: {e}")
                continue

        return transactions

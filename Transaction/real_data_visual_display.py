#!/usr/bin/env python3
"""
Visual Display with Real JSON Data

This script loads your actual processed transaction data from JSON files
and displays it in the visual interface, showing your real IBI transaction structure.
"""

import os
import sys
import json
import glob
from datetime import datetime
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.simple_models import Transaction, TransactionSet, TransactionMetadata
from modules.visual_display import VisualDisplayManager


def find_latest_json_file():
    """Find the most recent JSON file in the output directory."""
    json_pattern = "output/processed/*.json"
    json_files = glob.glob(json_pattern)

    if not json_files:
        return None

    # Sort by modification time, most recent first
    json_files.sort(key=os.path.getmtime, reverse=True)
    return json_files[0]


def load_json_transactions(json_file_path):
    """Load transaction data from JSON file."""
    print(f"Loading transaction data from: {json_file_path}")

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print("JSON file structure found:")
        print(f"- Top-level keys: {list(data.keys())}")

        # Extract transactions
        json_transactions = data.get('transactions', [])
        print(f"- Number of transactions: {len(json_transactions)}")

        # Extract metadata
        json_metadata = data.get('metadata', {})
        print(f"- Source file: {json_metadata.get('source_file', 'Unknown')}")
        print(f"- Date range: {json_metadata.get('date_range', {})}")
        print(f"- Bank: {json_metadata.get('bank', 'Unknown')}")

        # Convert JSON data to Transaction objects
        transactions = []
        for tx_data in json_transactions:
            try:
                # Convert date string to date object
                date_str = tx_data.get('date')
                if date_str:
                    transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                else:
                    continue  # Skip transactions without dates

                # Convert amount to Decimal
                amount = tx_data.get('amount')
                if amount is not None:
                    amount = Decimal(str(amount))
                else:
                    continue  # Skip transactions without amounts

                # Convert balance to Decimal if present
                balance = tx_data.get('balance')
                if balance is not None:
                    balance = Decimal(str(balance))

                # Get other fields
                description = tx_data.get('description', '').strip()
                if not description:
                    description = f"Transaction {tx_data.get('reference', 'No Ref')}"

                reference = tx_data.get('reference')
                if reference is not None:
                    reference = str(reference)

                category = tx_data.get('category')
                bank = tx_data.get('bank', 'IBI')
                account = tx_data.get('account')

                # Create Transaction object
                transaction = Transaction(
                    date=transaction_date,
                    description=description,
                    amount=amount,
                    balance=balance,
                    category=category,
                    reference=reference,
                    bank=bank,
                    account=account
                )

                transactions.append(transaction)

            except Exception as e:
                print(f"Warning: Skipped transaction due to error: {e}")
                continue

        print(f"Successfully converted {len(transactions)} transactions")

        # Create metadata object
        metadata = TransactionMetadata(
            source_file=json_metadata.get('source_file', json_file_path),
            import_date=datetime.now(),  # Use current time for demo
            total_transactions=len(transactions),
            date_range={
                'start': datetime.strptime(json_metadata.get('date_range', {}).get('start', '2024-01-01'), '%Y-%m-%d').date(),
                'end': datetime.strptime(json_metadata.get('date_range', {}).get('end', '2024-12-31'), '%Y-%m-%d').date()
            } if json_metadata.get('date_range') else {'start': None, 'end': None},
            bank=json_metadata.get('bank', 'IBI'),
            encoding=json_metadata.get('encoding', 'utf-8')
        )

        # Create TransactionSet
        transaction_set = TransactionSet(
            transactions=transactions,
            metadata=metadata
        )

        return transaction_set

    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None


def main():
    """Main function to load real data and display it."""
    print("="*60)
    print("REAL DATA VISUAL DISPLAY")
    print("="*60)
    print()

    # Find the latest JSON file
    json_file = find_latest_json_file()

    if not json_file:
        print("Error: No JSON files found in output/processed/ directory")
        print("Please run the main application to import and process Excel files first.")
        return

    # Load transaction data from JSON
    transaction_set = load_json_transactions(json_file)

    if not transaction_set:
        print("Failed to load transaction data from JSON file.")
        return

    # Display summary
    print()
    print("REAL TRANSACTION DATA SUMMARY:")
    print("-" * 40)
    print(f"Source: {transaction_set.metadata.source_file}")
    print(f"Bank: {transaction_set.metadata.bank}")
    print(f"Total Transactions: {len(transaction_set.transactions)}")

    date_range = transaction_set.metadata.date_range
    if date_range and date_range['start'] and date_range['end']:
        print(f"Date Range: {date_range['start']} to {date_range['end']}")

    # Show sample transactions
    print(f"\\nSample transactions:")
    for i, tx in enumerate(transaction_set.transactions[:5]):
        amount_str = f"₪{tx.amount}" if tx.amount else "N/A"
        balance_str = f"₪{tx.balance}" if tx.balance else "N/A"
        desc = tx.description[:30] + "..." if len(tx.description) > 30 else tx.description
        print(f"  {i+1}. {tx.date} | {desc} | {amount_str} | Bal: {balance_str}")

    if len(transaction_set.transactions) > 5:
        print(f"  ... and {len(transaction_set.transactions) - 5} more transactions")

    print()
    print("="*60)
    print("LAUNCHING VISUAL INTERFACE")
    print("="*60)
    print()
    print("Opening GUI with your REAL IBI transaction data...")
    print("Features you can try:")
    print("- Sort by Date, Amount, Balance, Reference")
    print("- Filter by date ranges (your data spans 2024)")
    print("- Search transaction descriptions and references")
    print("- View summary statistics for your actual spending")
    print("- Export your filtered data")
    print()
    print("The GUI window will open now and stay open until you close it.")
    print()

    # Launch visual display with real data
    visual_display = VisualDisplayManager()
    visual_display.run(transaction_set)

    print("GUI session completed!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\nOperation cancelled by user.")
    except Exception as e:
        print(f"\\nError: {e}")
        print("Make sure you have processed JSON files in output/processed/ directory.")
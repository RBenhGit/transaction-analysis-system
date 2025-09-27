"""
Display Manager

This module handles the display and presentation of transaction data,
including console output, summary statistics, and export capabilities.
"""

import os
import csv
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal
from tabulate import tabulate

from .simple_models import TransactionSet, Transaction, ImportResult
from .config_manager import ConfigManager


class DisplayManager:
    """
    Manages the display and presentation of transaction data.

    Provides various output formats and summary capabilities for
    transaction analysis and reporting.
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the display manager.

        Args:
            config_manager: ConfigManager instance, creates default if None
        """
        self.config_manager = config_manager or ConfigManager()
        self.display_config = self.config_manager.get_display_config()

    def show_transaction_summary(self, transaction_set: TransactionSet):
        """
        Display a summary of the transaction set.

        Args:
            transaction_set: TransactionSet to summarize
        """
        print("\n" + "="*60)
        print("TRANSACTION SUMMARY")
        print("="*60)

        metadata = transaction_set.metadata

        # Basic information
        print(f"Source File: {metadata.source_file}")
        print(f"Bank: {metadata.bank}")
        print(f"Import Date: {metadata.import_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Transactions: {metadata.total_transactions}")

        # Date range
        date_range = metadata.date_range
        start_date = date_range.get('start')
        end_date = date_range.get('end')

        if start_date and end_date:
            print(f"Date Range: {start_date} to {end_date}")
            days = (end_date - start_date).days + 1
            print(f"Period: {days} days")

        # Financial summary
        transactions = transaction_set.transactions
        if transactions:
            amounts = [t.amount for t in transactions if t.amount]

            if amounts:
                total_amount = sum(amounts)
                debits = [a for a in amounts if a < 0]
                credits = [a for a in amounts if a > 0]

                print(f"\nFINANCIAL SUMMARY:")
                print(f"Total Amount: ₪{total_amount:,.2f}")

                if debits:
                    total_debits = sum(debits)
                    print(f"Total Debits: ₪{total_debits:,.2f} ({len(debits)} transactions)")

                if credits:
                    total_credits = sum(credits)
                    print(f"Total Credits: ₪{total_credits:,.2f} ({len(credits)} transactions)")

                # Average transaction amounts
                if amounts:
                    avg_amount = total_amount / len(amounts)
                    print(f"Average Transaction: ₪{avg_amount:.2f}")

                # Largest transactions
                max_debit = min(debits) if debits else Decimal('0')
                max_credit = max(credits) if credits else Decimal('0')

                if max_debit < 0:
                    print(f"Largest Debit: ₪{max_debit:,.2f}")
                if max_credit > 0:
                    print(f"Largest Credit: ₪{max_credit:,.2f}")

        print("="*60)

    def show_transactions_table(
        self,
        transactions: List[Transaction],
        max_rows: Optional[int] = None,
        format_style: str = "grid"
    ):
        """
        Display transactions in a formatted table.

        Args:
            transactions: List of transactions to display
            max_rows: Maximum number of rows to show
            format_style: Table format style (grid, simple, plain, etc.)
        """
        if not transactions:
            print("No transactions to display.")
            return

        # Limit rows if specified
        max_display = max_rows or self.display_config.get("max_rows", 100)
        display_transactions = transactions[:max_display]

        # Prepare table data
        headers = ["Date", "Description", "Amount", "Balance", "Reference"]
        rows = []

        for trans in display_transactions:
            # Format date
            date_str = trans.date.strftime("%Y-%m-%d") if trans.date else "N/A"

            # Format description (truncate if too long)
            desc = trans.description[:50] + "..." if len(trans.description) > 50 else trans.description

            # Format amounts
            amount_str = f"₪{trans.amount:,.2f}" if trans.amount else "N/A"
            balance_str = f"₪{trans.balance:,.2f}" if trans.balance else "N/A"

            # Reference
            ref_str = trans.reference or ""

            rows.append([date_str, desc, amount_str, balance_str, ref_str])

        # Display table
        print(f"\nTRANSACTIONS (Showing {len(display_transactions)} of {len(transactions)})")
        print(tabulate(rows, headers=headers, tablefmt=format_style))

        if len(transactions) > max_display:
            print(f"\n... and {len(transactions) - max_display} more transactions")

    def show_monthly_summary(self, transaction_set: TransactionSet):
        """
        Display monthly summary of transactions.

        Args:
            transaction_set: TransactionSet to analyze
        """
        transactions = transaction_set.transactions
        if not transactions:
            print("No transactions to analyze.")
            return

        # Group transactions by month
        monthly_data = {}

        for trans in transactions:
            if not trans.date or not trans.amount:
                continue

            month_key = trans.date.strftime("%Y-%m")

            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "count": 0,
                    "total": Decimal('0'),
                    "debits": Decimal('0'),
                    "credits": Decimal('0'),
                    "debit_count": 0,
                    "credit_count": 0
                }

            data = monthly_data[month_key]
            data["count"] += 1
            data["total"] += trans.amount

            if trans.amount < 0:
                data["debits"] += trans.amount
                data["debit_count"] += 1
            else:
                data["credits"] += trans.amount
                data["credit_count"] += 1

        # Display monthly summary table
        print("\nMONTHLY SUMMARY")
        print("-" * 80)

        headers = ["Month", "Count", "Total", "Credits", "Debits", "Net"]
        rows = []

        for month in sorted(monthly_data.keys()):
            data = monthly_data[month]
            net_amount = data["credits"] + data["debits"]  # debits are negative

            rows.append([
                month,
                data["count"],
                f"₪{data['total']:,.2f}",
                f"₪{data['credits']:,.2f} ({data['credit_count']})",
                f"₪{data['debits']:,.2f} ({data['debit_count']})",
                f"₪{net_amount:,.2f}"
            ])

        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def show_category_analysis(self, transactions: List[Transaction]):
        """
        Display analysis by transaction categories.

        Args:
            transactions: List of transactions to analyze
        """
        if not transactions:
            print("No transactions to analyze.")
            return

        # Group by category
        category_data = {}

        for trans in transactions:
            category = trans.category or "Uncategorized"
            if category not in category_data:
                category_data[category] = {
                    "count": 0,
                    "total": Decimal('0'),
                    "transactions": []
                }

            category_data[category]["count"] += 1
            if trans.amount:
                category_data[category]["total"] += trans.amount
            category_data[category]["transactions"].append(trans)

        # Display category analysis
        print("\nCATEGORY ANALYSIS")
        print("-" * 60)

        headers = ["Category", "Count", "Total Amount", "Avg Amount"]
        rows = []

        for category in sorted(category_data.keys()):
            data = category_data[category]
            avg_amount = data["total"] / data["count"] if data["count"] > 0 else Decimal('0')

            rows.append([
                category[:30],  # Truncate long category names
                data["count"],
                f"₪{data['total']:,.2f}",
                f"₪{avg_amount:.2f}"
            ])

        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def export_to_csv(
        self,
        transaction_set: TransactionSet,
        output_path: Optional[str] = None
    ) -> str:
        """
        Export transactions to CSV format.

        Args:
            transaction_set: TransactionSet to export
            output_path: Path to save CSV file, auto-generate if None

        Returns:
            Path to saved CSV file
        """
        # Generate output path if not provided
        if not output_path:
            export_path = self.config_manager.get_export_path()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            bank = transaction_set.metadata.bank.lower()
            filename = f"{bank}_transactions_{timestamp}.csv"
            output_path = os.path.join(export_path, filename)

        # Write CSV file
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow([
                    'Date', 'Description', 'Amount', 'Balance',
                    'Category', 'Reference', 'Bank', 'Account'
                ])

                # Write transactions
                for trans in transaction_set.transactions:
                    writer.writerow([
                        trans.date.isoformat() if trans.date else '',
                        trans.description,
                        float(trans.amount) if trans.amount else '',
                        float(trans.balance) if trans.balance else '',
                        trans.category or '',
                        trans.reference or '',
                        trans.bank,
                        trans.account or ''
                    ])

            return output_path

        except IOError as e:
            raise IOError(f"Failed to write CSV file: {e}")

    def export_to_excel(
        self,
        transaction_set: TransactionSet,
        output_path: Optional[str] = None
    ) -> str:
        """
        Export transactions to Excel format.

        Args:
            transaction_set: TransactionSet to export
            output_path: Path to save Excel file, auto-generate if None

        Returns:
            Path to saved Excel file
        """
        import pandas as pd

        # Generate output path if not provided
        if not output_path:
            export_path = self.config_manager.get_export_path()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            bank = transaction_set.metadata.bank.lower()
            filename = f"{bank}_transactions_{timestamp}.xlsx"
            output_path = os.path.join(export_path, filename)

        # Prepare data for DataFrame
        data = []
        for trans in transaction_set.transactions:
            data.append({
                'Date': trans.date,
                'Description': trans.description,
                'Amount': float(trans.amount) if trans.amount else None,
                'Balance': float(trans.balance) if trans.balance else None,
                'Category': trans.category,
                'Reference': trans.reference,
                'Bank': trans.bank,
                'Account': trans.account
            })

        # Create DataFrame and save to Excel
        try:
            df = pd.DataFrame(data)

            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Main transactions sheet
                df.to_excel(writer, sheet_name='Transactions', index=False)

                # Summary sheet
                summary_data = self._prepare_summary_data(transaction_set)
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

            return output_path

        except Exception as e:
            raise IOError(f"Failed to write Excel file: {e}")

    def _prepare_summary_data(self, transaction_set: TransactionSet) -> List[Dict[str, Any]]:
        """
        Prepare summary data for Excel export.

        Args:
            transaction_set: TransactionSet to summarize

        Returns:
            List of dictionaries containing summary information
        """
        metadata = transaction_set.metadata
        transactions = transaction_set.transactions

        summary = [
            {"Metric": "Source File", "Value": metadata.source_file},
            {"Metric": "Bank", "Value": metadata.bank},
            {"Metric": "Import Date", "Value": metadata.import_date.strftime("%Y-%m-%d %H:%M:%S")},
            {"Metric": "Total Transactions", "Value": len(transactions)},
        ]

        if transactions:
            # Date range
            date_range = transaction_set.get_date_range()
            if date_range["start"]:
                summary.append({"Metric": "Start Date", "Value": date_range["start"].isoformat()})
            if date_range["end"]:
                summary.append({"Metric": "End Date", "Value": date_range["end"].isoformat()})

            # Financial summary
            amounts = [float(t.amount) for t in transactions if t.amount]
            if amounts:
                summary.extend([
                    {"Metric": "Total Amount", "Value": sum(amounts)},
                    {"Metric": "Average Amount", "Value": sum(amounts) / len(amounts)},
                    {"Metric": "Minimum Amount", "Value": min(amounts)},
                    {"Metric": "Maximum Amount", "Value": max(amounts)}
                ])

        return summary

    def show_import_result(self, result: ImportResult, show_transactions: bool = True):
        """
        Display the results of an import operation.

        Args:
            result: ImportResult to display
            show_transactions: Whether to show transaction details
        """
        print("\n" + "="*60)
        print("IMPORT RESULT")
        print("="*60)

        # Status
        status = "SUCCESS" if result.success else "FAILED"
        print(f"Status: {status}")

        # Processing time
        if result.processing_time:
            print(f"Processing Time: {result.processing_time:.2f} seconds")

        # Errors
        if result.errors:
            print(f"\nErrors ({len(result.errors)}):")
            for error in result.errors:
                print(f"  • {error}")

        # Warnings
        if result.warnings:
            print(f"\nWarnings ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"  • {warning}")

        # Transaction summary
        if result.success and result.transaction_set:
            print(f"\nProcessed {len(result.transaction_set.transactions)} transactions")

            if show_transactions:
                self.show_transaction_summary(result.transaction_set)

        print("="*60)

    def interactive_menu(self, transaction_set: TransactionSet):
        """
        Display an interactive menu for exploring transaction data.

        Args:
            transaction_set: TransactionSet to explore
        """
        while True:
            print("\n" + "="*50)
            print("TRANSACTION EXPLORER")
            print("="*50)
            print("1. Show summary")
            print("2. Show transactions table")
            print("3. Show monthly summary")
            print("4. Show category analysis")
            print("5. Export to CSV")
            print("6. Export to Excel")
            print("7. Export to JSON")
            print("0. Exit")

            choice = input("\nSelect option (0-7): ").strip()

            try:
                if choice == "0":
                    break
                elif choice == "1":
                    self.show_transaction_summary(transaction_set)
                elif choice == "2":
                    max_rows = input("Max rows to show (Enter for default): ").strip()
                    max_rows = int(max_rows) if max_rows.isdigit() else None
                    self.show_transactions_table(transaction_set.transactions, max_rows)
                elif choice == "3":
                    self.show_monthly_summary(transaction_set)
                elif choice == "4":
                    self.show_category_analysis(transaction_set.transactions)
                elif choice == "5":
                    path = self.export_to_csv(transaction_set)
                    print(f"✓ Exported to CSV: {path}")
                elif choice == "6":
                    path = self.export_to_excel(transaction_set)
                    print(f"✓ Exported to Excel: {path}")
                elif choice == "7":
                    from .json_adapter import JSONAdapter
                    adapter = JSONAdapter(self.config_manager)
                    path = adapter.export_to_json(transaction_set)
                    print(f"✓ Exported to JSON: {path}")
                else:
                    print("Invalid option. Please try again.")

            except Exception as e:
                print(f"Error: {e}")

            input("\nPress Enter to continue...")

    def print_file_list(self, files: List[Dict[str, Any]]):
        """
        Display a formatted list of files.

        Args:
            files: List of file information dictionaries
        """
        if not files:
            print("No files found.")
            return

        print(f"\nFound {len(files)} file(s):")
        print("-" * 80)

        headers = ["#", "Filename", "Size", "Modified"]
        rows = []

        for i, file_info in enumerate(files, 1):
            # Format file size
            size = file_info.get("size", 0)
            size_str = self._format_file_size(size)

            # Format modification time
            mod_time = file_info.get("modified", 0)
            mod_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M")

            rows.append([
                str(i),
                file_info.get("filename", ""),
                size_str,
                mod_str
            ])

        print(tabulate(rows, headers=headers, tablefmt="simple"))

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
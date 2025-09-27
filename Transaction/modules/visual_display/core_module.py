"""
Core Visual Display Module

This module contains the main VisualDisplayManager class that provides
a graphical user interface for viewing and interacting with transaction data.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional, Dict, Any, Callable
from datetime import date, datetime
from decimal import Decimal
import os

# Import from src module following hierarchy rules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.simple_models import Transaction, TransactionSet
from src.display_manager import DisplayManager
from src.config_manager import ConfigManager

from .utils import format_currency, format_date_display, get_amount_color, create_filter_query


class VisualDisplayManager:
    """
    Main visual display manager providing GUI interface for transaction data.

    This class creates a tkinter-based GUI for viewing, filtering, and interacting
    with transaction data in a user-friendly graphical interface.
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the visual display manager.

        Args:
            config_manager: ConfigManager instance, creates default if None
        """
        self.config_manager = config_manager or ConfigManager()
        self.display_manager = DisplayManager(config_manager)

        # GUI components
        self.root = None
        self.transaction_tree = None
        self.summary_frame = None
        self.filter_frame = None

        # Data
        self.current_transaction_set = None
        self.filtered_transactions = []

        # Filter variables
        self.filter_vars = {}

    def show_transactions(self, transaction_set: TransactionSet, start_mainloop: bool = True):
        """
        Display transactions in the GUI interface.

        Args:
            transaction_set: TransactionSet to display
            start_mainloop: Whether to start the tkinter mainloop (default True)
        """
        self.current_transaction_set = transaction_set
        self.filtered_transactions = transaction_set.transactions.copy()

        if self.root is None:
            self._create_main_window()

        self._populate_transaction_tree()
        self._update_summary_panel()

        self.root.deiconify()  # Show window if it was hidden
        self.root.lift()  # Bring to front

        if start_mainloop:
            # Start the GUI event loop to keep window open
            self.root.mainloop()

    def _create_main_window(self):
        """Create the main application window."""
        self.root = tk.Tk()
        self.root.title("Transaction Analysis - Visual Display")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')

        # Create main layout
        self._create_menu_bar()
        self._create_toolbar()
        self._create_main_panels()
        self._create_status_bar()

        # Initialize filter variables
        self._initialize_filter_vars()

        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export to CSV", command=self._export_csv)
        file_menu.add_command(label="Export to Excel", command=self._export_excel)
        file_menu.add_command(label="Export to JSON", command=self._export_json)
        file_menu.add_separator()
        file_menu.add_command(label="Close", command=self._on_closing)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self._refresh_view)
        view_menu.add_command(label="Clear Filters", command=self._clear_filters)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Monthly Summary", command=self._show_monthly_summary)
        tools_menu.add_command(label="Category Analysis", command=self._show_category_analysis)

    def _create_toolbar(self):
        """Create the application toolbar."""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        # Refresh button
        ttk.Button(toolbar, text="Refresh", command=self._refresh_view).pack(side=tk.LEFT, padx=2)

        # Export buttons
        ttk.Button(toolbar, text="Export CSV", command=self._export_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export Excel", command=self._export_excel).pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Filter controls
        ttk.Label(toolbar, text="Quick Search:").pack(side=tk.LEFT, padx=2)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=2)
        search_entry.bind('<KeyRelease>', self._on_search_change)

        ttk.Button(toolbar, text="Clear", command=self._clear_search).pack(side=tk.LEFT, padx=2)

    def _create_main_panels(self):
        """Create the main content panels."""
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel for filters and summary
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)

        # Right panel for transaction table
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=3)

        # Create filter panel
        self._create_filter_panel(left_panel)

        # Create summary panel
        self._create_summary_panel(left_panel)

        # Create transaction table
        self._create_transaction_table(right_panel)

    def _create_filter_panel(self, parent):
        """Create the filter panel."""
        self.filter_frame = ttk.LabelFrame(parent, text="Filters", padding=10)
        self.filter_frame.pack(fill=tk.X, pady=(0, 10))

        # Date range filter
        ttk.Label(self.filter_frame, text="Date Range:").grid(row=0, column=0, sticky=tk.W, pady=2)

        date_frame = ttk.Frame(self.filter_frame)
        date_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, pady=2)

        ttk.Label(date_frame, text="From:").grid(row=0, column=0, sticky=tk.W)
        self.start_date_var = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.start_date_var, width=12).grid(row=0, column=1, padx=2)

        ttk.Label(date_frame, text="To:").grid(row=1, column=0, sticky=tk.W)
        self.end_date_var = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.end_date_var, width=12).grid(row=1, column=1, padx=2)

        # Amount range filter
        ttk.Label(self.filter_frame, text="Amount Range:").grid(row=2, column=0, sticky=tk.W, pady=(10, 2))

        amount_frame = ttk.Frame(self.filter_frame)
        amount_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=2)

        ttk.Label(amount_frame, text="Min:").grid(row=0, column=0, sticky=tk.W)
        self.min_amount_var = tk.StringVar()
        ttk.Entry(amount_frame, textvariable=self.min_amount_var, width=12).grid(row=0, column=1, padx=2)

        ttk.Label(amount_frame, text="Max:").grid(row=1, column=0, sticky=tk.W)
        self.max_amount_var = tk.StringVar()
        ttk.Entry(amount_frame, textvariable=self.max_amount_var, width=12).grid(row=1, column=1, padx=2)

        # Transaction type filter
        ttk.Label(self.filter_frame, text="Type:").grid(row=4, column=0, sticky=tk.W, pady=(10, 2))
        self.type_var = tk.StringVar(value="All")
        type_combo = ttk.Combobox(self.filter_frame, textvariable=self.type_var,
                                 values=["All", "Credits", "Debits"], state="readonly", width=15)
        type_combo.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E, pady=2)

        # Filter buttons
        button_frame = ttk.Frame(self.filter_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(button_frame, text="Apply Filters", command=self._apply_filters).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear", command=self._clear_filters).pack(side=tk.LEFT, padx=2)

    def _create_summary_panel(self, parent):
        """Create the summary panel."""
        self.summary_frame = ttk.LabelFrame(parent, text="Summary", padding=10)
        self.summary_frame.pack(fill=tk.BOTH, expand=True)

        # Summary labels (will be populated dynamically)
        self.summary_labels = {}

    def _create_transaction_table(self, parent):
        """Create the transaction table."""
        # Table frame with scrollbars
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview
        columns = ("Date", "Description", "Amount", "Balance", "Category", "Reference")
        self.transaction_tree = ttk.Treeview(table_frame, columns=columns, show="tree headings")

        # Configure columns
        self.transaction_tree.column("#0", width=0, stretch=False)  # Hide tree column
        self.transaction_tree.column("Date", width=100, anchor=tk.CENTER)
        self.transaction_tree.column("Description", width=300, anchor=tk.W)
        self.transaction_tree.column("Amount", width=120, anchor=tk.E)
        self.transaction_tree.column("Balance", width=120, anchor=tk.E)
        self.transaction_tree.column("Category", width=150, anchor=tk.W)
        self.transaction_tree.column("Reference", width=100, anchor=tk.W)

        # Configure headings
        for col in columns:
            self.transaction_tree.heading(col, text=col, command=lambda c=col: self._sort_by_column(c))

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.transaction_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.transaction_tree.xview)

        self.transaction_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack components
        self.transaction_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind double-click event
        self.transaction_tree.bind("<Double-1>", self._on_transaction_double_click)

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_text = tk.StringVar()
        self.status_text.set("Ready")
        ttk.Label(self.status_bar, textvariable=self.status_text).pack(side=tk.LEFT, padx=5, pady=2)

    def _initialize_filter_vars(self):
        """Initialize filter variables."""
        self.search_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        self.min_amount_var = tk.StringVar()
        self.max_amount_var = tk.StringVar()
        self.type_var = tk.StringVar(value="All")

    def _populate_transaction_tree(self):
        """Populate the transaction tree with current data."""
        if not self.transaction_tree:
            return

        # Clear existing items
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)

        # Add transactions
        for i, transaction in enumerate(self.filtered_transactions):
            # Format values
            date_str = format_date_display(transaction.date)
            desc_str = transaction.description[:50] + "..." if len(transaction.description) > 50 else transaction.description
            amount_str = format_currency(transaction.amount)
            balance_str = format_currency(transaction.balance) if transaction.balance else ""
            category_str = transaction.category or ""
            reference_str = transaction.reference or ""

            # Insert item
            item_id = self.transaction_tree.insert("", tk.END, values=(
                date_str, desc_str, amount_str, balance_str, category_str, reference_str
            ))

            # Color coding for amounts
            if transaction.amount:
                color = get_amount_color(transaction.amount)
                if color:
                    self.transaction_tree.set(item_id, "Amount", amount_str)
                    # Note: tkinter treeview doesn't support per-cell coloring easily
                    # This would require custom styling or tags

        self.status_text.set(f"Showing {len(self.filtered_transactions)} transactions")

    def _update_summary_panel(self):
        """Update the summary panel with current data statistics."""
        if not self.summary_frame or not self.filtered_transactions:
            return

        # Clear existing labels
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        # Calculate statistics
        transactions = self.filtered_transactions
        total_count = len(transactions)

        amounts = [t.amount for t in transactions if t.amount]
        credits = [a for a in amounts if a > 0]
        debits = [a for a in amounts if a < 0]

        total_amount = sum(amounts) if amounts else Decimal('0')
        total_credits = sum(credits) if credits else Decimal('0')
        total_debits = sum(debits) if debits else Decimal('0')

        # Create summary labels
        row = 0

        ttk.Label(self.summary_frame, text="Transaction Count:", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(self.summary_frame, text=str(total_count)).grid(row=row, column=1, sticky=tk.E, pady=2)
        row += 1

        ttk.Label(self.summary_frame, text="Total Amount:", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(self.summary_frame, text=format_currency(total_amount)).grid(row=row, column=1, sticky=tk.E, pady=2)
        row += 1

        if credits:
            ttk.Label(self.summary_frame, text="Total Credits:", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Label(self.summary_frame, text=f"{format_currency(total_credits)} ({len(credits)})").grid(row=row, column=1, sticky=tk.E, pady=2)
            row += 1

        if debits:
            ttk.Label(self.summary_frame, text="Total Debits:", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Label(self.summary_frame, text=f"{format_currency(total_debits)} ({len(debits)})").grid(row=row, column=1, sticky=tk.E, pady=2)
            row += 1

        if amounts:
            avg_amount = total_amount / len(amounts)
            ttk.Label(self.summary_frame, text="Average:", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Label(self.summary_frame, text=format_currency(avg_amount)).grid(row=row, column=1, sticky=tk.E, pady=2)
            row += 1

        # Configure column weights
        self.summary_frame.columnconfigure(1, weight=1)

    def _apply_filters(self):
        """Apply current filters to transaction data."""
        if not self.current_transaction_set:
            return

        transactions = self.current_transaction_set.transactions
        filtered = []

        # Get filter values
        search_text = self.search_var.get().lower().strip()
        start_date_str = self.start_date_var.get().strip()
        end_date_str = self.end_date_var.get().strip()
        min_amount_str = self.min_amount_var.get().strip()
        max_amount_str = self.max_amount_var.get().strip()
        transaction_type = self.type_var.get()

        for transaction in transactions:
            # Text search filter
            if search_text and search_text not in transaction.description.lower():
                continue

            # Date range filter
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                    if transaction.date < start_date:
                        continue
                except ValueError:
                    pass  # Invalid date format, skip filter

            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                    if transaction.date > end_date:
                        continue
                except ValueError:
                    pass  # Invalid date format, skip filter

            # Amount range filter
            if min_amount_str:
                try:
                    min_amount = Decimal(min_amount_str)
                    if transaction.amount < min_amount:
                        continue
                except (ValueError, TypeError):
                    pass  # Invalid amount format, skip filter

            if max_amount_str:
                try:
                    max_amount = Decimal(max_amount_str)
                    if transaction.amount > max_amount:
                        continue
                except (ValueError, TypeError):
                    pass  # Invalid amount format, skip filter

            # Transaction type filter
            if transaction_type == "Credits" and transaction.amount <= 0:
                continue
            elif transaction_type == "Debits" and transaction.amount >= 0:
                continue

            filtered.append(transaction)

        self.filtered_transactions = filtered
        self._populate_transaction_tree()
        self._update_summary_panel()

    def _clear_filters(self):
        """Clear all filters and show all transactions."""
        self.search_var.set("")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.min_amount_var.set("")
        self.max_amount_var.set("")
        self.type_var.set("All")

        if self.current_transaction_set:
            self.filtered_transactions = self.current_transaction_set.transactions.copy()
            self._populate_transaction_tree()
            self._update_summary_panel()

    def _clear_search(self):
        """Clear the search field."""
        self.search_var.set("")
        self._apply_filters()

    def _on_search_change(self, event):
        """Handle search field changes."""
        self._apply_filters()

    def _sort_by_column(self, column):
        """Sort transactions by the specified column."""
        if not self.filtered_transactions:
            return

        reverse = False  # You could implement toggle logic here

        if column == "Date":
            self.filtered_transactions.sort(key=lambda t: t.date or date.min, reverse=reverse)
        elif column == "Description":
            self.filtered_transactions.sort(key=lambda t: t.description.lower(), reverse=reverse)
        elif column == "Amount":
            self.filtered_transactions.sort(key=lambda t: t.amount or Decimal('0'), reverse=reverse)
        elif column == "Balance":
            self.filtered_transactions.sort(key=lambda t: t.balance or Decimal('0'), reverse=reverse)
        elif column == "Category":
            self.filtered_transactions.sort(key=lambda t: (t.category or "").lower(), reverse=reverse)
        elif column == "Reference":
            self.filtered_transactions.sort(key=lambda t: (t.reference or "").lower(), reverse=reverse)

        self._populate_transaction_tree()

    def _on_transaction_double_click(self, event):
        """Handle double-click on transaction item."""
        selection = self.transaction_tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.transaction_tree.item(item, 'values')

        if values:
            # Show transaction details in a popup
            self._show_transaction_details(values)

    def _show_transaction_details(self, values):
        """Show detailed transaction information in a popup."""
        details_window = tk.Toplevel(self.root)
        details_window.title("Transaction Details")
        details_window.geometry("400x300")
        details_window.resizable(False, False)

        # Make window modal
        details_window.transient(self.root)
        details_window.grab_set()

        # Display transaction details
        labels = ["Date:", "Description:", "Amount:", "Balance:", "Category:", "Reference:"]

        for i, (label, value) in enumerate(zip(labels, values)):
            ttk.Label(details_window, text=label, font=("TkDefaultFont", 9, "bold")).grid(
                row=i, column=0, sticky=tk.W, padx=10, pady=5
            )
            ttk.Label(details_window, text=value, wraplength=250).grid(
                row=i, column=1, sticky=tk.W, padx=10, pady=5
            )

        # Close button
        ttk.Button(details_window, text="Close", command=details_window.destroy).grid(
            row=len(labels), column=0, columnspan=2, pady=20
        )

    def _refresh_view(self):
        """Refresh the current view."""
        if self.current_transaction_set:
            self._populate_transaction_tree()
            self._update_summary_panel()

    def _export_csv(self):
        """Export filtered transactions to CSV."""
        if not self.filtered_transactions:
            messagebox.showwarning("No Data", "No transactions to export.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export to CSV"
        )

        if filename:
            try:
                # Create a temporary transaction set with filtered data
                temp_metadata = self.current_transaction_set.metadata
                temp_transaction_set = TransactionSet(
                    transactions=self.filtered_transactions,
                    metadata=temp_metadata
                )

                path = self.display_manager.export_to_csv(temp_transaction_set, filename)
                messagebox.showinfo("Export Successful", f"Data exported to {path}")

            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data: {e}")

    def _export_excel(self):
        """Export filtered transactions to Excel."""
        if not self.filtered_transactions:
            messagebox.showwarning("No Data", "No transactions to export.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Export to Excel"
        )

        if filename:
            try:
                # Create a temporary transaction set with filtered data
                temp_metadata = self.current_transaction_set.metadata
                temp_transaction_set = TransactionSet(
                    transactions=self.filtered_transactions,
                    metadata=temp_metadata
                )

                path = self.display_manager.export_to_excel(temp_transaction_set, filename)
                messagebox.showinfo("Export Successful", f"Data exported to {path}")

            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data: {e}")

    def _export_json(self):
        """Export filtered transactions to JSON."""
        if not self.filtered_transactions:
            messagebox.showwarning("No Data", "No transactions to export.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export to JSON"
        )

        if filename:
            try:
                from ...src.json_adapter import JSONAdapter

                # Create a temporary transaction set with filtered data
                temp_metadata = self.current_transaction_set.metadata
                temp_transaction_set = TransactionSet(
                    transactions=self.filtered_transactions,
                    metadata=temp_metadata
                )

                adapter = JSONAdapter(self.config_manager)
                path = adapter.export_to_json(temp_transaction_set, filename)
                messagebox.showinfo("Export Successful", f"Data exported to {path}")

            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data: {e}")

    def _show_monthly_summary(self):
        """Show monthly summary in console."""
        if self.current_transaction_set:
            print("\n" + "="*60)
            print("MONTHLY SUMMARY")
            print("="*60)
            self.display_manager.show_monthly_summary(self.current_transaction_set)

    def _show_category_analysis(self):
        """Show category analysis in console."""
        if self.current_transaction_set:
            print("\n" + "="*60)
            print("CATEGORY ANALYSIS")
            print("="*60)
            self.display_manager.show_category_analysis(self.current_transaction_set.transactions)

    def run(self, transaction_set: TransactionSet):
        """
        Run the visual display with the given transaction set.

        This is a convenience method that shows transactions and starts the mainloop.
        The window will remain open until the user closes it.

        Args:
            transaction_set: TransactionSet to display
        """
        self.show_transactions(transaction_set, start_mainloop=True)

    def _on_closing(self):
        """Handle window closing."""
        if self.root:
            self.root.quit()  # Exit the mainloop
            self.root.destroy()  # Destroy the window
            self.root = None

    def close(self):
        """Close the display manager and clean up resources."""
        if self.root:
            self.root.quit()  # Exit the mainloop if running
            self.root.destroy()
            self.root = None
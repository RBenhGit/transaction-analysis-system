"""
Utility functions for the visual display module.

This module provides helper functions for formatting, styling, and data processing
specifically for the visual display components.
"""

from typing import Optional, Dict, Any, List
from datetime import date, datetime
from decimal import Decimal
import tkinter as tk


def format_currency(amount: Optional[Decimal], currency_symbol: str = "₪") -> str:
    """
    Format a decimal amount as currency string.

    Args:
        amount: Decimal amount to format
        currency_symbol: Currency symbol to use

    Returns:
        Formatted currency string
    """
    if amount is None:
        return ""

    # Format with thousands separator and 2 decimal places
    formatted = f"{currency_symbol}{amount:,.2f}"
    return formatted


def format_date_display(date_obj: Optional[date]) -> str:
    """
    Format a date object for display in the GUI.

    Args:
        date_obj: Date object to format

    Returns:
        Formatted date string
    """
    if date_obj is None:
        return ""

    return date_obj.strftime("%Y-%m-%d")


def get_amount_color(amount: Optional[Decimal]) -> Optional[str]:
    """
    Get color code for amount display based on positive/negative value.

    Args:
        amount: Amount to get color for

    Returns:
        Color string or None if no special color needed
    """
    if amount is None:
        return None

    if amount > 0:
        return "green"  # Credits in green
    elif amount < 0:
        return "red"    # Debits in red
    else:
        return None     # Zero amounts in default color


def create_filter_query(
    search_text: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    transaction_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a filter query dictionary from filter parameters.

    Args:
        search_text: Text to search in descriptions
        start_date: Start date for date range filter
        end_date: End date for date range filter
        min_amount: Minimum amount filter
        max_amount: Maximum amount filter
        transaction_type: Type filter ("Credits", "Debits", or "All")

    Returns:
        Dictionary containing filter parameters
    """
    query = {}

    if search_text and search_text.strip():
        query["search_text"] = search_text.strip().lower()

    if start_date:
        query["start_date"] = start_date

    if end_date:
        query["end_date"] = end_date

    if min_amount is not None:
        query["min_amount"] = min_amount

    if max_amount is not None:
        query["max_amount"] = max_amount

    if transaction_type and transaction_type != "All":
        query["transaction_type"] = transaction_type

    return query


def apply_transaction_filter(transactions: List, filter_query: Dict[str, Any]) -> List:
    """
    Apply filter query to a list of transactions.

    Args:
        transactions: List of transaction objects
        filter_query: Filter query dictionary

    Returns:
        Filtered list of transactions
    """
    filtered = []

    for transaction in transactions:
        # Text search filter
        search_text = filter_query.get("search_text")
        if search_text and search_text not in transaction.description.lower():
            continue

        # Date range filter
        start_date = filter_query.get("start_date")
        if start_date and transaction.date < start_date:
            continue

        end_date = filter_query.get("end_date")
        if end_date and transaction.date > end_date:
            continue

        # Amount range filter
        min_amount = filter_query.get("min_amount")
        if min_amount is not None and transaction.amount < min_amount:
            continue

        max_amount = filter_query.get("max_amount")
        if max_amount is not None and transaction.amount > max_amount:
            continue

        # Transaction type filter
        transaction_type = filter_query.get("transaction_type")
        if transaction_type == "Credits" and transaction.amount <= 0:
            continue
        elif transaction_type == "Debits" and transaction.amount >= 0:
            continue

        filtered.append(transaction)

    return filtered


def calculate_summary_stats(transactions: List) -> Dict[str, Any]:
    """
    Calculate summary statistics for a list of transactions.

    Args:
        transactions: List of transaction objects

    Returns:
        Dictionary containing summary statistics
    """
    if not transactions:
        return {
            "count": 0,
            "total_amount": Decimal('0'),
            "total_credits": Decimal('0'),
            "total_debits": Decimal('0'),
            "credit_count": 0,
            "debit_count": 0,
            "average_amount": Decimal('0'),
            "date_range": None
        }

    amounts = [t.amount for t in transactions if t.amount is not None]
    credits = [a for a in amounts if a > 0]
    debits = [a for a in amounts if a < 0]

    total_amount = sum(amounts) if amounts else Decimal('0')
    total_credits = sum(credits) if credits else Decimal('0')
    total_debits = sum(debits) if debits else Decimal('0')

    # Date range
    dates = [t.date for t in transactions if t.date]
    date_range = None
    if dates:
        date_range = {
            "start": min(dates),
            "end": max(dates)
        }

    return {
        "count": len(transactions),
        "total_amount": total_amount,
        "total_credits": total_credits,
        "total_debits": total_debits,
        "credit_count": len(credits),
        "debit_count": len(debits),
        "average_amount": total_amount / len(amounts) if amounts else Decimal('0'),
        "date_range": date_range
    }


def format_summary_text(stats: Dict[str, Any]) -> str:
    """
    Format summary statistics as human-readable text.

    Args:
        stats: Summary statistics dictionary

    Returns:
        Formatted summary text
    """
    lines = []

    lines.append(f"Total Transactions: {stats['count']:,}")

    if stats['count'] > 0:
        lines.append(f"Total Amount: {format_currency(stats['total_amount'])}")

        if stats['credit_count'] > 0:
            lines.append(f"Credits: {format_currency(stats['total_credits'])} ({stats['credit_count']} transactions)")

        if stats['debit_count'] > 0:
            lines.append(f"Debits: {format_currency(stats['total_debits'])} ({stats['debit_count']} transactions)")

        if stats['average_amount']:
            lines.append(f"Average: {format_currency(stats['average_amount'])}")

        date_range = stats.get('date_range')
        if date_range:
            start_str = format_date_display(date_range['start'])
            end_str = format_date_display(date_range['end'])
            lines.append(f"Date Range: {start_str} to {end_str}")

    return "\n".join(lines)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with optional suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def validate_date_string(date_str: str, date_format: str = "%Y-%m-%d") -> Optional[date]:
    """
    Validate and parse a date string.

    Args:
        date_str: Date string to validate
        date_format: Expected date format

    Returns:
        Parsed date object or None if invalid
    """
    if not date_str.strip():
        return None

    try:
        return datetime.strptime(date_str.strip(), date_format).date()
    except ValueError:
        return None


def validate_amount_string(amount_str: str) -> Optional[Decimal]:
    """
    Validate and parse an amount string.

    Args:
        amount_str: Amount string to validate

    Returns:
        Parsed Decimal amount or None if invalid
    """
    if not amount_str.strip():
        return None

    try:
        # Remove common formatting characters
        cleaned = amount_str.strip().replace(",", "").replace("₪", "").replace("$", "")
        return Decimal(cleaned)
    except (ValueError, TypeError):
        return None


def create_gui_styles() -> Dict[str, Dict[str, Any]]:
    """
    Create style definitions for GUI components.

    Returns:
        Dictionary of style definitions
    """
    return {
        "header": {
            "font": ("TkDefaultFont", 10, "bold"),
            "fg": "#333333"
        },
        "positive_amount": {
            "fg": "#008000"  # Green
        },
        "negative_amount": {
            "fg": "#CC0000"  # Red
        },
        "neutral_amount": {
            "fg": "#000000"  # Black
        },
        "summary_label": {
            "font": ("TkDefaultFont", 9, "bold"),
            "fg": "#555555"
        },
        "summary_value": {
            "font": ("TkDefaultFont", 9),
            "fg": "#000000"
        }
    }


def center_window(window, width: int, height: int):
    """
    Center a tkinter window on the screen.

    Args:
        window: Tkinter window object
        width: Window width
        height: Window height
    """
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # Set window geometry
    window.geometry(f"{width}x{height}+{x}+{y}")


def create_tooltip(widget, text: str):
    """
    Create a simple tooltip for a widget.

    Args:
        widget: Tkinter widget
        text: Tooltip text
    """
    def on_enter(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

        label = tk.Label(
            tooltip,
            text=text,
            background="lightyellow",
            relief="solid",
            borderwidth=1,
            font=("TkDefaultFont", 8)
        )
        label.pack()

        widget.tooltip = tooltip

    def on_leave(event):
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
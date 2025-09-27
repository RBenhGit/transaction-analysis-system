"""
Visual Display Module for Transaction Analysis System

This module provides graphical user interface components for visualizing
and interacting with transaction data through tkinter-based GUI elements.

Available Components:
- VisualDisplayManager: Main GUI interface for transaction viewing
- FilterPanel: Transaction filtering and search capabilities
- SummaryPanel: Financial summary and statistics display
- ExportPanel: GUI for data export operations

Features:
- Interactive transaction table with sorting and filtering
- Real-time search and data filtering
- Visual summary statistics and key metrics
- Integrated export capabilities for multiple formats
- Responsive GUI design with proper scaling

Usage:
    from modules.visual_display import VisualDisplayManager

    display_manager = VisualDisplayManager()
    display_manager.show_transactions(transaction_set)
"""

__version__ = "1.0.0"
__author__ = "Transaction Analysis System"

# Module metadata
MODULE_NAME = "visual_display"
MODULE_DESCRIPTION = "GUI-based visual display and interaction for transaction data"
DEPENDENCIES = ["tkinter", "pandas", "tabulate"]

# Import main classes
from .core_module import VisualDisplayManager
from .utils import (
    format_currency,
    format_date_display,
    get_amount_color,
    create_filter_query
)

def get_module_info():
    """Get information about this module."""
    return {
        "name": MODULE_NAME,
        "version": __version__,
        "description": MODULE_DESCRIPTION,
        "dependencies": DEPENDENCIES
    }

__all__ = [
    "VisualDisplayManager",
    "format_currency",
    "format_date_display",
    "get_amount_color",
    "create_filter_query",
    "get_module_info"
]
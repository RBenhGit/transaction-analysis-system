"""
Analytics Module for Transaction Analysis System

This module provides data analysis and statistical functions for transaction data.
It includes capabilities for:
- Statistical analysis of transaction patterns
- Trend analysis and forecasting
- Spending categorization and insights
- Financial health metrics

Available Components:
- transaction_analyzer: Core transaction analysis functions
- trend_analyzer: Time series analysis and trend detection
- category_analyzer: Spending category analysis
- metrics_calculator: Financial metrics and KPIs

Usage:
    from modules.analytics import TransactionAnalyzer

    analyzer = TransactionAnalyzer()
    insights = analyzer.analyze_transactions(transaction_data)
"""

__version__ = "1.0.0"
__author__ = "Transaction Analysis System"

# Module metadata
MODULE_NAME = "analytics"
MODULE_DESCRIPTION = "Data analysis and statistical functions"
DEPENDENCIES = ["pandas", "numpy", "scipy"]

def get_module_info():
    """Get information about this module."""
    return {
        "name": MODULE_NAME,
        "version": __version__,
        "description": MODULE_DESCRIPTION,
        "dependencies": DEPENDENCIES
    }
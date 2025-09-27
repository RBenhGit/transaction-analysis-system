"""
Visualization Module for Transaction Analysis System

This module provides chart and graph generation capabilities for transaction data.
It includes support for various chart types and export formats for data visualization.

Available Components:
- chart_generator: Core chart generation functions
- dashboard_builder: Interactive dashboard creation
- report_visualizer: Report-ready chart generation
- export_manager: Chart export and formatting

Supported Chart Types:
- Line charts for trends over time
- Bar charts for category comparisons
- Pie charts for spending distribution
- Scatter plots for correlation analysis
- Histograms for amount distribution

Usage:
    from modules.visualization import ChartGenerator

    generator = ChartGenerator()
    chart = generator.create_spending_chart(transaction_data)
"""

__version__ = "1.0.0"
__author__ = "Transaction Analysis System"

# Module metadata
MODULE_NAME = "visualization"
MODULE_DESCRIPTION = "Chart and graph generation for transaction data"
DEPENDENCIES = ["matplotlib", "seaborn", "plotly", "pandas"]

def get_module_info():
    """Get information about this module."""
    return {
        "name": MODULE_NAME,
        "version": __version__,
        "description": MODULE_DESCRIPTION,
        "dependencies": DEPENDENCIES
    }
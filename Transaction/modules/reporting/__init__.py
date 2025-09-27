"""
Reporting Module for Transaction Analysis System

This module provides report generation and formatting capabilities for transaction data.
It supports various report formats and templates for different use cases.

Available Components:
- report_generator: Core report generation functions
- template_manager: Report template handling
- formatter: Report formatting and styling
- export_manager: Multi-format export capabilities

Supported Report Types:
- Monthly financial summaries
- Annual spending reports
- Category breakdown reports
- Trend analysis reports
- Custom analytical reports

Export Formats:
- PDF reports with charts and tables
- Excel workbooks with multiple sheets
- HTML reports with interactive elements
- CSV data exports

Usage:
    from modules.reporting import ReportGenerator

    generator = ReportGenerator()
    report = generator.create_monthly_report(transaction_data)
"""

__version__ = "1.0.0"
__author__ = "Transaction Analysis System"

# Module metadata
MODULE_NAME = "reporting"
MODULE_DESCRIPTION = "Report generation and formatting"
DEPENDENCIES = ["reportlab", "openpyxl", "jinja2", "pandas"]

def get_module_info():
    """Get information about this module."""
    return {
        "name": MODULE_NAME,
        "version": __version__,
        "description": MODULE_DESCRIPTION,
        "dependencies": DEPENDENCIES
    }
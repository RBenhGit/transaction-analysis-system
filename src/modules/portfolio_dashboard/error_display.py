"""
Streamlit Error Display Component.

User-friendly error messaging for portfolio dashboard with actionable guidance.
"""

import streamlit as st
from typing import Dict, Any, List, Optional


def display_error_summary(error_summary: Dict[str, Any]):
    """
    Display comprehensive error summary in Streamlit.

    Args:
        error_summary: Error summary from ErrorCollector.get_error_summary()
    """
    if not error_summary:
        return

    total_errors = error_summary.get('total_errors', 0)
    total_warnings = error_summary.get('total_warnings', 0)

    if total_errors == 0 and total_warnings == 0:
        return

    # Show summary header
    st.markdown("---")
    st.subheader("⚠️ Data Quality Report")

    # Display metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Errors",
            total_errors,
            delta=None,
            help="Critical errors that prevented processing"
        )
    with col2:
        st.metric(
            "Warnings",
            total_warnings,
            delta=None,
            help="Non-critical issues that were handled automatically"
        )

    # Show error breakdown by type
    if total_errors > 0:
        st.markdown("#### Error Breakdown")
        error_types = error_summary.get('error_types', {})

        if error_types:
            for error_type, count in error_types.items():
                st.warning(f"**{error_type}**: {count} occurrence(s)")

    # Expandable detailed errors
    if total_errors > 0:
        with st.expander("🔍 View Detailed Errors", expanded=False):
            display_error_details(error_summary.get('errors', []))

    # Expandable warnings
    if total_warnings > 0:
        with st.expander("📋 View Warnings", expanded=False):
            warnings = error_summary.get('warnings', [])
            for idx, warning in enumerate(warnings, 1):
                st.info(f"{idx}. {warning}")


def display_error_details(errors: List[Dict[str, Any]]):
    """
    Display detailed error information with user guidance.

    Args:
        errors: List of error dictionaries
    """
    for idx, error in enumerate(errors, 1):
        error_type = error.get('error_type', 'Unknown Error')
        message = error.get('message', 'No message provided')
        details = error.get('details', {})

        # Create collapsible error entry
        with st.container():
            st.markdown(f"**Error {idx}: {error_type}**")
            st.error(message)

            # Show details if available
            if details:
                st.json(details)

            # Provide actionable guidance based on error type
            guidance = _get_error_guidance(error_type, details)
            if guidance:
                st.info(f"💡 **How to fix:** {guidance}")

            st.markdown("---")


def display_validation_errors(builder):
    """
    Display portfolio builder errors in a user-friendly format.

    Args:
        builder: PortfolioBuilder instance with error_collector
    """
    if not hasattr(builder, 'error_collector'):
        return

    if not builder.has_errors() and not builder.has_warnings():
        st.success("✅ All transactions processed successfully with no errors!")
        return

    error_summary = builder.get_error_summary()
    display_error_summary(error_summary)


def show_file_loading_error(filename: str, error_message: str):
    """
    Show user-friendly error message for file loading failures.

    Args:
        filename: Name of the file that failed to load
        error_message: Technical error message
    """
    st.error(f"❌ Failed to load file: **{filename}**")

    # Categorize error and provide specific guidance
    if "FileNotFoundError" in error_message or "No such file" in error_message:
        st.warning(
            "**File not found.** Please check:\n"
            "- The file exists in the Data_Files directory\n"
            "- The filename is spelled correctly\n"
            "- The file hasn't been moved or deleted"
        )
    elif "PermissionError" in error_message or "Permission denied" in error_message:
        st.warning(
            "**Permission denied.** Please:\n"
            "- Close the Excel file if it's open in another program\n"
            "- Check file permissions\n"
            "- Try running the application as administrator"
        )
    elif "missing required columns" in error_message.lower():
        st.warning(
            "**Incorrect file format.** This file is missing required columns.\n\n"
            "**Required IBI columns (in Hebrew):**\n"
            "- תאריך (Date)\n"
            "- סוג פעולה (Transaction Type)\n"
            "- שם נייר (Security Name)\n"
            "- מס' נייר / סימבול (Symbol)\n"
            "- כמות (Quantity)\n"
            "- מטבע (Currency)\n"
            "- יתרה שקלית (Balance)\n\n"
            "Please ensure you're using an IBI securities trading statement file."
        )
    elif "parse" in error_message.lower() or "date" in error_message.lower():
        st.warning(
            "**Date format issue.** The dates in this file couldn't be parsed.\n\n"
            "Expected format: DD/MM/YYYY (e.g., 31/12/2024)\n\n"
            "Please check that date columns are formatted correctly in Excel."
        )
    else:
        st.warning(
            "**Unexpected error occurred.**\n\n"
            "Technical details:\n"
            f"```\n{error_message}\n```\n\n"
            "Try:\n"
            "- Re-downloading the file from IBI\n"
            "- Checking the file isn't corrupted\n"
            "- Verifying it's an Excel file (.xlsx or .xls)"
        )


def show_empty_portfolio_message():
    """Display helpful message when portfolio is empty."""
    st.info(
        "📭 **Portfolio is empty**\n\n"
        "This could mean:\n"
        "- No transaction files have been loaded yet\n"
        "- All positions have been closed (sold completely)\n"
        "- Transaction files don't contain any buy/sell transactions\n\n"
        "**Next steps:**\n"
        "1. Load IBI transaction files from the Data_Files directory\n"
        "2. Ensure files contain securities trading data (not just dividends/fees)\n"
        "3. Check that files are in the correct IBI format"
    )


def show_data_quality_warning(warning_type: str, details: Optional[str] = None):
    """
    Show specific data quality warnings with guidance.

    Args:
        warning_type: Type of warning (e.g., 'missing_dates', 'invalid_symbols')
        details: Additional context about the warning
    """
    warnings_config = {
        'missing_dates': {
            'icon': '📅',
            'title': 'Some dates could not be parsed',
            'message': 'These transactions were skipped. Check Excel date formatting.',
            'action': 'Ensure dates are in DD/MM/YYYY format in Excel.'
        },
        'invalid_symbols': {
            'icon': '🔤',
            'title': 'Some security symbols are missing or invalid',
            'message': 'Transactions without valid symbols were excluded.',
            'action': 'Verify security symbols in the IBI statement.'
        },
        'currency_mismatch': {
            'icon': '💱',
            'title': 'Currency inconsistencies detected',
            'message': 'Some transactions have mismatched currencies for the same security.',
            'action': 'Review transactions and ensure currency consistency.'
        },
        'insufficient_shares': {
            'icon': '📉',
            'title': 'Cannot sell more shares than owned',
            'message': 'Some sell transactions were skipped due to insufficient shares.',
            'action': 'Check transaction chronology and verify data completeness.'
        },
        'negative_quantities': {
            'icon': '⚠️',
            'title': 'Negative quantities detected',
            'message': 'Transactions with negative quantities were skipped.',
            'action': 'Review transaction data for data entry errors.'
        }
    }

    config = warnings_config.get(warning_type, {
        'icon': '⚠️',
        'title': 'Data quality issue detected',
        'message': details or 'Please review your data.',
        'action': 'Check the transaction file for errors.'
    })

    st.warning(
        f"{config['icon']} **{config['title']}**\n\n"
        f"{config['message']}\n\n"
        f"**Action:** {config['action']}"
    )


def _get_error_guidance(error_type: str, details: Dict) -> str:
    """
    Get user-friendly guidance for specific error types.

    Args:
        error_type: Type of error
        details: Error details dictionary

    Returns:
        Helpful guidance message
    """
    guidance_map = {
        'InsufficientSharesError': (
            "You're trying to sell more shares than you own. This usually means:\n"
            "1. Transaction files are incomplete (missing earlier buy transactions)\n"
            "2. Transactions are out of chronological order\n"
            "3. There's a data error in the IBI statement\n\n"
            "Check your transaction history and ensure all files are loaded."
        ),
        'CurrencyMismatchError': (
            "A security is being traded in different currencies. This is unusual and may indicate:\n"
            "1. Data entry error in the IBI statement\n"
            "2. Symbol reuse for different securities\n\n"
            "Review the transactions for this security and verify the currency."
        ),
        'NegativeQuantityError': (
            "A transaction has a negative quantity. This is a data quality issue.\n"
            "Quantities should always be positive (the transaction type determines buy/sell).\n\n"
            "Check the IBI Excel file and correct the quantity value."
        ),
        'MissingRequiredFieldError': (
            "Required data is missing from a transaction.\n\n"
            "Ensure all rows in the Excel file have:\n"
            "- Security symbol\n"
            "- Security name\n"
            "- Transaction type\n"
            "- Date"
        ),
        'InvalidDateError': (
            "A date value couldn't be parsed.\n\n"
            "Expected format: DD/MM/YYYY\n"
            "Example: 31/12/2024\n\n"
            "Fix the date in Excel and reload the file."
        ),
        'TransactionProcessingError': (
            "An error occurred while processing a transaction.\n"
            "This transaction was skipped. Review the error details above and:\n"
            "1. Check the data in the Excel file\n"
            "2. Ensure all required fields are present\n"
            "3. Verify data types are correct (numbers for quantities, dates for dates, etc.)"
        ),
        'PositionCalculationError': (
            "An error occurred during position calculation.\n"
            "This usually indicates:\n"
            "1. Invalid numeric values (division by zero, etc.)\n"
            "2. Data type issues\n\n"
            "Review the transaction data and ensure all numeric fields contain valid numbers."
        )
    }

    return guidance_map.get(error_type, "Review the error details and check your data for issues.")


def show_processing_summary(
    total_transactions: int,
    processed: int,
    skipped: int,
    errors: int,
    warnings: int
):
    """
    Display processing summary with visual indicators.

    Args:
        total_transactions: Total number of transactions in source
        processed: Number successfully processed
        skipped: Number skipped due to errors
        errors: Number of errors
        warnings: Number of warnings
    """
    st.markdown("---")
    st.subheader("📊 Processing Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Transactions", total_transactions)

    with col2:
        success_rate = (processed / total_transactions * 100) if total_transactions > 0 else 0
        st.metric(
            "Processed",
            processed,
            delta=f"{success_rate:.1f}%",
            help="Successfully processed transactions"
        )

    with col3:
        st.metric(
            "Skipped",
            skipped,
            delta=f"-{skipped}" if skipped > 0 else None,
            delta_color="inverse",
            help="Transactions skipped due to errors"
        )

    with col4:
        st.metric(
            "Issues",
            errors + warnings,
            help=f"{errors} errors, {warnings} warnings"
        )

    # Show status indicator
    if errors == 0 and warnings == 0:
        st.success("✅ Perfect! All transactions processed without issues.")
    elif errors == 0:
        st.info(f"✓ Completed with {warnings} warning(s). Review warnings above.")
    elif skipped < total_transactions * 0.1:  # Less than 10% failed
        st.warning(f"⚠️ Completed with {errors} error(s). Some transactions were skipped.")
    else:
        st.error(f"❌ Significant issues detected. {skipped} transactions couldn't be processed.")

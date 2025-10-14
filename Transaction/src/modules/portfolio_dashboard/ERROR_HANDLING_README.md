# Portfolio Dashboard Error Handling System

## Overview

Comprehensive error handling and data quality validation system for the Transaction Portfolio Dashboard. Provides robust error detection, user-friendly messaging, and detailed logging for troubleshooting.

## Components

### 1. Error Classes (`errors.py`)

Custom exception hierarchy for portfolio-specific errors:

- **PortfolioError** - Base exception for all portfolio errors
- **DataValidationError** - Data quality validation failures
- **TransactionProcessingError** - Transaction processing failures
- **PositionCalculationError** - Position calculation errors
- **InsufficientSharesError** - Attempting to sell more shares than owned
- **NegativeQuantityError** - Negative quantity detection
- **MissingRequiredFieldError** - Missing required data
- **InvalidDateError** - Invalid date format
- **CurrencyMismatchError** - Currency inconsistency

### 2. Error Collector (`errors.py`)

Batch error collection system that allows processing to continue despite errors:

```python
from src.modules.portfolio_dashboard.errors import ErrorCollector

# Create collector (fail_fast=False allows batch error collection)
collector = ErrorCollector(fail_fast=False)

# Add errors during processing
collector.add_error(error)
collector.add_warning(message)

# Get summary
summary = collector.get_error_summary()
print(f"Total errors: {summary['total_errors']}")
print(f"Error types: {summary['error_types']}")
```

### 3. Enhanced Portfolio Builder (`builder.py`)

PortfolioBuilder with comprehensive error handling:

```python
from src.modules.portfolio_dashboard.builder import PortfolioBuilder

# Create builder with error collection
builder = PortfolioBuilder(fail_fast=False)

# Build portfolio (errors are collected, not raised)
positions = builder.build(transactions)

# Check for errors
if builder.has_errors():
    error_summary = builder.get_error_summary()
    print(f"Errors occurred: {error_summary}")

# Check for warnings
if builder.has_warnings():
    print("Warnings detected - review data quality")
```

**Features:**
- Try-catch blocks around all critical operations
- Data validation before processing
- Currency consistency checks
- Insufficient shares detection
- Graceful degradation (skips invalid transactions)
- Detailed error logging

### 4. Enhanced IBI Adapter (`ibi_adapter.py`)

IBI adapter with robust Excel file validation:

```python
from src.adapters.ibi_adapter import IBIAdapter

adapter = IBIAdapter()

try:
    # Transform with comprehensive validation
    df = adapter.transform(raw_df)
except ValueError as e:
    # Get specific error message
    print(f"Validation failed: {e}")
```

**Features:**
- Column validation with missing column detection
- Date parsing with fallback strategies
- Numeric value validation (handles NaN, infinity)
- String field cleaning
- Empty field detection and removal
- Detailed logging of all issues

### 5. Streamlit Error Display (`error_display.py`)

User-friendly error messaging for Streamlit interface:

```python
from src.modules.portfolio_dashboard.error_display import (
    display_error_summary,
    display_validation_errors,
    show_file_loading_error,
    show_processing_summary
)

# Display error summary
error_summary = builder.get_error_summary()
display_error_summary(error_summary)

# Or use convenience function
display_validation_errors(builder)

# Show file loading errors
try:
    df = load_file(filename)
except Exception as e:
    show_file_loading_error(filename, str(e))

# Show processing summary
show_processing_summary(
    total_transactions=1000,
    processed=980,
    skipped=20,
    errors=15,
    warnings=5
)
```

**Features:**
- Color-coded error/warning indicators
- Expandable detailed error views
- Actionable guidance for each error type
- Context-specific help messages
- Processing statistics dashboard

### 6. Logging Configuration (`logging_config.py`)

Comprehensive logging with file rotation:

```python
from src.modules.portfolio_dashboard.logging_config import (
    setup_default_logging,
    TransactionLogger,
    create_error_report
)

# Setup logging at application start
logger_config = setup_default_logging(
    log_level="INFO",
    log_dir="logs",
    enable_file_logging=True
)

# Use logger in your module
import logging
logger = logging.getLogger(__name__)

logger.info("Processing started")
logger.warning("Data quality issue detected")
logger.error("Processing failed", exc_info=True)

# Log individual transactions
txn_logger = TransactionLogger(log_dir="logs")
txn_logger.log_transaction_processing(
    transaction_id="IBI_20240101_BUY_AAPL",
    symbol="AAPL",
    transaction_type="Buy",
    quantity=10.0,
    status="success"
)

# Generate error report
error_summary = builder.get_error_summary()
report = create_error_report(
    error_summary,
    output_file="logs/error_report.txt"
)
```

**Features:**
- Console and file logging
- Rotating log files (10 MB max, 5 backups)
- Separate error log file
- Transaction-level logging
- Structured log formatting
- Error report generation

## Error Handling Workflow

### 1. Application Startup

```python
# app.py or main entry point
from src.modules.portfolio_dashboard.logging_config import setup_default_logging

# Setup logging
logger_config = setup_default_logging(
    log_level="INFO",
    log_dir="logs",
    enable_file_logging=True
)
```

### 2. File Loading

```python
import streamlit as st
from src.modules.portfolio_dashboard.error_display import show_file_loading_error

try:
    # Load Excel file
    df = load_excel_file(filename)
except Exception as e:
    # Show user-friendly error
    show_file_loading_error(filename, str(e))
    st.stop()
```

### 3. Data Transformation

```python
from src.adapters.ibi_adapter import IBIAdapter
import logging

logger = logging.getLogger(__name__)
adapter = IBIAdapter()

try:
    # Transform with validation
    df_transformed = adapter.transform(df)
    logger.info(f"Successfully transformed {len(df_transformed)} rows")
except ValueError as e:
    logger.error(f"Transformation failed: {e}")
    st.error(f"Cannot process file: {e}")
    st.stop()
```

### 4. Portfolio Building

```python
from src.modules.portfolio_dashboard.builder import PortfolioBuilder
from src.modules.portfolio_dashboard.error_display import (
    display_validation_errors,
    show_processing_summary
)

# Create builder with error collection
builder = PortfolioBuilder(fail_fast=False)

# Build portfolio
positions = builder.build(transactions)

# Show validation results
display_validation_errors(builder)

# Show processing summary
if builder.has_errors() or builder.has_warnings():
    summary = builder.get_error_summary()
    show_processing_summary(
        total_transactions=len(transactions),
        processed=len(transactions) - summary['total_errors'],
        skipped=summary['total_errors'],
        errors=summary['total_errors'],
        warnings=summary['total_warnings']
    )
```

### 5. Error Reporting

```python
from src.modules.portfolio_dashboard.logging_config import create_error_report

# Generate detailed error report
if builder.has_errors():
    error_summary = builder.get_error_summary()

    # Create report file
    report = create_error_report(
        error_summary,
        output_file=f"logs/error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )

    # Offer download in Streamlit
    st.download_button(
        label="Download Error Report",
        data=report,
        file_name="error_report.txt",
        mime="text/plain"
    )
```

## Common Error Scenarios

### Scenario 1: Missing Required Columns

**Error:** `ValueError: IBI Excel file is missing required columns`

**Cause:** Excel file doesn't have expected IBI format

**User Guidance:**
```
Incorrect file format. This file is missing required columns.

Required IBI columns (in Hebrew):
- תאריך (Date)
- סוג פעולה (Transaction Type)
- שם נייר (Security Name)
- מס' נייר / סימבול (Symbol)
...

Please ensure you're using an IBI securities trading statement file.
```

### Scenario 2: Insufficient Shares

**Error:** `InsufficientSharesError`

**Cause:** Trying to sell more shares than owned

**User Guidance:**
```
Cannot sell more shares than you own. This usually means:
1. Transaction files are incomplete (missing earlier buy transactions)
2. Transactions are out of chronological order
3. There's a data error in the IBI statement

Check your transaction history and ensure all files are loaded.
```

### Scenario 3: Invalid Dates

**Error:** `InvalidDateError`

**Cause:** Date format doesn't match expected DD/MM/YYYY

**User Guidance:**
```
Date format issue. The dates in this file couldn't be parsed.

Expected format: DD/MM/YYYY (e.g., 31/12/2024)

Please check that date columns are formatted correctly in Excel.
```

### Scenario 4: Currency Mismatch

**Error:** `CurrencyMismatchError`

**Cause:** Same security traded in different currencies

**User Guidance:**
```
Currency mismatch detected.

A security is being traded in different currencies. This may indicate:
1. Data entry error in the IBI statement
2. Symbol reuse for different securities

Review the transactions for this security and verify the currency.
```

## Log Files

### Location

All log files are stored in the `logs/` directory:

```
logs/
├── portfolio_20240115.log           # Main log (all levels)
├── portfolio_errors_20240115.log    # Errors only
├── transactions_20240115.log        # Transaction-level log
└── error_report_20240115_143022.txt # Generated error report
```

### Log Rotation

- **Max Size:** 10 MB per file
- **Backups:** 5 previous versions kept
- **Encoding:** UTF-8 (supports Hebrew characters)

### Log Levels

- **DEBUG:** Detailed diagnostic information
- **INFO:** General informational messages
- **WARNING:** Warning messages (non-critical issues)
- **ERROR:** Error messages (critical issues)
- **CRITICAL:** Critical errors (system failures)

## Testing Error Handling

### Test with Invalid Data

```python
# Create test data with errors
test_transactions = [
    # Missing required fields
    Transaction(date=None, security_symbol="", ...),

    # Negative quantity
    Transaction(quantity=-10, ...),

    # Currency mismatch
    Transaction(currency="$", ...),  # When position uses "₪"

    # Insufficient shares
    Transaction(is_sell=True, quantity=1000, ...)  # More than owned
]

# Build and check errors
builder = PortfolioBuilder(fail_fast=False)
positions = builder.build(test_transactions)

# Verify error collection
assert builder.has_errors()
summary = builder.get_error_summary()
print(f"Detected {summary['total_errors']} errors")
```

## Integration with Streamlit

### Complete Example

```python
import streamlit as st
from src.modules.portfolio_dashboard.builder import PortfolioBuilder
from src.modules.portfolio_dashboard.error_display import (
    display_validation_errors,
    show_file_loading_error,
    show_empty_portfolio_message
)
from src.modules.portfolio_dashboard.logging_config import setup_default_logging

# Setup logging
setup_default_logging(log_level="INFO", log_dir="logs")

# Streamlit app
st.title("Portfolio Dashboard")

# File upload
uploaded_file = st.file_uploader("Upload IBI Transaction File", type=['xlsx', 'xls'])

if uploaded_file:
    try:
        # Load and transform
        df = load_excel(uploaded_file)
        transactions = transform_to_transactions(df)

        # Build portfolio
        builder = PortfolioBuilder(fail_fast=False)
        positions = builder.build(transactions)

        # Display results
        if positions:
            display_portfolio(positions)
        else:
            show_empty_portfolio_message()

        # Show any errors/warnings
        display_validation_errors(builder)

    except Exception as e:
        show_file_loading_error(uploaded_file.name, str(e))
```

## Configuration

### Adjust Error Tolerance

```python
# Strict mode - fail on first error
builder = PortfolioBuilder(fail_fast=True)

# Lenient mode - collect all errors
builder = PortfolioBuilder(fail_fast=False)
```

### Customize Logging

```python
# Production: Less verbose
setup_default_logging(log_level="WARNING", enable_file_logging=True)

# Development: More verbose
setup_default_logging(log_level="DEBUG", enable_file_logging=True)

# Minimal: Console only
setup_default_logging(log_level="INFO", enable_file_logging=False)
```

## Best Practices

1. **Always use error collection mode** in production (`fail_fast=False`)
2. **Display user-friendly messages** in Streamlit (use `error_display.py` functions)
3. **Log all errors** for debugging (enable file logging)
4. **Generate error reports** for complex issues
5. **Validate data early** (at adapter level)
6. **Provide actionable guidance** in error messages
7. **Test with invalid data** to verify error handling works

## Support

For issues or questions about error handling:

1. Check the log files in `logs/` directory
2. Review error reports for detailed information
3. Enable DEBUG logging for more details
4. Check CLAUDE.md for project documentation
5. Review code comments in error handling modules

## Future Enhancements

- [ ] Email notifications for critical errors
- [ ] Error analytics dashboard
- [ ] Automatic error recovery suggestions
- [ ] Integration with error tracking services (Sentry, etc.)
- [ ] Machine learning for error pattern detection
- [ ] Custom error handlers per transaction type
- [ ] Error rate monitoring and alerts

"""
Logging Configuration for Portfolio Dashboard.

Provides comprehensive logging with file rotation, structured formatting,
and different log levels for development and production.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class PortfolioLogger:
    """
    Centralized logging configuration for portfolio dashboard.

    Features:
    - Console logging with color-coded levels
    - File logging with rotation
    - Structured log formatting
    - Separate error log file
    - Configurable log levels
    """

    def __init__(
        self,
        log_dir: str = "logs",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        enable_console: bool = True,
        enable_file: bool = True
    ):
        """
        Initialize logging configuration.

        Args:
            log_dir: Directory for log files
            console_level: Logging level for console output
            file_level: Logging level for file output
            enable_console: Enable console logging
            enable_file: Enable file logging
        """
        self.log_dir = Path(log_dir)
        self.console_level = console_level
        self.file_level = file_level
        self.enable_console = enable_console
        self.enable_file = enable_file

        # Create log directory if it doesn't exist
        if enable_file:
            self.log_dir.mkdir(parents=True, exist_ok=True)

        # Configure root logger
        self._configure_logging()

    def _configure_logging(self):
        """Configure logging handlers and formatters."""
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Capture everything, filter in handlers

        # Clear existing handlers
        root_logger.handlers.clear()

        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.console_level)
            console_handler.setFormatter(self._get_console_formatter())
            root_logger.addHandler(console_handler)

        # File handlers
        if self.enable_file:
            # Main log file (all levels)
            main_log_file = self.log_dir / f"portfolio_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                main_log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(self.file_level)
            file_handler.setFormatter(self._get_file_formatter())
            root_logger.addHandler(file_handler)

            # Error log file (errors and critical only)
            error_log_file = self.log_dir / f"portfolio_errors_{datetime.now().strftime('%Y%m%d')}.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(self._get_file_formatter())
            root_logger.addHandler(error_handler)

    def _get_console_formatter(self) -> logging.Formatter:
        """
        Get formatter for console output.

        Returns:
            Logging formatter with simplified format
        """
        return logging.Formatter(
            fmt='%(levelname)-8s | %(name)-25s | %(message)s',
            datefmt='%H:%M:%S'
        )

    def _get_file_formatter(self) -> logging.Formatter:
        """
        Get formatter for file output.

        Returns:
            Logging formatter with detailed format
        """
        return logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get logger instance for a module.

        Args:
            name: Logger name (usually __name__)

        Returns:
            Logger instance
        """
        return logging.getLogger(name)


class TransactionLogger:
    """
    Specialized logger for transaction processing.

    Logs transaction-level events to separate file for analysis.
    """

    def __init__(self, log_dir: str = "logs"):
        """
        Initialize transaction logger.

        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger('transaction_log')
        self.logger.setLevel(logging.DEBUG)

        # Transaction log file
        log_file = self.log_dir / f"transactions_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=10,
            encoding='utf-8'
        )

        formatter = logging.Formatter(
            fmt='%(asctime)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_transaction_processing(
        self,
        transaction_id: str,
        symbol: str,
        transaction_type: str,
        quantity: float,
        status: str,
        details: str = ""
    ):
        """
        Log transaction processing event.

        Args:
            transaction_id: Transaction ID
            symbol: Security symbol
            transaction_type: Type of transaction
            quantity: Transaction quantity
            status: Processing status (success/error/skipped)
            details: Additional details
        """
        message = (
            f"TXN={transaction_id} | "
            f"SYMBOL={symbol} | "
            f"TYPE={transaction_type} | "
            f"QTY={quantity} | "
            f"STATUS={status}"
        )

        if details:
            message += f" | DETAILS={details}"

        if status == "error":
            self.logger.error(message)
        elif status == "warning":
            self.logger.warning(message)
        else:
            self.logger.info(message)


def setup_default_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_file_logging: bool = True
) -> PortfolioLogger:
    """
    Setup default logging configuration for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        enable_file_logging: Whether to enable file logging

    Returns:
        Configured PortfolioLogger instance
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    level = level_map.get(log_level.upper(), logging.INFO)

    logger_config = PortfolioLogger(
        log_dir=log_dir,
        console_level=level,
        file_level=logging.DEBUG,
        enable_console=True,
        enable_file=enable_file_logging
    )

    return logger_config


def create_error_report(
    error_summary: dict,
    output_file: Optional[str] = None
) -> str:
    """
    Create detailed error report from error summary.

    Args:
        error_summary: Error summary dictionary from ErrorCollector
        output_file: Optional file path to save report

    Returns:
        Formatted error report string
    """
    report_lines = [
        "=" * 80,
        "PORTFOLIO ERROR REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 80,
        "",
        "SUMMARY",
        "-" * 80,
        f"Total Errors:   {error_summary.get('total_errors', 0)}",
        f"Total Warnings: {error_summary.get('total_warnings', 0)}",
        ""
    ]

    # Error type breakdown
    error_types = error_summary.get('error_types', {})
    if error_types:
        report_lines.append("ERROR BREAKDOWN")
        report_lines.append("-" * 80)
        for error_type, count in error_types.items():
            report_lines.append(f"  {error_type}: {count}")
        report_lines.append("")

    # Detailed errors
    errors = error_summary.get('errors', [])
    if errors:
        report_lines.append("DETAILED ERRORS")
        report_lines.append("-" * 80)
        for idx, error in enumerate(errors, 1):
            report_lines.append(f"\nError #{idx}:")
            report_lines.append(f"  Type: {error.get('error_type', 'Unknown')}")
            report_lines.append(f"  Message: {error.get('message', 'No message')}")

            details = error.get('details', {})
            if details:
                report_lines.append("  Details:")
                for key, value in details.items():
                    report_lines.append(f"    {key}: {value}")
        report_lines.append("")

    # Warnings
    warnings = error_summary.get('warnings', [])
    if warnings:
        report_lines.append("WARNINGS")
        report_lines.append("-" * 80)
        for idx, warning in enumerate(warnings, 1):
            report_lines.append(f"{idx}. {warning}")
        report_lines.append("")

    report_lines.append("=" * 80)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 80)

    report = "\n".join(report_lines)

    # Save to file if requested
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logging.getLogger(__name__).info(f"Error report saved to: {output_file}")
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to save error report: {e}")

    return report


# Example usage documentation
"""
Usage Example:

# 1. Setup logging at application start
from src.modules.portfolio_dashboard.logging_config import setup_default_logging

logger_config = setup_default_logging(
    log_level="INFO",
    log_dir="logs",
    enable_file_logging=True
)

# 2. Get logger in your module
import logging
logger = logging.getLogger(__name__)

# 3. Use logger
logger.info("Processing transactions...")
logger.warning("Missing data detected")
logger.error("Failed to process transaction", exc_info=True)

# 4. Create error report
from src.modules.portfolio_dashboard.logging_config import create_error_report

error_summary = builder.get_error_summary()
report = create_error_report(
    error_summary,
    output_file="logs/error_report.txt"
)
print(report)

# 5. Log individual transactions
from src.modules.portfolio_dashboard.logging_config import TransactionLogger

txn_logger = TransactionLogger(log_dir="logs")
txn_logger.log_transaction_processing(
    transaction_id="IBI_20240101_BUY_AAPL",
    symbol="AAPL",
    transaction_type="Buy",
    quantity=10.0,
    status="success"
)
"""

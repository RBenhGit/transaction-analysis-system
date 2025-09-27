"""
JSON Adapter

This module provides the main adapter interface that coordinates between
Excel imports, bank-specific adapters, and the standardized JSON output format.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Type
from pathlib import Path

from .simple_models import TransactionSet, ImportResult
from .config_manager import ConfigManager
from adapters.base_adapter import BaseAdapter
from adapters.ibi_adapter import IBIAdapter


class JSONAdapter:
    """
    Main adapter that coordinates the import process and provides JSON output.

    This adapter:
    1. Determines the appropriate bank adapter to use
    2. Processes the data through the bank adapter
    3. Provides standardized JSON export capabilities
    4. Manages the overall import workflow
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the JSON adapter.

        Args:
            config_manager: ConfigManager instance, creates default if None
        """
        self.config_manager = config_manager or ConfigManager()
        self._bank_adapters: Dict[str, Type[BaseAdapter]] = {}
        self._register_default_adapters()

    def _register_default_adapters(self):
        """Register default bank adapters."""
        self._bank_adapters = {
            "IBI": IBIAdapter
        }

    def register_adapter(self, bank_name: str, adapter_class: Type[BaseAdapter]):
        """
        Register a new bank adapter.

        Args:
            bank_name: Name of the bank (e.g., "HAPOALIM")
            adapter_class: Bank adapter class that inherits from BaseAdapter
        """
        self._bank_adapters[bank_name.upper()] = adapter_class

    def get_available_banks(self) -> List[str]:
        """Get list of available bank adapters."""
        return list(self._bank_adapters.keys())

    def auto_detect_bank(self, df) -> Optional[str]:
        """
        Automatically detect which bank format the data uses.

        Args:
            df: Pandas DataFrame containing the raw data

        Returns:
            Bank name if detected, None otherwise
        """
        import pandas as pd

        for bank_name, adapter_class in self._bank_adapters.items():
            try:
                # Get configuration for this bank
                config = self.config_manager.get_bank_config(bank_name)
                if not config:
                    continue

                # Create adapter instance
                adapter = adapter_class(config)

                # Test if this adapter can handle the data
                if adapter.validate_data_format(df):
                    return bank_name

            except Exception:
                # If adapter fails, continue to next one
                continue

        return None

    def process_dataframe(
        self,
        df,
        bank_name: Optional[str] = None,
        source_file: str = ""
    ) -> ImportResult:
        """
        Process a DataFrame using the appropriate bank adapter.

        Args:
            df: Pandas DataFrame containing raw transaction data
            bank_name: Specific bank to use, auto-detect if None
            source_file: Path to source file for metadata

        Returns:
            ImportResult containing processed transactions or errors
        """
        import pandas as pd

        # Auto-detect bank if not specified
        if not bank_name:
            detected_bank = self.auto_detect_bank(df)
            if not detected_bank:
                result = ImportResult(success=False)
                result.add_error("Could not auto-detect bank format")
                return result
            bank_name = detected_bank

        # Get bank adapter
        adapter = self._get_bank_adapter(bank_name)
        if not adapter:
            result = ImportResult(success=False)
            result.add_error(f"No adapter available for bank: {bank_name}")
            return result

        # Process the data
        result = adapter.process_dataframe(df)

        # Add source file to metadata if successful
        if result.success and result.transaction_set:
            result.transaction_set.metadata.source_file = source_file

        return result

    def _get_bank_adapter(self, bank_name: str) -> Optional[BaseAdapter]:
        """
        Get an instance of the appropriate bank adapter.

        Args:
            bank_name: Name of the bank

        Returns:
            Bank adapter instance or None if not available
        """
        bank_name = bank_name.upper()

        if bank_name not in self._bank_adapters:
            return None

        # Get configuration
        config = self.config_manager.get_bank_config(bank_name)
        if not config:
            return None

        # Create adapter instance
        adapter_class = self._bank_adapters[bank_name]
        return adapter_class(config)

    def export_to_json(
        self,
        transaction_set: TransactionSet,
        output_path: Optional[str] = None,
        pretty: bool = True
    ) -> str:
        """
        Export transaction set to JSON format.

        Args:
            transaction_set: TransactionSet to export
            output_path: Path to save JSON file, auto-generate if None
            pretty: Whether to format JSON with indentation

        Returns:
            Path to saved JSON file
        """
        # Generate output path if not provided
        if not output_path:
            processed_path = self.config_manager.get_processed_path()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            bank = transaction_set.metadata.bank.lower()
            filename = f"{bank}_transactions_{timestamp}.json"
            output_path = os.path.join(processed_path, filename)

        # Prepare data for JSON export
        json_data = self._prepare_json_data(transaction_set)

        # Write JSON file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
                else:
                    json.dump(json_data, f, ensure_ascii=False, default=str)

            return output_path

        except IOError as e:
            raise IOError(f"Failed to write JSON file: {e}")

    def _prepare_json_data(self, transaction_set: TransactionSet) -> Dict[str, Any]:
        """
        Prepare transaction set for JSON serialization.

        Args:
            transaction_set: TransactionSet to prepare

        Returns:
            Dictionary ready for JSON serialization
        """
        # Convert transactions to dictionaries
        transactions_data = []
        for transaction in transaction_set.transactions:
            transaction_dict = {
                "date": transaction.date.isoformat() if transaction.date else None,
                "description": transaction.description,
                "amount": float(transaction.amount) if transaction.amount else None,
                "balance": float(transaction.balance) if transaction.balance else None,
                "category": transaction.category,
                "reference": transaction.reference,
                "bank": transaction.bank,
                "account": transaction.account
            }
            transactions_data.append(transaction_dict)

        # Prepare metadata
        metadata = transaction_set.metadata
        metadata_dict = {
            "source_file": metadata.source_file,
            "import_date": metadata.import_date.isoformat(),
            "total_transactions": metadata.total_transactions,
            "date_range": {
                "start": metadata.date_range["start"].isoformat() if metadata.date_range["start"] else None,
                "end": metadata.date_range["end"].isoformat() if metadata.date_range["end"] else None
            },
            "bank": metadata.bank,
            "encoding": metadata.encoding
        }

        # Combine into final structure
        return {
            "transactions": transactions_data,
            "metadata": metadata_dict,
            "export_info": {
                "export_date": datetime.now().isoformat(),
                "format_version": "1.0",
                "exported_by": "Transaction Analysis System"
            }
        }

    def import_from_json(self, json_path: str) -> ImportResult:
        """
        Import transactions from a JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            ImportResult containing imported transactions
        """
        result = ImportResult(success=True)

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            # Parse the JSON data back to TransactionSet
            transaction_set = self._parse_json_data(json_data)
            result.transaction_set = transaction_set

        except (json.JSONDecodeError, IOError, KeyError, ValueError) as e:
            result.add_error(f"Failed to import JSON file: {e}")

        return result

    def _parse_json_data(self, json_data: Dict[str, Any]) -> TransactionSet:
        """
        Parse JSON data back to TransactionSet.

        Args:
            json_data: Dictionary from JSON file

        Returns:
            TransactionSet object
        """
        from datetime import date
        from decimal import Decimal
        from .simple_models import Transaction, TransactionMetadata

        # Parse transactions
        transactions = []
        for trans_data in json_data.get("transactions", []):
            transaction = Transaction(
                date=date.fromisoformat(trans_data["date"]) if trans_data["date"] else None,
                description=trans_data["description"] or "",
                amount=Decimal(str(trans_data["amount"])) if trans_data["amount"] is not None else Decimal('0'),
                balance=Decimal(str(trans_data["balance"])) if trans_data["balance"] is not None else None,
                category=trans_data.get("category"),
                reference=trans_data.get("reference"),
                bank=trans_data["bank"],
                account=trans_data.get("account")
            )
            transactions.append(transaction)

        # Parse metadata
        metadata_dict = json_data.get("metadata", {})
        date_range = metadata_dict.get("date_range", {})

        metadata = TransactionMetadata(
            source_file=metadata_dict.get("source_file", ""),
            import_date=datetime.fromisoformat(metadata_dict.get("import_date", datetime.now().isoformat())),
            total_transactions=metadata_dict.get("total_transactions", len(transactions)),
            date_range={
                "start": date.fromisoformat(date_range["start"]) if date_range.get("start") else None,
                "end": date.fromisoformat(date_range["end"]) if date_range.get("end") else None
            },
            bank=metadata_dict.get("bank", "UNKNOWN"),
            encoding=metadata_dict.get("encoding")
        )

        return TransactionSet(transactions=transactions, metadata=metadata)

    def get_processing_summary(self, result: ImportResult) -> Dict[str, Any]:
        """
        Generate a summary of the processing results.

        Args:
            result: ImportResult to summarize

        Returns:
            Dictionary containing processing summary
        """
        summary = {
            "success": result.success,
            "processing_time": result.processing_time,
            "errors": result.errors,
            "warnings": result.warnings
        }

        if result.transaction_set:
            ts = result.transaction_set
            summary.update({
                "total_transactions": len(ts.transactions),
                "date_range": ts.get_date_range(),
                "total_amount": float(ts.get_total_amount()),
                "bank": ts.metadata.bank,
                "source_file": ts.metadata.source_file
            })

        return summary

    def validate_json_schema(self, json_data: Dict[str, Any]) -> List[str]:
        """
        Validate JSON data against expected schema.

        Args:
            json_data: JSON data to validate

        Returns:
            List of validation errors
        """
        errors = []

        # Check required top-level keys
        required_keys = ["transactions", "metadata"]
        for key in required_keys:
            if key not in json_data:
                errors.append(f"Missing required key: {key}")

        # Validate transactions structure
        if "transactions" in json_data:
            if not isinstance(json_data["transactions"], list):
                errors.append("Transactions must be a list")
            else:
                for i, trans in enumerate(json_data["transactions"]):
                    if not isinstance(trans, dict):
                        errors.append(f"Transaction {i} must be a dictionary")
                        continue

                    # Check required transaction fields
                    required_trans_fields = ["date", "description", "amount", "bank"]
                    for field in required_trans_fields:
                        if field not in trans:
                            errors.append(f"Transaction {i} missing required field: {field}")

        # Validate metadata structure
        if "metadata" in json_data:
            metadata = json_data["metadata"]
            if not isinstance(metadata, dict):
                errors.append("Metadata must be a dictionary")
            else:
                required_meta_fields = ["source_file", "import_date", "total_transactions", "bank"]
                for field in required_meta_fields:
                    if field not in metadata:
                        errors.append(f"Metadata missing required field: {field}")

        return errors
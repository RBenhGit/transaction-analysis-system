"""
Configuration Manager

This module handles loading and managing configuration for the transaction
analysis system, including bank adapter configurations and application settings.
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from .simple_models import AdapterConfig


class ConfigManager:
    """
    Manages application configuration including bank adapter settings.
    """

    def __init__(self, config_file: str = "config.json"):
        """
        Initialize ConfigManager with specified config file.

        Args:
            config_file: Path to the configuration JSON file
        """
        self.config_file = config_file
        self.config_data: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from file, create default if doesn't exist."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config file: {e}")
                self.config_data = self._get_default_config()
        else:
            self.config_data = self._get_default_config()
            self.save_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration structure."""
        return {
            "banks": {
                "IBI": {
                    "column_mappings": {
                        "date": "תאריך",
                        "description": "תיאור",
                        "amount": "סכום",
                        "balance": "יתרה",
                        "reference": "אסמכתא"
                    },
                    "date_format": "%d/%m/%Y",
                    "encoding": "utf-8",
                    "skip_rows": 0
                }
            },
            "output": {
                "default_format": "json",
                "export_path": "./output/exports/",
                "processed_path": "./output/processed/",
                "reports_path": "./output/reports/"
            },
            "display": {
                "max_rows": 100,
                "date_format": "%Y-%m-%d",
                "amount_precision": 2,
                "show_balance": True
            },
            "import": {
                "data_files_path": "./Data_Files/",
                "supported_extensions": [".xlsx", ".xls"],
                "auto_detect_bank": True,
                "backup_imports": True
            }
        }

    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving config file: {e}")

    def get_bank_config(self, bank_name: str) -> Optional[AdapterConfig]:
        """
        Get adapter configuration for a specific bank.

        Args:
            bank_name: Name of the bank (e.g., "IBI")

        Returns:
            AdapterConfig object or None if bank not found
        """
        banks_config = self.config_data.get("banks", {})
        bank_config = banks_config.get(bank_name.upper())

        if not bank_config:
            return None

        try:
            return AdapterConfig(
                bank_name=bank_name.upper(),
                column_mappings=bank_config.get("column_mappings", {}),
                date_format=bank_config.get("date_format", "%d/%m/%Y"),
                encoding=bank_config.get("encoding", "utf-8"),
                skip_rows=bank_config.get("skip_rows", 0),
                amount_columns=bank_config.get("amount_columns")
            )
        except Exception as e:
            print(f"Error creating adapter config for {bank_name}: {e}")
            return None

    def get_available_banks(self) -> List[str]:
        """Get list of configured bank names."""
        return list(self.config_data.get("banks", {}).keys())

    def add_bank_config(self, bank_name: str, config: Dict[str, Any]):
        """
        Add or update bank configuration.

        Args:
            bank_name: Name of the bank
            config: Bank configuration dictionary
        """
        if "banks" not in self.config_data:
            self.config_data["banks"] = {}

        self.config_data["banks"][bank_name.upper()] = config
        self.save_config()

    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration settings."""
        return self.config_data.get("output", {
            "default_format": "json",
            "export_path": "./output/exports/",
            "processed_path": "./output/processed/",
            "reports_path": "./output/reports/"
        })

    def get_display_config(self) -> Dict[str, Any]:
        """Get display configuration settings."""
        return self.config_data.get("display", {
            "max_rows": 100,
            "date_format": "%Y-%m-%d",
            "amount_precision": 2,
            "show_balance": True
        })

    def get_import_config(self) -> Dict[str, Any]:
        """Get import configuration settings."""
        return self.config_data.get("import", {
            "data_files_path": "./Data_Files/",
            "supported_extensions": [".xlsx", ".xls"],
            "auto_detect_bank": True,
            "backup_imports": True
        })

    def get_data_files_path(self) -> str:
        """Get the path to data files directory."""
        import_config = self.get_import_config()
        return import_config.get("data_files_path", "./Data_Files/")

    def get_export_path(self) -> str:
        """Get the path for exported files."""
        output_config = self.get_output_config()
        export_path = output_config.get("export_path", "./output/exports/")

        # Ensure directory exists
        Path(export_path).mkdir(parents=True, exist_ok=True)

        return export_path

    def get_processed_path(self) -> str:
        """Get the path for processed files."""
        output_config = self.get_output_config()
        processed_path = output_config.get("processed_path", "./output/processed/")

        # Ensure directory exists
        Path(processed_path).mkdir(parents=True, exist_ok=True)

        return processed_path

    def get_reports_path(self) -> str:
        """Get the path for report files."""
        output_config = self.get_output_config()
        reports_path = output_config.get("reports_path", "./output/reports/")

        # Ensure directory exists
        Path(reports_path).mkdir(parents=True, exist_ok=True)

        return reports_path

    def update_setting(self, section: str, key: str, value: Any):
        """
        Update a specific configuration setting.

        Args:
            section: Configuration section (e.g., "display", "output")
            key: Setting key
            value: New value
        """
        if section not in self.config_data:
            self.config_data[section] = {}

        self.config_data[section][key] = value
        self.save_config()

    def validate_config(self) -> List[str]:
        """
        Validate configuration and return list of issues.

        Returns:
            List of validation error messages
        """
        issues = []

        # Check required sections
        required_sections = ["banks", "output", "display", "import"]
        for section in required_sections:
            if section not in self.config_data:
                issues.append(f"Missing required configuration section: {section}")

        # Validate bank configurations
        banks = self.config_data.get("banks", {})
        for bank_name, bank_config in banks.items():
            if not isinstance(bank_config, dict):
                issues.append(f"Bank config for {bank_name} must be a dictionary")
                continue

            # Check required bank config fields
            required_fields = ["column_mappings"]
            for field in required_fields:
                if field not in bank_config:
                    issues.append(f"Bank {bank_name} missing required field: {field}")

            # Validate column mappings
            column_mappings = bank_config.get("column_mappings", {})
            required_columns = ["date", "description", "amount"]
            for column in required_columns:
                if column not in column_mappings:
                    issues.append(f"Bank {bank_name} missing column mapping for: {column}")

        # Validate paths exist
        import_config = self.get_import_config()
        data_files_path = import_config.get("data_files_path", "./Data_Files/")
        if not os.path.exists(data_files_path):
            issues.append(f"Data files path does not exist: {data_files_path}")

        return issues

    def create_bank_template(self, bank_name: str) -> Dict[str, Any]:
        """
        Create a template configuration for a new bank.

        Args:
            bank_name: Name of the new bank

        Returns:
            Template configuration dictionary
        """
        return {
            "column_mappings": {
                "date": "Date",
                "description": "Description",
                "amount": "Amount",
                "balance": "Balance",
                "reference": "Reference"
            },
            "date_format": "%d/%m/%Y",
            "encoding": "utf-8",
            "skip_rows": 0,
            "amount_columns": {
                "debit": "Debit",
                "credit": "Credit"
            }
        }

    def export_config(self, export_path: str):
        """
        Export configuration to a specified file.

        Args:
            export_path: Path to export the configuration
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"Failed to export config to {export_path}: {e}")

    def import_config(self, import_path: str, merge: bool = False):
        """
        Import configuration from a file.

        Args:
            import_path: Path to import configuration from
            merge: If True, merge with existing config; if False, replace entirely
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            if merge:
                # Deep merge with existing configuration
                self._deep_merge(self.config_data, imported_config)
            else:
                # Replace entire configuration
                self.config_data = imported_config

            self.save_config()

        except (json.JSONDecodeError, IOError) as e:
            raise IOError(f"Failed to import config from {import_path}: {e}")

    def _deep_merge(self, base_dict: Dict, update_dict: Dict):
        """Recursively merge two dictionaries."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
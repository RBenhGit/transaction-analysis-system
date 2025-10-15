"""
IBI Test Data Fixtures

Provides real anonymized IBI transaction data for integration testing.
Uses actual IBI Excel files from Data_Files directory.
"""

import os
from pathlib import Path
from typing import List, Dict, Any


class IBITestDataFixtures:
    """Manages test data files and expected outcomes for IBI integration tests."""

    # Base path to test data (relative to project root)
    DATA_DIR = Path(__file__).parent.parent.parent / "Data_Files"

    # Test files configuration
    TEST_FILES = {
        "IBI_2022_2025": {
            "file": "IBI trans 2022-5_10_2025.xlsx",
            "description": "Real IBI transactions from 2022 to early 2025",
            "sheet": None,  # Use default sheet
        }
    }

    # Known expected outcomes for validation
    EXPECTED_OUTCOMES = {
        "IBI_2022_2025": {
            # These are placeholder values - update after running tests with real data
            "min_transactions": 50,  # Minimum expected transactions
            "has_buy_transactions": True,
            "has_sell_transactions": True,
            "has_tax_transactions": True,
            "has_fee_transactions": True,
            "expected_currencies": ["$", "₪"],  # USD and NIS
            "expected_symbols": [],  # Will be populated dynamically
        }
    }

    @classmethod
    def get_file_path(cls, dataset_name: str) -> Path:
        """
        Get full path to test data file.

        Args:
            dataset_name: Name of the dataset (key from TEST_FILES)

        Returns:
            Path to the Excel file

        Raises:
            ValueError: If dataset name is not found
            FileNotFoundError: If file doesn't exist
        """
        if dataset_name not in cls.TEST_FILES:
            raise ValueError(
                f"Unknown dataset: {dataset_name}. "
                f"Available: {', '.join(cls.TEST_FILES.keys())}"
            )

        file_config = cls.TEST_FILES[dataset_name]
        file_path = cls.DATA_DIR / file_config["file"]

        if not file_path.exists():
            raise FileNotFoundError(
                f"Test data file not found: {file_path}\n"
                f"Expected location: {cls.DATA_DIR}"
            )

        return file_path

    @classmethod
    def get_expected_outcomes(cls, dataset_name: str) -> Dict[str, Any]:
        """
        Get expected outcomes for a dataset.

        Args:
            dataset_name: Name of the dataset

        Returns:
            Dictionary of expected outcomes
        """
        return cls.EXPECTED_OUTCOMES.get(dataset_name, {})

    @classmethod
    def list_available_datasets(cls) -> List[str]:
        """Get list of available test datasets."""
        return list(cls.TEST_FILES.keys())

    @classmethod
    def get_dataset_info(cls, dataset_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a dataset.

        Args:
            dataset_name: Name of the dataset

        Returns:
            Dictionary with dataset configuration and metadata
        """
        if dataset_name not in cls.TEST_FILES:
            raise ValueError(f"Unknown dataset: {dataset_name}")

        config = cls.TEST_FILES[dataset_name].copy()
        config["file_path"] = str(cls.get_file_path(dataset_name))
        config["exists"] = cls.get_file_path(dataset_name).exists()
        config["expected_outcomes"] = cls.get_expected_outcomes(dataset_name)

        return config


# Convenience function for quick access
def get_test_file(dataset_name: str = "IBI_2022_2025") -> Path:
    """
    Quick access to test data file path.

    Args:
        dataset_name: Name of the dataset (default: IBI_2022_2025)

    Returns:
        Path to the test file
    """
    return IBITestDataFixtures.get_file_path(dataset_name)

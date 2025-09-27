#!/usr/bin/env python3
"""
Transaction Analysis System - Main Application

This is the main entry point for the transaction analysis system.
It provides an interactive interface for importing, processing, and analyzing
Excel transaction files from various banks.
"""

import os
import sys
from typing import List, Dict, Any, Optional

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.excel_importer import ExcelImporter
from src.display_manager import DisplayManager
from src.config_manager import ConfigManager
from src.simple_models import ImportResult, TransactionSet


class TransactionAnalyzer:
    """
    Main application class for the transaction analysis system.
    """

    def __init__(self):
        """Initialize the transaction analyzer."""
        print("Initializing Transaction Analysis System...")

        # Initialize core components
        self.config_manager = ConfigManager()
        self.excel_importer = ExcelImporter(self.config_manager)
        self.display_manager = DisplayManager(self.config_manager)

        # Validate configuration
        config_issues = self.config_manager.validate_config()
        if config_issues:
            print("Warning:  Configuration issues detected:")
            for issue in config_issues:
                print(f"   * {issue}")
            print()

        print("System initialized successfully!")

    def main_menu(self):
        """Display and handle the main menu."""
        while True:
            self._print_header()
            print("MAIN MENU")
            print("="*50)
            print("1. Import Excel files")
            print("2. Browse available files")
            print("3. System information")
            print("4. Configuration")
            print("0. Exit")
            print("="*50)

            choice = input("Select option (0-4): ").strip()

            try:
                if choice == "0":
                    print("Thank you for using Transaction Analysis System!")
                    break
                elif choice == "1":
                    self.import_menu()
                elif choice == "2":
                    self.browse_files()
                elif choice == "3":
                    self.show_system_info()
                elif choice == "4":
                    self.configuration_menu()
                else:
                    print("Invalid option. Please try again.")

            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user.")
            except Exception as e:
                print(f"Error: {e}")

            if choice != "0":
                input("\nPress Enter to continue...")

    def import_menu(self):
        """Handle the import menu and file selection."""
        print("\n" + "="*50)
        print("IMPORT EXCEL FILES")
        print("="*50)

        # Discover available files
        files = self.excel_importer.discover_files()

        if not files:
            data_path = self.config_manager.get_data_files_path()
            print(f"ERROR: No Excel files found in: {data_path}")
            print("Please add Excel files to the Data_Files directory.")
            return

        # Display files
        self.display_manager.print_file_list(files)

        print("\nImport options:")
        print("* Enter file number(s) to import specific files (e.g., 1,3,5)")
        print("* Enter 'all' to import all files")
        print("* Enter 'preview N' to preview file N")
        print("* Enter 'back' to return to main menu")

        choice = input("\nYour choice: ").strip().lower()

        if choice == "back":
            return
        elif choice == "all":
            self._import_all_files(files)
        elif choice.startswith("preview "):
            try:
                file_num = int(choice.split()[1])
                self._preview_file(files, file_num)
            except (ValueError, IndexError):
                print("ERROR: Invalid preview command. Use: preview N")
        else:
            # Parse file numbers
            try:
                file_numbers = [int(x.strip()) for x in choice.split(",")]
                self._import_selected_files(files, file_numbers)
            except ValueError:
                print("ERROR: Invalid input. Use file numbers separated by commas.")

    def _import_all_files(self, files: List[Dict[str, Any]]):
        """Import all available files."""
        print(f"\nProcessing: Importing {len(files)} files...")

        file_paths = [f["path"] for f in files]
        results = self.excel_importer.batch_import(file_paths)

        self._display_batch_results(results)

    def _import_selected_files(self, files: List[Dict[str, Any]], file_numbers: List[int]):
        """Import selected files by number."""
        selected_files = []

        for num in file_numbers:
            if 1 <= num <= len(files):
                selected_files.append(files[num - 1])
            else:
                print(f"ERROR: Invalid file number: {num}")

        if selected_files:
            print(f"\nProcessing: Importing {len(selected_files)} selected files...")
            file_paths = [f["path"] for f in selected_files]
            results = self.excel_importer.batch_import(file_paths)
            self._display_batch_results(results)

    def _preview_file(self, files: List[Dict[str, Any]], file_number: int):
        """Preview a specific file."""
        if not (1 <= file_number <= len(files)):
            print(f"ERROR: Invalid file number: {file_number}")
            return

        file_info = files[file_number - 1]
        file_path = file_info["path"]

        print(f"\n🔍 Previewing: {file_info['filename']}")

        try:
            preview = self.excel_importer.preview_file(file_path)

            if "error" in preview:
                print(f"ERROR: Error: {preview['error']}")
                return

            print(f"📊 File Information:")
            print(f"   * Total rows: {preview['total_rows']}")
            print(f"   * Total columns: {preview['total_columns']}")
            print(f"   * Detected bank: {preview['detected_bank'] or 'Unknown'}")

            if preview["data"]:
                print(f"\n📋 First {preview['preview_rows']} rows:")
                # Display preview data in a simple format
                for i, row in enumerate(preview["data"][:5]):  # Show max 5 rows
                    print(f"   Row {i+1}: {list(row.values())[:3]}...")  # Show first 3 columns

            # Ask if user wants to import this file
            import_choice = input(f"\nImport this file? (y/n): ").strip().lower()
            if import_choice == 'y':
                result = self.excel_importer.import_file(file_path)
                self.display_manager.show_import_result(result)

                if result.success and result.transaction_set:
                    explore = input("Explore the imported data? (y/n): ").strip().lower()
                    if explore == 'y':
                        self.display_manager.interactive_menu(result.transaction_set)

        except Exception as e:
            print(f"ERROR: Error previewing file: {e}")

    def _display_batch_results(self, results: List[ImportResult]):
        """Display results from batch import."""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        print(f"\n📊 Import Summary:")
        print(f"   OK: Successful: {len(successful)}")
        print(f"   ERROR: Failed: {len(failed)}")

        if failed:
            print(f"\nERROR: Failed imports:")
            for result in failed:
                print(f"   * {'; '.join(result.errors)}")

        if successful:
            total_transactions = sum(
                len(r.transaction_set.transactions) for r in successful
                if r.transaction_set
            )
            print(f"\nOK: Total transactions imported: {total_transactions}")

            # Ask if user wants to explore any of the imported datasets
            if len(successful) == 1:
                explore = input("Explore the imported data? (y/n): ").strip().lower()
                if explore == 'y' and successful[0].transaction_set:
                    self.display_manager.interactive_menu(successful[0].transaction_set)

    def browse_files(self):
        """Browse and analyze available files."""
        print("\n" + "="*50)
        print("BROWSE FILES")
        print("="*50)

        files = self.excel_importer.discover_files()

        if not files:
            data_path = self.config_manager.get_data_files_path()
            print(f"ERROR: No Excel files found in: {data_path}")
            return

        # Display detailed file information
        print(f"Folder: Data Files Directory: {self.config_manager.get_data_files_path()}")
        print(f"Stats: Found {len(files)} Excel file(s):\n")

        for i, file_info in enumerate(files, 1):
            print(f"{i}. {file_info['filename']}")
            print(f"   📏 Size: {self._format_file_size(file_info['size'])}")

            # Get file statistics
            try:
                stats = self.excel_importer.get_file_statistics(file_info['path'])
                if stats['error']:
                    print(f"   ERROR: Error: {stats['error']}")
                else:
                    print(f"   📋 Sheets: {len(stats['sheets'])}")
                    print(f"   📊 Rows: {stats['total_rows']:,}")
                    print(f"   🏦 Bank: {stats['detected_bank'] or 'Unknown'}")
            except Exception as e:
                print(f"   ERROR: Analysis error: {e}")

            print()

    def show_system_info(self):
        """Display system information and status."""
        print("\n" + "="*50)
        print("SYSTEM INFORMATION")
        print("="*50)

        print(f"📁 Project Directory: {os.getcwd()}")
        print(f"📂 Data Files Path: {self.config_manager.get_data_files_path()}")
        print(f"📤 Export Path: {self.config_manager.get_export_path()}")
        print(f"🔄 Processed Path: {self.config_manager.get_processed_path()}")

        # Available banks
        available_banks = self.config_manager.get_available_banks()
        print(f"\n🏦 Configured Banks: {', '.join(available_banks)}")

        # Configuration status
        config_issues = self.config_manager.validate_config()
        if config_issues:
            print(f"\nWarning:  Configuration Issues:")
            for issue in config_issues:
                print(f"   * {issue}")
        else:
            print(f"\nOK: Configuration: Valid")

        # Directory status
        paths_to_check = [
            ("Data Files", self.config_manager.get_data_files_path()),
            ("Export", self.config_manager.get_export_path()),
            ("Processed", self.config_manager.get_processed_path()),
        ]

        print(f"\n📂 Directory Status:")
        for name, path in paths_to_check:
            exists = "OK:" if os.path.exists(path) else "ERROR:"
            print(f"   {exists} {name}: {path}")

    def configuration_menu(self):
        """Handle configuration management."""
        print("\n" + "="*50)
        print("CONFIGURATION")
        print("="*50)
        print("1. View current configuration")
        print("2. Add new bank adapter")
        print("3. Export configuration")
        print("4. Import configuration")
        print("0. Back to main menu")

        choice = input("\nSelect option (0-4): ").strip()

        if choice == "0":
            return
        elif choice == "1":
            self._view_configuration()
        elif choice == "2":
            self._add_bank_adapter()
        elif choice == "3":
            self._export_configuration()
        elif choice == "4":
            self._import_configuration()
        else:
            print("ERROR: Invalid option.")

    def _view_configuration(self):
        """Display current configuration."""
        import json

        print("\n📋 Current Configuration:")
        print("="*40)
        print(json.dumps(self.config_manager.config_data, indent=2, ensure_ascii=False))

    def _add_bank_adapter(self):
        """Interactive bank adapter creation."""
        print("\nAdd: Add New Bank Adapter")
        print("="*30)

        bank_name = input("Bank name: ").strip().upper()
        if not bank_name:
            print("ERROR: Bank name cannot be empty.")
            return

        if bank_name in self.config_manager.get_available_banks():
            print(f"ERROR: Bank '{bank_name}' already exists.")
            return

        print(f"\nCreating adapter for {bank_name}...")
        print("Please provide column mappings:")

        template = self.config_manager.create_bank_template(bank_name)
        config = template.copy()

        # Get column mappings
        for field in ["date", "description", "amount", "balance", "reference"]:
            default = template["column_mappings"][field]
            value = input(f"  {field.title()} column name [{default}]: ").strip()
            if value:
                config["column_mappings"][field] = value

        # Get other settings
        date_format = input(f"Date format [{template['date_format']}]: ").strip()
        if date_format:
            config["date_format"] = date_format

        encoding = input(f"File encoding [{template['encoding']}]: ").strip()
        if encoding:
            config["encoding"] = encoding

        # Save configuration
        self.config_manager.add_bank_config(bank_name, config)
        print(f"OK: Bank adapter '{bank_name}' added successfully!")

    def _export_configuration(self):
        """Export configuration to file."""
        export_path = input("Export path [config_backup.json]: ").strip()
        if not export_path:
            export_path = "config_backup.json"

        try:
            self.config_manager.export_config(export_path)
            print(f"OK: Configuration exported to: {export_path}")
        except Exception as e:
            print(f"ERROR: Export failed: {e}")

    def _import_configuration(self):
        """Import configuration from file."""
        import_path = input("Import path: ").strip()
        if not import_path or not os.path.exists(import_path):
            print("ERROR: File not found.")
            return

        merge = input("Merge with existing config? (y/n) [n]: ").strip().lower() == 'y'

        try:
            self.config_manager.import_config(import_path, merge)
            print(f"OK: Configuration imported from: {import_path}")
        except Exception as e:
            print(f"ERROR: Import failed: {e}")

    def _print_header(self):
        """Print application header."""
        print("\n" + "="*50)
        print("TRANSACTION ANALYSIS SYSTEM")
        print("="*50)

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


def main():
    """Main entry point."""
    try:
        app = TransactionAnalyzer()
        app.main_menu()
    except KeyboardInterrupt:
        print("\n\nExiting Transaction Analysis System. Goodbye!")
    except Exception as e:
        print(f"\nERROR: Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
End-to-end application test.
Tests the complete workflow from Excel to JSON output.
"""

import os
import sys
import json

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'adapters'))
sys.path.insert(0, project_root)

def test_complete_workflow():
    """Test the complete Excel to JSON workflow."""
    print("=" * 60)
    print("END-TO-END WORKFLOW TEST")
    print("=" * 60)

    try:
        # Import required modules
        from src.excel_importer import ExcelImporter
        from src.json_adapter import JSONAdapter

        print("+ All modules imported successfully")

        # Initialize components
        importer = ExcelImporter()
        json_adapter = JSONAdapter()

        print("+ Components initialized")

        # Find Excel files
        data_dir = os.path.join(project_root, 'Data_Files')
        excel_files = [f for f in os.listdir(data_dir) if f.endswith(('.xlsx', '.xls'))]

        if not excel_files:
            print("- No Excel files found for testing")
            return False

        test_file = os.path.join(data_dir, excel_files[0])
        print(f"+ Testing with: {excel_files[0]}")

        # Step 1: Load Excel file
        df = importer.load_excel_file(test_file)
        print(f"+ Excel loaded: {len(df)} rows, {len(df.columns)} columns")

        # Step 2: Process through JSON adapter
        result = json_adapter.process_dataframe(df, bank_name="IBI", source_file=excel_files[0])

        if not result.success:
            print(f"- Processing failed: {'; '.join(result.errors)}")
            return False

        print("+ Data processing successful")

        # Step 3: Verify transaction data
        transactions = result.transaction_set.transactions
        metadata = result.transaction_set.metadata

        print(f"+ Processed {len(transactions)} transactions")
        print(f"+ Date range: {metadata.date_range['start']} to {metadata.date_range['end']}")
        print(f"+ Bank: {metadata.bank}")

        # Step 4: Test JSON export
        json_path = json_adapter.export_to_json(result.transaction_set)
        print(f"+ JSON exported to: {json_path}")

        # Step 5: Verify JSON file
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)

            print(f"+ JSON file verified: {len(exported_data['transactions'])} transactions")
            print(f"+ File size: {os.path.getsize(json_path) / 1024:.1f} KB")

            # Test import back from JSON
            import_result = json_adapter.import_from_json(json_path)
            if import_result.success:
                imported_count = len(import_result.transaction_set.transactions)
                print(f"+ JSON import verified: {imported_count} transactions")

                # Compare counts
                if imported_count == len(transactions):
                    print("+ Round-trip test successful")
                else:
                    print(f"- Round-trip count mismatch: {imported_count} vs {len(transactions)}")
                    return False
            else:
                print(f"- JSON import failed: {'; '.join(import_result.errors)}")
                return False

        else:
            print(f"- JSON file not found: {json_path}")
            return False

        # Step 6: Test with different Excel files
        if len(excel_files) > 1:
            print(f"+ Testing with second file: {excel_files[1]}")
            test_file2 = os.path.join(data_dir, excel_files[1])
            df2 = importer.load_excel_file(test_file2)
            result2 = json_adapter.process_dataframe(df2, bank_name="IBI", source_file=excel_files[1])

            if result2.success:
                print(f"+ Second file processed: {len(result2.transaction_set.transactions)} transactions")
            else:
                print(f"- Second file failed: {'; '.join(result2.errors)}")

        print("\n" + "=" * 60)
        print("END-TO-END TEST SUMMARY")
        print("=" * 60)
        print("WORKFLOW VERIFIED SUCCESSFULLY!")
        print(f"- Excel import: WORKING")
        print(f"- Data processing: WORKING")
        print(f"- Bank adapter (IBI): WORKING")
        print(f"- JSON export: WORKING")
        print(f"- JSON import: WORKING")
        print(f"- Round-trip test: PASSED")

        return True

    except Exception as e:
        print(f"- End-to-end test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
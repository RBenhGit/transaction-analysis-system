"""
Test script to validate classifier metadata columns in IBI adapter.
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.adapters.ibi_adapter import IBIAdapter
from src.input.excel_reader import ExcelReader

def test_classifier_metadata():
    """Test that classifier metadata columns are added correctly."""

    print("=" * 80)
    print("Testing Classifier Metadata Integration")
    print("=" * 80)

    # Load real IBI data
    data_dir = Path(__file__).parent / "Data_Files"
    excel_files = list(data_dir.glob("IBI trans *.xlsx"))

    if not excel_files:
        print("❌ No IBI Excel files found in Data_Files/")
        return False

    # Test with the most recent file
    test_file = excel_files[-1]
    print(f"\n📂 Testing with: {test_file.name}")

    # Read Excel file
    reader = ExcelReader()
    df_raw = reader.read(str(test_file))
    print(f"✅ Loaded {len(df_raw)} raw transactions")

    # Transform with adapter
    adapter = IBIAdapter()
    df_transformed = adapter.transform(df_raw)
    print(f"✅ Transformed {len(df_transformed)} transactions")

    # Check for new metadata columns
    expected_columns = [
        'transaction_effect',
        'is_phantom',
        'share_direction',
        'share_quantity_abs',
        'cost_basis'
    ]

    print("\n" + "=" * 80)
    print("Checking Metadata Columns")
    print("=" * 80)

    all_present = True
    for col in expected_columns:
        if col in df_transformed.columns:
            print(f"✅ {col}: Present")
        else:
            print(f"❌ {col}: MISSING")
            all_present = False

    if not all_present:
        print("\n❌ Some metadata columns are missing!")
        return False

    # Analyze metadata distribution
    print("\n" + "=" * 80)
    print("Metadata Distribution")
    print("=" * 80)

    print("\n1. Transaction Effects:")
    print(df_transformed['transaction_effect'].value_counts())

    print("\n2. Phantom Positions:")
    phantom_count = df_transformed['is_phantom'].sum()
    real_count = len(df_transformed) - phantom_count
    print(f"   Real positions: {real_count}")
    print(f"   Phantom positions: {phantom_count}")

    print("\n3. Share Direction:")
    print(df_transformed['share_direction'].value_counts())

    print("\n4. Share Quantity (absolute):")
    print(f"   Min: {df_transformed['share_quantity_abs'].min():.2f}")
    print(f"   Max: {df_transformed['share_quantity_abs'].max():.2f}")
    print(f"   Mean: {df_transformed['share_quantity_abs'].mean():.2f}")

    print("\n5. Cost Basis:")
    print(f"   Min: {df_transformed['cost_basis'].min():.2f}")
    print(f"   Max: {df_transformed['cost_basis'].max():.2f}")
    print(f"   Mean: {df_transformed['cost_basis'].mean():.2f}")

    # Sample transactions
    print("\n" + "=" * 80)
    print("Sample Transactions with Metadata")
    print("=" * 80)

    # Show a few buy transactions
    buys = df_transformed[df_transformed['transaction_effect'] == 'buy'].head(2)
    print("\n📊 Buy Transactions:")
    for idx, row in buys.iterrows():
        print(f"\n   {row['security_name']} ({row['security_symbol']})")
        print(f"   Type: {row['transaction_type']}")
        print(f"   Effect: {row['transaction_effect']}")
        print(f"   Direction: {row['share_direction']}")
        print(f"   Quantity: {row['share_quantity_abs']:.2f}")
        print(f"   Cost Basis: {row['cost_basis']:.2f} {row['currency']}")
        print(f"   Phantom: {row['is_phantom']}")

    # Show a few sell transactions
    sells = df_transformed[df_transformed['transaction_effect'] == 'sell'].head(2)
    print("\n📊 Sell Transactions:")
    for idx, row in sells.iterrows():
        print(f"\n   {row['security_name']} ({row['security_symbol']})")
        print(f"   Type: {row['transaction_type']}")
        print(f"   Effect: {row['transaction_effect']}")
        print(f"   Direction: {row['share_direction']}")
        print(f"   Quantity: {row['share_quantity_abs']:.2f}")
        print(f"   Cost Basis: {row['cost_basis']:.2f} {row['currency']}")
        print(f"   Phantom: {row['is_phantom']}")

    # Show phantom positions
    phantoms = df_transformed[df_transformed['is_phantom'] == True].head(2)
    if len(phantoms) > 0:
        print("\n👻 Phantom Positions:")
        for idx, row in phantoms.iterrows():
            print(f"\n   {row['security_name']} ({row['security_symbol']})")
            print(f"   Type: {row['transaction_type']}")
            print(f"   Effect: {row['transaction_effect']}")
            print(f"   Phantom: {row['is_phantom']}")

    print("\n" + "=" * 80)
    print("✅ All tests passed! Classifier metadata integration successful.")
    print("=" * 80)

    return True

if __name__ == "__main__":
    try:
        success = test_classifier_metadata()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

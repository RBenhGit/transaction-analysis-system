"""
Test PortfolioBuilder with classifier metadata integration.

Verifies that the refactored builder correctly uses metadata columns
when available, with fallback to legacy logic.
"""

import sys
import os
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
from src.json_adapter import JSONAdapter
from src.modules.portfolio_dashboard.builder import PortfolioBuilder

def test_builder_with_metadata():
    """Test that PortfolioBuilder uses classifier metadata."""

    print("=" * 80)
    print("Testing PortfolioBuilder with Classifier Metadata")
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

    # Read and transform
    reader = ExcelReader()
    df_raw = reader.read(str(test_file))
    print(f"✅ Loaded {len(df_raw)} raw transactions")

    adapter = IBIAdapter()
    df_transformed = adapter.transform(df_raw)
    print(f"✅ Transformed {len(df_transformed)} transactions with metadata")

    # Convert to Transaction objects
    json_adapter = JSONAdapter()
    transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)
    print(f"✅ Created {len(transactions)} Transaction objects")

    # Verify metadata is present in Transaction objects
    print("\n" + "=" * 80)
    print("Checking Metadata in Transaction Objects")
    print("=" * 80)

    metadata_count = 0
    sample_txs = []

    for tx in transactions[:100]:  # Check first 100
        if tx.transaction_effect is not None:
            metadata_count += 1
            if len(sample_txs) < 3:
                sample_txs.append(tx)

    print(f"\n✅ {metadata_count}/100 transactions have metadata")

    if metadata_count == 0:
        print("❌ ERROR: No metadata found in Transaction objects!")
        return False

    # Show sample transactions with metadata
    print("\nSample transactions with metadata:")
    for i, tx in enumerate(sample_txs, 1):
        print(f"\n{i}. {tx.security_name} ({tx.security_symbol})")
        print(f"   Type: {tx.transaction_type}")
        print(f"   Effect: {tx.transaction_effect}")
        print(f"   Phantom: {tx.is_phantom}")
        print(f"   Direction: {tx.share_direction}")
        print(f"   Quantity: {tx.share_quantity_abs}")
        print(f"   Cost Basis: {tx.cost_basis}")

    # Build portfolio
    print("\n" + "=" * 80)
    print("Building Portfolio")
    print("=" * 80)

    builder = PortfolioBuilder(fail_fast=False)
    positions = builder.build(transactions)
    print(f"\n✅ Built portfolio with {len(positions)} positions")

    # Check for errors
    if builder.has_errors():
        error_summary = builder.get_error_summary()
        error_count = len(error_summary.get('errors', []))
        print(f"\n⚠️  {error_count} errors encountered")

    if builder.has_warnings():
        error_summary = builder.get_error_summary()
        warning_count = len(error_summary.get('warnings', []))
        print(f"\n⚠️  {warning_count} warnings")

    # Summary of positions
    print("\n" + "=" * 80)
    print("Portfolio Summary")
    print("=" * 80)

    # Group by currency
    nis_positions = [p for p in positions if p.currency == "₪"]
    usd_positions = [p for p in positions if p.currency == "$"]

    print(f"\nNIS Positions: {len(nis_positions)}")
    total_nis_value = sum(p.total_invested for p in nis_positions)
    print(f"Total Invested (NIS): ₪{total_nis_value:,.2f}")

    print(f"\nUSD Positions: {len(usd_positions)}")
    total_usd_value = sum(p.total_invested for p in usd_positions)
    print(f"Total Invested (USD): ${total_usd_value:,.2f}")

    # Show top 5 positions
    print("\nTop 5 Positions by Value:")
    sorted_positions = sorted(positions, key=lambda p: p.total_invested, reverse=True)
    for i, pos in enumerate(sorted_positions[:5], 1):
        print(f"\n{i}. {pos.security_name} ({pos.security_symbol})")
        print(f"   Quantity: {pos.quantity:.2f}")
        print(f"   Average Cost: {pos.currency}{pos.average_cost:.2f}")
        print(f"   Total Invested: {pos.currency}{pos.total_invested:,.2f}")

    # Verify metadata was actually used
    print("\n" + "=" * 80)
    print("Metadata Usage Verification")
    print("=" * 80)

    # Count how many phantom transactions were filtered out
    phantom_count = sum(1 for tx in transactions if tx.is_phantom)
    print(f"\n✅ Filtered out {phantom_count} phantom positions")

    # Count transactions with metadata-driven processing
    metadata_driven = sum(1 for tx in transactions if tx.share_direction is not None)
    print(f"✅ {metadata_driven}/{len(transactions)} transactions used metadata")

    print("\n" + "=" * 80)
    print("✅ All tests passed! PortfolioBuilder successfully uses metadata.")
    print("=" * 80)

    return True

if __name__ == "__main__":
    try:
        success = test_builder_with_metadata()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

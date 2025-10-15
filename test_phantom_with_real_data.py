"""
Test phantom detection with real IBI data.

Validates that phantom positions (tax entries, fees) are properly excluded
from portfolio calculations.
"""

from src.input.excel_reader import ExcelReader
from src.adapters.ibi_adapter import IBIAdapter
from src.json_adapter import JSONAdapter
from src.modules.portfolio_dashboard.builder import PortfolioBuilder


def test_phantom_detection_with_real_data():
    """Test phantom detection using real IBI transaction data."""

    print("=" * 80)
    print("Testing Phantom Position Detection with Real IBI Data")
    print("=" * 80)

    # Load real IBI transactions using the proper data flow
    file_path = "Data_Files/IBI trans 2022-5_10_2025.xlsx"

    print(f"\nLoading transactions from: {file_path}")

    # Step 1: Read Excel file
    reader = ExcelReader()
    df_raw = reader.read(file_path)

    # Step 2: Transform using IBI adapter
    adapter = IBIAdapter()
    df_transformed = adapter.transform(df_raw)

    # Step 3: Convert to Transaction objects
    json_adapter = JSONAdapter()
    transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)

    print(f"Loaded {len(transactions)} total transactions")

    # Identify phantom transactions
    phantom_count = 0
    phantom_symbols = set()
    phantom_names = set()

    print("\nScanning for phantom securities...")
    builder = PortfolioBuilder()

    for tx in transactions:
        if builder._is_phantom_security(tx):
            phantom_count += 1
            phantom_symbols.add(tx.security_symbol)
            phantom_names.add(tx.security_name)

    print(f"\nPhantom Detection Results:")
    print(f"   Total transactions: {len(transactions)}")
    print(f"   Phantom transactions: {phantom_count}")
    print(f"   Real stock transactions: {len(transactions) - phantom_count}")

    print(f"\nUnique phantom symbols found ({len(phantom_symbols)}):")
    for symbol in sorted(phantom_symbols):
        print(f"   - {symbol}")

    print(f"\nUnique phantom security names found ({len(phantom_names)}):")
    for name in sorted(phantom_names):
        # Handle Hebrew text encoding for Windows console
        try:
            print(f"   - {name}")
        except UnicodeEncodeError:
            # Print safe ASCII representation if Hebrew can't be displayed
            print(f"   - [Hebrew text: {len(name)} chars]")

    # Build portfolio (phantoms should be excluded)
    print("\nBuilding portfolio (excluding phantoms)...")
    positions = builder.build(transactions)

    print(f"\nPortfolio built successfully")
    print(f"   Active positions: {len(positions)}")

    # Verify no phantom symbols in portfolio
    print("\nVerification: Checking for phantom symbols in portfolio...")
    phantom_in_portfolio = []
    for pos in positions:
        if pos.security_symbol.startswith('999'):
            phantom_in_portfolio.append(pos.security_symbol)
        if pos.security_symbol.upper() in ['FEE', 'TAX']:
            phantom_in_portfolio.append(pos.security_symbol)
        if any(pattern in pos.security_name for pattern in ['מס ששולם', 'דמי טפול', 'עמלת']):
            phantom_in_portfolio.append(f"{pos.security_symbol} ({pos.security_name})")

    if phantom_in_portfolio:
        print(f"FAILED: Found {len(phantom_in_portfolio)} phantom positions in portfolio:")
        for phantom in phantom_in_portfolio:
            print(f"   - {phantom}")
        return False
    else:
        print("SUCCESS: No phantom positions found in portfolio!")

    # Display sample positions
    print("\nSample Portfolio Positions (first 5):")
    for pos in positions[:5]:
        try:
            print(f"   {pos.security_symbol:8} | {pos.security_name:30} | Qty: {pos.quantity:>8.2f} | Avg Cost: ${pos.average_cost:>8.2f}")
        except UnicodeEncodeError:
            # Handle Hebrew security names for Windows console
            print(f"   {pos.security_symbol:8} | [Hebrew name] | Qty: {pos.quantity:>8.2f} | Avg Cost: ${pos.average_cost:>8.2f}")

    print("\n" + "=" * 80)
    print("Test completed successfully!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    try:
        success = test_phantom_detection_with_real_data()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

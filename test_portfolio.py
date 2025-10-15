"""
Test script for Portfolio Dashboard with REAL IBI transaction data.
"""

import sys
import io

# Fix Windows console encoding for Hebrew characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.input.excel_reader import ExcelReader
from src.adapters.ibi_adapter import IBIAdapter
from src.json_adapter import JSONAdapter
from src.modules.portfolio_dashboard import PortfolioBuilder

def main():
    print("=" * 80)
    print("PORTFOLIO DASHBOARD TEST - REAL IBI DATA")
    print("=" * 80)

    # Load REAL IBI 2024 transactions
    print("\n1. Loading real IBI transaction file...")
    reader = ExcelReader()
    excel_file = "Data_Files/IBI trans 2024.xlsx"

    try:
        df_raw = reader.read(excel_file)
        print(f"   [OK] Loaded {len(df_raw)} rows from {excel_file}")
    except Exception as e:
        print(f"   [ERROR] Error loading file: {e}")
        return

    # Transform with IBI adapter
    print("\n2. Transforming with IBI adapter...")
    adapter = IBIAdapter()
    df_transformed = adapter.transform(df_raw)
    print(f"   [OK] Transformed to standard format")

    # Convert to Transaction objects
    print("\n3. Converting to Transaction objects...")
    json_adapter = JSONAdapter()
    transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)
    print(f"   [OK] Created {len(transactions)} Transaction objects from real data")

    # Build portfolio separated by currency
    print("\n4. Building portfolio from real transactions...")
    builder = PortfolioBuilder()
    positions_by_currency = builder.build_by_currency(transactions)
    total_positions = sum(len(positions) for positions in positions_by_currency.values())
    print(f"   [OK] Portfolio built with {total_positions} positions across {len(positions_by_currency)} currencies")

    # Display results
    print("\n" + "=" * 80)
    print("CURRENT PORTFOLIO (FROM REAL TRANSACTIONS) - SEPARATED BY CURRENCY")
    print("=" * 80)

    if len(positions_by_currency) == 0:
        print("\nNo current positions (all positions closed)")
    else:
        for currency in sorted(positions_by_currency.keys()):
            positions = positions_by_currency[currency]
            currency_name = "Shekel (NIS)" if currency == "₪" else "Dollar (USD)" if currency == "$" else currency

            print(f"\n{'=' * 80}")
            print(f"{currency} {currency_name} PORTFOLIO")
            print(f"{'=' * 80}")
            print(f"Positions: {len(positions)}")
            print("-" * 80)

            currency_total = 0
            for i, pos in enumerate(positions, 1):
                print(f"\n{i}. {pos.security_name} ({pos.security_symbol})")
                print(f"   Quantity:       {pos.quantity:.2f} shares")
                print(f"   Average Cost:   {pos.currency}{pos.average_cost:.2f} per share")
                print(f"   Total Invested: {pos.currency}{pos.total_invested:,.2f}")
                currency_total += pos.total_invested

            print("\n" + "-" * 80)
            print(f"{currency} TOTAL INVESTED: {currency}{currency_total:,.2f}")
            print("=" * 80)

    print("\n" + "=" * 80)
    print("[SUCCESS] Test completed successfully with REAL data")
    print("=" * 80)

if __name__ == "__main__":
    main()

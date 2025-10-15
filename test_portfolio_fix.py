"""Test portfolio calculation with fixes."""
import pandas as pd
from src.input.excel_reader import ExcelReader
from src.adapters.ibi_adapter import IBIAdapter
from src.json_adapter import JSONAdapter
from src.modules.portfolio_dashboard import PortfolioBuilder

# Load and process
print("Loading data...")
reader = ExcelReader()
df_raw = reader.read('Data_Files/IBI trans 2022-5_10_2025.xlsx')

print("Transforming data...")
adapter = IBIAdapter()
df_transformed = adapter.transform(df_raw)

print("Converting to transactions...")
json_adapter = JSONAdapter()
transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)

print(f"Total transactions: {len(transactions)}")

# Build portfolio
print("Building portfolio...")
builder = PortfolioBuilder()
positions_by_currency = builder.build_by_currency(transactions)

# Calculate totals
print("\nCALCULATED PORTFOLIO (AFTER FIX):")
print("=" * 70)

usd_total = 0
nis_total = 0

for currency in sorted(positions_by_currency.keys()):
    positions = positions_by_currency[currency]
    total = sum(pos.total_invested for pos in positions)

    if currency == '$':
        usd_total = total
        print(f'USD Total Cost Basis: ${total:,.2f}')
        print(f'USD Number of positions: {len(positions)}')
    else:
        nis_total = total
        print(f'NIS Total Cost Basis: {total:,.2f} shekels')
        print(f'NIS Number of positions: {len(positions)}')

print("\nEXPECTED FROM IBI ACTUAL PORTFOLIO:")
print("=" * 70)
print("NIS Total: 88,061.82 shekels")
print("USD Total: $194,933.26")

print("\nCOMPARISON:")
print("=" * 70)
nis_diff = nis_total - 88061.82
usd_diff = usd_total - 194933.26
print(f'NIS: {nis_total:,.2f} vs 88,061.82 (diff: {nis_diff:+,.2f})')
print(f'USD: ${usd_total:,.2f} vs $194,933.26 (diff: ${usd_diff:+,.2f})')

# Check if reasonable
if abs(nis_diff) < 10000 and abs(usd_diff) < 10000:
    print("\n✓ Portfolio calculations look reasonable!")
else:
    print("\n✗ Portfolio calculations still have issues")

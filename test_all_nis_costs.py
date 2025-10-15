"""Test all NIS position costs."""
import pandas as pd
from src.input.excel_reader import ExcelReader
from src.adapters.ibi_adapter import IBIAdapter
from src.json_adapter import JSONAdapter
from src.modules.portfolio_dashboard import PortfolioBuilder

# Load data
reader = ExcelReader()
df_raw = reader.read('Data_Files/IBI trans 2022-5_10_2025.xlsx')
adapter = IBIAdapter()
df_transformed = adapter.transform(df_raw)
json_adapter = JSONAdapter()
transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)

# Build portfolio
builder = PortfolioBuilder()
positions_by_currency = builder.build_by_currency(transactions)

# Show each NIS position
shekel_key = [k for k in positions_by_currency.keys() if k != '$'][0]
nis_positions = positions_by_currency[shekel_key]

print("NIS Positions (sorted by cost):")
print("=" * 80)
for pos in sorted(nis_positions, key=lambda p: p.total_invested, reverse=True):
    print(f"{pos.security_symbol:20} {pos.quantity:10.2f} {pos.total_invested:30,.2f}")

    # Flag astronomical values
    if pos.total_invested > 1000000:
        print(f"  ^^^ ASTRONOMICAL VALUE ^^^")

print()
print(f"Total: {sum(p.total_invested for p in nis_positions):,.2f}")

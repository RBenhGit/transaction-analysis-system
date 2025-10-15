"""Detailed test with logging."""
import pandas as pd
from src.input.excel_reader import ExcelReader
from src.adapters.ibi_adapter import IBIAdapter
from src.json_adapter import JSONAdapter
from src.modules.portfolio_dashboard import PortfolioBuilder
from src.modules.portfolio_dashboard.position import Position

# Custom builder with logging
class LoggingBuilder(PortfolioBuilder):
    def _process_buy(self, position: Position, tx):
        old_invested = position.total_invested
        super()._process_buy(position, tx)
        new_invested = position.total_invested
        added_cost = new_invested - old_invested

        # Check for astronomical values
        if added_cost > 1000000:  # More than 1 million
            print(f"HUGE COST ADDED: {added_cost:,.0f}")
            print(f"  Security: {tx.security_name}")
            print(f"  Type: {tx.transaction_type}")
            print(f"  Currency: {tx.currency}")
            print(f"  Quantity: {tx.quantity}")
            print(f"  Execution Price: {tx.execution_price}")
            print(f"  Amount Local: {tx.amount_local_currency}")
            print(f"  Amount Foreign: {tx.amount_foreign_currency}")
            print()

# Load data
reader = ExcelReader()
df_raw = reader.read('Data_Files/IBI trans 2022-5_10_2025.xlsx')
adapter = IBIAdapter()
df_transformed = adapter.transform(df_raw)
json_adapter = JSONAdapter()
transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)

print(f"Building portfolio with logging...")
builder = LoggingBuilder()
positions_by_currency = builder.build_by_currency(transactions)

# Show totals
for currency in sorted(positions_by_currency.keys()):
    positions = positions_by_currency[currency]
    total = sum(pos.total_invested for pos in positions)
    if currency == '$':
        print(f"USD Total: ${total:,.2f}")
    else:
        print(f"NIS Total: {total:,.2f} shekels")

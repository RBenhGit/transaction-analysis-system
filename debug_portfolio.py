"""Debug portfolio calculation."""
import pandas as pd
from src.input.excel_reader import ExcelReader
from src.adapters.ibi_adapter import IBIAdapter
from src.json_adapter import JSONAdapter

# Load and process
reader = ExcelReader()
df_raw = reader.read('Data_Files/IBI trans 2022-5_10_2025.xlsx')
adapter = IBIAdapter()
df = adapter.transform(df_raw)

# Get NIS transactions for one security
nis_df = df[df['currency'] != '$']
security_name = 'סקופ'  # Scope - a simple NIS stock

security_txns = nis_df[nis_df['security_name'] == security_name].sort_values('date')

print("Analyzing security:")
print(f"Total transactions: {len(security_txns)}\n")

# Manual calculation
total_cost = 0
total_qty = 0

for idx, row in security_txns.iterrows():
    tx_type = row['transaction_type']
    qty = row['quantity']
    amount_local = row['amount_local_currency']
    amount_foreign = row['amount_foreign_currency']

    if 'קניה' in tx_type or 'הפקדה' in tx_type:  # Buy or Deposit
        cost = abs(amount_local)  # Use actual cost from IBI
        total_cost += cost
        total_qty += qty
        print(f"BUY/DEPOSIT: Qty={qty:6.1f} Cost={cost:10.2f} Running Total: Qty={total_qty:7.1f} Cost={total_cost:12.2f}")

    elif 'מכירה' in tx_type or 'משיכה' in tx_type:  # Sell or Withdrawal
        avg_cost = total_cost / total_qty if total_qty > 0 else 0
        sold_cost = qty * avg_cost
        total_cost -= sold_cost
        total_qty -= qty
        print(f"SELL:        Qty={qty:6.1f} Cost={sold_cost:10.2f} Running Total: Qty={total_qty:7.1f} Cost={total_cost:12.2f}")

print(f"\nFinal position:")
print(f"Quantity: {total_qty:.2f}")
print(f"Cost Basis: {total_cost:,.2f} shekels")

# Compare with IBI actual
print("\nFrom IBI actual portfolio:")
print("Quantity: 139.00")
print("Cost: 21,402.09 shekels")

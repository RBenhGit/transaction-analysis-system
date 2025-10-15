# Assets Portfolio Dashboard - Simple Chronological Implementation Plan

## 📋 Executive Summary

**Purpose**: Build a simple dashboard that shows what assets you currently own by processing transactions chronologically from first to last.

**Approach**:
- Start with empty portfolio
- Process each transaction in date order
- Update holdings as we go
- Display current positions

**NO complex analytics** - just show what you own right now.

---

## 🎯 Core Concept: Chronological Processing

```
Start: Portfolio = {}

Transaction 1: Buy 100 AAPL @ $150
→ Portfolio = { AAPL: 100 shares @ $150 avg cost }

Transaction 2: Buy 50 AAPL @ $160
→ Portfolio = { AAPL: 150 shares @ $153.33 avg cost }

Transaction 3: Sell 80 AAPL @ $170
→ Portfolio = { AAPL: 70 shares @ $153.33 avg cost }

Transaction 4: Buy 200 MSFT @ $300
→ Portfolio = {
    AAPL: 70 shares @ $153.33 avg cost,
    MSFT: 200 shares @ $300 avg cost
  }

End: Display current portfolio
```

---

## 📊 Simple Data Model

### Position (What you own right now)

```python
class Position:
    security_name: str          # "Apple Inc"
    security_symbol: str        # "AAPL"
    quantity: float             # 70.0 (actual shares owned)
    average_cost: float         # $153.33 per share (your cost basis)
    total_invested: float       # $10,733.10 (actual money you paid)
    currency: str               # "$" or "₪"
```

### Portfolio (All your positions)

```python
class Portfolio:
    positions: List[Position]   # List of what you own
    last_updated: datetime      # When was this calculated
```

### ⚠️ Important: Nominal vs Actual Values

**This module tracks ACTUAL VALUES only:**

1. **Actual Quantity**: Real number of shares you currently own
   - Example: Buy 100, Buy 50, Sell 80 → **Actual = 70 shares**

2. **Actual Cost Basis**: Real money you paid (weighted average)
   - Example: Buy 100 @ $150 + Buy 50 @ $160 → **Actual avg cost = $153.33**
   - This is what you ACTUALLY paid per share

3. **Actual Amount Invested**: Real cash invested (still in positions)
   - Example: 70 shares @ $153.33 avg = **Actual invested = $10,733.10**
   - This reflects money still tied up in the position

4. **Actual Transaction Data**: Use real values from loaded Excel files
   - `amount_local_currency` = actual NIS amount from transaction
   - `amount_foreign_currency` = actual foreign currency amount
   - `execution_price` = actual price per share executed
   - `quantity` = actual number of shares in transaction

**NOT included yet:**
- ❌ Current market value (nominal/market value)
- ❌ Unrealized gains (difference between market and cost)
- ❌ Projected values or estimates

**All values are historical actuals from your transaction history.**

---

## 🏗️ Simple Module Structure

```
src/modules/portfolio_dashboard/
├── __init__.py
│
├── builder.py                  # Main: builds portfolio from transactions
│   └── PortfolioBuilder        # Process transactions chronologically
│
├── position.py                 # Position data model
│   └── Position
│
└── view.py                     # Streamlit display
    └── display_portfolio()     # Show current holdings table
```

Just 3 files. That's all.

---

## 🔨 Implementation Plan

### Step 1: Build the Position Model
**File**: `src/modules/portfolio_dashboard/position.py`

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Position:
    """What you currently own for one security"""

    security_name: str
    security_symbol: str
    quantity: float
    average_cost: float
    total_invested: float
    currency: str

    def __str__(self):
        return f"{self.security_name}: {self.quantity} shares @ ${self.average_cost:.2f}"
```

**Test**: Create a position manually and print it.

---

### Step 2: Build the Portfolio Builder
**File**: `src/modules/portfolio_dashboard/builder.py`

```python
from typing import List, Dict
from src.models.transaction import Transaction
from .position import Position

class PortfolioBuilder:
    """Builds portfolio by processing transactions chronologically"""

    def __init__(self):
        self.positions: Dict[str, Position] = {}  # symbol -> position

    def build(self, transactions: List[Transaction]) -> List[Position]:
        """
        Main function: Process all transactions in order
        """
        # 1. Sort transactions by date (oldest first)
        sorted_txs = sorted(transactions, key=lambda t: t.date)

        # 2. Process each transaction
        for tx in sorted_txs:
            self._process_transaction(tx)

        # 3. Return current positions (filter out zero quantities)
        return [p for p in self.positions.values() if p.quantity > 0]

    def _process_transaction(self, tx: Transaction):
        """Process one transaction and update positions"""

        symbol = tx.security_symbol

        # Get existing position or create new one
        if symbol not in self.positions:
            self.positions[symbol] = Position(
                security_name=tx.security_name,
                security_symbol=symbol,
                quantity=0.0,
                average_cost=0.0,
                total_invested=0.0,
                currency=tx.currency
            )

        position = self.positions[symbol]

        # Update position based on transaction type
        if tx.is_buy:
            self._process_buy(position, tx)
        elif tx.is_sell:
            self._process_sell(position, tx)
        # Ignore dividends, fees, taxes for now

    def _process_buy(self, position: Position, tx: Transaction):
        """Add shares to position"""

        # Calculate new total
        new_quantity = position.quantity + tx.quantity
        new_total_invested = position.total_invested + (tx.quantity * tx.execution_price)

        # Update position
        position.quantity = new_quantity
        position.total_invested = new_total_invested
        position.average_cost = new_total_invested / new_quantity if new_quantity > 0 else 0

    def _process_sell(self, position: Position, tx: Transaction):
        """Remove shares from position"""

        # Calculate new total (reduce by average cost, not sale price)
        sold_value = tx.quantity * position.average_cost

        # Update position
        position.quantity -= tx.quantity
        position.total_invested -= sold_value

        # Average cost stays the same (we sold at our average cost basis)
```

**Test**:
```python
# Test with simple transactions
transactions = [
    buy_tx(date="2024-01-01", symbol="AAPL", qty=100, price=150),
    buy_tx(date="2024-02-01", symbol="AAPL", qty=50, price=160),
    sell_tx(date="2024-03-01", symbol="AAPL", qty=80, price=170)
]

builder = PortfolioBuilder()
positions = builder.build(transactions)

print(positions)
# Should show: AAPL: 70 shares @ $153.33
```

---

### Step 3: Display in Streamlit
**File**: `src/modules/portfolio_dashboard/view.py`

```python
import streamlit as st
import pandas as pd
from typing import List
from .position import Position

def display_portfolio(positions: List[Position]):
    """Display current portfolio holdings"""

    st.subheader("📊 Current Portfolio Holdings")

    if not positions:
        st.info("No positions. Portfolio is empty.")
        return

    # Convert to DataFrame for display
    data = []
    for pos in positions:
        data.append({
            "Security": pos.security_name,
            "Symbol": pos.security_symbol,
            "Quantity": f"{pos.quantity:.2f}",
            "Avg Cost": f"{pos.currency}{pos.average_cost:.2f}",
            "Total Invested": f"{pos.currency}{pos.total_invested:,.2f}",
        })

    df = pd.DataFrame(data)

    # Display table
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Summary
    total_invested = sum(pos.total_invested for pos in positions)
    st.metric("Total Invested", f"₪{total_invested:,.2f}")
```

---

### Step 4: Add to Main App
**File**: `app.py` (add new tab)

```python
# Import
from src.modules.portfolio_dashboard.builder import PortfolioBuilder
from src.modules.portfolio_dashboard.view import display_portfolio

# In main app, add new tab
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Transactions",
    "📊 Analytics",
    "💹 Securities",
    "📈 Charts",
    "🏦 Portfolio"  # NEW TAB
])

# ... existing tabs ...

with tab5:
    st.subheader("Assets Portfolio")

    # ⚠️ CRITICAL: Use REAL loaded transactions from Excel files
    # The 'transactions' variable already contains actual IBI transaction data
    # loaded from Data_Files/*.xlsx via load_ibi_data()

    if transactions is None or len(transactions) == 0:
        st.warning("No transactions loaded. Please select a transaction file from the sidebar.")
    else:
        # Build portfolio from REAL transaction data
        builder = PortfolioBuilder()
        positions = builder.build(transactions)  # transactions = actual loaded data

        # Display actual portfolio
        display_portfolio(positions)

        # Show data source
        st.caption(f"📊 Portfolio calculated from {len(transactions)} real transactions")
```

**Critical Notes:**
- `transactions` variable contains **actual Transaction objects** from loaded Excel files
- These are real IBI broker transactions with actual quantities, prices, and amounts
- NO mock data - portfolio reflects your actual holdings based on real transaction history

---

## 🎨 Simple Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🏦 CURRENT PORTFOLIO                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Summary                                                     │
│  ┌────────────────────┬────────────────────────────────┐   │
│  │ Total Invested     │ Number of Positions            │   │
│  │ ₪145,230           │ 8                              │   │
│  └────────────────────┴────────────────────────────────┘   │
│                                                              │
│  Holdings                                                    │
│  ┌──────────────┬────────┬──────────┬──────────┬─────────┐ │
│  │ Security     │ Symbol │ Quantity │ Avg Cost │ Invested│ │
│  ├──────────────┼────────┼──────────┼──────────┼─────────┤ │
│  │ Apple Inc    │ AAPL   │ 100.00   │ $150.00  │ $15,000 │ │
│  │ Microsoft    │ MSFT   │ 50.00    │ $320.00  │ $16,000 │ │
│  │ Tesla Inc    │ TSLA   │ 25.00    │ $245.00  │ $6,125  │ │
│  │ ...          │        │          │          │         │ │
│  └──────────────┴────────┴──────────┴──────────┴─────────┘ │
│                                                              │
│  [📥 Export to Excel]                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Testing Plan

### Unit Tests (Development Only - Use Mock Data)

**Note**: These tests use simplified mock data for logic verification only.

### Test 1: Single Buy
```python
txs = [buy("AAPL", 100, 150)]
result = builder.build(txs)
assert result[0].quantity == 100
assert result[0].average_cost == 150
```

### Test 2: Multiple Buys (Average Cost)
```python
txs = [
    buy("AAPL", 100, 150),
    buy("AAPL", 100, 170)
]
result = builder.build(txs)
assert result[0].quantity == 200
assert result[0].average_cost == 160  # (150+170)/2
```

### Test 3: Buy Then Sell
```python
txs = [
    buy("AAPL", 100, 150),
    sell("AAPL", 50, 170)
]
result = builder.build(txs)
assert result[0].quantity == 50
assert result[0].average_cost == 150  # Cost basis unchanged
```

### Test 4: Multiple Securities
```python
txs = [
    buy("AAPL", 100, 150),
    buy("MSFT", 50, 300)
]
result = builder.build(txs)
assert len(result) == 2
```

### Test 5: Sell All (Position Closed)
```python
txs = [
    buy("AAPL", 100, 150),
    sell("AAPL", 100, 170)
]
result = builder.build(txs)
assert len(result) == 0  # Position removed when quantity = 0
```

### Test 6: Date Order Matters
```python
# Transactions out of order in file
txs = [
    sell("AAPL", 50, 170, date="2024-03-01"),  # Later
    buy("AAPL", 100, 150, date="2024-01-01")   # Earlier
]
result = builder.build(txs)
assert result[0].quantity == 50  # Processes buy first, then sell
```

---

### Integration Test (REAL DATA - Critical!)

**Test 7: Real IBI Transaction Data**
```python
# Load ACTUAL Excel file
from src.input.excel_reader import ExcelReader
from adapters.ibi_adapter import IBIAdapter
from src.json_adapter import JSONAdapter

# Load real IBI 2024 transactions
reader = ExcelReader()
df_raw = reader.read("Data_Files/IBI trans 2024.xlsx")

# Transform with IBI adapter
adapter = IBIAdapter()
df_transformed = adapter.transform(df_raw)

# Convert to Transaction objects
json_adapter = JSONAdapter()
transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)

# Build portfolio from REAL data
builder = PortfolioBuilder()
positions = builder.build(transactions)

# Verify against actual broker statement
print(f"Total positions: {len(positions)}")
print(f"Total transactions processed: {len(transactions)}")

for pos in positions:
    print(f"{pos.security_name}: {pos.quantity} shares @ {pos.currency}{pos.average_cost:.2f}")
    print(f"  Total invested: {pos.currency}{pos.total_invested:,.2f}")
```

**Validation Steps:**
1. Compare position quantities with actual broker statement
2. Verify total invested amounts match actual cash spent
3. Check that all securities from broker statement appear in portfolio
4. Confirm no positions exist that shouldn't be there

---

## 🚀 Implementation Steps (In Order)

### Day 1: Setup
- [ ] Create module folder: `src/modules/portfolio_dashboard/`
- [ ] Create `__init__.py`
- [ ] Create `position.py` with Position dataclass
- [ ] Test: Create and print a Position object

### Day 2: Core Logic
- [ ] Create `builder.py` with PortfolioBuilder class
- [ ] Implement `build()` method (sort transactions)
- [ ] Implement `_process_buy()` method
- [ ] Test: Process single buy transaction

### Day 3: Buy/Sell Logic
- [ ] Implement `_process_sell()` method
- [ ] Handle multiple buys (average cost calculation)
- [ ] Handle sell reducing position
- [ ] Test: All test cases above

### Day 4: Streamlit Integration
- [ ] Create `view.py` with display function
- [ ] Add Portfolio tab to main app
- [ ] Wire up: transactions → builder → display
- [ ] Test: View portfolio in browser

### Day 5: Polish
- [ ] Add export to Excel button
- [ ] Handle edge cases (empty portfolio, etc.)
- [ ] Add helpful messages
- [ ] Final testing with real IBI data

---

## 📝 What This Does NOT Include (Yet)

❌ Current market prices (just shows what you paid)
❌ Profit/loss calculations (no comparison to current value)
❌ Charts and visualizations (just a table)
❌ Performance metrics (Sharpe ratio, etc.)
❌ Tax calculations
❌ Dividend tracking
❌ Fee impact on returns
❌ Historical portfolio snapshots

**These can be added later, one at a time.**

---

## 🎯 Success Criteria

### Functional Requirements
✅ Display all current holdings from **real IBI transaction history**
✅ Correct actual quantity for each position
✅ Correct actual average cost calculation (weighted by shares)
✅ Handle buys and sells properly (maintain accurate cost basis)
✅ Process transactions in chronological order (date-sorted)
✅ Show empty portfolio if no current positions
✅ Export actual portfolio data to Excel

### Data Accuracy Requirements
✅ **Use ONLY real loaded transaction data** from Excel files
✅ All calculations based on **actual execution prices** from transactions
✅ All quantities reflect **actual shares bought/sold**
✅ All amounts use **actual transaction amounts** (local and foreign currency)
✅ Portfolio totals match **actual money invested** (verifiable against broker statements)

### Validation Requirements
✅ Position quantities match actual broker statement holdings
✅ Average cost calculations are mathematically correct
✅ Closed positions (quantity = 0) are properly removed
✅ Multi-currency positions handled correctly (maintain currency from transactions)
✅ No phantom positions (all positions traceable to actual transactions)

---

## 📋 File Checklist

**New Files to Create:**
```
src/modules/portfolio_dashboard/
├── __init__.py                    # Empty (or imports)
├── position.py                    # Position dataclass
├── builder.py                     # PortfolioBuilder class
└── view.py                        # display_portfolio() function
```

**Files to Modify:**
```
app.py                             # Add Portfolio tab
```

**Total**: 4 new files, 1 modified file

---

## 💡 Future Enhancements (After MVP Works)

### Phase 2: Add Current Prices
- Fetch live prices from Yahoo Finance
- Show current value vs invested
- Calculate unrealized gain/loss

### Phase 3: Add Simple Charts
- Pie chart: allocation by security
- Bar chart: holdings by value

### Phase 4: Historical Snapshots
- Save portfolio state at end of each month
- Show portfolio growth over time

### Phase 5: Advanced Analytics
- Performance metrics
- Risk calculations
- Tax reporting

**But not now. First, just get the basic portfolio working.**

---

## 🏁 Summary

**Goal**: Show what assets you own right now based on **actual transaction history**

**Data Flow (All Real Values)**:
```
1. Load Excel files → Real IBI transaction data
2. IBI Adapter transforms → Real Transaction objects with actual:
   - Execution prices
   - Quantities
   - Amounts (local & foreign currency)
3. PortfolioBuilder processes → Actual positions with real:
   - Share quantities
   - Average costs (weighted)
   - Money invested
4. Display → Real portfolio holdings
```

**How**:
1. Sort **real transactions** by date
2. Process each **actual transaction** chronologically
3. Update positions with **actual quantities and costs**
4. Display **actual final positions**

**Output**: Simple table showing **real values**:
- What you own (actual security name from transactions)
- How much you own (actual quantity calculated from buys/sells)
- What you paid on average (actual weighted average cost)
- Total amount invested (actual money still in positions)

**Critical**: Every number displayed is derived from **actual loaded transaction data**. No estimates, no mock data, no projections - just facts from your transaction history.

**That's it. Keep it simple and real.**

---

*Document Version: 2.0 - Simplified*
*Focus: Chronological portfolio building only*
*Estimated Time: 3-5 days*

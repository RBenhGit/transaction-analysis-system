# Assets Portfolio Dashboard - Implementation Plan

## 📋 Executive Summary

The **Assets Portfolio Dashboard** module is a comprehensive investment portfolio tracking system that transforms transaction-level data into actionable portfolio insights. It calculates current holdings, tracks performance, analyzes asset allocation, and provides real-time portfolio valuation using live market data.

**Key Purpose**: Convert raw transaction history → Current portfolio positions → Performance analytics → Investment insights

---

## 🎯 Module Objectives

### Primary Goals
1. **Position Tracking**: Calculate current holdings for each security from transaction history
2. **Performance Analysis**: Track realized/unrealized gains, ROI, and portfolio performance
3. **Asset Allocation**: Visualize portfolio distribution by security, sector, currency, and geography
4. **Live Valuation**: Fetch real-time prices and calculate current portfolio value
5. **Historical Performance**: Track portfolio value over time with benchmarking

### Success Metrics
- Accurate position calculations (100% match with broker statements)
- Real-time price updates (< 5 second refresh)
- Complete transaction reconciliation
- Interactive visualizations for all metrics
- Export capabilities for all reports

---

## 🏗️ Architecture Design

### 1. Data Flow Architecture

```
Transaction History (Input)
         ↓
Position Calculator (Core Engine)
         ↓
    ┌────┴────┐
    ↓         ↓
Current      Historical
Holdings     Positions
    ↓         ↓
    └────┬────┘
         ↓
Portfolio Aggregator
         ↓
    ┌────┴────┐
    ↓         ↓
Analytics   Visualizations
Module      Module
```

### 2. Module Structure

```
src/modules/portfolio_dashboard/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── position_calculator.py      # FIFO/LIFO position tracking
│   ├── portfolio_engine.py         # Main portfolio aggregation
│   ├── performance_calculator.py   # ROI, gains/losses calculations
│   └── allocation_analyzer.py      # Asset allocation analysis
│
├── data/
│   ├── __init__.py
│   ├── market_data.py              # Live price fetching (yfinance)
│   ├── portfolio_state.py          # Current holdings state management
│   └── historical_positions.py     # Time-series position tracking
│
├── analytics/
│   ├── __init__.py
│   ├── performance_metrics.py      # Sharpe, volatility, beta
│   ├── risk_analytics.py           # Portfolio risk analysis
│   ├── tax_analytics.py            # Capital gains tax tracking
│   └── benchmark_comparison.py     # Compare vs S&P500, etc.
│
├── visualization/
│   ├── __init__.py
│   ├── holdings_view.py            # Current positions table
│   ├── allocation_charts.py        # Pie/tree charts for allocation
│   ├── performance_charts.py       # Performance over time
│   ├── risk_charts.py              # Risk metrics visualization
│   └── dashboard_layout.py         # Main portfolio dashboard
│
├── export/
│   ├── __init__.py
│   ├── portfolio_reports.py        # PDF/Excel report generation
│   └── tax_reports.py              # Tax documents generation
│
└── models/
    ├── __init__.py
    ├── position.py                 # Position data model
    ├── portfolio_snapshot.py       # Portfolio state at point in time
    └── performance_metrics.py      # Performance metrics models
```

---

## 📊 Core Data Models

### 1. Position Model

```python
class Position(BaseModel):
    """Represents current holding of a single security"""

    # Identification
    security_name: str
    security_symbol: str
    currency: str

    # Quantity tracking
    quantity: float                    # Current shares held
    average_cost_basis: float          # Average purchase price per share
    total_cost_basis: float            # Total investment amount

    # Current valuation
    current_price: float               # Latest market price
    current_value: float               # quantity * current_price
    last_price_update: datetime

    # Performance
    unrealized_gain_loss: float        # current_value - total_cost_basis
    unrealized_gain_loss_pct: float    # % return

    # History tracking
    first_purchase_date: datetime
    last_transaction_date: datetime
    total_buys: int
    total_sells: int
    realized_gains: float              # From closed positions

    # Tax tracking
    holding_period_days: int
    tax_lot_method: str                # "FIFO", "LIFO", "SpecificID"
    estimated_capital_gains_tax: float
```

### 2. Portfolio Snapshot Model

```python
class PortfolioSnapshot(BaseModel):
    """Portfolio state at a specific point in time"""

    # Identification
    snapshot_date: datetime
    account_name: str
    bank: str

    # Holdings
    positions: List[Position]
    total_positions: int

    # Valuation
    total_market_value: float          # Sum of all current values
    total_cost_basis: float            # Sum of all investments
    cash_balance: float                # Available cash
    total_portfolio_value: float       # market_value + cash

    # Performance
    total_unrealized_gain_loss: float
    total_unrealized_gain_loss_pct: float
    total_realized_gains: float        # Historical
    total_return: float                # realized + unrealized
    total_return_pct: float

    # Asset allocation
    allocation_by_security: Dict[str, float]    # % of portfolio
    allocation_by_currency: Dict[str, float]
    allocation_by_sector: Dict[str, float]      # If sector data available

    # Risk metrics
    portfolio_volatility: float
    sharpe_ratio: float
    beta: float                        # vs benchmark
    max_drawdown: float

    # Fees & costs
    total_fees_paid: float
    total_taxes_paid: float
```

### 3. Performance Metrics Model

```python
class PerformanceMetrics(BaseModel):
    """Performance analytics over time period"""

    # Time period
    start_date: datetime
    end_date: datetime
    period_days: int

    # Returns
    total_return: float                # Dollar amount
    total_return_pct: float            # Percentage
    annualized_return_pct: float

    # Time-weighted metrics
    time_weighted_return: float        # Accounts for cash flows
    money_weighted_return: float       # IRR

    # Risk metrics
    volatility: float                  # Std dev of returns
    sharpe_ratio: float                # Risk-adjusted return
    sortino_ratio: float               # Downside risk adjusted
    max_drawdown: float                # Largest peak-to-trough decline

    # Benchmark comparison
    benchmark_return: float            # S&P 500 or other
    alpha: float                       # Excess return vs benchmark
    beta: float                        # Volatility vs benchmark

    # Win/loss tracking
    winning_trades: int
    losing_trades: int
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: float               # Total wins / total losses
```

---

## 🔧 Core Components Implementation

### 1. Position Calculator

**Purpose**: Calculate current holdings from transaction history using FIFO/LIFO accounting

**Key Functions**:
```python
class PositionCalculator:
    def calculate_positions(self, transactions: List[Transaction]) -> List[Position]:
        """Main function to calculate all current positions"""

    def process_buy(self, transaction: Transaction, position: Position):
        """Update position with buy transaction"""

    def process_sell(self, transaction: Transaction, position: Position):
        """Update position with sell, calculate realized gains"""

    def calculate_average_cost(self, position: Position) -> float:
        """Calculate weighted average cost basis"""

    def calculate_realized_gains(self, sell_tx: Transaction, position: Position) -> float:
        """Calculate realized gains on sale using FIFO"""

    def reconcile_positions(self, calculated: List[Position], broker_statement: dict) -> bool:
        """Verify calculated positions match broker statement"""
```

**Algorithm**: FIFO (First-In-First-Out)
```
For each transaction in chronological order:
    If BUY:
        - Add shares to position
        - Update total cost basis
        - Recalculate average cost
        - Track buy in tax lot queue

    If SELL:
        - Remove shares from position using FIFO
        - Calculate realized gain = (sell_price - cost_basis) * quantity
        - Update remaining cost basis
        - Track capital gains for tax

    If DIVIDEND:
        - Add to realized income
        - No position impact

    If FEE/TAX:
        - Track for performance calculation
        - No position impact
```

### 2. Portfolio Engine

**Purpose**: Aggregate positions into complete portfolio view with live valuation

**Key Functions**:
```python
class PortfolioEngine:
    def __init__(self, market_data_provider: MarketDataProvider):
        self.market_data = market_data_provider
        self.position_calculator = PositionCalculator()

    def build_portfolio_snapshot(self, transactions: List[Transaction]) -> PortfolioSnapshot:
        """Create current portfolio snapshot with live prices"""

    def update_market_values(self, positions: List[Position]) -> List[Position]:
        """Fetch latest prices and update position values"""

    def calculate_allocation(self, positions: List[Position]) -> Dict:
        """Calculate asset allocation percentages"""

    def calculate_portfolio_metrics(self, snapshot: PortfolioSnapshot) -> PerformanceMetrics:
        """Calculate all portfolio-level metrics"""
```

### 3. Market Data Provider

**Purpose**: Fetch real-time prices from Yahoo Finance or other sources

**Key Functions**:
```python
class MarketDataProvider:
    def __init__(self, provider: str = "yfinance"):
        self.provider = provider
        self.cache = {}  # Price cache with TTL

    def get_current_price(self, symbol: str, currency: str = "USD") -> float:
        """Get latest price for symbol"""

    def get_historical_prices(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get historical price data"""

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Get currency exchange rate"""

    def batch_get_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Efficiently fetch multiple prices"""

    def map_ibi_symbol_to_ticker(self, ibi_symbol: str) -> str:
        """Map IBI broker symbol to Yahoo Finance ticker"""
```

**Symbol Mapping Strategy**:
```python
SYMBOL_MAPPING = {
    # IBI uses internal codes, need to map to standard tickers
    "594": "AAPL",      # Apple Inc
    "617": "MSFT",      # Microsoft
    "9993983": "SPY",   # S&P 500 ETF
    # ... more mappings
}

# For unmapped symbols:
# 1. Try direct lookup
# 2. Search by security name
# 3. Manual mapping configuration file
# 4. User input for unknown symbols
```

### 4. Performance Calculator

**Purpose**: Calculate portfolio performance metrics and risk analytics

**Key Functions**:
```python
class PerformanceCalculator:
    def calculate_total_return(self, portfolio: PortfolioSnapshot) -> float:
        """Total return = realized + unrealized gains"""

    def calculate_time_weighted_return(self, portfolio_history: List[PortfolioSnapshot]) -> float:
        """TWR accounts for timing of cash flows"""

    def calculate_annualized_return(self, total_return: float, days: int) -> float:
        """Annualize return for comparison"""

    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.04) -> float:
        """Risk-adjusted return metric"""

    def calculate_max_drawdown(self, portfolio_values: List[float]) -> float:
        """Largest peak-to-trough decline"""

    def calculate_volatility(self, returns: List[float]) -> float:
        """Standard deviation of returns"""
```

---

## 📈 Visualization Components

### 1. Holdings View (Main Table)

**Component**: `holdings_view.py`

**Display**:
```
┌─────────────┬──────────┬──────────┬────────────┬──────────────┬─────────────┬──────────────────┐
│ Security    │ Symbol   │ Quantity │ Avg Cost   │ Current      │ Market      │ Gain/Loss        │
│             │          │          │            │ Price        │ Value       │ ($ / %)          │
├─────────────┼──────────┼──────────┼────────────┼──────────────┼─────────────┼──────────────────┤
│ Apple Inc   │ AAPL     │ 100.00   │ $150.00    │ $189.50 ↑    │ $18,950.00  │ +$3,950 (+26.3%) │
│ Microsoft   │ MSFT     │ 50.00    │ $320.00    │ $378.20 ↑    │ $18,910.00  │ +$2,910 (+18.2%) │
│ Tesla Inc   │ TSLA     │ 25.00    │ $245.00    │ $201.30 ↓    │ $5,032.50   │ -$1,093 (-17.8%) │
└─────────────┴──────────┴──────────┴────────────┴──────────────┴─────────────┴──────────────────┘
                                                          Total: $42,892.50      Total: +$5,767 (+15.5%)
```

**Features**:
- Sortable by any column
- Color coding (green=profit, red=loss)
- Real-time price updates with arrows
- Click to drill down to transaction history for that security
- Export to Excel/CSV

### 2. Allocation Charts

**Component**: `allocation_charts.py`

**Chart Types**:

a) **Security Allocation (Pie Chart)**
```
        AAPL (44.2%)
       /              \
    MSFT (44.1%)    TSLA (11.7%)
```

b) **Currency Allocation (Donut Chart)**
```
    USD: 85.3%
    ILS: 12.5%
    EUR: 2.2%
```

c) **Asset Type Allocation (Treemap)**
```
┌──────────────────────────────────────────┐
│         US Stocks (75%)                  │
│  ┌────────────┬──────────────────────┐  │
│  │ AAPL (44%) │   MSFT (31%)         │  │
│  └────────────┴──────────────────────┘  │
├──────────────┬───────────────────────────┤
│ ETFs (15%)   │  Cash (10%)              │
└──────────────┴───────────────────────────┘
```

### 3. Performance Charts

**Component**: `performance_charts.py`

**Chart Types**:

a) **Portfolio Value Over Time (Line Chart)**
```
Portfolio Value Timeline
$50K ┤                                    ●
     │                              ●
$45K ┤                        ●
     │                  ●
$40K ┤            ●
     │      ●
$35K ┤●
     └────────────────────────────────────
      Jan  Feb  Mar  Apr  May  Jun  Jul

  — Portfolio Value
  - - Invested Capital
```

b) **Cumulative Returns (Area Chart)**
```
Cumulative Return %
30% ┤                                    ███
    │                              ███████
20% ┤                        ███████
    │                  ███████
10% ┤            ███████
    │      ███████
 0% ┤███████
    └────────────────────────────────────
     Jan  Feb  Mar  Apr  May  Jun  Jul
```

c) **Monthly Returns Heatmap**
```
        Jan   Feb   Mar   Apr   May   Jun   Jul   Aug   Sep   Oct   Nov   Dec
2024   +5.2% +2.1% -1.5% +8.3% +3.7% +1.2% +4.5%  -     -     -     -     -
2023   +3.1% +1.8% +2.4% -0.5% +6.2% +4.1% +2.8% +1.5% -2.1% +3.4% +5.6% +7.2%
```

### 4. Risk Analytics Charts

**Component**: `risk_charts.py`

**Displays**:
- Risk/Return Scatter Plot (vs benchmark)
- Drawdown Chart (peak-to-trough visualization)
- Volatility Cone (expected price ranges)
- Correlation Matrix (if multiple positions)

---

## 🔄 User Workflows

### Workflow 1: View Current Portfolio

```
1. User selects "Portfolio Dashboard" from sidebar
2. System loads all transaction files
3. Position Calculator processes transactions → current holdings
4. Market Data Provider fetches latest prices
5. Portfolio Engine builds snapshot with live valuations
6. Dashboard displays:
   - Summary metrics (total value, gains, allocation)
   - Holdings table with current positions
   - Allocation charts
   - Performance charts
```

### Workflow 2: Track Performance Over Time

```
1. User selects date range (e.g., "Last 6 months")
2. System generates daily portfolio snapshots for period
3. Performance Calculator computes metrics:
   - Daily returns
   - Cumulative return
   - Volatility
   - Sharpe ratio
   - Max drawdown
4. Charts display:
   - Portfolio value timeline
   - Returns chart
   - Risk metrics
5. Compare to benchmark (S&P 500)
```

### Workflow 3: Analyze Asset Allocation

```
1. User clicks "Allocation" tab
2. System calculates:
   - % by security
   - % by currency
   - % by sector (if available)
   - % by geography (US vs International)
3. Display:
   - Interactive pie charts
   - Treemap visualization
   - Allocation table with drill-down
4. User can set target allocations
5. System shows rebalancing suggestions
```

### Workflow 4: Generate Tax Report

```
1. User selects tax year (e.g., 2024)
2. Position Calculator identifies:
   - All realized gains/losses
   - Holding periods (short-term vs long-term)
   - Wash sales (if applicable)
3. Tax Analytics calculates:
   - Total capital gains
   - Tax liability estimate
   - Tax-loss harvesting opportunities
4. Generate PDF report for tax filing
```

---

## 🎨 Dashboard Layout Design

### Main Portfolio Dashboard (Streamlit Layout)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🏦 ASSETS PORTFOLIO DASHBOARD                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  📊 PORTFOLIO SUMMARY                                                        │
│  ┌────────────┬────────────┬────────────┬────────────┬────────────────────┐│
│  │ Total      │ Total      │ Total      │ Total      │ Today's            ││
│  │ Value      │ Cost       │ Gain/Loss  │ Return     │ Change             ││
│  │ $42,893    │ $37,126    │ +$5,767    │ +15.5%     │ +$234 (+0.5%) ↑    ││
│  └────────────┴────────────┴────────────┴────────────┴────────────────────┘│
│                                                                              │
│  TABS: [📋 Holdings] [📊 Performance] [🥧 Allocation] [📈 Analytics] [💸 Tax]│
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  📋 CURRENT HOLDINGS                                                  │  │
│  │                                                                        │  │
│  │  [Search: ____] [Filter by: All ▾] [Sort by: Value ▾] [🔄 Refresh]   │  │
│  │                                                                        │  │
│  │  ┌──────────┬────────┬─────┬──────┬────────┬────────┬──────────────┐ │  │
│  │  │ Security │ Symbol │ Qty │ Cost │ Price  │ Value  │ Gain/Loss    │ │  │
│  │  ├──────────┼────────┼─────┼──────┼────────┼────────┼──────────────┤ │  │
│  │  │ Apple    │ AAPL   │ 100 │ $150 │ $189.5 │$18,950 │+$3,950(26%)  │ │  │
│  │  │ ...      │        │     │      │        │        │              │ │  │
│  │  └──────────┴────────┴─────┴──────┴────────┴────────┴──────────────┘ │  │
│  │                                                                        │  │
│  │  [�� Export to Excel] [📄 Generate PDF Report] [⚙️ Configure]        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌────────────────────────────────┬─────────────────────────────────────┐  │
│  │  📊 ALLOCATION                 │  📈 PERFORMANCE                      │  │
│  │                                │                                      │  │
│  │  [Pie chart showing            │  [Line chart showing portfolio       │  │
│  │   allocation by security]      │   value over time]                  │  │
│  │                                │                                      │  │
│  └────────────────────────────────┴─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technical Implementation Details

### 1. Real-Time Price Updates

**Strategy**: WebSocket or polling with smart caching

```python
class PriceUpdateManager:
    def __init__(self, update_interval: int = 60):
        self.update_interval = update_interval  # seconds
        self.cache = {}
        self.last_update = {}

    def should_update(self, symbol: str) -> bool:
        """Check if price needs refresh"""
        if symbol not in self.last_update:
            return True
        elapsed = (datetime.now() - self.last_update[symbol]).seconds
        return elapsed >= self.update_interval

    def update_prices_batch(self, symbols: List[str]):
        """Update multiple symbols efficiently"""
        import yfinance as yf
        tickers = yf.Tickers(' '.join(symbols))
        for symbol in symbols:
            try:
                self.cache[symbol] = tickers.tickers[symbol].info['currentPrice']
                self.last_update[symbol] = datetime.now()
            except:
                # Fallback to last known price
                pass
```

**Streamlit Integration**:
```python
# In Streamlit app
if 'price_update_manager' not in st.session_state:
    st.session_state.price_update_manager = PriceUpdateManager(update_interval=60)

# Auto-refresh every 60 seconds
st_autorefresh = st_autorefresh(interval=60000, key="portfolio_refresh")
```

### 2. Position Calculation Algorithm (FIFO)

```python
def calculate_position_fifo(transactions: List[Transaction]) -> Position:
    """
    Calculate current position using FIFO (First-In-First-Out) method.

    This is the default tax method in most countries including Israel.
    """
    tax_lots = []  # Queue of (quantity, cost_basis, purchase_date)
    total_quantity = 0.0
    total_cost = 0.0
    realized_gains = 0.0

    for tx in sorted(transactions, key=lambda x: x.date):
        if tx.is_buy:
            # Add new tax lot
            lot = TaxLot(
                quantity=tx.quantity,
                cost_per_share=tx.execution_price,
                purchase_date=tx.date,
                fees=tx.transaction_fee + tx.additional_fees
            )
            tax_lots.append(lot)
            total_quantity += tx.quantity
            total_cost += tx.quantity * tx.execution_price + lot.fees

        elif tx.is_sell:
            # Sell from oldest lots first (FIFO)
            remaining_to_sell = tx.quantity

            while remaining_to_sell > 0 and tax_lots:
                lot = tax_lots[0]

                if lot.quantity <= remaining_to_sell:
                    # Sell entire lot
                    proceeds = lot.quantity * tx.execution_price
                    cost = lot.quantity * lot.cost_per_share + lot.fees
                    realized_gains += proceeds - cost

                    remaining_to_sell -= lot.quantity
                    total_quantity -= lot.quantity
                    total_cost -= cost
                    tax_lots.pop(0)
                else:
                    # Partial lot sale
                    proceeds = remaining_to_sell * tx.execution_price
                    cost = remaining_to_sell * lot.cost_per_share
                    realized_gains += proceeds - cost

                    lot.quantity -= remaining_to_sell
                    total_quantity -= remaining_to_sell
                    total_cost -= cost
                    remaining_to_sell = 0

    # Calculate average cost basis from remaining lots
    avg_cost = total_cost / total_quantity if total_quantity > 0 else 0.0

    return Position(
        quantity=total_quantity,
        total_cost_basis=total_cost,
        average_cost_basis=avg_cost,
        realized_gains=realized_gains,
        remaining_tax_lots=tax_lots
    )
```

### 3. Currency Conversion

```python
class CurrencyConverter:
    def __init__(self):
        self.rates_cache = {}
        self.base_currency = "ILS"  # Israeli Shekel

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        """Get exchange rate, with caching"""
        if from_currency == to_currency:
            return 1.0

        cache_key = f"{from_currency}_{to_currency}"

        if cache_key in self.rates_cache:
            rate, timestamp = self.rates_cache[cache_key]
            if (datetime.now() - timestamp).seconds < 3600:  # 1 hour cache
                return rate

        # Fetch from yfinance
        import yfinance as yf
        ticker = f"{from_currency}{to_currency}=X"
        rate = yf.Ticker(ticker).info.get('regularMarketPrice', 1.0)

        self.rates_cache[cache_key] = (rate, datetime.now())
        return rate

    def convert_to_base(self, amount: float, from_currency: str) -> float:
        """Convert any currency to base currency (ILS)"""
        rate = self.get_rate(from_currency, self.base_currency)
        return amount * rate
```

### 4. Performance Metrics Calculation

```python
class PortfolioMetricsCalculator:
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.04) -> float:
        """
        Sharpe Ratio = (Portfolio Return - Risk Free Rate) / Portfolio Volatility

        Higher is better. > 1.0 is good, > 2.0 is excellent.
        """
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        return np.sqrt(252) * excess_returns.mean() / returns.std()

    def calculate_max_drawdown(self, portfolio_values: pd.Series) -> float:
        """
        Max Drawdown = Largest peak-to-trough decline

        Measures worst possible loss from any peak.
        """
        cumulative = (1 + portfolio_values).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()

    def calculate_time_weighted_return(self, snapshots: List[PortfolioSnapshot]) -> float:
        """
        TWR = ((1 + R1) × (1 + R2) × ... × (1 + Rn)) - 1

        Accounts for timing of cash flows, good for performance comparison.
        """
        if len(snapshots) < 2:
            return 0.0

        returns = []
        for i in range(1, len(snapshots)):
            prev = snapshots[i-1]
            curr = snapshots[i]

            # Remove cash flows to get true performance
            return_pct = (curr.total_value - curr.cash_flows) / prev.total_value
            returns.append(return_pct)

        twr = np.prod([1 + r for r in returns]) - 1
        return twr
```

---

## 📦 Dependencies & Libraries

### Core Dependencies
```python
# requirements.txt additions for Portfolio Dashboard

# Market data
yfinance>=0.2.28              # Yahoo Finance API for prices
pandas-datareader>=0.10.0     # Alternative data source

# Financial calculations
numpy-financial>=1.0.0        # NPV, IRR calculations
empyrical>=0.5.5              # Portfolio performance metrics

# Visualization
plotly>=5.17.0                # Interactive charts
streamlit-autorefresh>=1.0.0  # Auto-refresh functionality

# Currency conversion
forex-python>=1.8             # Forex rates (alternative)

# PDF generation (for reports)
reportlab>=4.0.0              # PDF creation
```

### Optional Advanced Features
```python
# Advanced analytics (optional)
pyfolio>=0.9.2                # Quantopian's portfolio analytics
bt>=0.2.9                     # Backtesting library
quantstats>=0.0.59            # Portfolio analytics & reports

# Machine learning (future enhancement)
scikit-learn>=1.3.0           # For clustering, predictions
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/test_position_calculator.py

def test_fifo_position_calculation():
    """Test FIFO position calculation with buy-sell sequence"""
    transactions = [
        create_buy(date="2024-01-01", symbol="AAPL", qty=100, price=150),
        create_buy(date="2024-02-01", symbol="AAPL", qty=50, price=160),
        create_sell(date="2024-03-01", symbol="AAPL", qty=80, price=170),
    ]

    position = PositionCalculator().calculate_position(transactions)

    assert position.quantity == 70  # 150 bought, 80 sold
    assert position.average_cost_basis == pytest.approx(155.71, 0.01)
    assert position.realized_gains > 0  # Sold at profit

def test_currency_conversion():
    """Test multi-currency position handling"""
    transactions = [
        create_buy(date="2024-01-01", symbol="AAPL", qty=100, price=150, currency="USD"),
    ]

    converter = CurrencyConverter()
    position = PositionCalculator(converter).calculate_position(transactions)

    assert position.currency == "USD"
    assert position.cost_basis_in_ils > position.cost_basis_in_usd

def test_dividend_tracking():
    """Test dividend income tracking"""
    transactions = [
        create_buy(date="2024-01-01", symbol="AAPL", qty=100, price=150),
        create_dividend(date="2024-04-01", symbol="AAPL", amount=0.25, qty=100),
    ]

    position = PositionCalculator().calculate_position(transactions)

    assert position.quantity == 100  # Dividends don't change quantity
    assert position.total_dividends == 25.0  # 100 shares * $0.25
```

### Integration Tests

```python
# tests/test_portfolio_integration.py

def test_full_portfolio_workflow():
    """Test complete workflow from transactions to dashboard"""
    # 1. Load transactions
    transactions = load_test_transactions("test_data/ibi_2024.xlsx")

    # 2. Calculate positions
    calculator = PositionCalculator()
    positions = calculator.calculate_all_positions(transactions)

    # 3. Get market prices
    market_data = MarketDataProvider()
    positions = market_data.update_prices(positions)

    # 4. Build portfolio snapshot
    engine = PortfolioEngine()
    snapshot = engine.build_snapshot(positions)

    # 5. Verify metrics
    assert snapshot.total_positions > 0
    assert snapshot.total_market_value > 0
    assert snapshot.allocation_by_security is not None
```

### Data Validation Tests

```python
def test_position_reconciliation():
    """Test calculated positions match broker statement"""
    # Load actual broker statement
    broker_positions = load_broker_statement("broker_statement_2024.pdf")

    # Calculate from transactions
    transactions = load_transactions("ibi_trans_2024.xlsx")
    calculated_positions = PositionCalculator().calculate_all_positions(transactions)

    # Compare
    for symbol, broker_qty in broker_positions.items():
        calc_pos = next(p for p in calculated_positions if p.symbol == symbol)
        assert calc_pos.quantity == broker_qty, f"Mismatch for {symbol}"
```

---

## 🚀 Implementation Roadmap

### Phase 1: Core Position Tracking (Week 1-2)
- [ ] Implement Position data model
- [ ] Build PositionCalculator with FIFO logic
- [ ] Create unit tests for position calculation
- [ ] Handle buy/sell transactions
- [ ] Test with real IBI transaction data

### Phase 2: Market Data Integration (Week 2-3)
- [ ] Implement MarketDataProvider with yfinance
- [ ] Create symbol mapping system (IBI → Yahoo Finance)
- [ ] Add currency conversion
- [ ] Implement price caching and auto-refresh
- [ ] Test with multiple securities

### Phase 3: Portfolio Aggregation (Week 3-4)
- [ ] Build PortfolioEngine
- [ ] Implement PortfolioSnapshot creation
- [ ] Calculate allocation metrics
- [ ] Add performance metrics calculation
- [ ] Integration testing

### Phase 4: Visualization Layer (Week 4-5)
- [ ] Create holdings table view
- [ ] Build allocation charts (pie, donut, treemap)
- [ ] Implement performance charts (line, area)
- [ ] Add interactive filtering
- [ ] Responsive layout

### Phase 5: Advanced Analytics (Week 5-6)
- [ ] Implement risk metrics (Sharpe, volatility, drawdown)
- [ ] Add benchmark comparison
- [ ] Create tax analytics
- [ ] Build report generation
- [ ] Add export functionality

### Phase 6: Polish & Optimization (Week 6-7)
- [ ] Performance optimization
- [ ] Error handling and edge cases
- [ ] User documentation
- [ ] Video tutorials
- [ ] Final testing

---

## 🔐 Security & Privacy Considerations

1. **Sensitive Data Handling**
   - Never log actual portfolio values or positions
   - Sanitize data in error messages
   - Use environment variables for API keys

2. **API Key Management**
   ```python
   # .env file
   YAHOO_FINANCE_API_KEY=xxx  # If using premium API
   ALPHA_VANTAGE_KEY=xxx      # Backup data source
   ```

3. **Data Storage**
   - All calculations in memory only
   - No persistent storage of portfolio snapshots (unless user exports)
   - Clear session state on exit

---

## 📚 Documentation Plan

### User Documentation
1. **Quick Start Guide** - 5-minute setup and first portfolio view
2. **Feature Guide** - Detailed explanation of all features
3. **FAQ** - Common questions and troubleshooting
4. **Video Tutorials** - Screen recordings of key workflows

### Developer Documentation
1. **Architecture Overview** - High-level system design
2. **API Reference** - All classes and methods
3. **Extension Guide** - How to add new features
4. **Testing Guide** - How to write and run tests

---

## 🎯 Success Criteria

### Functional Requirements
✅ Accurately calculate positions from transactions (100% accuracy vs broker)
✅ Display real-time portfolio value with < 5 second refresh
✅ Support multiple securities and currencies
✅ Generate comprehensive performance metrics
✅ Provide interactive visualizations
✅ Export reports in PDF/Excel format

### Performance Requirements
✅ Load portfolio in < 3 seconds
✅ Update prices in < 2 seconds
✅ Handle 1000+ transactions without lag
✅ Responsive UI (60 FPS interactions)

### Quality Requirements
✅ 90%+ test coverage
✅ Handle edge cases (dividends, splits, fees)
✅ Clear error messages
✅ Comprehensive documentation

---

## 🔄 Future Enhancements

### Phase 2 Features (Post-MVP)
1. **Stock Splits Handling** - Automatic adjustment for splits
2. **Dividend Reinvestment** - DRIP tracking
3. **Multi-Account Support** - Aggregate multiple portfolios
4. **Custom Benchmarks** - Compare vs custom indices
5. **Alerts & Notifications** - Price alerts, rebalancing reminders
6. **Tax-Loss Harvesting** - Identify tax-saving opportunities
7. **What-If Analysis** - Simulate portfolio changes
8. **AI Insights** - ML-powered portfolio recommendations

### Advanced Analytics
- Monte Carlo simulations for risk assessment
- Factor analysis (value, growth, momentum exposure)
- Portfolio optimization suggestions
- Correlation analysis across holdings

---

## 📝 Configuration Example

```json
// config/portfolio_dashboard.json
{
  "market_data": {
    "provider": "yfinance",
    "update_interval_seconds": 60,
    "cache_duration_seconds": 300,
    "fallback_provider": "alpha_vantage"
  },

  "calculations": {
    "tax_lot_method": "FIFO",
    "base_currency": "ILS",
    "risk_free_rate": 0.04,
    "benchmark": "^GSPC"
  },

  "display": {
    "theme": "light",
    "auto_refresh": true,
    "default_date_range": "1Y",
    "precision_decimals": 2
  },

  "symbol_mapping": {
    "594": "AAPL",
    "617": "MSFT",
    "custom_mappings": "config/symbol_map.json"
  },

  "export": {
    "default_format": "xlsx",
    "include_charts": true,
    "company_logo": "assets/logo.png"
  }
}
```

---

## 🏁 Conclusion

This comprehensive plan provides a complete roadmap for implementing the **Assets Portfolio Dashboard** module. The modular architecture ensures easy maintenance and extensibility, while the phased implementation approach allows for iterative development and testing.

**Next Steps**:
1. Review and approve this plan
2. Set up development environment
3. Begin Phase 1: Core Position Tracking
4. Iterate based on user feedback

**Estimated Timeline**: 6-7 weeks for full implementation
**Team Size**: 1-2 developers
**Effort**: ~200-250 development hours

---

*Document Version: 1.0*
*Last Updated: 2025-01-15*
*Author: Transaction Analysis System Team*

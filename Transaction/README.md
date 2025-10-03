# Transaction Analysis System

A comprehensive securities trading analysis dashboard for IBI broker data with complete support for all 13 transaction fields.

🔗 **GitHub Repository:** https://github.com/RBenhGit/transaction-analysis-system

## ✨ Features

### Complete IBI Broker Support (13 Fields)
- ✅ **Stock Names** (שם נייר) - Full security identification
- ✅ **Transaction Types** (סוג פעולה) - Buy/Sell/Dividend/Tax/Fee
- ✅ **Security Symbols** (מס' נייר / סימבול) - Stock symbols and IDs
- ✅ **Trade Details** - Quantity, execution price, currency
- ✅ **Fees & Costs** - Transaction fees and additional charges
- ✅ **Multi-Currency** - Foreign currency and NIS amounts
- ✅ **Balance Tracking** - Real-time account balance
- ✅ **Tax Estimates** - Capital gains tax calculations

### Interactive Dashboard
- 📊 **Transaction History** - Filterable by date, type, and security
- 📈 **Analytics** - Transaction distributions and trends
- 💹 **Securities Analysis** - Most traded stocks and amounts
- 📉 **Charts** - Balance history, fees, and performance metrics
- 💾 **Export** - JSON export with complete metadata

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
```bash
cd Transaction
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`

## 📁 Project Structure

```
Transaction/
├── app.py                      # Main Streamlit application
├── CLAUDE.md                   # Project documentation
├── config.json                 # Bank configuration
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
│
├── Data_Files/                 # Excel transaction files
│   ├── IBI trans 2022.xlsx
│   ├── IBI trans 2023.xlsx
│   └── IBI trans 2024.xlsx
│
├── adapters/                   # Bank-specific adapters
│   ├── __init__.py
│   ├── base_adapter.py        # Abstract base class
│   └── ibi_adapter.py         # IBI broker adapter (13 fields)
│
├── src/                        # Core modules
│   ├── __init__.py
│   ├── json_adapter.py        # JSON standardization
│   ├── models/
│   │   ├── __init__.py
│   │   └── transaction.py     # Transaction model (13 fields)
│   └── input/
│       ├── __init__.py
│       ├── excel_reader.py    # Excel file reader
│       └── file_discovery.py  # File discovery
│
├── output/                     # Generated exports
│   └── demo_ibi_*.json        # JSON exports
│
└── .claude/                    # Claude Code configuration
    ├── settings.json           # Project settings
    └── settings.local.json     # Local settings
```

## 📊 Usage

### 1. Launch Application
```bash
streamlit run app.py
```

### 2. Select File
- Use the sidebar to select an IBI Excel file
- Files are automatically discovered from `Data_Files/`

### 3. Explore Data
- **Transactions Tab**: View and filter transaction history
- **Analytics Tab**: See transaction type distributions and trends
- **Securities Tab**: Analyze most traded stocks
- **Charts Tab**: View balance history and fee analysis

### 4. Filter & Analyze
- Filter by date range
- Filter by transaction type
- Filter by security name
- View summary statistics

### 5. Export (Optional)
- Click "Export to JSON" to save data
- Exports include complete metadata and statistics

## 🔧 Configuration

### IBI Field Mapping

All 13 IBI fields are configured in `config.json`:

```json
{
  "banks": {
    "IBI": {
      "account_type": "securities_trading",
      "column_mapping": {
        "date": "תאריך",
        "transaction_type": "סוג פעולה",
        "security_name": "שם נייר",
        "security_symbol": "מס' נייר / סימבול",
        "quantity": "כמות",
        "execution_price": "שער ביצוע",
        "currency": "מטבע",
        "transaction_fee": "עמלת פעולה",
        "additional_fees": "עמלות נלוות",
        "amount_foreign_currency": "תמורה במט\"ח",
        "amount_local_currency": "תמורה בשקלים",
        "balance": "יתרה שקלית",
        "capital_gains_tax_estimate": "אומדן מס רווחי הון"
      }
    }
  }
}
```

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Complete project documentation
- **[IBI_FIELD_ANALYSIS.md](IBI_FIELD_ANALYSIS.md)** - IBI field structure analysis
- **[MEMORY_CONTEXT_SETUP_PLAN.md](MEMORY_CONTEXT_SETUP_PLAN.md)** - Claude Code setup guide

## 🧪 Demo Script

Test the data loading without the full UI:

```bash
python demo_ibi_reader.py
```

This will:
- Load the most recent IBI file
- Display all 13 fields
- Show summary statistics
- Export to JSON

## 🎯 Key Features in Detail

### Transaction Model
Complete Pydantic model with all 13 fields, type validation, and helper methods:
- `is_buy` - Check if transaction is a buy order
- `is_sell` - Check if transaction is a sell order
- `is_dividend` - Check if dividend transaction
- `is_fee` - Check if fee transaction
- `is_tax` - Check if tax-related
- `total_cost` - Calculate total including fees

### IBI Adapter
Handles all IBI-specific transformations:
- Column mapping (Hebrew to English)
- Date parsing (DD/MM/YYYY format)
- Type conversions
- Data validation
- Transaction categorization

### JSON Adapter
Standardizes data format:
- DataFrame to Transaction objects
- Metadata generation
- Statistics calculation
- JSON export with proper encoding

## 🔍 Real Data Example

From your IBI 2024 file (536 transactions):

**Transaction Types (Top 5):**
- הפקדה דיבידנד מטח: 77
- משיכה: 70
- קניה חול מטח: 69
- משיכת מס חול מטח: 68
- הפקדה: 67

**Most Traded:**
- 119 unique securities
- Total fees: ₪946.04
- Buy/Sell ratio tracked
- Multi-currency support

## 🛠️ Technology Stack

- **Python 3.8+**
- **Streamlit** - Interactive dashboard
- **Pandas** - Data processing
- **Plotly** - Interactive charts
- **Pydantic** - Data validation
- **OpenPyXL** - Excel file reading

## 📝 License

This project is for internal use and analysis of financial transaction data.

## 🤝 Contributing

1. Follow the folder structure in `CLAUDE.md`
2. All new bank adapters inherit from `BaseAdapter`
3. Use type hints and docstrings
4. Test with real data
5. Update documentation

---

**Built with ❤️ using Claude Code**

🤖 Generated with [Claude Code](https://claude.com/claude-code)

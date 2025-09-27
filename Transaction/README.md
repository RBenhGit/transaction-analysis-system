# Transaction Analysis System

A comprehensive Python-based transaction analysis system designed to import Excel files from various banks, standardize the data through a JSON adapter pattern, and provide powerful data visualization and analysis capabilities.

## 🌟 Features

### 📊 Data Import & Processing
- **Excel File Import**: Automatic discovery and import of bank transaction files
- **Multi-Bank Support**: Extensible adapter pattern for different bank formats
- **IBI Bank Support**: Built-in support for IBI (Israel Beinleumi Bank) transaction files
- **JSON Standardization**: Converts all transaction data to a unified JSON format
- **Data Validation**: Comprehensive validation and error handling

### 🖥️ Visual Display Interface
- **Interactive GUI**: Modern tkinter-based graphical interface
- **Real-time Filtering**: Filter transactions by date range, amount, and type
- **Live Search**: Search transaction descriptions and references
- **Dynamic Sorting**: Sort by any column (date, amount, balance, etc.)
- **Summary Statistics**: Live calculation of totals, averages, and transaction counts
- **Export Capabilities**: Export to CSV, Excel, and JSON formats

### 🏗️ Modular Architecture
- **Adapter Pattern**: Easy addition of new bank formats
- **Module System**: Self-contained feature modules
- **Configuration Management**: Flexible configuration system
- **Comprehensive Testing**: Unit tests for all major components

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RBenhGit/transaction-analysis-system.git
   cd transaction-analysis-system
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Visual Display with Real Data

For immediate visual exploration of your transaction data:

```bash
# If you have processed JSON files
python run_real_data_gui.py

# Or import directly from Excel files
python visual_with_excel.py

# Or try the demo with sample data
python demo_visual_display.py
```

## 📁 Project Structure

```
Transaction/
├── 📄 main.py                      # Main application entry point
├── 📄 requirements.txt             # Python dependencies
├── 📄 config.json                  # Configuration file
├── 📄 .gitignore                   # Git ignore file
├── 📁 src/                         # Core source code
│   ├── 📄 excel_importer.py        # Excel file import logic
│   ├── 📄 json_adapter.py          # Data standardization layer
│   ├── 📄 data_models.py           # Data models and schemas
│   ├── 📄 display_manager.py       # Console data presentation
│   ├── 📄 config_manager.py        # Configuration management
│   └── 📄 utils.py                 # Utility functions
├── 📁 adapters/                    # Bank-specific adapters
│   ├── 📄 base_adapter.py          # Abstract base adapter
│   └── 📄 ibi_adapter.py           # IBI bank adapter
├── 📁 modules/                     # Feature modules
│   ├── 📁 visual_display/          # GUI visualization module
│   ├── 📁 analytics/               # Data analysis module
│   ├── 📁 visualization/           # Charts and graphs module
│   ├── 📁 reporting/               # Report generation module
│   └── 📁 database/                # Database integration module
├── 📁 tests/                       # Unit tests
├── 📁 docs/                        # Documentation
└── 📁 output/                      # Generated files
    ├── 📁 processed/               # Processed JSON data
    ├── 📁 reports/                 # Generated reports
    └── 📁 exports/                 # Exported files
```

## 💻 Usage Examples

### Basic Import and Analysis

```python
from src.excel_importer import ExcelImporter
from src.json_adapter import JSONAdapter
from adapters.ibi_adapter import IBIAdapter

# Initialize components
importer = ExcelImporter()
adapter = JSONAdapter()
ibi_adapter = IBIAdapter()

# Import and process data
raw_data = importer.load_file("path/to/transactions.xlsx")
result = adapter.process(raw_data, ibi_adapter)

if result.success:
    transactions = result.transaction_set.transactions
    print(f"Loaded {len(transactions)} transactions")
```

### Visual Display

```python
from modules.visual_display import VisualDisplayManager

# Launch visual interface
visual_display = VisualDisplayManager()
visual_display.run(transaction_set)  # Opens GUI window
```

### Data Analysis

```python
from modules.analytics import TransactionAnalyzer

# Analyze transaction patterns
analyzer = TransactionAnalyzer()
analysis = analyzer.analyze_transactions(transactions)
print(f"Monthly spending trend: {analysis['trend']}")
```

## 🏦 Supported Banks

### IBI (Israel Beinleumi Bank)
- ✅ Full support for IBI Excel export format
- ✅ Hebrew text handling
- ✅ Date format: DD/MM/YYYY
- ✅ Automatic header and footer detection
- ✅ Reference number extraction

### Adding New Banks
The system uses an adapter pattern for easy extension:

1. Create new adapter in `adapters/` directory
2. Inherit from `BaseAdapter`
3. Implement required parsing methods
4. Add configuration entry
5. Update tests

## 🎯 Key Features Detailed

### Visual Display Interface

The GUI provides powerful data exploration capabilities:

- **Interactive Table**: Sort and filter transaction data
- **Smart Filtering**:
  - Date range selection
  - Amount range filtering
  - Transaction type (credits/debits)
  - Real-time text search
- **Live Statistics**: Automatic calculation of:
  - Total transaction count
  - Sum of credits and debits
  - Average transaction amounts
  - Date range coverage
- **Export Options**: Save filtered data in multiple formats
- **Transaction Details**: Double-click for detailed view

### JSON Data Schema

All transaction data is standardized to this format:

```json
{
  "transactions": [
    {
      "date": "YYYY-MM-DD",
      "description": "Transaction description",
      "amount": 123.45,
      "balance": 1000.00,
      "category": "Optional category",
      "reference": "Bank reference number",
      "bank": "Bank identifier",
      "account": "Account number"
    }
  ],
  "metadata": {
    "source_file": "original_file.xlsx",
    "import_date": "2024-01-01T12:00:00",
    "total_transactions": 100,
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    },
    "bank": "IBI"
  }
}
```

## 🛠️ Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test module
python -m pytest tests/test_excel_importer.py

# Run with coverage
python -m pytest tests/ --cov=src
```

### Adding New Modules

Follow the established module structure:

```
modules/your_module/
├── __init__.py              # Module initialization
├── README.md                # Module documentation
├── core_module.py           # Main functionality
├── utils.py                 # Module utilities
├── tests/                   # Module tests
│   ├── __init__.py
│   └── test_core_module.py
└── examples/                # Usage examples
    └── example_usage.py
```

### Code Standards

- Follow PEP 8 style guidelines
- Include comprehensive docstrings
- Add type hints for all functions
- Write unit tests for new features
- Update documentation for API changes

## 📋 Requirements

### System Requirements
- Python 3.8+
- Windows/macOS/Linux
- 2GB RAM minimum
- tkinter (usually included with Python)

### Python Dependencies
```
pandas>=2.0.0
openpyxl>=3.1.0
pydantic>=2.0.0
typing-extensions>=4.5.0
python-dateutil>=2.8.0
tabulate>=0.9.0
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the project structure and coding standards
4. Write tests for new functionality
5. Update documentation
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔒 Privacy & Security

- **No Personal Data**: Repository contains only source code
- **Secure by Design**: Personal financial data is excluded via .gitignore
- **Local Processing**: All data processing happens locally
- **No External APIs**: No data sent to external services

## 📞 Support

- **Documentation**: See [CLAUDE.md](CLAUDE.md) for detailed project documentation
- **Visual Display Guide**: See [HOW_TO_RUN_VISUAL_DISPLAY.md](HOW_TO_RUN_VISUAL_DISPLAY.md)
- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/RBenhGit/transaction-analysis-system/issues)

## 🎯 Roadmap

- [ ] Additional bank adapters
- [ ] Advanced analytics and reporting
- [ ] Data visualization with matplotlib/plotly
- [ ] Database integration
- [ ] Web interface
- [ ] API endpoints
- [ ] Machine learning categorization
- [ ] Export to accounting software formats

---

**Made with ❤️ for better financial data analysis**
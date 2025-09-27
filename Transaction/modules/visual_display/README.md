# Visual Display Module

## Overview

The Visual Display Module provides a graphical user interface (GUI) for viewing and interacting with transaction data in the Transaction Analysis System. Built using Python's tkinter library, it offers an intuitive visual interface for transaction exploration, filtering, and analysis.

## Features

### Main Interface
- **Interactive Transaction Table**: Scrollable table displaying all transaction data
- **Real-time Search**: Live text search across transaction descriptions
- **Column Sorting**: Click column headers to sort by date, amount, description, etc.
- **Transaction Details**: Double-click transactions for detailed popup view

### Filtering Capabilities
- **Date Range Filter**: Filter transactions by start and end dates
- **Amount Range Filter**: Filter by minimum and maximum amounts
- **Transaction Type Filter**: Show only credits, debits, or all transactions
- **Text Search**: Real-time search through transaction descriptions
- **Clear Filters**: Reset all filters with one click

### Summary Panel
- **Live Statistics**: Real-time calculation of totals and averages
- **Transaction Counts**: Count of total, credit, and debit transactions
- **Financial Totals**: Total amounts for credits, debits, and net balance
- **Date Range Display**: Shows the span of filtered transactions

### Export Integration
- **CSV Export**: Export filtered data to comma-separated values format
- **Excel Export**: Export to Excel workbook with summary sheet
- **JSON Export**: Export to structured JSON format
- **File Dialog Integration**: User-friendly file selection for exports

## Installation

The Visual Display Module uses only built-in Python libraries and existing project dependencies:

- `tkinter` (built-in with Python)
- `pandas` (already in requirements.txt)
- `tabulate` (already in requirements.txt)

No additional installations required.

## Usage

### Basic Usage

```python
from modules.visual_display import VisualDisplayManager
from src.json_adapter import JSONAdapter

# Load your transaction data
adapter = JSONAdapter()
result = adapter.import_from_json('transactions.json')

if result.success:
    # Create and show visual display
    display_manager = VisualDisplayManager()
    display_manager.show_transactions(result.transaction_set)
```

### Advanced Usage

```python
from modules.visual_display import VisualDisplayManager
from src.config_manager import ConfigManager

# Initialize with custom configuration
config_manager = ConfigManager()
display_manager = VisualDisplayManager(config_manager)

# Show transactions
display_manager.show_transactions(transaction_set)

# The GUI will remain open for user interaction
# Window can be hidden and reshown as needed
```

### Integration with Main Application

```python
# In main.py or application flow
if result.success:
    print("\\nTransaction data loaded successfully!")

    # Show console summary
    display_manager.show_transaction_summary(result.transaction_set)

    # Launch visual interface
    visual_display = VisualDisplayManager()
    visual_display.show_transactions(result.transaction_set)

    # Continue with other operations...
```

## Component Architecture

### Core Components

#### VisualDisplayManager
The main class managing the GUI interface and user interactions.

**Key Methods:**
- `show_transactions(transaction_set)`: Display transaction data in GUI
- `_apply_filters()`: Apply current filter settings to data
- `_populate_transaction_tree()`: Refresh the transaction table
- `_update_summary_panel()`: Update statistics display

#### Filter System
Comprehensive filtering system with multiple criteria:

```python
# Filter by date range
start_date = "2024-01-01"
end_date = "2024-12-31"

# Filter by amount range
min_amount = "100.00"
max_amount = "5000.00"

# Filter by transaction type
transaction_type = "Credits"  # or "Debits" or "All"

# Text search
search_text = "salary"
```

#### Summary Statistics
Real-time calculation and display of:
- Total transaction count
- Sum of all amounts
- Credit total and count
- Debit total and count
- Average transaction amount
- Date range of displayed data

### Utility Functions

The module includes comprehensive utility functions in `utils.py`:

```python
from modules.visual_display.utils import (
    format_currency,
    format_date_display,
    get_amount_color,
    calculate_summary_stats
)

# Format amounts for display
formatted = format_currency(Decimal('1234.56'))  # "₪1,234.56"

# Format dates consistently
date_str = format_date_display(date(2024, 1, 15))  # "2024-01-15"

# Get color coding for amounts
color = get_amount_color(Decimal('-100.00'))  # "red"

# Calculate summary statistics
stats = calculate_summary_stats(transactions)
```

## GUI Layout

### Main Window Structure
```
┌─────────────────────────────────────────────────────────┐
│ Menu Bar: File | View | Tools                           │
├─────────────────────────────────────────────────────────┤
│ Toolbar: [Refresh] [Export CSV] [Export Excel] Search   │
├──────────────────┬──────────────────────────────────────┤
│ Left Panel       │ Right Panel                          │
│ ┌──────────────┐ │ ┌──────────────────────────────────┐ │
│ │ Filters      │ │ │ Transaction Table                │ │
│ │ - Date Range │ │ │ Date | Description | Amount | ... │ │
│ │ - Amount     │ │ │ ──────────────────────────────── │ │
│ │ - Type       │ │ │ [Transaction rows with sorting]  │ │
│ │ [Apply] [Clear] │ │ [Scrollbars for navigation]     │ │
│ └──────────────┘ │ └──────────────────────────────────┘ │
│ ┌──────────────┐ │                                      │
│ │ Summary      │ │                                      │
│ │ - Count: 123 │ │                                      │
│ │ - Total: ₪X  │ │                                      │
│ │ - Credits: Y │ │                                      │
│ │ - Debits: Z  │ │                                      │
│ └──────────────┘ │                                      │
└──────────────────┴──────────────────────────────────────┤
│ Status Bar: Ready | Showing X transactions              │
└─────────────────────────────────────────────────────────┘
```

### Filter Panel Controls
- **Date Range**: Start and end date input fields (YYYY-MM-DD format)
- **Amount Range**: Minimum and maximum amount input fields
- **Transaction Type**: Dropdown for Credits/Debits/All
- **Apply Filters**: Button to apply current filter settings
- **Clear Filters**: Button to reset all filters

### Transaction Table
- **Sortable Columns**: Click headers to sort by any column
- **Auto-sizing**: Columns adjust to content with horizontal scrolling
- **Row Selection**: Click to select, double-click for details
- **Context Menu**: Right-click for additional options (future enhancement)

## Error Handling

The module includes comprehensive error handling:

```python
try:
    display_manager.show_transactions(transaction_set)
except Exception as e:
    messagebox.showerror("Display Error", f"Failed to display transactions: {e}")
```

### Common Error Scenarios
- **Invalid Date Formats**: Graceful handling of malformed date inputs
- **Invalid Amount Formats**: Automatic cleaning and validation of amount inputs
- **Export Failures**: User-friendly error messages for file operation failures
- **Data Loading Issues**: Proper error reporting for data access problems

## Performance Considerations

### Large Dataset Handling
- **Efficient Filtering**: Optimized filter algorithms for large transaction sets
- **Lazy Loading**: Table population optimized for responsiveness
- **Memory Management**: Proper cleanup of GUI resources

### Responsive Design
- **Non-blocking Operations**: Filter and export operations don't freeze GUI
- **Progress Indication**: Status bar updates during long operations
- **Resizable Interface**: Window and panels adapt to user preferences

## Testing

### Unit Tests
Located in `tests/test_core_module.py`:

```python
# Test filter functionality
def test_apply_filters():
    # Test various filter combinations
    pass

# Test export functionality
def test_export_operations():
    # Test CSV, Excel, and JSON exports
    pass

# Test GUI component creation
def test_gui_creation():
    # Test window and widget creation
    pass
```

### Integration Tests
Test integration with existing system components:
- Data model compatibility
- Export manager integration
- Configuration system usage

## Examples

### Example 1: Basic Transaction Display
```python
from modules.visual_display import VisualDisplayManager
from src.excel_importer import ExcelImporter
from src.json_adapter import JSONAdapter
from adapters.ibi_adapter import IBIAdapter

# Import transaction data
importer = ExcelImporter()
adapter = JSONAdapter()
ibi_adapter = IBIAdapter()

# Load and process data
raw_data = importer.load_file("Data_Files/IBI trans 2024.xlsx")
result = adapter.process(raw_data, ibi_adapter)

if result.success:
    # Show in visual interface
    visual_display = VisualDisplayManager()
    visual_display.show_transactions(result.transaction_set)

    # GUI remains open for user interaction
    print("Visual interface launched. Use the GUI to explore your data.")
```

### Example 2: Filtered Data Analysis
```python
# Launch visual display
visual_display = VisualDisplayManager()
visual_display.show_transactions(transaction_set)

# User can now:
# 1. Filter by date range (e.g., 2024-01-01 to 2024-03-31)
# 2. Filter by amount (e.g., > ₪1000)
# 3. Search for specific descriptions (e.g., "salary")
# 4. Export filtered results to Excel
# 5. View real-time summary statistics
```

### Example 3: Custom Configuration
```python
from src.config_manager import ConfigManager

# Custom configuration
config = ConfigManager()
config.display_config["max_rows"] = 500  # Show more rows by default

# Initialize with custom config
visual_display = VisualDisplayManager(config)
visual_display.show_transactions(transaction_set)
```

## Future Enhancements

### Planned Features
- **Chart Integration**: Direct integration with visualization module
- **Category Management**: GUI-based category assignment and editing
- **Batch Operations**: Multi-select transactions for batch operations
- **Custom Views**: Save and restore filter presets
- **Enhanced Export**: Template-based export options

### Technical Improvements
- **Theme Support**: Light/dark theme options
- **Keyboard Shortcuts**: Hotkeys for common operations
- **Accessibility**: Screen reader and keyboard navigation support
- **Internationalization**: Multi-language support

## Module Dependencies

### Internal Dependencies
- `src.data_models`: Transaction and TransactionSet classes
- `src.display_manager`: Export functionality integration
- `src.config_manager`: Configuration management
- `src.json_adapter`: JSON export capabilities

### External Dependencies
- `tkinter`: GUI framework (built-in with Python)
- `pandas`: Data manipulation for exports
- `decimal`: Precise financial calculations

## API Reference

### VisualDisplayManager Class

#### Constructor
```python
VisualDisplayManager(config_manager: Optional[ConfigManager] = None)
```

#### Methods
```python
show_transactions(transaction_set: TransactionSet) -> None
close() -> None
```

### Utility Functions

#### Formatting Functions
```python
format_currency(amount: Optional[Decimal], currency_symbol: str = "₪") -> str
format_date_display(date_obj: Optional[date]) -> str
get_amount_color(amount: Optional[Decimal]) -> Optional[str]
```

#### Filter Functions
```python
create_filter_query(**kwargs) -> Dict[str, Any]
apply_transaction_filter(transactions: List, filter_query: Dict[str, Any]) -> List
```

#### Statistics Functions
```python
calculate_summary_stats(transactions: List) -> Dict[str, Any]
format_summary_text(stats: Dict[str, Any]) -> str
```

## Contributing

When contributing to the Visual Display Module:

1. **Follow Module Guidelines**: Adhere to the established module structure
2. **Import Hierarchy**: Only import from `src/` modules, not other `modules/`
3. **Self-contained Design**: Keep the module independently functional
4. **Comprehensive Testing**: Write tests for all new functionality
5. **Documentation**: Update this README for any new features
6. **Code Standards**: Follow PEP 8 and project coding conventions

## License

This module is part of the Transaction Analysis System and follows the same license terms.
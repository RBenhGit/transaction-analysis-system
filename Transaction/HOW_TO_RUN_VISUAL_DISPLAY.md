# How to Run the Visual Display Module

The Visual Display Module provides a graphical user interface (GUI) for viewing and analyzing transaction data. Here are the different ways to run it:

## Quick Start Methods

### Method 1: Real Data Display (RECOMMENDED)
```bash
python run_real_data_gui.py
```
This loads your actual IBI transaction data from processed JSON files and opens the GUI. **Shows your real 536 transactions from 2024, not mock data!**

### Method 2: Alternative Real Data Scripts
```bash
python real_data_visual_display.py
# OR
python json_visual_display.py
```
Alternative scripts that also load your real JSON data with different approaches.

### Method 3: Direct Excel Import
```bash
python visual_with_excel.py
```
This directly imports from your Excel files and opens the GUI. Takes longer but processes fresh data.

### Method 4: Demo with Sample Data
```bash
python demo_visual_display.py
```
Sample data demo (only use if you want to see the interface without real data).

### Method 5: Example Script with Multiple Options
```bash
cd modules/visual_display/examples
python example_usage.py
```
This provides an interactive menu with 5 different demonstration scenarios.

## Integration with Your Data

### Using with Excel Files
If you have Excel files in the `Data_Files/` directory (like your IBI transaction files), the visual display can import and display them:

```python
from modules.visual_display import VisualDisplayManager
from src.excel_importer import ExcelImporter
from src.json_adapter import JSONAdapter
from adapters.ibi_adapter import IBIAdapter

# Import your data
importer = ExcelImporter()
adapter = JSONAdapter()
ibi_adapter = IBIAdapter()

# Load Excel file
result = adapter.process(
    importer.load_file("Data_Files/IBI trans 2024.xlsx"),
    ibi_adapter
)

if result.success:
    # Launch visual display (window stays open until closed)
    visual_display = VisualDisplayManager()
    visual_display.run(result.transaction_set)  # This keeps the window open
```

### Using with Existing Transaction Data
If you already have transaction data loaded:

```python
from modules.visual_display import VisualDisplayManager

# Assuming you have a transaction_set from previous import
visual_display = VisualDisplayManager()
visual_display.run(transaction_set)  # Window stays open until manually closed
```

## GUI Features Overview

When the visual display window opens, you'll see:

### Main Window Layout
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
│ │ - Total: $X  │ │                                      │
│ │ - Credits: Y │ │                                      │
│ │ - Debits: Z  │ │                                      │
│ └──────────────┘ │                                      │
└──────────────────┴──────────────────────────────────────┤
│ Status Bar: Ready | Showing X transactions              │
└─────────────────────────────────────────────────────────┘
```

### Key Features to Try

#### 1. Transaction Table
- **Sort**: Click any column header to sort by that column
- **Details**: Double-click any row to see detailed transaction information
- **Navigation**: Use scrollbars to navigate through large datasets

#### 2. Filtering (Left Panel)
- **Date Range**: Enter start and end dates (YYYY-MM-DD format)
- **Amount Range**: Set minimum and maximum amounts
- **Transaction Type**: Choose Credits, Debits, or All
- **Apply Filters**: Click to apply your filter settings
- **Clear Filters**: Reset all filters to show all data

#### 3. Search (Toolbar)
- **Quick Search**: Type in the search box to find transactions by description
- **Real-time**: Results update as you type
- **Clear**: Click Clear button to remove search

#### 4. Summary Panel (Left Panel)
- **Live Statistics**: Updates automatically as you filter
- **Transaction Count**: Total number of visible transactions
- **Financial Totals**: Sum of credits, debits, and net amount
- **Date Range**: Shows the span of currently displayed data

#### 5. Export Functions
- **File Menu**: Export to CSV, Excel, or JSON
- **Toolbar Buttons**: Quick access to CSV and Excel export
- **Filtered Data**: Only exports currently visible (filtered) transactions
- **File Dialog**: Choose where to save your exported data

## Advanced Usage

### Programmatic Control
You can control the visual display programmatically:

```python
from modules.visual_display import VisualDisplayManager
from modules.visual_display.utils import apply_transaction_filter, create_filter_query

# Create display manager
manager = VisualDisplayManager()

# Load your data
manager.show_transactions(transaction_set)

# The GUI window is now open and interactive
```

### Custom Configuration
You can customize the display with your own settings:

```python
from src.config_manager import ConfigManager
from modules.visual_display import VisualDisplayManager

# Custom configuration
config = ConfigManager()
config.display_config["max_rows"] = 500  # Show more rows

# Use custom config
visual_display = VisualDisplayManager(config)
visual_display.show_transactions(transaction_set)
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the project root directory
2. **No Data**: If using real data, ensure Excel files are in `Data_Files/` directory
3. **GUI Not Opening**: On some systems, you may need to install tkinter separately
4. **Character Encoding**: If you see Unicode errors, the sample data scripts should work fine

### System Requirements
- Python 3.8+
- tkinter (usually included with Python)
- pandas, openpyxl (from requirements.txt)
- All existing project dependencies

### Performance Notes
- The GUI handles large datasets efficiently
- Filtering is fast even with thousands of transactions
- Export operations may take a moment for very large datasets

## Integration with Main Application

To add visual display to your main application workflow, you can modify `main.py` to include a new menu option. The visual display integrates seamlessly with the existing import and processing pipeline.

## Next Steps

1. **Start with the demo**: Run `python demo_visual_display.py`
2. **Try with your data**: Use `python run_visual_display.py`
3. **Explore features**: Use filtering, sorting, and export functions
4. **Integrate**: Add visual display calls to your existing workflows

The visual display module provides an intuitive way to explore your transaction data with immediate visual feedback and powerful filtering capabilities.
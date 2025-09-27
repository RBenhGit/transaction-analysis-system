# Analytics Module

## Overview
The Analytics module provides comprehensive data analysis and statistical functions for transaction data analysis.

## Features
- **Transaction Pattern Analysis**: Identify spending patterns and behaviors
- **Trend Analysis**: Time series analysis and trend detection
- **Category Analysis**: Automatic spending categorization and insights
- **Financial Metrics**: Calculate key financial performance indicators
- **Statistical Analysis**: Descriptive and inferential statistics

## Components

### TransactionAnalyzer
Core class for analyzing transaction data.

```python
from modules.analytics import TransactionAnalyzer

analyzer = TransactionAnalyzer()
insights = analyzer.analyze_transactions(transaction_data)
```

### TrendAnalyzer
Time series analysis and forecasting.

```python
from modules.analytics.trend_analyzer import TrendAnalyzer

trend_analyzer = TrendAnalyzer()
trends = trend_analyzer.detect_trends(transaction_data)
```

### CategoryAnalyzer
Spending category analysis and classification.

```python
from modules.analytics.category_analyzer import CategoryAnalyzer

category_analyzer = CategoryAnalyzer()
categories = category_analyzer.categorize_transactions(transaction_data)
```

## Dependencies
- pandas: Data manipulation and analysis
- numpy: Numerical computations
- scipy: Statistical functions
- matplotlib: Data visualization (optional)

## Usage Examples

### Basic Transaction Analysis
```python
from modules.analytics import TransactionAnalyzer
from src.json_adapter import JSONAdapter

# Load transaction data
json_adapter = JSONAdapter()
result = json_adapter.import_from_json('transactions.json')
transactions = result.transaction_set.transactions

# Analyze transactions
analyzer = TransactionAnalyzer()
analysis = analyzer.analyze_transactions(transactions)

print(f"Total transactions: {analysis['total_count']}")
print(f"Average amount: {analysis['average_amount']}")
print(f"Spending trend: {analysis['trend']}")
```

### Monthly Spending Analysis
```python
from modules.analytics.trend_analyzer import TrendAnalyzer

trend_analyzer = TrendAnalyzer()
monthly_data = trend_analyzer.group_by_month(transactions)
spending_trend = trend_analyzer.calculate_trend(monthly_data)

print(f"Monthly spending trend: {spending_trend}")
```

## Development Guidelines
1. All analysis functions should accept transaction data in the standard format
2. Return results as dictionaries with clear, descriptive keys
3. Include proper error handling for invalid data
4. Add comprehensive docstrings with examples
5. Write unit tests for all analysis functions

## File Structure
```
modules/analytics/
├── __init__.py
├── README.md
├── transaction_analyzer.py    # Core analysis functions
├── trend_analyzer.py         # Time series analysis
├── category_analyzer.py      # Category classification
├── metrics_calculator.py     # Financial metrics
└── tests/                    # Module-specific tests
    ├── __init__.py
    ├── test_transaction_analyzer.py
    ├── test_trend_analyzer.py
    └── test_category_analyzer.py
```
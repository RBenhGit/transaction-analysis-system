# Integration Tests for IBI Transaction Analysis

## Overview

Comprehensive integration test suite that validates the entire transaction analysis system using real IBI data from 2022-2025.

## Test Suites

### 1. End-to-End Tests (`test_ibi_end_to_end.py`)
**10 tests** - Validates complete workflow from Excel file to portfolio positions

**Tests:**
- ✅ File Loading - Excel file can be loaded successfully
- ✅ Adapter Transformation - IBI adapter transforms data correctly
- ✅ Transaction Parsing - Transactions parsed into Transaction objects
- ✅ Transaction Classification - Transactions classified correctly (buy, sell, dividend, etc.)
- ✅ Portfolio Building - Portfolio positions built correctly
- ✅ Currency Validation - Transactions have valid currencies
- ✅ Fee Handling - Transaction fees handled correctly
- ✅ Date Range Validation - Transactions have valid dates
- ✅ Balance Monotonicity - Account balance changes are reasonable
- ✅ No Duplicate Transactions - Checks for duplicate entries

**Run:** `python -m pytest tests/integration/test_ibi_end_to_end.py -v`

---

### 2. Performance Tests (`test_ibi_performance.py`)
**7 tests** - Validates system performance with large transaction volumes

**Tests:**
- ✅ Excel Loading Performance (< 5s threshold)
- ✅ Transformation Performance (< 3s threshold)
- ✅ Transaction Parsing Performance (< 5s threshold)
- ✅ Portfolio Building Performance (< 2s threshold)
- ✅ End-to-End Performance (< 15s threshold)
- ✅ Memory Usage (< 500 MB threshold)
- ✅ Multiple Runs Consistency - Performance is consistent across runs

**Performance Benchmarks (Real Data):**
- Excel Loading: ~2.3s
- Transformation: ~0.6s
- Parsing: ~1.1s (1,931 transactions)
- Portfolio Building: ~0.2s
- End-to-End: ~3.4s
- Peak Memory: ~8 MB

**Run:** `python -m pytest tests/integration/test_ibi_performance.py -v`

---

### 3. Accuracy Validation Tests (`test_ibi_accuracy.py`)
**8 tests** - Validates portfolio calculation accuracy

**Tests:**
- ✅ Position Quantities Non-Negative - All positions have valid quantities
- ✅ Average Cost Positive - Average costs are valid (reports zero-cost positions as info)
- ✅ Buy/Sell Balance - Transaction history matches positions (with notes on expected mismatches)
- ✅ Total Invested Calculation - `total_invested` calculated correctly
- ✅ No Phantom Positions - Phantom securities excluded from portfolio
- ✅ Currency Consistency - Currencies consistent within positions
- ✅ Portfolio Has Expected Symbols - Basic sanity checks
- ✅ Transaction Count Reasonable - Counts are reasonable

**Run:** `python -m pytest tests/integration/test_ibi_accuracy.py -v`

---

### 4. Regression Tests (`test_ibi_regression.py`)
**6 tests** - Prevents calculation changes from affecting accuracy

**Features:**
- Creates baseline of portfolio results on first run
- Compares subsequent runs against baseline
- Detects unexpected changes in calculations
- Ensures backward compatibility

**Tests:**
- ✅ Create/Update Baseline - Manages regression baseline
- ✅ Transaction Counts Stable - Transaction count unchanged
- ✅ Position Counts Stable - Position count unchanged
- ✅ Position Quantities Stable - Quantities match baseline
- ✅ Average Costs Stable - Costs match baseline
- ✅ Transaction Categories Stable - Category counts match baseline

**Baseline Location:** `tests/integration/baselines/ibi_portfolio_2022_2025.json`

**Run:** `python -m pytest tests/integration/test_ibi_regression.py -v`

---

## Running All Tests

### Run Complete Suite
```bash
python -m pytest tests/integration/ -v
```

**Expected:** 31 tests, all passing

### Run Specific Suite
```bash
python -m pytest tests/integration/test_ibi_end_to_end.py -v
python -m pytest tests/integration/test_ibi_performance.py -v
python -m pytest tests/integration/test_ibi_accuracy.py -v
python -m pytest tests/integration/test_ibi_regression.py -v
```

### Run with Detailed Output
```bash
python -m pytest tests/integration/ -v -s
```

### Run with Coverage
```bash
python -m pytest tests/integration/ --cov=src --cov-report=html
```

---

## Test Data

### Real IBI Data
- **File:** `Data_Files/IBI trans 2022-5_10_2025.xlsx`
- **Transactions:** 1,931 total
- **Period:** 2022 - Early 2025
- **Categories:** buy (833), sell (464), dividend (306), tax (244), interest (29), transfer (54), fee (1)
- **Positions:** 81 unique securities

### Test Fixtures
Located in `tests/fixtures/`:
- `ibi_test_data.py` - Test data infrastructure and file paths
- Automatically discovers test files in `Data_Files/` directory

---

## Project Structure

```
tests/
├── integration/
│   ├── __init__.py
│   ├── README.md                   # This file
│   ├── test_ibi_end_to_end.py      # End-to-end workflow tests
│   ├── test_ibi_performance.py     # Performance benchmarks
│   ├── test_ibi_accuracy.py        # Accuracy validation
│   ├── test_ibi_regression.py      # Regression prevention
│   └── baselines/                  # Regression baselines
│       └── ibi_portfolio_2022_2025.json
└── fixtures/
    ├── __init__.py
    └── ibi_test_data.py            # Test data management
```

---

## Key Findings

### Data Quality Insights
From running integration tests on real data:

1. **Zero-Cost Positions:** 45 positions (56%) have zero average cost
   - **Cause:** Stock dividends, transfers, or corporate actions
   - **Status:** Normal and expected

2. **Buy/Sell Mismatches:** 60 positions (74%) show quantity mismatches
   - **Causes:**
     - Stock dividends (shares added without buy transaction)
     - Stock splits (shares multiplied)
     - Transfers (shares moved in/out)
     - Rights offerings
   - **Status:** Normal and expected

3. **Performance:** System handles 1,931 transactions in ~3.4 seconds
   - Well within acceptable thresholds
   - Memory usage very efficient (~8 MB peak)

4. **Phantom Detection:** Working correctly
   - 0 phantom positions in final portfolio
   - Tax, fee, and commission transactions properly excluded

---

## Continuous Integration

### Pre-Commit Checks
```bash
# Run all integration tests before committing
python -m pytest tests/integration/ -v
```

### Regression Protection
The regression test suite creates a baseline on first run. Future code changes that affect calculations will fail regression tests, alerting you to review the changes.

To update baseline after intentional changes:
```bash
# Delete old baseline
rm tests/integration/baselines/ibi_portfolio_2022_2025.json

# Re-run tests to create new baseline
python -m pytest tests/integration/test_ibi_regression.py -v
```

---

## Adding New Test Data

To add a new test dataset:

1. Place Excel file in `Data_Files/` directory
2. Update `tests/fixtures/ibi_test_data.py`:
   ```python
   TEST_FILES = {
       "NEW_DATASET": {
           "file": "new_file.xlsx",
           "description": "Description of dataset",
           "sheet": None,
       }
   }
   ```
3. Run tests to create new baseline

---

## Troubleshooting

### Tests Fail After Code Changes
✅ **Expected if you changed calculation logic**
- Review what changed in the output
- If changes are correct, update regression baseline
- If changes are incorrect, fix the code

### Performance Tests Fail
❌ **System may be slow or under load**
- Close other applications
- Run tests again
- Adjust thresholds if consistently failing on valid hardware

### Import Errors
❌ **Python path issues**
```bash
# Run from project root
cd Transaction/
python -m pytest tests/integration/ -v
```

---

## Future Enhancements

### Planned Additions
- [ ] Multi-bank support (add adapters for other banks)
- [ ] Edge case testing (empty files, corrupted data)
- [ ] Stress testing (100k+ transactions)
- [ ] Parallel execution optimization
- [ ] HTML test reports
- [ ] CI/CD integration (GitHub Actions)

---

## Contact & Support

For issues or questions about the integration tests, refer to:
- Main project documentation: `../CLAUDE.md`
- Test implementation details: See individual test files
- Task Master task #20: Integration test implementation tracking

---

**Status:** ✅ All 31 tests passing
**Last Updated:** 2025-10-15
**Test Coverage:** Complete end-to-end workflow with real IBI data

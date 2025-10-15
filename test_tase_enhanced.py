"""
Enhanced TASE Price Fetcher Tests with Real Portfolio Symbols.

Tests the complete TASE integration including:
- Symbol translation (Hebrew → numeric ID)
- Numeric TASE ID handling
- Yahoo Finance integration
"""

import sys
from pathlib import Path
import io

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modules.portfolio_dashboard.price_fetcher import (
    fetch_current_price,
    _fetch_tase_price_yahoo,
    fetch_with_fallback
)
from modules.portfolio_dashboard.tase_symbol_mapper import (
    translate_tase_symbol,
    is_hebrew_name,
    is_tase_numeric_id,
    is_us_stock_symbol,
    get_symbol_info
)


def test_symbol_translation():
    """Test TASE symbol translation logic."""
    print("=" * 70)
    print("TEST 1: Symbol Translation Logic")
    print("=" * 70)

    test_cases = [
        # (input_symbol, expected_output, description)
        ("מזטפ", "695437.TA", "Hebrew name → Numeric ID"),
        ("695437", "695437.TA", "Numeric TASE ID → .TA suffix"),
        ("MSFT", "MSFT", "US stock → Unchanged"),
        ("סקופ", "288019.TA", "Hebrew name (Scopus)"),
        ("פמס", "315010.TA", "Hebrew name (FIMI)"),
        ("AAPL", "AAPL", "US stock (Apple)"),
    ]

    print(f"\n{'Input':<20} {'Expected':<15} {'Actual':<15} {'Status':<10} Description")
    print("-" * 70)

    passed = 0
    failed = 0

    for input_symbol, expected, description in test_cases:
        actual = translate_tase_symbol(input_symbol)
        status = "✓ PASS" if actual == expected else "✗ FAIL"

        if actual == expected:
            passed += 1
        else:
            failed += 1

        print(f"{input_symbol:<20} {expected:<15} {actual or 'None':<15} {status:<10} {description}")

    print(f"\nResults: {passed} passed, {failed} failed")
    print("=" * 70)


def test_symbol_detection():
    """Test symbol type detection functions."""
    print("\n" + "=" * 70)
    print("TEST 2: Symbol Type Detection")
    print("=" * 70)

    test_symbols = [
        "מזטפ",      # Hebrew
        "695437",    # Numeric TASE
        "MSFT",      # US stock
        "סקופ",      # Hebrew
        "AAPL",      # US stock
        "1176593",   # Numeric TASE
    ]

    print(f"\n{'Symbol':<15} {'Hebrew':<10} {'TASE ID':<10} {'US Stock':<10}")
    print("-" * 70)

    for symbol in test_symbols:
        is_heb = "Yes" if is_hebrew_name(symbol) else "No"
        is_tase = "Yes" if is_tase_numeric_id(symbol) else "No"
        is_us = "Yes" if is_us_stock_symbol(symbol) else "No"

        print(f"{symbol:<15} {is_heb:<10} {is_tase:<10} {is_us:<10}")

    print("=" * 70)


def test_tase_price_fetching():
    """Test actual TASE price fetching from Yahoo Finance."""
    print("\n" + "=" * 70)
    print("TEST 3: TASE Price Fetching (Live API Calls)")
    print("=" * 70)

    # Use numeric TASE IDs that are known to exist on Yahoo Finance
    tase_stocks = [
        ("695437", "Mizrahi Tefahot Bank"),  # Major Israeli bank
        ("288019", "Scopus Video Networks"),
        ("507012", "Ituran Location"),
    ]

    print("\n[TASE Stocks - Numeric IDs]\n")

    successful = 0
    total = len(tase_stocks)

    for symbol, name in tase_stocks:
        print(f"Testing {name} ({symbol})...")
        price = fetch_current_price(symbol, currency="₪")

        if price and price > 0:
            print(f"  ✓ SUCCESS: {symbol} = ILS {price:.2f}")
            successful += 1
        else:
            print(f"  ✗ FAILED: Could not fetch price for {symbol}")
        print()

    print(f"Results: {successful}/{total} TASE stocks fetched successfully")
    print("=" * 70)


def test_hebrew_symbol_fetching():
    """Test fetching prices using Hebrew symbol names."""
    print("\n" + "=" * 70)
    print("TEST 4: Hebrew Symbol Name Fetching")
    print("=" * 70)

    # Hebrew symbols from actual portfolio
    hebrew_symbols = [
        ("מזטפ", "Mizrahi Tefahot"),
        ("סקופ", "Scopus"),
    ]

    print("\n[TASE Stocks - Hebrew Names]\n")

    for symbol, name in hebrew_symbols:
        print(f"Testing {name} ({symbol})...")

        # Show translation
        translated = translate_tase_symbol(symbol)
        print(f"  Translated to: {translated}")

        # Fetch price
        price = fetch_current_price(symbol, currency="₪")

        if price and price > 0:
            print(f"  ✓ SUCCESS: {symbol} = ILS {price:.2f}")
        else:
            print(f"  ✗ FAILED: Could not fetch price")
        print()

    print("=" * 70)


def test_us_vs_tase_comparison():
    """Test both US and TASE stocks to verify dual support."""
    print("\n" + "=" * 70)
    print("TEST 5: US vs TASE Stock Comparison")
    print("=" * 70)

    stocks = [
        ("AAPL", "$", "Apple Inc (US)"),
        ("MSFT", "$", "Microsoft (US)"),
        ("695437", "₪", "Mizrahi Tefahot (TASE)"),
        ("288019", "₪", "Scopus (TASE)"),
    ]

    print(f"\n{'Symbol':<15} {'Currency':<10} {'Price':<15} {'Name'}")
    print("-" * 70)

    for symbol, currency, name in stocks:
        price = fetch_current_price(symbol, currency)

        if price:
            price_str = f"{currency}{price:.2f}"
            status = "✓"
        else:
            price_str = "N/A"
            status = "✗"

        print(f"{status} {symbol:<13} {currency:<10} {price_str:<15} {name}")

    print("=" * 70)


def test_fallback_mechanism():
    """Test price fallback mechanisms."""
    print("\n" + "=" * 70)
    print("TEST 6: Price Fallback Mechanism")
    print("=" * 70)

    # Test with valid TASE stock
    print("\nTest 1: Valid TASE stock (should fetch live)")
    result = fetch_with_fallback("695437", currency="₪")
    print(f"  Symbol: {result.symbol}")
    print(f"  Price: ₪{result.price:.2f}" if result.price else "  Price: None")
    print(f"  Source: {result.source}")
    print(f"  Timestamp: {result.timestamp}")
    print(f"  Is Stale: {result.is_stale}")

    # Test with invalid symbol (should use fallback)
    print("\nTest 2: Invalid symbol (should show fallback behavior)")
    result = fetch_with_fallback("INVALID_SYMBOL_999", currency="₪")
    print(f"  Symbol: {result.symbol}")
    print(f"  Price: {result.price}")
    print(f"  Source: {result.source}")

    print("\n" + "=" * 70)


def test_symbol_diagnostics():
    """Test symbol diagnostics utility."""
    print("\n" + "=" * 70)
    print("TEST 7: Symbol Diagnostics")
    print("=" * 70)

    test_symbols = ["מזטפ", "695437", "MSFT", "סקופ"]

    for symbol in test_symbols:
        info = get_symbol_info(symbol)
        print(f"\nSymbol: {symbol}")
        print(f"  Is Hebrew: {info['is_hebrew']}")
        print(f"  Is Numeric TASE ID: {info['is_numeric_tase_id']}")
        print(f"  Is US Stock: {info['is_us_stock']}")
        print(f"  Translated: {info['translated_symbol']}")
        print(f"  In Mapping: {info['in_mapping']}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ENHANCED TASE PRICE FETCHER TEST SUITE")
    print("=" * 70)

    # Run all tests
    test_symbol_translation()
    test_symbol_detection()
    test_tase_price_fetching()
    test_hebrew_symbol_fetching()
    test_us_vs_tase_comparison()
    test_fallback_mechanism()
    test_symbol_diagnostics()

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)

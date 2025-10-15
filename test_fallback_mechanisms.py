"""
Test Price Fallback Mechanisms.

This script tests the fallback system in price_fetcher.py.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modules.portfolio_dashboard.price_fetcher import (
    fetch_with_fallback,
    set_manual_price,
    get_manual_price,
    clear_manual_price,
    save_price_cache,
    load_price_cache,
    save_manual_prices,
    load_manual_prices,
    initialize_cache,
    cleanup_cache,
    PriceData
)

def test_manual_prices():
    """Test manual price setting and retrieval."""
    print("=" * 60)
    print("Testing Manual Price System")
    print("=" * 60)

    # Set manual price
    print("\n1. Setting manual price for TEST symbol...")
    price_data = set_manual_price("TEST", 100.50, "$")
    print(f"   [OK] Manual price set: ${price_data.price:.2f}")
    print(f"   Source: {price_data.source}")

    # Retrieve manual price
    print("\n2. Retrieving manual price...")
    manual_price = get_manual_price("TEST")
    if manual_price == 100.50:
        print(f"   [OK] Manual price retrieved: ${manual_price:.2f}")
    else:
        print(f"   [FAIL] Expected $100.50, got {manual_price}")

    # Clear manual price
    print("\n3. Clearing manual price...")
    if clear_manual_price("TEST"):
        print("   [OK] Manual price cleared")
    else:
        print("   [FAIL] Failed to clear manual price")

    # Verify cleared
    print("\n4. Verifying price is cleared...")
    cleared_price = get_manual_price("TEST")
    if cleared_price is None:
        print("   [OK] Price confirmed cleared")
    else:
        print(f"   [FAIL] Price still exists: {cleared_price}")

    print("\n" + "=" * 60)


def test_fallback_sequence():
    """Test the complete fallback sequence."""
    print("\n" + "=" * 60)
    print("Testing Fallback Sequence")
    print("=" * 60)

    # Test 1: Manual price (highest priority)
    print("\n1. Testing Fallback Level 1: Manual Price")
    set_manual_price("AAPL", 200.00, "$")
    result = fetch_with_fallback("AAPL", "$")
    print(f"   Symbol: {result.symbol}")
    print(f"   Price: ${result.price:.2f}")
    print(f"   Source: {result.source}")
    if result.source == "manual":
        print("   [OK] Manual price has highest priority")
    else:
        print(f"   [FAIL] Expected 'manual', got '{result.source}'")

    # Clear manual price for next test
    clear_manual_price("AAPL")

    # Test 2: Live price (second priority)
    print("\n2. Testing Fallback Level 2: Live API Price")
    result = fetch_with_fallback("AAPL", "$")
    print(f"   Symbol: {result.symbol}")
    print(f"   Price: ${result.price:.2f}" if result.price else "   Price: None")
    print(f"   Source: {result.source}")
    if result.source in ["yfinance", "tase_yahoo"]:
        print("   [OK] Live API fetch successful")
    else:
        print(f"   [INFO] Live fetch not available, source: {result.source}")

    # Test 3: Unavailable symbol
    print("\n3. Testing Fallback Level 4: Unavailable")
    result = fetch_with_fallback("INVALID_SYMBOL_XYZ", "$", allow_stale=False)
    print(f"   Symbol: {result.symbol}")
    print(f"   Price: {result.price}")
    print(f"   Source: {result.source}")
    if result.source == "unavailable":
        print("   [OK] Correctly marked as unavailable")
    else:
        print(f"   [FAIL] Expected 'unavailable', got '{result.source}'")

    print("\n" + "=" * 60)


def test_cache_persistence():
    """Test cache saving and loading."""
    print("\n" + "=" * 60)
    print("Testing Cache Persistence")
    print("=" * 60)

    # Set up test data
    print("\n1. Setting up test prices...")
    set_manual_price("MSFT", 350.00, "$")
    set_manual_price("GOOGL", 140.00, "$")
    print("   [OK] Test prices set")

    # Save caches
    print("\n2. Saving caches to disk...")
    if save_manual_prices() and save_price_cache():
        print("   [OK] Caches saved successfully")
    else:
        print("   [FAIL] Cache save failed")

    # Clear in-memory data
    print("\n3. Clearing in-memory data...")
    clear_manual_price("MSFT")
    clear_manual_price("GOOGL")
    print("   [OK] In-memory data cleared")

    # Load caches
    print("\n4. Loading caches from disk...")
    if load_manual_prices():
        print("   [OK] Manual prices loaded")
    else:
        print("   [WARN] No manual prices to load")

    # Verify loaded data
    print("\n5. Verifying loaded data...")
    msft_price = get_manual_price("MSFT")
    googl_price = get_manual_price("GOOGL")

    if msft_price == 350.00 and googl_price == 140.00:
        print(f"   [OK] MSFT: ${msft_price:.2f}, GOOGL: ${googl_price:.2f}")
    else:
        print(f"   [FAIL] Unexpected prices - MSFT: {msft_price}, GOOGL: {googl_price}")

    # Clean up test files
    print("\n6. Cleaning up test data...")
    clear_manual_price("MSFT")
    clear_manual_price("GOOGL")
    save_manual_prices()
    print("   [OK] Test data cleaned up")

    print("\n" + "=" * 60)


def test_price_data_staleness():
    """Test staleness detection in PriceData."""
    print("\n" + "=" * 60)
    print("Testing Price Staleness Detection")
    print("=" * 60)

    from datetime import datetime, timedelta

    # Fresh price
    print("\n1. Testing fresh price...")
    fresh_price = PriceData(
        price=100.0,
        source="yfinance",
        symbol="TEST",
        currency="$"
    )
    print(f"   Timestamp: {fresh_price.timestamp}")
    print(f"   Is Stale: {fresh_price.is_stale}")
    if not fresh_price.is_stale:
        print("   [OK] Fresh price correctly identified")
    else:
        print("   [FAIL] Fresh price marked as stale")

    # Stale price (25 hours old)
    print("\n2. Testing stale price (25 hours old)...")
    old_timestamp = datetime.now() - timedelta(hours=25)
    stale_price = PriceData(
        price=100.0,
        source="yfinance",
        symbol="TEST",
        currency="$",
        timestamp=old_timestamp
    )
    print(f"   Timestamp: {stale_price.timestamp}")
    print(f"   Is Stale: {stale_price.is_stale}")
    if stale_price.is_stale:
        print("   [OK] Stale price correctly identified")
    else:
        print("   [FAIL] Stale price not detected")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\n[START] Testing Price Fallback Mechanisms\n")

    # Initialize cache system
    initialize_cache()

    # Run tests
    test_manual_prices()
    test_fallback_sequence()
    test_cache_persistence()
    test_price_data_staleness()

    # Cleanup
    cleanup_cache()

    print("\n[COMPLETE] All fallback tests completed!\n")

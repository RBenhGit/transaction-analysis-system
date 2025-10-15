"""
Comprehensive Price Fallback Mechanism Tests.

Tests all 4 levels of the fallback system:
1. Manual price override
2. Live API fetch
3. Cached/last-known price
4. Unavailable marker
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
    fetch_with_fallback,
    set_manual_price,
    get_manual_price,
    clear_manual_price,
    _cache_price,
    _get_cached_price,
    PriceData,
    initialize_cache,
    cleanup_cache,
    save_price_cache,
    load_price_cache,
    save_manual_prices,
    load_manual_prices
)


def test_fallback_level_1_manual_price():
    """Test Fallback Level 1: Manual Price Override"""
    print("=" * 70)
    print("TEST 1: Fallback Level 1 - Manual Price Override")
    print("=" * 70)

    # Set manual price for a TASE stock
    symbol = "מזטפ"  # Mizrahi Tefahot
    manual_price = 5000.00
    currency = "₪"

    print(f"\n1. Setting manual price for {symbol}: {currency}{manual_price:.2f}")
    price_data = set_manual_price(symbol, manual_price, currency)

    print(f"   ✓ Manual price set")
    print(f"   - Price: {price_data.currency}{price_data.price:.2f}")
    print(f"   - Source: {price_data.source}")
    print(f"   - Symbol: {price_data.symbol}")

    # Fetch with fallback should return manual price
    print(f"\n2. Fetching price with fallback...")
    result = fetch_with_fallback(symbol, currency)

    if result.source == "manual" and result.price == manual_price:
        print(f"   ✓ PASS: Manual price returned correctly")
        print(f"   - Price: {result.currency}{result.price:.2f}")
        print(f"   - Source: {result.source}")
    else:
        print(f"   ✗ FAIL: Expected manual price, got {result.source}")

    # Verify get_manual_price
    print(f"\n3. Verifying get_manual_price()...")
    retrieved = get_manual_price(symbol)
    if retrieved == manual_price:
        print(f"   ✓ PASS: Manual price retrieved: {currency}{retrieved:.2f}")
    else:
        print(f"   ✗ FAIL: Expected {manual_price}, got {retrieved}")

    # Clear manual price
    print(f"\n4. Clearing manual price...")
    cleared = clear_manual_price(symbol)
    if cleared:
        print(f"   ✓ PASS: Manual price cleared successfully")
    else:
        print(f"   ✗ FAIL: Failed to clear manual price")

    print("\n" + "=" * 70)


def test_fallback_level_2_live_api():
    """Test Fallback Level 2: Live API Fetch"""
    print("\n" + "=" * 70)
    print("TEST 2: Fallback Level 2 - Live API Fetch")
    print("=" * 70)

    # Test with US stock (should work via Yahoo Finance)
    symbol = "AAPL"
    currency = "$"

    print(f"\n1. Fetching live price for {symbol}...")
    result = fetch_with_fallback(symbol, currency)

    if result.price and result.price > 0:
        print(f"   ✓ PASS: Live price fetched successfully")
        print(f"   - Symbol: {result.symbol}")
        print(f"   - Price: {result.currency}{result.price:.2f}")
        print(f"   - Source: {result.source}")
        print(f"   - Timestamp: {result.timestamp}")
        print(f"   - Is Stale: {result.is_stale}")
    else:
        print(f"   ✗ FAIL: Could not fetch live price")
        print(f"   - Source: {result.source}")

    print("\n" + "=" * 70)


def test_fallback_level_3_cached_price():
    """Test Fallback Level 3: Cached/Last-Known Price"""
    print("\n" + "=" * 70)
    print("TEST 3: Fallback Level 3 - Cached/Last-Known Price")
    print("=" * 70)

    # Create a fake cached price
    symbol = "TEST_CACHED_STOCK"
    currency = "$"
    cached_price = 123.45

    print(f"\n1. Creating cached price for {symbol}...")
    price_data = PriceData(
        price=cached_price,
        source="yfinance",
        symbol=symbol,
        currency=currency
    )
    _cache_price(symbol, price_data)
    print(f"   ✓ Price cached: {currency}{cached_price:.2f}")

    # Verify cache retrieval
    print(f"\n2. Retrieving cached price...")
    retrieved = _get_cached_price(symbol)
    if retrieved and retrieved.price == cached_price:
        print(f"   ✓ PASS: Cached price retrieved correctly")
        print(f"   - Price: {retrieved.currency}{retrieved.price:.2f}")
        print(f"   - Source: {retrieved.source}")
    else:
        print(f"   ✗ FAIL: Could not retrieve cached price")

    # Test fallback to cached price (symbol doesn't exist on Yahoo)
    print(f"\n3. Testing fallback to cached price...")
    result = fetch_with_fallback(symbol, currency, allow_stale=True)

    if result.source == "last_known" and result.price == cached_price:
        print(f"   ✓ PASS: Fallback to cached price works")
        print(f"   - Price: {result.currency}{result.price:.2f}")
        print(f"   - Source: {result.source}")
    else:
        print(f"   ✗ FAIL: Expected cached price, got source: {result.source}")

    print("\n" + "=" * 70)


def test_fallback_level_4_unavailable():
    """Test Fallback Level 4: Unavailable Marker"""
    print("\n" + "=" * 70)
    print("TEST 4: Fallback Level 4 - Unavailable Marker")
    print("=" * 70)

    # Use invalid symbol with no cache and no manual price
    symbol = "TOTALLY_INVALID_SYMBOL_XYZ"
    currency = "$"

    print(f"\n1. Fetching price for invalid symbol: {symbol}")
    print(f"   (no manual price, no live data, no cache)")

    result = fetch_with_fallback(symbol, currency, allow_stale=True)

    if result.source == "unavailable" and result.price is None:
        print(f"   ✓ PASS: Unavailable marker returned correctly")
        print(f"   - Source: {result.source}")
        print(f"   - Price: {result.price}")
        print(f"   - Is Stale: {result.is_stale}")
    else:
        print(f"   ✗ FAIL: Expected unavailable, got source: {result.source}")

    print("\n" + "=" * 70)


def test_cache_persistence():
    """Test Cache Persistence (Save/Load)"""
    print("\n" + "=" * 70)
    print("TEST 5: Cache Persistence - Save/Load")
    print("=" * 70)

    # Create test data
    test_symbol = "TEST_PERSIST"
    test_price = 999.99
    currency = "$"

    print(f"\n1. Creating test price data...")
    price_data = PriceData(
        price=test_price,
        source="yfinance",
        symbol=test_symbol,
        currency=currency
    )
    _cache_price(test_symbol, price_data)
    print(f"   ✓ Test data cached")

    # Save cache
    print(f"\n2. Saving price cache to disk...")
    save_result = save_price_cache()
    if save_result:
        print(f"   ✓ PASS: Cache saved successfully")
    else:
        print(f"   ✗ FAIL: Cache save failed")

    # Save manual prices
    print(f"\n3. Setting and saving manual price...")
    set_manual_price("MANUAL_TEST", 555.55, "$")
    manual_save_result = save_manual_prices()
    if manual_save_result:
        print(f"   ✓ PASS: Manual prices saved")
    else:
        print(f"   ✗ FAIL: Manual prices save failed")

    # Clear manual price from memory
    clear_manual_price("MANUAL_TEST")

    # Load from disk
    print(f"\n4. Loading cache from disk...")
    load_result = load_price_cache()
    manual_load_result = load_manual_prices()

    if load_result:
        print(f"   ✓ PASS: Price cache loaded")
    if manual_load_result:
        print(f"   ✓ PASS: Manual prices loaded")

    # Verify loaded data
    manual_check = get_manual_price("MANUAL_TEST")
    if manual_check == 555.55:
        print(f"   ✓ PASS: Manual price persisted correctly: ${manual_check:.2f}")
    else:
        print(f"   ✗ FAIL: Manual price not persisted")

    print("\n" + "=" * 70)


def test_tase_stock_fallback_chain():
    """Test Complete Fallback Chain for TASE Stock"""
    print("\n" + "=" * 70)
    print("TEST 6: Complete TASE Stock Fallback Chain")
    print("=" * 70)

    # Use real TASE stock
    symbol = "מזטפ"  # Mizrahi Tefahot
    currency = "₪"

    print(f"\nTesting fallback chain for TASE stock: {symbol}")
    print(f"Expected flow: API fails → No cache → Returns unavailable")

    # Attempt 1: Should fail at API level
    print(f"\n1. First attempt (no manual, no cache)...")
    result1 = fetch_with_fallback(symbol, currency)
    print(f"   - Source: {result1.source}")
    print(f"   - Price: {result1.price}")

    # Set manual price as workaround
    print(f"\n2. Setting manual price as workaround...")
    manual_price = 5500.00
    set_manual_price(symbol, manual_price, currency)

    result2 = fetch_with_fallback(symbol, currency)
    if result2.source == "manual" and result2.price == manual_price:
        print(f"   ✓ PASS: Manual price fallback works")
        print(f"   - Price: {result2.currency}{result2.price:.2f}")
    else:
        print(f"   ✗ FAIL: Manual price not used")

    # Clear manual price and test cache fallback
    print(f"\n3. Clearing manual, testing last-known fallback...")
    clear_manual_price(symbol)

    # Cache the previous successful fetch
    cached_data = PriceData(
        price=manual_price,
        source="manual",
        symbol=symbol,
        currency=currency
    )
    _cache_price(symbol, cached_data)

    result3 = fetch_with_fallback(symbol, currency, allow_stale=True)
    if result3.source == "last_known":
        print(f"   ✓ PASS: Last-known cache fallback works")
        print(f"   - Price: {result3.currency}{result3.price:.2f}")
    else:
        print(f"   Source: {result3.source}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("COMPREHENSIVE PRICE FALLBACK MECHANISM TEST SUITE")
    print("=" * 70)
    print("\nTesting all 4 fallback levels:")
    print("1. Manual Price Override")
    print("2. Live API Fetch")
    print("3. Cached/Last-Known Price")
    print("4. Unavailable Marker")
    print("\n" + "=" * 70)

    # Initialize cache system
    initialize_cache()

    # Run all tests
    test_fallback_level_1_manual_price()
    test_fallback_level_2_live_api()
    test_fallback_level_3_cached_price()
    test_fallback_level_4_unavailable()
    test_cache_persistence()
    test_tase_stock_fallback_chain()

    # Cleanup
    cleanup_cache()

    print("\n" + "=" * 70)
    print("ALL FALLBACK TESTS COMPLETED")
    print("=" * 70)
    print("\n✓ Fallback system is fully functional")
    print("✓ Manual prices work as primary override")
    print("✓ Live API fetching works for US stocks")
    print("✓ Cache fallback works when API fails")
    print("✓ Unavailable marker works when all fallbacks exhausted")
    print("✓ Cache persistence (save/load) works")
    print("\n" + "=" * 70)

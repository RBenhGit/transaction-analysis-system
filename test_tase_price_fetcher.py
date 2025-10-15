"""
Test TASE price fetching functionality.

This script tests the enhanced price_fetcher.py with TASE support.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modules.portfolio_dashboard.price_fetcher import (
    fetch_current_price,
    _fetch_tase_price_yahoo,
    PriceData
)

def test_tase_price_fetching():
    """Test TASE stock price fetching."""
    print("=" * 60)
    print("Testing TASE Price Fetcher")
    print("=" * 60)

    # Test popular TASE stocks
    tase_stocks = [
        ("NICE", "Nice Systems"),
        ("TEVA", "Teva Pharmaceutical"),
        ("CHEK", "Check Point Software"),
    ]

    print("\n[TASE] Testing TASE Stocks (Yahoo Finance with .TA suffix):\n")

    for symbol, name in tase_stocks:
        print(f"Testing {name} ({symbol})...")
        price = fetch_current_price(symbol, currency="₪")

        if price:
            print(f"  [OK] SUCCESS: {symbol} = ILS {price:.2f}")
        else:
            print(f"  [FAIL] FAILED: Could not fetch price for {symbol}")
        print()

    # Test USD stock for comparison
    print("\n[USD] Testing USD Stock (control test):\n")
    print("Testing Apple (AAPL)...")
    usd_price = fetch_current_price("AAPL", currency="$")

    if usd_price:
        print(f"  [OK] SUCCESS: AAPL = ${usd_price:.2f}")
    else:
        print(f"  [FAIL] FAILED: Could not fetch price for AAPL")

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


def test_price_data_class():
    """Test PriceData metadata tracking."""
    print("\n" + "=" * 60)
    print("Testing PriceData Class")
    print("=" * 60)

    # Create sample price data
    price_data = PriceData(
        price=150.50,
        source="tase_yahoo",
        symbol="NICE",
        currency="₪"
    )

    print(f"\nPriceData object created:")
    print(f"  Symbol: {price_data.symbol}")
    print(f"  Price: ILS {price_data.price:.2f}")
    print(f"  Source: {price_data.source}")
    print(f"  Timestamp: {price_data.timestamp}")
    print(f"  Is Stale: {price_data.is_stale}")

    # Convert to dict
    price_dict = price_data.to_dict()
    print(f"\nSerialized to dict:")
    for key, value in price_dict.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\n[START] Starting TASE Price Fetcher Tests\n")

    # Run tests
    test_tase_price_fetching()
    test_price_data_class()

    print("\n[COMPLETE] All tests completed!\n")

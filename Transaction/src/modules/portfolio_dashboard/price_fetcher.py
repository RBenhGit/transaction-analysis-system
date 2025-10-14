"""
Stock Price Fetcher with Best Practices.

Implements robust API calls with:
- Retry logic with exponential backoff
- Proper error handling and logging
- Rate limiting protection
- Timeout handling
- Input validation
"""

import yfinance as yf
from typing import Dict, Optional, List
import streamlit as st
import time
import logging
from functools import wraps


# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Configuration constants
CACHE_TTL = 600  # 10 minutes
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0  # seconds
MAX_RETRY_DELAY = 10.0  # seconds
REQUEST_TIMEOUT = 10  # seconds
RATE_LIMIT_DELAY = 0.5  # seconds between requests


class PriceFetchError(Exception):
    """Custom exception for price fetching errors."""
    pass


def retry_with_backoff(max_retries: int = MAX_RETRIES):
    """
    Decorator for retry logic with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = INITIAL_RETRY_DELAY
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Don't retry on specific errors
                    if "404" in str(e) or "delisted" in str(e).lower():
                        logger.debug(f"Symbol not found, skipping retries: {e}")
                        return None

                    # If rate limited, wait longer
                    if "429" in str(e) or "Too Many Requests" in str(e):
                        delay = min(delay * 2, MAX_RETRY_DELAY)
                        logger.warning(f"Rate limited, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                    else:
                        logger.debug(f"Attempt {attempt + 1}/{max_retries} failed: {e}")

                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay = min(delay * 2, MAX_RETRY_DELAY)

            # All retries exhausted
            logger.error(f"All {max_retries} attempts failed: {last_exception}")
            return None

        return wrapper
    return decorator


@st.cache_data(ttl=CACHE_TTL)
@retry_with_backoff(max_retries=MAX_RETRIES)
def fetch_current_price(symbol: str, currency: str = "$") -> Optional[float]:
    """
    Fetch current stock price for a single symbol with robust error handling.

    Args:
        symbol: Stock ticker symbol
        currency: Currency symbol ("$" for USD, "₪" for NIS)

    Returns:
        Current price as float, or None if fetch fails

    Raises:
        PriceFetchError: If critical error occurs during fetch
    """
    # Skip TASE stocks (not supported by Yahoo Finance)
    if currency == "₪":
        return None

    # Validate symbol
    if not symbol or not isinstance(symbol, str):
        logger.error(f"Invalid symbol: {symbol}")
        return None

    try:
        # Create ticker object
        ticker = yf.Ticker(symbol)

        # Fetch historical data with timeout
        hist = ticker.history(period="1d", timeout=REQUEST_TIMEOUT)

        # Validate response
        if hist is None or hist.empty:
            logger.debug(f"No data returned for {symbol}")
            return None

        # Extract closing price
        close_price = hist['Close'].iloc[-1]

        # Validate price
        if close_price is None or close_price <= 0:
            logger.warning(f"Invalid price for {symbol}: {close_price}")
            return None

        return float(close_price)

    except IndexError as e:
        logger.debug(f"No price data for {symbol}: {e}")
        return None
    except ValueError as e:
        logger.error(f"Value error for {symbol}: {e}")
        return None
    except Exception as e:
        # Log unexpected errors but don't crash
        logger.error(f"Unexpected error fetching {symbol}: {type(e).__name__}: {e}")
        raise  # Re-raise for retry decorator


@st.cache_data(ttl=CACHE_TTL)
def fetch_multiple_prices_batch(
    symbols: List[str],
    currency: str = "$",
    progress_callback=None
) -> Dict[str, Optional[float]]:
    """
    Fetch prices for multiple symbols with rate limiting and progress tracking.

    Args:
        symbols: List of stock ticker symbols
        currency: Currency for all symbols
        progress_callback: Optional callback function for progress updates

    Returns:
        Dictionary mapping symbol to price (or None if fetch failed)
    """
    prices = {}

    # Skip if empty or NIS
    if not symbols or currency == "₪":
        return {symbol: None for symbol in symbols}

    total = len(symbols)
    logger.info(f"Fetching prices for {total} {currency} symbols")

    for i, symbol in enumerate(symbols):
        # Rate limiting delay (except first request)
        if i > 0:
            time.sleep(RATE_LIMIT_DELAY)

        # Fetch price
        try:
            price = fetch_current_price(symbol, currency)
            prices[symbol] = price

            if price:
                logger.debug(f"✓ {symbol}: ${price:.2f}")
            else:
                logger.debug(f"✗ {symbol}: No price")

        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            prices[symbol] = None

        # Update progress
        if progress_callback:
            progress_callback((i + 1) / total)

    # Log summary
    successful = sum(1 for p in prices.values() if p is not None)
    logger.info(f"Price fetch complete: {successful}/{total} successful")

    return prices


@st.cache_data(ttl=CACHE_TTL)
def fetch_multiple_prices(positions: list) -> Dict[str, Optional[float]]:
    """
    Fetch current prices for multiple positions grouped by currency.

    Args:
        positions: List of Position objects with security_symbol and currency

    Returns:
        Dictionary mapping symbol to current price
    """
    if not positions:
        return {}

    prices = {}

    # Group positions by currency
    usd_symbols = [pos.security_symbol for pos in positions if pos.currency == "$"]
    nis_symbols = [pos.security_symbol for pos in positions if pos.currency == "₪"]

    # Fetch USD prices
    if usd_symbols:
        logger.info(f"Fetching prices for {len(usd_symbols)} USD stocks")
        usd_prices = fetch_multiple_prices_batch(usd_symbols, "$")
        prices.update(usd_prices)

    # Skip NIS (not supported)
    if nis_symbols:
        logger.info(f"Skipping {len(nis_symbols)} NIS stocks (TASE not supported)")
        for symbol in nis_symbols:
            prices[symbol] = None

    return prices


def update_positions_with_prices(positions: list) -> list:
    """
    Update position objects with current market prices.

    Args:
        positions: List of Position objects

    Returns:
        Updated list of Position objects with current_price and market_value set
    """
    if not positions:
        return positions

    try:
        # Fetch all prices
        prices = fetch_multiple_prices(positions)

        # Update each position
        updated_count = 0
        for pos in positions:
            price = prices.get(pos.security_symbol)

            if price and price > 0:
                pos.current_price = price
                pos.market_value = pos.quantity * price
                updated_count += 1

        logger.info(f"Updated {updated_count}/{len(positions)} positions with current prices")

    except Exception as e:
        logger.error(f"Error updating positions with prices: {e}")
        # Don't fail - just leave prices as None

    return positions


def clear_price_cache():
    """Clear the price cache (useful for manual refresh)."""
    try:
        fetch_current_price.clear()
        fetch_multiple_prices_batch.clear()
        fetch_multiple_prices.clear()
        logger.info("Price cache cleared")
    except Exception as e:
        logger.warning(f"Error clearing cache: {e}")


def get_cache_status() -> Dict[str, any]:
    """
    Get information about the cache status.

    Returns:
        Dictionary with cache statistics
    """
    return {
        "cache_ttl_seconds": CACHE_TTL,
        "cache_ttl_minutes": CACHE_TTL / 60,
        "max_retries": MAX_RETRIES,
        "rate_limit_delay_seconds": RATE_LIMIT_DELAY,
        "request_timeout_seconds": REQUEST_TIMEOUT
    }

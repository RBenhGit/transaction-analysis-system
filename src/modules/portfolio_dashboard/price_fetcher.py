"""
Stock Price Fetcher with Best Practices.

Implements robust API calls with:
- Retry logic with exponential backoff
- Proper error handling and logging
- Rate limiting protection
- Timeout handling
- Input validation
- TASE (Tel Aviv Stock Exchange) support
- Multiple data source fallback
"""

import yfinance as yf
from typing import Dict, Optional, List, Literal
import streamlit as st
import time
import logging
from functools import wraps
from datetime import datetime, timedelta
import requests
import json
from pathlib import Path
from .tase_symbol_mapper import translate_tase_symbol, is_tase_numeric_id, is_hebrew_name


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

# TASE-specific configuration
TASE_CACHE_TTL = 3600  # 1 hour for TASE prices (less frequent updates)
PRICE_STALENESS_THRESHOLD = 86400  # 24 hours in seconds

# Data source priorities
DataSource = Literal["yfinance", "tase_yahoo", "manual", "last_known", "unavailable"]

# Price cache storage
_price_cache: Dict[str, 'PriceData'] = {}
_manual_prices: Dict[str, float] = {}

# Cache file path
CACHE_DIR = Path(__file__).parent.parent.parent.parent / "output" / "cache"
PRICE_CACHE_FILE = CACHE_DIR / "price_cache.json"
MANUAL_PRICE_FILE = CACHE_DIR / "manual_prices.json"


class PriceFetchError(Exception):
    """Custom exception for price fetching errors."""
    pass


class PriceData:
    """
    Container for price data with metadata.

    Attributes:
        price: The stock price (float or None)
        source: Data source used to fetch the price
        timestamp: When the price was fetched
        is_stale: Whether the price is older than staleness threshold
        symbol: Stock symbol
        currency: Currency of the price
    """
    def __init__(
        self,
        price: Optional[float],
        source: DataSource,
        symbol: str,
        currency: str = "$",
        timestamp: Optional[datetime] = None
    ):
        self.price = price
        self.source = source
        self.symbol = symbol
        self.currency = currency
        self.timestamp = timestamp or datetime.now()
        self.is_stale = self._check_staleness()

    def _check_staleness(self) -> bool:
        """Check if price is stale (older than threshold)."""
        if self.price is None:
            return True
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > PRICE_STALENESS_THRESHOLD

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "price": self.price,
            "source": self.source,
            "symbol": self.symbol,
            "currency": self.currency,
            "timestamp": self.timestamp.isoformat(),
            "is_stale": self.is_stale
        }


# ============================================================================
# Price Cache and Fallback Functions
# ============================================================================

def _cache_price(symbol: str, price_data: PriceData) -> None:
    """
    Cache price data for fallback use.

    Args:
        symbol: Stock symbol
        price_data: PriceData object to cache
    """
    _price_cache[symbol] = price_data
    logger.debug(f"Cached price for {symbol}: {price_data.price}")


def _get_cached_price(symbol: str) -> Optional[PriceData]:
    """
    Retrieve cached price data.

    Args:
        symbol: Stock symbol

    Returns:
        Cached PriceData or None if not found
    """
    return _price_cache.get(symbol)


def set_manual_price(symbol: str, price: float, currency: str = "$") -> PriceData:
    """
    Set a manual price for a symbol (user override).

    Args:
        symbol: Stock symbol
        price: Manual price value
        currency: Currency symbol

    Returns:
        PriceData object with manual price
    """
    _manual_prices[symbol] = price

    price_data = PriceData(
        price=price,
        source="manual",
        symbol=symbol,
        currency=currency
    )

    # Cache the manual price
    _cache_price(symbol, price_data)

    logger.info(f"Manual price set for {symbol}: {currency}{price:.2f}")
    return price_data


def get_manual_price(symbol: str) -> Optional[float]:
    """
    Retrieve manually set price for a symbol.

    Args:
        symbol: Stock symbol

    Returns:
        Manual price or None if not set
    """
    return _manual_prices.get(symbol)


def clear_manual_price(symbol: str) -> bool:
    """
    Clear manual price for a symbol.

    Args:
        symbol: Stock symbol

    Returns:
        True if price was cleared, False if not found
    """
    if symbol in _manual_prices:
        del _manual_prices[symbol]
        logger.info(f"Manual price cleared for {symbol}")
        return True
    return False


def fetch_with_fallback(
    symbol: str,
    currency: str = "$",
    allow_stale: bool = True
) -> PriceData:
    """
    Fetch price with comprehensive fallback mechanism.

    Fallback order:
    1. Manual price (if set)
    2. Live price from API
    3. Cached price (last known)
    4. Unavailable

    Args:
        symbol: Stock symbol
        currency: Currency symbol
        allow_stale: Whether to allow stale cached prices as fallback

    Returns:
        PriceData object with price and source information
    """
    # Fallback 1: Check for manual price first
    manual_price = get_manual_price(symbol)
    if manual_price is not None:
        logger.debug(f"Using manual price for {symbol}")
        return PriceData(
            price=manual_price,
            source="manual",
            symbol=symbol,
            currency=currency
        )

    # Fallback 2: Try to fetch live price
    try:
        live_price = fetch_current_price(symbol, currency)

        if live_price is not None:
            price_data = PriceData(
                price=live_price,
                source="tase_yahoo" if currency == "₪" else "yfinance",
                symbol=symbol,
                currency=currency
            )
            # Cache successful fetch
            _cache_price(symbol, price_data)
            return price_data

    except Exception as e:
        logger.warning(f"Live price fetch failed for {symbol}: {e}")

    # Fallback 3: Use cached price (last known)
    if allow_stale:
        cached_price = _get_cached_price(symbol)
        if cached_price is not None:
            logger.info(f"Using cached price for {symbol} (age: {cached_price.timestamp})")
            # Update source to indicate it's from cache
            cached_price.source = "last_known"
            return cached_price

    # Fallback 4: Price unavailable
    logger.warning(f"No price available for {symbol} (all fallbacks exhausted)")
    return PriceData(
        price=None,
        source="unavailable",
        symbol=symbol,
        currency=currency
    )


# ============================================================================
# Cache Persistence Functions
# ============================================================================

def save_price_cache() -> bool:
    """
    Save price cache to JSON file for persistence.

    Returns:
        True if save successful, False otherwise
    """
    try:
        # Create cache directory if it doesn't exist
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Convert PriceData objects to dictionaries
        cache_data = {
            symbol: price_data.to_dict()
            for symbol, price_data in _price_cache.items()
        }

        # Write to file
        with open(PRICE_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)

        logger.info(f"Price cache saved: {len(cache_data)} entries")
        return True

    except Exception as e:
        logger.error(f"Error saving price cache: {e}")
        return False


def load_price_cache() -> bool:
    """
    Load price cache from JSON file.

    Returns:
        True if load successful, False otherwise
    """
    try:
        if not PRICE_CACHE_FILE.exists():
            logger.info("No price cache file found")
            return False

        with open(PRICE_CACHE_FILE, 'r') as f:
            cache_data = json.load(f)

        # Convert dictionaries back to PriceData objects
        for symbol, data in cache_data.items():
            _price_cache[symbol] = PriceData(
                price=data['price'],
                source=data['source'],
                symbol=data['symbol'],
                currency=data['currency'],
                timestamp=datetime.fromisoformat(data['timestamp'])
            )

        logger.info(f"Price cache loaded: {len(_price_cache)} entries")
        return True

    except Exception as e:
        logger.error(f"Error loading price cache: {e}")
        return False


def save_manual_prices() -> bool:
    """
    Save manual prices to JSON file for persistence.

    Returns:
        True if save successful, False otherwise
    """
    try:
        # Create cache directory if it doesn't exist
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(MANUAL_PRICE_FILE, 'w') as f:
            json.dump(_manual_prices, f, indent=2)

        logger.info(f"Manual prices saved: {len(_manual_prices)} entries")
        return True

    except Exception as e:
        logger.error(f"Error saving manual prices: {e}")
        return False


def load_manual_prices() -> bool:
    """
    Load manual prices from JSON file.

    Returns:
        True if load successful, False otherwise
    """
    try:
        if not MANUAL_PRICE_FILE.exists():
            logger.info("No manual prices file found")
            return False

        with open(MANUAL_PRICE_FILE, 'r') as f:
            loaded_prices = json.load(f)

        _manual_prices.update(loaded_prices)

        logger.info(f"Manual prices loaded: {len(_manual_prices)} entries")
        return True

    except Exception as e:
        logger.error(f"Error loading manual prices: {e}")
        return False


def initialize_cache() -> None:
    """
    Initialize cache by loading from persistent storage.
    Call this at application startup.
    """
    logger.info("Initializing price cache...")
    load_price_cache()
    load_manual_prices()


def cleanup_cache() -> None:
    """
    Save cache and clean up at application shutdown.
    """
    logger.info("Cleaning up price cache...")
    save_price_cache()
    save_manual_prices()


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


@retry_with_backoff(max_retries=MAX_RETRIES)
def _fetch_tase_price_yahoo(symbol: str) -> Optional[float]:
    """
    Fetch TASE stock price using Yahoo Finance.

    Supports multiple TASE symbol formats:
    - Hebrew names (e.g., "מזטפ") → Translated to numeric ID + .TA
    - Numeric TASE IDs (e.g., "695437") → Appends .TA
    - Already formatted (e.g., "695437.TA") → Used as-is

    Args:
        symbol: TASE stock symbol (Hebrew name, numeric ID, or Yahoo format)

    Returns:
        Current price in ILS (Shekels), or None if fetch fails
    """
    try:
        # Translate symbol to Yahoo Finance format
        yahoo_symbol = translate_tase_symbol(symbol)

        if yahoo_symbol is None:
            logger.warning(f"Could not translate TASE symbol: {symbol}")
            # Fallback: try adding .TA suffix if it's not already there
            yahoo_symbol = f"{symbol}.TA" if not symbol.endswith('.TA') else symbol

        logger.debug(f"Fetching TASE price: {symbol} → {yahoo_symbol}")

        ticker = yf.Ticker(yahoo_symbol)
        hist = ticker.history(period="1d", timeout=REQUEST_TIMEOUT)

        if hist is None or hist.empty:
            logger.debug(f"No TASE data for {yahoo_symbol} (original: {symbol})")
            return None

        close_price = hist['Close'].iloc[-1]

        if close_price is None or close_price <= 0:
            logger.warning(f"Invalid TASE price for {yahoo_symbol}: {close_price}")
            return None

        logger.info(f"✓ Fetched TASE price for {yahoo_symbol}: ₪{close_price:.2f}")
        return float(close_price)

    except Exception as e:
        logger.debug(f"TASE Yahoo fetch failed for {symbol}: {e}")
        return None


@st.cache_data(ttl=CACHE_TTL)
@retry_with_backoff(max_retries=MAX_RETRIES)
def fetch_current_price(symbol: str, currency: str = "$") -> Optional[float]:
    """
    Fetch current stock price for a single symbol with robust error handling.

    Supports both US stocks (via yfinance) and TASE stocks (via yfinance with .TA suffix).

    Args:
        symbol: Stock ticker symbol
        currency: Currency symbol ("$" for USD, "₪" for NIS)

    Returns:
        Current price as float, or None if fetch fails

    Raises:
        PriceFetchError: If critical error occurs during fetch
    """
    # Validate symbol
    if not symbol or not isinstance(symbol, str):
        logger.error(f"Invalid symbol: {symbol}")
        return None

    # Route to appropriate fetcher based on currency
    if currency == "₪":
        return _fetch_tase_price_yahoo(symbol)

    # US stocks - standard yfinance
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

    Supports both USD and ILS (TASE) stocks.

    Args:
        symbols: List of stock ticker symbols
        currency: Currency for all symbols ("$" for USD, "₪" for ILS)
        progress_callback: Optional callback function for progress updates

    Returns:
        Dictionary mapping symbol to price (or None if fetch failed)
    """
    prices = {}

    # Skip if empty
    if not symbols:
        return {}

    total = len(symbols)
    currency_name = "TASE" if currency == "₪" else "USD"
    logger.info(f"Fetching prices for {total} {currency_name} symbols")

    for i, symbol in enumerate(symbols):
        # Rate limiting delay (except first request)
        if i > 0:
            time.sleep(RATE_LIMIT_DELAY)

        # Fetch price
        try:
            price = fetch_current_price(symbol, currency)
            prices[symbol] = price

            if price:
                currency_symbol = currency
                logger.debug(f"✓ {symbol}: {currency_symbol}{price:.2f}")
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
    logger.info(f"Price fetch complete: {successful}/{total} successful ({currency_name})")

    return prices


@st.cache_data(ttl=CACHE_TTL)
def fetch_multiple_prices(positions: list) -> Dict[str, Optional[float]]:
    """
    Fetch current prices for multiple positions grouped by currency.

    Supports both USD and TASE (ILS) stocks.

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

    # Fetch TASE (NIS) prices
    if nis_symbols:
        logger.info(f"Fetching prices for {len(nis_symbols)} TASE (ILS) stocks")
        nis_prices = fetch_multiple_prices_batch(nis_symbols, "₪")
        prices.update(nis_prices)

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

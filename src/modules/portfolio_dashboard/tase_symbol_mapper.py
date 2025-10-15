"""
TASE Symbol Mapping Utility.

Converts TASE stock identifiers (Hebrew names or numeric IDs) to Yahoo Finance format.
TASE stocks on Yahoo Finance use the format: NUMERIC_ID.TA

For example:
- Hebrew name "מזטפ" (Mizrahi Tefahot) → 695437.TA
- Numeric ID "695437" → 695437.TA
- US stock "MSFT" → "MSFT" (no change)
"""

import logging
from typing import Optional, Dict
import re

logger = logging.getLogger(__name__)

# Known TASE stock mappings: Hebrew name → Numeric TASE ID
# This can be expanded by reading from nis_stock_identifiers.csv
TASE_SYMBOL_MAP: Dict[str, str] = {
    # Common TASE stocks from nis_stock_identifiers.csv
    "סקופ": "288019",      # Scopus
    "פמס": "315010",       # FIMI
    "מטרקס": "445015",     # Matrix
    "מטריקס": "445015",    # Matrix (alternate spelling)
    "מחשר": "507012",      # Ituran
    "מיחשוב ישר קב": "507012",  # Ituran (full name)
    "מזטפ": "695437",      # Mizrahi Tefahot
    "מזרחי טפחות": "695437",  # Mizrahi Tefahot (full name)
    "קלטו": "1083955",     # Qualitau
    "קווליטאו": "1083955",  # Qualitau (alternate)
    "אטרא": "1096106",     # Atara
    "אטראו שוקי הון": "1096106",  # Atara (full name)
    "נקסנ": "1176593",     # Next Vision
    "נקסט ויז'ן": "1176593",  # Next Vision (full name)
}


def is_tase_numeric_id(symbol: str) -> bool:
    """
    Check if a symbol is a numeric TASE ID.

    TASE IDs are typically 5-8 digit numbers.

    Args:
        symbol: Stock symbol to check

    Returns:
        True if symbol appears to be a numeric TASE ID
    """
    if not symbol:
        return False

    # Remove whitespace
    symbol_clean = symbol.strip()

    # Check if it's a 5-8 digit number
    return bool(re.match(r'^\d{5,8}$', symbol_clean))


def is_hebrew_name(symbol: str) -> bool:
    """
    Check if a symbol contains Hebrew characters.

    Args:
        symbol: Stock symbol to check

    Returns:
        True if symbol contains Hebrew characters
    """
    if not symbol:
        return False

    # Hebrew Unicode range: U+0590 to U+05FF
    return bool(re.search(r'[\u0590-\u05FF]', symbol))


def is_us_stock_symbol(symbol: str) -> bool:
    """
    Check if a symbol appears to be a US stock ticker.

    US symbols are typically:
    - 1-5 uppercase letters
    - May contain periods (e.g., BRK.B)

    Args:
        symbol: Stock symbol to check

    Returns:
        True if symbol appears to be a US stock ticker
    """
    if not symbol:
        return False

    symbol_clean = symbol.strip()

    # Check for typical US stock format
    # Examples: AAPL, MSFT, BRK.B, V US, GOOG US
    us_pattern = r'^[A-Z]{1,5}(\.[A-Z])?(\s+US)?$'
    return bool(re.match(us_pattern, symbol_clean, re.IGNORECASE))


def translate_tase_symbol(symbol: str) -> Optional[str]:
    """
    Translate a TASE symbol to Yahoo Finance format.

    Handles three cases:
    1. Hebrew name → Look up numeric ID → Add .TA suffix
    2. Numeric TASE ID → Add .TA suffix
    3. US stock symbol → Return unchanged

    Args:
        symbol: Stock symbol (Hebrew name, numeric ID, or US ticker)

    Returns:
        Yahoo Finance compatible symbol, or None if translation fails

    Examples:
        >>> translate_tase_symbol("מזטפ")
        "695437.TA"

        >>> translate_tase_symbol("695437")
        "695437.TA"

        >>> translate_tase_symbol("MSFT")
        "MSFT"
    """
    if not symbol:
        logger.warning("Empty symbol provided for translation")
        return None

    symbol_clean = symbol.strip()

    # Case 1: US stock symbol - return unchanged
    if is_us_stock_symbol(symbol_clean):
        logger.debug(f"US stock detected: {symbol_clean}")
        return symbol_clean

    # Case 2: Hebrew name - translate to numeric ID
    if is_hebrew_name(symbol_clean):
        # Try direct lookup
        if symbol_clean in TASE_SYMBOL_MAP:
            numeric_id = TASE_SYMBOL_MAP[symbol_clean]
            yahoo_symbol = f"{numeric_id}.TA"
            logger.debug(f"Translated Hebrew name '{symbol_clean}' → {yahoo_symbol}")
            return yahoo_symbol
        else:
            logger.warning(f"Hebrew symbol '{symbol_clean}' not found in mapping")
            return None

    # Case 3: Numeric TASE ID - add .TA suffix
    if is_tase_numeric_id(symbol_clean):
        yahoo_symbol = f"{symbol_clean}.TA"
        logger.debug(f"Translated numeric TASE ID {symbol_clean} → {yahoo_symbol}")
        return yahoo_symbol

    # Unknown format
    logger.warning(f"Unknown symbol format: '{symbol_clean}'")
    return None


def load_tase_mapping_from_csv(csv_path: str) -> Dict[str, str]:
    """
    Load TASE symbol mappings from CSV file.

    Expected CSV format:
    מספר נייר,סימבול
    288019,סקופ

    Args:
        csv_path: Path to nis_stock_identifiers.csv

    Returns:
        Dictionary mapping Hebrew name → numeric TASE ID
    """
    import pandas as pd

    try:
        df = pd.read_csv(csv_path, encoding='utf-8')

        # Build mapping: symbol (Hebrew) → numeric ID
        mapping = {}
        for _, row in df.iterrows():
            numeric_id = str(row.get('מספר נייר', '')).strip()
            hebrew_symbol = str(row.get('סימבול', '')).strip()

            if numeric_id and hebrew_symbol:
                mapping[hebrew_symbol] = numeric_id
                logger.debug(f"Loaded mapping: {hebrew_symbol} → {numeric_id}")

        logger.info(f"Loaded {len(mapping)} TASE symbol mappings from {csv_path}")
        return mapping

    except Exception as e:
        logger.error(f"Error loading TASE mappings from {csv_path}: {e}")
        return {}


def update_mapping_from_csv(csv_path: str = None):
    """
    Update the global TASE_SYMBOL_MAP from CSV file.

    Args:
        csv_path: Optional path to CSV file. If None, uses default location.
    """
    if csv_path is None:
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent.parent
        csv_path = project_root / "nis_stock_identifiers.csv"

    new_mappings = load_tase_mapping_from_csv(str(csv_path))
    TASE_SYMBOL_MAP.update(new_mappings)
    logger.info(f"Updated TASE symbol mapping: {len(TASE_SYMBOL_MAP)} total entries")


def get_symbol_info(symbol: str) -> Dict[str, any]:
    """
    Get diagnostic information about a symbol.

    Useful for debugging symbol translation issues.

    Args:
        symbol: Stock symbol to analyze

    Returns:
        Dictionary with symbol type and translation info
    """
    return {
        "original_symbol": symbol,
        "is_hebrew": is_hebrew_name(symbol),
        "is_numeric_tase_id": is_tase_numeric_id(symbol),
        "is_us_stock": is_us_stock_symbol(symbol),
        "translated_symbol": translate_tase_symbol(symbol),
        "in_mapping": symbol in TASE_SYMBOL_MAP if is_hebrew_name(symbol) else None
    }


# Auto-load mappings on import (optional)
# Uncomment if you want to automatically load from CSV
# try:
#     update_mapping_from_csv()
# except Exception as e:
#     logger.warning(f"Could not auto-load TASE mappings: {e}")

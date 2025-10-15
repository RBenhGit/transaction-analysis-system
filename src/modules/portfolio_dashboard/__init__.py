"""
Portfolio Dashboard Module

Simple chronological portfolio builder that processes transactions
to show current asset holdings with current market prices.
Includes portfolio validation against actual broker positions.
"""

from .position import Position
from .builder import PortfolioBuilder
from .actual_loader import ActualPortfolioLoader
from .view import (
    display_portfolio,
    display_portfolio_by_currency,
    display_validation_results
)
from .price_fetcher import (
    fetch_current_price,
    update_positions_with_prices,
    clear_price_cache,
    get_cache_status
)
from .validator import (
    PortfolioValidator,
    ValidationResult,
    PositionDiscrepancy,
    DiscrepancyType
)

__all__ = [
    'Position',
    'PortfolioBuilder',
    'ActualPortfolioLoader',
    'display_portfolio',
    'display_portfolio_by_currency',
    'display_validation_results',
    'fetch_current_price',
    'update_positions_with_prices',
    'clear_price_cache',
    'get_cache_status',
    'PortfolioValidator',
    'ValidationResult',
    'PositionDiscrepancy',
    'DiscrepancyType'
]

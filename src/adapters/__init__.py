"""
Bank/Broker Adapters Package

This package contains adapters for different bank and broker formats.
Each adapter handles the specific column mappings and data transformations
for its institution.
"""

from .base_adapter import BaseAdapter
from .ibi_adapter import IBIAdapter

__all__ = ['BaseAdapter', 'IBIAdapter']

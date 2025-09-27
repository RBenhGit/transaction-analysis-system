"""
Modules Package for Transaction Analysis System

This package contains feature modules that extend the core functionality
of the Transaction Analysis System. Each module should be self-contained
and follow the established coding standards.

Available Modules:
- analytics: Data analysis and statistical functions
- visualization: Chart and graph generation
- reporting: Report generation and formatting
- web_interface: Web-based user interface components
- database: Database integration and management

Module Development Guidelines:
1. Each module must be in its own subdirectory
2. Include __init__.py, README.md, and appropriate tests
3. Follow PEP 8 coding standards
4. Can import from src/ but not from other modules/
5. Include comprehensive docstrings and type hints
"""

__version__ = "1.0.0"
__author__ = "Transaction Analysis System"

# Module registry for dynamic loading
AVAILABLE_MODULES = [
    "analytics",
    "visualization",
    "reporting",
    "web_interface",
    "database"
]

def get_available_modules():
    """
    Get list of available modules in this package.

    Returns:
        List[str]: Available module names
    """
    return AVAILABLE_MODULES.copy()

def is_module_available(module_name: str) -> bool:
    """
    Check if a specific module is available.

    Args:
        module_name: Name of the module to check

    Returns:
        bool: True if module is available, False otherwise
    """
    return module_name in AVAILABLE_MODULES
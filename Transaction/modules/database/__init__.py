"""
Database Module for Transaction Analysis System

This module provides database integration and management capabilities for persistent
storage of transaction data, analysis results, and system configurations.

Available Components:
- database_manager: Core database operations
- migration_manager: Database schema migrations
- query_builder: SQL query construction and execution
- backup_manager: Database backup and restore operations

Supported Databases:
- SQLite: Default local database
- PostgreSQL: Production database option
- MySQL: Alternative production database
- MongoDB: NoSQL option for flexible schemas

Features:
- Transaction data persistence
- Analysis result caching
- User configuration storage
- Historical data archiving
- Query optimization and indexing

Usage:
    from modules.database import DatabaseManager

    db = DatabaseManager()
    db.save_transactions(transaction_data)
    results = db.query_transactions(date_range=(start, end))
"""

__version__ = "1.0.0"
__author__ = "Transaction Analysis System"

# Module metadata
MODULE_NAME = "database"
MODULE_DESCRIPTION = "Database integration and management"
DEPENDENCIES = ["sqlite3", "sqlalchemy", "psycopg2", "pymongo"]

def get_module_info():
    """Get information about this module."""
    return {
        "name": MODULE_NAME,
        "version": __version__,
        "description": MODULE_DESCRIPTION,
        "dependencies": DEPENDENCIES
    }
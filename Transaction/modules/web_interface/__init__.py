"""
Web Interface Module for Transaction Analysis System

This module provides web-based user interface components for the transaction analysis system.
It includes both backend API endpoints and frontend components for web-based interaction.

Available Components:
- api_server: Flask/FastAPI backend server
- web_dashboard: Main dashboard interface
- upload_handler: File upload and processing interface
- export_interface: Data export and download interface

Supported Features:
- File upload and processing via web interface
- Interactive data visualization in browser
- Real-time analysis results display
- Export functionality for reports and data
- RESTful API for external integrations

Technology Stack:
- Backend: Flask or FastAPI
- Frontend: HTML/CSS/JavaScript with modern frameworks
- Database: SQLite for session storage
- Charts: Chart.js or D3.js for interactive visualizations

Usage:
    from modules.web_interface import WebServer

    server = WebServer()
    server.run(host='localhost', port=8080)
"""

__version__ = "1.0.0"
__author__ = "Transaction Analysis System"

# Module metadata
MODULE_NAME = "web_interface"
MODULE_DESCRIPTION = "Web-based user interface components"
DEPENDENCIES = ["flask", "fastapi", "jinja2", "requests"]

def get_module_info():
    """Get information about this module."""
    return {
        "name": MODULE_NAME,
        "version": __version__,
        "description": MODULE_DESCRIPTION,
        "dependencies": DEPENDENCIES
    }
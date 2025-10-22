"""Streamlit multi‑page application for GCC oil forecasting.

Importing this package initialises the available Streamlit pages.  See the
individual modules for page implementations.
"""

# Expose pages to Streamlit's multipage app loader by referencing them here.
from .Home import run as _home  # noqa: F401
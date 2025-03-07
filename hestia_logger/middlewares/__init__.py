"""
Hestia Logger - Middlewares Module.

Provides middleware for request logging in web frameworks.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

# Define public API for `middlewares`
__all__ = ["middleware"]

# Expose middleware module
from .middleware import middleware

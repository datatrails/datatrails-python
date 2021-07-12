""" Type aliases used for identifying complex input and return types for RKVST

TODO: Create more explicit type aliases, Current type aliases default to
Dict[Unknown, Unknown] and List[Unknown].  Minimising the potential effectiveness of
the type hinting.

- Look at TypedDict for explicit formatting of dictionaries
"""

from typing import Optional

NoneOnError = Optional
"""Means the function returns None if a Error occurs upstream"""

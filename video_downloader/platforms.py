"""
Platform definitions and detection for supported video sites.

Re-exports platform URL patterns from utils for external use.
Referenced by README.md in the project structure diagram.
"""

from .utils import PLATFORM_PATTERNS, detect_platform

__all__ = ["PLATFORM_PATTERNS", "detect_platform"]

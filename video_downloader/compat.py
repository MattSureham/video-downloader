"""
Cross-platform compatibility module.

Provides Windows/Unix compatibility utilities:
- Terminal initialization (colorama, UTF-8 console)
- Safe filename sanitization (reserved names, MAX_PATH)
- Cross-platform path utilities
- Emoji-safe print helpers

Usage:
    from .compat import init_terminal, safe_filename, safe_print
    init_terminal()
    name = safe_filename("my:video?.mp4")
"""

import os
import re
import sys

# ============================================================================
# Platform Detection
# ============================================================================

IS_WINDOWS: bool = sys.platform == "win32"
IS_MACOS: bool = sys.platform == "darwin"
IS_LINUX: bool = sys.platform.startswith("linux")

# ============================================================================
# Windows Reserved Filenames
# ============================================================================
# Names that cannot be used as file/directory names on Windows,
# regardless of extension. Case-insensitive.

WINDOWS_RESERVED_NAMES: set = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5",
    "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
    "LPT6", "LPT7", "LPT8", "LPT9",
}

# Windows MAX_PATH.  260 chars is the safe common denominator
# (extended paths with \\? prefix allow 32,767 but are not universally supported).
WINDOWS_MAX_PATH: int = 260

# ============================================================================
# Terminal Initialization
# ============================================================================

_terminal_initialized: bool = False


def init_terminal() -> None:
    """Initialize terminal for cross-platform compatibility.

    On Windows:
    - Activates colorama for ANSI/VT escape code support.
    - Reconfigures stdout/stderr to UTF-8 encoding.
    - Enables virtual terminal processing on the console.

    On macOS/Linux: no-op (these already support ANSI natively).

    Call once at application startup, before any colored/emoji output.
    """
    global _terminal_initialized
    if _terminal_initialized:
        return

    if IS_WINDOWS:
        # --- Colorama: translate ANSI codes to Windows API calls ---
        try:
            import colorama
            colorama.init(autoreset=False, strip=False, convert=False)
        except ImportError:
            pass

        # --- UTF-8 stdout/stderr ---
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

        # --- Enable VT100 escape sequences on Windows console ---
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32

            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            ENABLE_PROCESSED_OUTPUT = 0x0001

            mode = ENABLE_PROCESSED_OUTPUT | ENABLE_VIRTUAL_TERMINAL_PROCESSING

            # STD_OUTPUT_HANDLE = -11, STD_ERROR_HANDLE = -12
            for std_handle in (-11, -12):
                handle = kernel32.GetStdHandle(std_handle)
                kernel32.SetConsoleMode(handle, mode)
        except Exception:
            pass

    _terminal_initialized = True


def is_unicode_capable() -> bool:
    """Check whether the current terminal can render Unicode properly.

    On Windows, only Windows Terminal (WT_SESSION env var exists)
    and UTF-8 code-page consoles are considered capable.
    """
    if IS_WINDOWS:
        if os.environ.get("WT_SESSION"):
            return True
        try:
            import locale
            return locale.getpreferredencoding().upper() in ("UTF-8", "UTF8")
        except Exception:
            return False
    return True


# ============================================================================
# Emoji-Aware Printing
# ============================================================================

# Emoji -> ASCII fallback table for common emoji used in this project
_EMOJI_MAP: dict = {
    "\U0001f3ac": "[VIDEO]",
    "\U0001f680": ">>>",
    "\U0001f4c1": "[DIR]",
    "\U0001f4c4": "[FILE]",
    "\U0001f4ca": "[STATS]",
    "✅": "[OK]",
    "❌": "[FAIL]",
    "\U0001f44b": "[BYE]",
    "\U0001f4cc": "[TITLE]",
    "\U0001f464": "[AUTHOR]",
    "⏱️": "[TIME]",
    "\U0001f441️": "[VIEWS]",
    "\U0001f4c5": "[DATE]",
    "\U0001f517": "[LINK]",
    "\U0001f5bc️": "[IMG]",
    "\U0001f4dd": "[DESC]",
    "\U0001f4cb": "[FORMATS]",
    "⚠️": "[WARN]",
    "\U0001f527": "[TOOLS]",
    "\U0001f3b5": "[AUDIO]",
    "\U0001f504": "[RETRY]",
    "\U0001f4e6": "[PACKAGE]",
    "\U0001f91d": "[CONTRIB]",
    "\U0001f64f": "[THANKS]",
    "\U0001f4e7": "[EMAIL]",
    "\U0001f50d": "[SEARCH]",
    "\U0001f3af": "[TARGET]",
    "\U0001f4a1": "[TIP]",
    "\U0001f525": "[HOT]",
    "✨": "[NEW]",
    "⏰": "[CLOCK]",
    "\U0001f4f9": "[CAM]",
}


def _fallback_emoji(text: str) -> str:
    """Replace emoji characters with ASCII fallback equivalents."""
    result = text
    for emoji, fallback in _EMOJI_MAP.items():
        result = result.replace(emoji, fallback)
    return result


def safe_print(*args, **kwargs) -> None:
    """Print text that degrades gracefully on terminals without Unicode.

    On terminals that support Unicode, behaves exactly like ``print()``.
    On Windows terminals without Unicode support, replaces emoji
    characters with ASCII fallback equivalents.

    Accepts the same keyword arguments as the built-in ``print()``
    (sep, end, file, flush).
    """
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    file = kwargs.get("file", None)
    flush = kwargs.get("flush", False)

    text_args = [str(a) for a in args]

    if not is_unicode_capable():
        text_args = [_fallback_emoji(a) for a in text_args]

    if file is not None:
        print(sep.join(text_args), end=end, file=file, flush=flush)
    else:
        print(sep.join(text_args), end=end, flush=flush)


# ============================================================================
# Safe Filename Sanitization
# ============================================================================


def _is_reserved_windows_name(name: str) -> bool:
    """Check if *name* is a Windows reserved filename (case-insensitive).

    Checks both the full name and the stem (name before the first dot),
    so ``CON.txt``, ``com1``, and ``lpt9`` are all caught.
    """
    upper = name.upper()
    checks = {upper}
    if "." in upper:
        checks.add(upper.split(".")[0])
    return bool(checks & WINDOWS_RESERVED_NAMES)


def safe_filename(
    filename: str,
    replace_spaces: bool = True,
    max_length: int = 255,
) -> str:
    """Create a platform-safe filename from *filename*.

    Sanitization steps (in order):

    1. Strip characters illegal on Windows (``<>:"/\\|?*`` and control chars).
    2. Optionally replace spaces with underscores.
    3. Collapse repeated underscores.
    4. Strip leading/trailing underscores and dots.
    5. Remove trailing dots and spaces (Windows-truncated silently).
    6. Handle Windows reserved names (CON, PRN, ...) by prefixing ``_``.
    7. Truncate to *max_length*, preserving the extension when possible.

    Args:
        filename: Raw filename, optionally with extension.
        replace_spaces: Replace spaces with underscores (default True).
        max_length: Maximum total filename length (default 255).

    Returns:
        A safe filename string. Never empty — falls back to ``"video"``.
    """
    # 1. Remove characters illegal on Windows
    illegal = r'[<>:"/\\|?*\x00-\x1f]'
    filename = re.sub(illegal, "", filename)

    # 2. Optional space -> underscore
    if replace_spaces:
        filename = filename.replace(" ", "_")

    # 3. Collapse multiple underscores
    filename = re.sub(r"_+", "_", filename)

    # 4. Strip leading/trailing underscores & dots
    filename = filename.strip("_.")

    # 5. Strip trailing dots & spaces (Windows drops these silently)
    filename = filename.rstrip(". ")

    # 6. Handle Windows reserved names
    if "." in filename:
        stem, ext = filename.rsplit(".", 1)
        if _is_reserved_windows_name(stem):
            stem = "_" + stem
            filename = f"{stem}.{ext}"
    elif _is_reserved_windows_name(filename):
        filename = "_" + filename

    # 7. Truncate, preserving extension when possible
    if len(filename) > max_length:
        if "." in filename:
            stem, ext = filename.rsplit(".", 1)
            max_stem = max_length - len(ext) - 1  # -1 for the dot
            if max_stem > 0:
                filename = f"{stem[:max_stem]}.{ext}"
            else:
                filename = filename[:max_length]
        else:
            filename = filename[:max_length]

    # 8. Fallback if everything was stripped
    if not filename:
        filename = "video"

    return filename


# ============================================================================
# Cross-Platform Path Utilities
# ============================================================================


def normalize_output_path(output_dir: str, filename: str) -> str:
    """Combine *output_dir* and *filename* into a safe output path.

    On Windows, ensures the combined path is within the 260-character
    MAX_PATH limit by truncating the filename component if necessary.

    Args:
        output_dir: Directory path (e.g. ``"./downloads"``).
        filename: Filename to append.

    Returns:
        A normalized path string.
    """
    path = os.path.join(output_dir, filename)

    if IS_WINDOWS and len(path) >= WINDOWS_MAX_PATH:
        dir_len = len(output_dir) + 1  # +1 for separator
        max_name_len = WINDOWS_MAX_PATH - dir_len - 10  # 10-char safety margin

        if max_name_len <= 0:
            # Directory itself is already too long — fall back to CWD
            safe_name = safe_filename(filename, max_length=200)
            path = os.path.join(".", safe_name)
        else:
            safe_name = safe_filename(filename, max_length=max_name_len)
            path = os.path.join(output_dir, safe_name)

    return os.path.normpath(path)


def get_default_download_dir() -> str:
    """Return the default download directory for the current OS.

    Windows: ``%USERPROFILE%\\Downloads``
    macOS:   ``~/Downloads``
    Linux:   ``$XDG_DOWNLOAD_DIR`` or ``~/Downloads``
    """
    home = os.path.expanduser("~")

    if IS_WINDOWS:
        userprofile = os.environ.get("USERPROFILE", home)
        downloads = os.path.join(userprofile, "Downloads")
        if os.path.isdir(downloads):
            return downloads
        return os.path.join(home, "Downloads")

    if IS_LINUX:
        xdg = os.environ.get("XDG_DOWNLOAD_DIR", "")
        if xdg:
            return xdg

    return os.path.join(home, "Downloads")


def get_package_dir() -> str:
    """Return the installation directory of this package.

    Works both from source and when bundled with PyInstaller.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

"""
Модуль утиліт
"""

from .clipboard import ClipboardManager, setup_clipboard_menu, auto_paste_if_valid
from .validators import *

__all__ = ['ClipboardManager', 'setup_clipboard_menu', 'auto_paste_if_valid']
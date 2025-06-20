"""
Модуль типів QR-кодів
"""

from .base import BaseQRType, get_qr_type, get_all_qr_types, register_qr_type
# Імпорти для автоматичної реєстрації типів
from . import text_qr, url_qr, email_qr

__all__ = ['BaseQRType', 'get_qr_type', 'get_all_qr_types', 'register_qr_type']
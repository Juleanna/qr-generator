#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL тип QR-коду
"""

import tkinter as tk
from typing import Dict, Any, Tuple
from urllib.parse import urlparse
from .base import BaseQRType, register_qr_type
from ..utils.clipboard import setup_clipboard_menu, auto_paste_if_valid, is_url

class URLQRType(BaseQRType):
    """Клас для створення URL QR-кодів"""
    
    def __init__(self):
        super().__init__("Веб-сайт (URL)", "🌐")
    
    def create_input_fields(self, parent: tk.Widget, clipboard_manager=None) -> Dict[str, tk.Widget]:
        """Створення полів для введення URL"""
        self.input_widgets = {}
        
        # Очищення контейнера
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Поле для URL
        url_entry = self.create_label_entry_pair(
            parent,
            "URL веб-сайту:",
            entry_width=60,
            placeholder="https://"
        )
        
        self.input_widgets['url'] = url_entry
        
        # Налаштування буфера обміну з валідатором URL
        if clipboard_manager:
            setup_clipboard_menu(url_entry, clipboard_manager)
            auto_paste_if_valid(url_entry, clipboard_manager, is_url)
        
        # Приклади
        examples_frame = tk.Frame(parent)
        examples_frame.pack(fill='x', pady=(5, 10))
        
        tk.Label(examples_frame, text="Приклади:", font=('Arial', 9, 'bold')).pack(anchor='w')
        examples_text = ("• https://www.google.com\n"
                        "• https://github.com/username/repo\n" 
                        "• ftp://files.example.com")
        tk.Label(examples_frame, text=examples_text, font=('Arial', 9), 
                fg='gray', justify='left').pack(anchor='w')
        
        # Додаткові опції
        options_frame = tk.LabelFrame(parent, text="Додаткові параметри", padding="5")
        options_frame.pack(fill='x', pady=(0, 10))
        
        # Короткий URL
        shorten_cb, self.shorten_var = self.create_checkbutton(
            options_frame, 
            "Показати попередження для довгих URL (>100 символів)"
        )
        self.input_widgets['warn_long'] = self.shorten_var
        
        # Перевірка доступності
        check_cb, self.check_var = self.create_checkbutton(
            options_frame,
            "Перевірити доступність URL (потребує інтернет)"
        )
        self.input_widgets['check_availability'] = self.check_var
        
        return self.input_widgets
    
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Валідація URL"""
        url = data.get('url', '').strip()
        
        if not url:
            return False, "Будь ласка, введіть URL"
        
        # Автоматичне додавання протоколу
        if not url.startswith(('http://', 'https://', 'ftp://', 'ftps://')):
            url = 'https://' + url
            # Оновлюємо поле
            if 'url' in self.input_widgets:
                self.input_widgets['url'].delete(0, tk.END)
                self.input_widgets['url'].insert(0, url)
        
        # Валідація URL
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False, "Невірний формат URL. Переконайтесь, що URL містить домен."
        except Exception:
            return False, "Невірний формат URL"
        
        # Перевірка довжини
        if data.get('warn_long', False) and len(url) > 100:
            return False, f"URL занадто довгий ({len(url)} символів). Рекомендується використовувати короткі URL."
        
        # Перевірка доступності (опціонально)
        if data.get('check_availability', False):
            if not self._check_url_availability(url):
                return False, f"URL недоступний або не відповідає. Перевірте правильність адреси."
        
        return True, url
    
    def _check_url_availability(self, url: str) -> bool:
        """Перевірка доступності URL"""
        try:
            import urllib.request
            import urllib.error
            
            # Створюємо запит з таймаутом
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'QR-Generator/2.0')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.getcode() == 200
        except (urllib.error.URLError, urllib.error.HTTPError, Exception):
            return False
    
    def generate_qr_data(self, data: Dict[str, Any]) -> str:
        """Генерація даних для QR-коду"""
        return data.get('url', '').strip()
    
    def get_info_text(self) -> str:
        """Інформація про URL тип QR-коду"""
        return ("URL QR-код перенаправляє користувача на веб-сайт при скануванні. "
                "Автоматично додається https:// якщо протокол не вказано. "
                "Підтримуються протоколи: http, https, ftp, ftps.")

# Реєстрація типу
register_qr_type('url', URLQRType)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Телефонний тип QR-коду
"""

import tkinter as tk
from typing import Dict, Any, Tuple
from .base import BaseQRType, register_qr_type
from ..utils.clipboard import setup_clipboard_menu, auto_paste_if_valid, is_phone
from ..utils.validators import Validators

class PhoneQRType(BaseQRType):
    """Клас для створення телефонних QR-кодів"""
    
    def __init__(self):
        super().__init__("Телефон", "📞")
    
    def create_input_fields(self, parent: tk.Widget, clipboard_manager=None) -> Dict[str, tk.Widget]:
        """Створення полів для телефону"""
        self.input_widgets = {}
        
        # Очищення контейнера
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Номер телефону
        phone_entry = self.create_label_entry_pair(
            parent,
            "Номер телефону:",
            entry_width=60,
            placeholder="+380"
        )
        self.input_widgets['phone'] = phone_entry
        
        # Налаштування буфера обміну з валідатором телефону
        if clipboard_manager:
            setup_clipboard_menu(phone_entry, clipboard_manager)
            auto_paste_if_valid(phone_entry, clipboard_manager, is_phone)
        
        # Додаткові опції
        options_frame = tk.LabelFrame(parent, text="Додаткові опції", padding="5")
        options_frame.pack(fill='x', pady=(10, 0))
        
        # Показати форматування
        format_cb, self.format_var = self.create_checkbutton(
            options_frame,
            "Показати допомогу з форматування"
        )
        self.input_widgets['show_format'] = self.format_var
        
        # Інформація про формат
        self.info_frame = tk.Frame(parent)
        self.info_frame.pack(fill='x', pady=(10, 0))
        
        self.format_info = tk.Label(
            self.info_frame,
            text="",
            font=('Arial', 9),
            fg='blue',
            justify='left',
            wraplength=500
        )
        self.format_info.pack(anchor='w')
        
        # Оновлення інформації при зміні чекбоксу
        def update_format_info():
            if self.format_var.get():
                info_text = ("📱 Формати номерів:\n"
                           "• Міжнародний: +380123456789\n"
                           "• З дефісами: +380-12-345-67-89\n"
                           "• З дужками: +380 (12) 345-67-89\n"
                           "• З пробілами: +380 12 345 67 89")
                self.format_info.config(text=info_text)
            else:
                self.format_info.config(text="💡 Підказка: QR-код дозволить користувачеві зателефонувати одним дотиком")
        
        format_cb.config(command=update_format_info)
        update_format_info()  # Початкове відображення
        
        # Приклади країн
        examples_frame = tk.Frame(parent)
        examples_frame.pack(fill='x', pady=(10, 0))
        
        tk.Label(examples_frame, text="Приклади:", font=('Arial', 9, 'bold')).pack(anchor='w')
        examples_text = ("🇺🇦 Україна: +380123456789\n"
                        "🇺🇸 США: +1234567890\n"
                        "🇩🇪 Німеччина: +4912345678\n"
                        "🇵🇱 Польща: +48123456789")
        tk.Label(examples_frame, text=examples_text, font=('Arial', 9), 
                fg='gray', justify='left').pack(anchor='w')
        
        return self.input_widgets
    
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Валідація телефонних даних"""
        phone = data.get('phone', '').strip()
        
        return Validators.validate_phone(phone)
    
    def generate_qr_data(self, data: Dict[str, Any]) -> str:
        """Генерація tel: URL"""
        phone = data.get('phone', '').strip()
        
        # Очищення номера (залишаємо тільки + та цифри)
        import re
        phone_clean = re.sub(r'[^\d+]', '', phone)
        
        return f"tel:{phone_clean}"
    
    def get_info_text(self) -> str:
        """Інформація про телефонний тип QR-коду"""
        return ("Телефонний QR-код дозволяє користувачеві зателефонувати на вказаний номер "
                "одним дотиком. Підтримує міжнародний формат з кодом країни.")

# Реєстрація типу
register_qr_type('phone', PhoneQRType)
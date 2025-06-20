#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Текстовий тип QR-коду
"""

import tkinter as tk
from typing import Dict, Any, Tuple
from .base import BaseQRType, register_qr_type
from ..utils.clipboard import setup_clipboard_menu, auto_paste_if_valid

class TextQRType(BaseQRType):
    """Клас для створення текстових QR-кодів"""
    
    def __init__(self):
        super().__init__("Звичайний текст", "📝")
    
    def create_input_fields(self, parent: tk.Widget, clipboard_manager=None) -> Dict[str, tk.Widget]:
        """Створення полів для введення тексту"""
        self.input_widgets = {}
        
        # Очищення контейнера
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Поле для тексту
        text_widget = self.create_label_text_pair(
            parent, 
            "Текст для кодування:", 
            text_height=8,
            text_width=60
        )
        
        self.input_widgets['text'] = text_widget
        
        # Налаштування буфера обміну
        if clipboard_manager:
            setup_clipboard_menu(text_widget, clipboard_manager)
            # Автовставка будь-якого тексту
            auto_paste_if_valid(text_widget, clipboard_manager)
        
        # Лічильник символів
        self.char_count_var = tk.StringVar()
        self.char_count_var.set("Символів: 0 / 4296")
        
        count_label = tk.Label(parent, textvariable=self.char_count_var, 
                              font=('Arial', 9), fg='gray')
        count_label.pack(anchor='w', pady=(5, 0))
        
        # Оновлення лічильника при зміні тексту
        def update_char_count(*args):
            try:
                text = text_widget.get("1.0", tk.END).rstrip('\n')
                char_count = len(text)
                self.char_count_var.set(f"Символів: {char_count} / 4296")
                
                # Зміна кольору при наближенні до ліміту
                if char_count > 4296:
                    count_label.config(fg='red')
                elif char_count > 3800:
                    count_label.config(fg='orange')
                else:
                    count_label.config(fg='gray')
            except:
                pass
        
        # Прив'язка до зміни тексту
        text_widget.bind('<KeyRelease>', update_char_count)
        text_widget.bind('<ButtonRelease>', update_char_count)
        text_widget.bind('<FocusOut>', update_char_count)
        
        return self.input_widgets
    
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Валідація текстових даних"""
        text = data.get('text', '').strip()
        
        if not text:
            return False, "Будь ласка, введіть текст для кодування"
        
        if len(text) > 4296:
            return False, f"Текст занадто довгий ({len(text)} символів). Максимум: 4296 символів"
        
        # Перевірка на підтримувані символи
        try:
            text.encode('utf-8')
        except UnicodeEncodeError:
            return False, "Текст містить непідтримувані символи"
        
        return True, text
    
    def generate_qr_data(self, data: Dict[str, Any]) -> str:
        """Генерація даних для QR-коду"""
        return data.get('text', '').strip()
    
    def get_info_text(self) -> str:
        """Інформація про текстовий тип QR-коду"""
        return ("Звичайний текст - найпростіший тип QR-коду. Може містити будь-який текст "
                "до 4296 символів. Підтримує UTF-8 кодування для міжнародних символів.")

# Реєстрація типу
register_qr_type('text', TextQRType)
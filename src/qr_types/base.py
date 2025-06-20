#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Базовий клас для всіх типів QR-кодів
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
import tkinter as tk
from tkinter import ttk, scrolledtext

class BaseQRType(ABC):
    """Абстрактний базовий клас для всіх типів QR-кодів"""
    
    def __init__(self, name: str, icon: str = "📝"):
        self.name = name
        self.icon = icon
        self.input_widgets = {}
    
    @property
    def display_name(self) -> str:
        """Повертає ім'я для відображення в UI"""
        return f"{self.icon} {self.name}"
    
    @abstractmethod
    def create_input_fields(self, parent: tk.Widget, clipboard_manager=None) -> Dict[str, tk.Widget]:
        """
        Створення полів вводу для даного типу QR-коду
        
        Args:
            parent: Батьківський віджет
            clipboard_manager: Менеджер буфера обміну
            
        Returns:
            Словник з віджетами вводу
        """
        pass
    
    @abstractmethod
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Валідація введених даних
        
        Args:
            data: Словник з даними з полів вводу
            
        Returns:
            Кортеж (успішність, повідомлення про помилку)
        """
        pass
    
    @abstractmethod
    def generate_qr_data(self, data: Dict[str, Any]) -> str:
        """
        Генерація рядка даних для QR-коду
        
        Args:
            data: Валідовані дані
            
        Returns:
            Рядок для генерації QR-коду
        """
        pass
    
    def get_info_text(self) -> str:
        """Повертає інформаційний текст про тип QR-коду"""
        return f"QR-код типу {self.name}"
    
    def get_input_data(self) -> Dict[str, Any]:
        """Отримання даних з полів вводу"""
        data = {}
        
        for key, widget in self.input_widgets.items():
            if isinstance(widget, (tk.Entry, ttk.Combobox)):
                data[key] = widget.get()
            elif isinstance(widget, scrolledtext.ScrolledText):
                data[key] = widget.get(1.0, tk.END).strip()
            elif isinstance(widget, tk.BooleanVar):
                data[key] = widget.get()
            elif hasattr(widget, 'get'):
                data[key] = widget.get()
        
        return data
    
    def clear_input_fields(self):
        """Очищення всіх полів вводу"""
        for key, widget in self.input_widgets.items():
            if isinstance(widget, (tk.Entry, ttk.Combobox)):
                widget.delete(0, tk.END)
            elif isinstance(widget, scrolledtext.ScrolledText):
                widget.delete(1.0, tk.END)
            elif isinstance(widget, tk.BooleanVar):
                widget.set(False)
    
    def create_label_entry_pair(self, parent: tk.Widget, label_text: str, 
                               entry_width: int = 60, placeholder: str = "",
                               is_password: bool = False) -> tk.Entry:
        """
        Створення пари лейбл-поле вводу
        
        Args:
            parent: Батьківський віджет
            label_text: Текст лейбла
            entry_width: Ширина поля вводу
            placeholder: Підказка
            is_password: Чи це поле паролю
            
        Returns:
            Створений Entry віджет
        """
        ttk.Label(parent, text=label_text).pack(anchor='w', pady=(0, 5))
        
        entry = tk.Entry(parent, width=entry_width)
        if is_password:
            entry.config(show="*")
        
        entry.pack(fill='x', pady=(0, 10))
        
        if placeholder:
            entry.insert(0, placeholder)
        
        return entry
    
    def create_label_text_pair(self, parent: tk.Widget, label_text: str,
                              text_height: int = 4, text_width: int = 60) -> scrolledtext.ScrolledText:
        """
        Створення пари лейбл-текстове поле
        
        Args:
            parent: Батьківський віджет
            label_text: Текст лейбла
            text_height: Висота текстового поля
            text_width: Ширина текстового поля
            
        Returns:
            Створений ScrolledText віджет
        """
        ttk.Label(parent, text=label_text).pack(anchor='w', pady=(0, 5))
        
        text_widget = scrolledtext.ScrolledText(parent, width=text_width, height=text_height, wrap=tk.WORD)
        text_widget.pack(fill='both', expand=True, pady=(0, 10))
        
        return text_widget
    
    def create_combobox(self, parent: tk.Widget, label_text: str, 
                       values: list, default_value: str = "") -> ttk.Combobox:
        """
        Створення комбобоксу з лейблом
        
        Args:
            parent: Батьківський віджет
            label_text: Текст лейбла
            values: Список значень
            default_value: Значення за замовчуванням
            
        Returns:
            Створений Combobox віджет
        """
        ttk.Label(parent, text=label_text).pack(anchor='w', pady=(0, 5))
        
        combo = ttk.Combobox(parent, values=values, state="readonly")
        if default_value:
            combo.set(default_value)
        combo.pack(fill='x', pady=(0, 10))
        
        return combo
    
    def create_checkbutton(self, parent: tk.Widget, text: str) -> Tuple[ttk.Checkbutton, tk.BooleanVar]:
        """
        Створення чекбоксу
        
        Args:
            parent: Батьківський віджет
            text: Текст чекбоксу
            
        Returns:
            Кортеж (Checkbutton віджет, BooleanVar)
        """
        var = tk.BooleanVar()
        checkbox = ttk.Checkbutton(parent, text=text, variable=var)
        checkbox.pack(anchor='w', pady=(0, 10))
        
        return checkbox, var

# Реєстр всіх доступних типів QR-кодів
QR_TYPES_REGISTRY = {}

def register_qr_type(type_key: str, qr_type_class: type):
    """Реєстрація нового типу QR-коду"""
    QR_TYPES_REGISTRY[type_key] = qr_type_class

def get_qr_type(type_key: str) -> Optional[BaseQRType]:
    """Отримання екземпляру типу QR-коду за ключем"""
    if type_key in QR_TYPES_REGISTRY:
        return QR_TYPES_REGISTRY[type_key]()
    return None

def get_all_qr_types() -> Dict[str, BaseQRType]:
    """Отримання всіх доступних типів QR-кодів"""
    return {key: cls() for key, cls in QR_TYPES_REGISTRY.items()}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль налаштувань для QR Code Generator
"""

import json
import os
from typing import Dict, Any

class Settings:
    """Клас для управління налаштуваннями додатку"""
    
    def __init__(self, settings_file: str = "qr_settings.json"):
        self.settings_file = settings_file
        self.default_settings = {
            "save_folder": os.path.expanduser("~/Desktop/QR_Codes"),
            "error_correction": "M",
            "border": 4,
            "box_size": 10,
            "last_qr_type": "text",
            "fg_color": "#000000",
            "bg_color": "#FFFFFF",
            "module_style": "square",
            "export_format": "PNG",
            "high_quality": True,
            "transparent_bg": False,
            "window_geometry": "1100x900",
            "auto_save": False,
            "show_tips": True,
            "language": "uk"
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Завантаження налаштувань з файлу"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Доповнюємо відсутні налаштування значеннями за замовчуванням
                for key, value in self.default_settings.items():
                    if key not in loaded_settings:
                        loaded_settings[key] = value
                
                return loaded_settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"Помилка завантаження налаштувань: {e}")
            return self.default_settings.copy()
    
    def save_settings(self) -> bool:
        """Збереження налаштувань у файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Помилка збереження налаштувань: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Отримання значення налаштування"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Встановлення значення налаштування"""
        self.settings[key] = value
    
    def reset_to_defaults(self):
        """Скидання до значень за замовчуванням"""
        self.settings = self.default_settings.copy()
    
    def update(self, new_settings: Dict[str, Any]):
        """Оновлення кількох налаштувань одночасно"""
        self.settings.update(new_settings)

# Глобальний екземпляр налаштувань
app_settings = Settings()
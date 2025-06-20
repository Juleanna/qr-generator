#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль валідаторів для різних типів даних
"""

import re
from urllib.parse import urlparse
from typing import Tuple, Optional

class Validators:
    """Клас з валідаторами для різних типів даних"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Валідація email адреси
        
        Args:
            email: Email адреса для валідації
            
        Returns:
            Кортеж (валідність, повідомлення)
        """
        email = email.strip()
        
        if not email:
            return False, "Email адреса не може бути порожньою"
        
        # Перевірка довжини
        if len(email) > 254:
            return False, "Email адреса занадто довга"
        
        # Базова перевірка формату
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        if not email_pattern.match(email):
            return False, "Невірний формат email адреси"
        
        # Перевірка частин email
        local, domain = email.rsplit('@', 1)
        
        if len(local) > 64:
            return False, "Локальна частина email занадто довга"
        
        if len(domain) > 253:
            return False, "Доменна частина email занадто довга"
        
        return True, email
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """
        Валідація URL
        
        Args:
            url: URL для валідації
            
        Returns:
            Кортеж (валідність, результат або повідомлення про помилку)
        """
        url = url.strip()
        
        if not url:
            return False, "URL не може бути порожнім"
        
        # Автоматичне додавання протоколу
        if not url.startswith(('http://', 'https://', 'ftp://', 'ftps://')):
            url = 'https://' + url
        
        try:
            result = urlparse(url)
            
            # Перевірка обов'язкових частин
            if not result.scheme:
                return False, "URL повинен містити протокол (http://, https://)"
            
            if not result.netloc:
                return False, "URL повинен містити домен"
            
            # Перевірка довжини
            if len(url) > 2048:
                return False, "URL занадто довгий (максимум 2048 символів)"
            
            # Перевірка валідних символів в домені
            domain_pattern = re.compile(
                r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
            )
            
            domain = result.netloc.split(':')[0]  # Видаляємо порт якщо є
            if not domain_pattern.match(domain):
                return False, "Невірний формат домену"
            
            return True, url
            
        except Exception as e:
            return False, f"Помилка парсингу URL: {str(e)}"
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Валідація номера телефону
        
        Args:
            phone: Номер телефону для валідації
            
        Returns:
            Кортеж (валідність, очищений номер або повідомлення про помилку)
        """
        if not phone:
            return False, "Номер телефону не може бути порожнім"
        
        # Очищення від зайвих символів, залишаємо тільки цифри та +
        phone_clean = re.sub(r'[^\d+]', '', phone.strip())
        
        if not phone_clean:
            return False, "Номер телефону повинен містити цифри"
        
        # Перевірка формату
        if not phone_clean.startswith('+'):
            return False, "Номер телефону повинен починатися з +"
        
        # Перевірка довжини (без +)
        digits_only = phone_clean[1:]
        if len(digits_only) < 7:
            return False, "Номер телефону занадто короткий"
        
        if len(digits_only) > 15:
            return False, "Номер телефону занадто довгий"
        
        # Перевірка що після + йдуть тільки цифри
        if not digits_only.isdigit():
            return False, "Номер телефону може містити тільки цифри після +"
        
        return True, phone_clean
    
    @staticmethod
    def validate_text_length(text: str, min_length: int = 0, max_length: int = 4296) -> Tuple[bool, str]:
        """
        Валідація довжини тексту
        
        Args:
            text: Текст для валідації
            min_length: Мінімальна довжина
            max_length: Максимальна довжина
            
        Returns:
            Кортеж (валідність, повідомлення)
        """
        text = text.strip() if text else ""
        text_length = len(text)
        
        if text_length < min_length:
            return False, f"Текст занадто короткий (мінімум {min_length} символів)"
        
        if text_length > max_length:
            return False, f"Текст занадто довгий (максимум {max_length} символів)"
        
        if min_length > 0 and not text:
            return False, "Поле не може бути порожнім"
        
        return True, text
    
    @staticmethod
    def validate_wifi_ssid(ssid: str) -> Tuple[bool, str]:
        """
        Валідація SSID WiFi мережі
        
        Args:
            ssid: SSID для валідації
            
        Returns:
            Кортеж (валідність, повідомлення)
        """
        ssid = ssid.strip() if ssid else ""
        
        if not ssid:
            return False, "SSID не може бути порожнім"
        
        if len(ssid) > 32:
            return False, "SSID занадто довгий (максимум 32 символи)"
        
        # Перевірка на заборонені символи (контрольні символи)
        if any(ord(c) < 32 or ord(c) == 127 for c in ssid):
            return False, "SSID містить недопустимі символи"
        
        return True, ssid
    
    @staticmethod
    def validate_wifi_password(password: str, security_type: str) -> Tuple[bool, str]:
        """
        Валідація паролю WiFi
        
        Args:
            password: Пароль для валідації
            security_type: Тип шифрування (WPA, WEP, nopass)
            
        Returns:
            Кортеж (валідність, повідомлення)
        """
        if security_type == 'nopass':
            return True, ""  # Для відкритих мереж пароль не потрібен
        
        if not password:
            return False, f"Пароль обов'язковий для {security_type} шифрування"
        
        if security_type == 'WEP':
            # WEP: 5 або 13 символів (ASCII) або 10/26 hex символів
            if len(password) not in [5, 10, 13, 26]:
                return False, "WEP пароль повинен бути 5, 10, 13 або 26 символів"
            
            if len(password) in [10, 26]:
                # Перевірка hex формату
                if not all(c in '0123456789ABCDEFabcdef' for c in password):
                    return False, "WEP пароль у hex форматі може містити тільки 0-9, A-F"
        
        elif security_type in ['WPA', 'WPA2', 'WPA3']:
            # WPA: 8-63 символи
            if len(password) < 8:
                return False, "WPA пароль повинен містити мінімум 8 символів"
            
            if len(password) > 63:
                return False, "WPA пароль повинен містити максимум 63 символи"
            
            # Перевірка на допустимі символи (ASCII 32-126)
            if any(ord(c) < 32 or ord(c) > 126 for c in password):
                return False, "WPA пароль містить недопустимі символи"
        
        return True, password
    
    @staticmethod
    def validate_vcard_field(field_value: str, field_name: str, required: bool = False, max_length: int = 255) -> Tuple[bool, str]:
        """
        Валідація поля vCard
        
        Args:
            field_value: Значення поля
            field_name: Назва поля
            required: Чи є поле обов'язковим
            max_length: Максимальна довжина
            
        Returns:
            Кортеж (валідність, повідомлення)
        """
        field_value = field_value.strip() if field_value else ""
        
        if required and not field_value:
            return False, f"{field_name} є обов'язковим полем"
        
        if len(field_value) > max_length:
            return False, f"{field_name} занадто довге (максимум {max_length} символів)"
        
        # Перевірка на заборонені символи для vCard (контрольні символи окрім \n)
        forbidden_chars = [c for c in field_value if ord(c) < 32 and c != '\n']
        if forbidden_chars:
            return False, f"{field_name} містить недопустимі символи"
        
        return True, field_value

# Функції-обгортки для зручності
def is_valid_email(email: str) -> bool:
    """Швидка перевірка валідності email"""
    return Validators.validate_email(email)[0]

def is_valid_url(url: str) -> bool:
    """Швидка перевірка валідності URL"""
    return Validators.validate_url(url)[0]

def is_valid_phone(phone: str) -> bool:
    """Швидка перевірка валідності телефону"""
    return Validators.validate_phone(phone)[0]

def clean_phone(phone: str) -> Optional[str]:
    """Очищення номера телефону"""
    valid, result = Validators.validate_phone(phone)
    return result if valid else None

def normalize_url(url: str) -> Optional[str]:
    """Нормалізація URL (додавання протоколу)"""
    valid, result = Validators.validate_url(url)
    return result if valid else None
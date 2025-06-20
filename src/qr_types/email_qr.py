#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email тип QR-коду
"""

import tkinter as tk
import re
import urllib.parse
from typing import Dict, Any, Tuple
from .base import BaseQRType, register_qr_type
from ..utils.clipboard import setup_clipboard_menu, auto_paste_if_valid, is_email

class EmailQRType(BaseQRType):
    """Клас для створення Email QR-кодів"""
    
    def __init__(self):
        super().__init__("Email", "📧")
    
    def create_input_fields(self, parent: tk.Widget, clipboard_manager=None) -> Dict[str, tk.Widget]:
        """Створення полів для email"""
        self.input_widgets = {}
        
        # Очищення контейнера
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Email адреса
        email_entry = self.create_label_entry_pair(
            parent,
            "Email адреса:",
            entry_width=60,
            placeholder="example@domain.com"
        )
        self.input_widgets['email'] = email_entry
        
        # Налаштування буфера обміну з валідатором email
        if clipboard_manager:
            setup_clipboard_menu(email_entry, clipboard_manager)
            auto_paste_if_valid(email_entry, clipboard_manager, is_email)
        
        # Тема листа
        subject_entry = self.create_label_entry_pair(
            parent,
            "Тема листа (необов'язково):",
            entry_width=60
        )
        self.input_widgets['subject'] = subject_entry
        
        # Налаштування буфера обміну для теми
        if clipboard_manager:
            setup_clipboard_menu(subject_entry, clipboard_manager)
        
        # Текст листа
        body_text = self.create_label_text_pair(
            parent,
            "Текст листа (необов'язково):",
            text_height=6,
            text_width=60
        )
        self.input_widgets['body'] = body_text
        
        # Налаштування буфера обміну для тексту
        if clipboard_manager:
            setup_clipboard_menu(body_text, clipboard_manager)
        
        # Додаткові опції
        options_frame = tk.LabelFrame(parent, text="Додаткові опції", padding="5")
        options_frame.pack(fill='x', pady=(10, 0))
        
        # CC email
        cc_entry = self.create_label_entry_pair(
            options_frame,
            "CC (копія) - через кому:",
            entry_width=60,
            placeholder="email1@domain.com, email2@domain.com"
        )
        self.input_widgets['cc'] = cc_entry
        
        # BCC email  
        bcc_entry = self.create_label_entry_pair(
            options_frame,
            "BCC (прихована копія) - через кому:",
            entry_width=60
        )
        self.input_widgets['bcc'] = bcc_entry
        
        # Інформація
        info_frame = tk.Frame(parent)
        info_frame.pack(fill='x', pady=(10, 0))
        
        info_text = ("💡 Підказка: QR-код відкриє поштовий клієнт з заповненими полями.\n"
                    "Користувач зможе відредагувати та відправити лист.")
        tk.Label(info_frame, text=info_text, font=('Arial', 9), 
                fg='blue', justify='left', wraplength=500).pack(anchor='w')
        
        return self.input_widgets
    
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Валідація email даних"""
        email = data.get('email', '').strip()
        
        if not email:
            return False, "Будь ласка, введіть email адресу"
        
        # Валідація основного email
        if not self._validate_email(email):
            return False, "Невірний формат email адреси"
        
        # Валідація CC emails
        cc = data.get('cc', '').strip()
        if cc:
            cc_emails = [e.strip() for e in cc.split(',') if e.strip()]
            for cc_email in cc_emails:
                if not self._validate_email(cc_email):
                    return False, f"Невірний формат CC email: {cc_email}"
        
        # Валідація BCC emails
        bcc = data.get('bcc', '').strip()
        if bcc:
            bcc_emails = [e.strip() for e in bcc.split(',') if e.strip()]
            for bcc_email in bcc_emails:
                if not self._validate_email(bcc_email):
                    return False, f"Невірний формат BCC email: {bcc_email}"
        
        # Перевірка довжини теми
        subject = data.get('subject', '').strip()
        if len(subject) > 200:
            return False, "Тема листа занадто довга (максимум 200 символів)"
        
        # Перевірка довжини тексту
        body = data.get('body', '').strip()
        if len(body) > 2000:
            return False, "Текст листа занадто довгий (максимум 2000 символів)"
        
        return True, email
    
    def _validate_email(self, email: str) -> bool:
        """Валідація email адреси"""
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        return bool(email_pattern.match(email.strip()))
    
    def generate_qr_data(self, data: Dict[str, Any]) -> str:
        """Генерація mailto URL"""
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        body = data.get('body', '').strip()
        cc = data.get('cc', '').strip()
        bcc = data.get('bcc', '').strip()
        
        mailto_url = f"mailto:{email}"
        params = []
        
        if subject:
            params.append(f"subject={urllib.parse.quote(subject)}")
        
        if body:
            params.append(f"body={urllib.parse.quote(body)}")
        
        if cc:
            # Очищуємо та форматуємо CC emails
            cc_emails = [e.strip() for e in cc.split(',') if e.strip()]
            if cc_emails:
                params.append(f"cc={urllib.parse.quote(','.join(cc_emails))}")
        
        if bcc:
            # Очищуємо та форматуємо BCC emails
            bcc_emails = [e.strip() for e in bcc.split(',') if e.strip()]
            if bcc_emails:
                params.append(f"bcc={urllib.parse.quote(','.join(bcc_emails))}")
        
        if params:
            mailto_url += "?" + "&".join(params)
        
        return mailto_url
    
    def get_info_text(self) -> str:
        """Інформація про Email тип QR-коду"""
        return ("Email QR-код створює новий лист з вказаною адресою, темою та текстом "
                "в поштовому клієнті користувача. Підтримує CC, BCC та форматування тексту.")

# Реєстрація типу
register_qr_type('email', EmailQRType)
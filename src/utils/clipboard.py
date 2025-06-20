#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для роботи з буфером обміну
"""

import tkinter as tk
from typing import Optional

class ClipboardManager:
    """Клас для управління буфером обміну"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
    
    def get_text(self) -> Optional[str]:
        """Отримання тексту з буфера обміну"""
        try:
            return self.root.clipboard_get()
        except tk.TclError:
            return None
    
    def set_text(self, text: str) -> bool:
        """Встановлення тексту в буфер обміну"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()  # Потрібно для деяких систем
            return True
        except tk.TclError:
            return False
    
    def has_text(self) -> bool:
        """Перевірка наявності тексту в буфері обміну"""
        try:
            self.root.clipboard_get()
            return True
        except tk.TclError:
            return False

def setup_clipboard_menu(widget, clipboard_manager: ClipboardManager):
    """Налаштування контекстного меню для віджету з функціями буфера обміну"""
    
    def show_context_menu(event):
        """Показати контекстне меню"""
        try:
            # Створення контекстного меню
            context_menu = tk.Menu(widget, tearoff=0)
            
            # Додавання пунктів меню
            context_menu.add_command(label="Вирізати", command=lambda: cut_text(widget))
            context_menu.add_command(label="Копіювати", command=lambda: copy_text(widget))
            context_menu.add_command(label="Вставити", command=lambda: paste_text(widget, clipboard_manager))
            context_menu.add_separator()
            context_menu.add_command(label="Виділити все", command=lambda: select_all(widget))
            
            # Показ меню
            context_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(f"Помилка контекстного меню: {e}")
        finally:
            # Знищення меню після використання
            try:
                context_menu.destroy()
            except:
                pass
    
    # Прив'язка до правої кнопки миші
    widget.bind("<Button-3>", show_context_menu)
    
    # Прив'язка до клавіатурних скорочень
    widget.bind("<Control-c>", lambda e: copy_text(widget))
    widget.bind("<Control-x>", lambda e: cut_text(widget))
    widget.bind("<Control-v>", lambda e: paste_text(widget, clipboard_manager))
    widget.bind("<Control-a>", lambda e: select_all(widget))

def copy_text(widget):
    """Копіювання виділеного тексту"""
    try:
        if hasattr(widget, 'selection_get'):
            selected_text = widget.selection_get()
            widget.clipboard_clear()
            widget.clipboard_append(selected_text)
    except tk.TclError:
        pass

def cut_text(widget):
    """Вирізання виділеного тексту"""
    try:
        if hasattr(widget, 'selection_get') and hasattr(widget, 'delete'):
            selected_text = widget.selection_get()
            widget.clipboard_clear()
            widget.clipboard_append(selected_text)
            
            # Видалення виділеного тексту
            if hasattr(widget, 'index'):  # Text widget
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            elif hasattr(widget, 'selection_range'):  # Entry widget
                start = widget.index(tk.SEL_FIRST)
                end = widget.index(tk.SEL_LAST)
                widget.delete(start, end)
    except tk.TclError:
        pass

def paste_text(widget, clipboard_manager: ClipboardManager):
    """Вставка тексту з буфера обміну"""
    try:
        clipboard_text = clipboard_manager.get_text()
        if clipboard_text:
            if hasattr(widget, 'insert'):
                # Для Text та Entry віджетів
                if hasattr(widget, 'selection_get'):
                    try:
                        # Якщо є виділення, замінюємо його
                        if hasattr(widget, 'index'):  # Text widget
                            widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                            widget.insert(tk.INSERT, clipboard_text)
                        elif hasattr(widget, 'selection_range'):  # Entry widget
                            start = widget.index(tk.SEL_FIRST)
                            end = widget.index(tk.SEL_LAST)
                            widget.delete(start, end)
                            widget.insert(start, clipboard_text)
                    except tk.TclError:
                        # Немає виділення, вставляємо в поточну позицію
                        widget.insert(tk.INSERT, clipboard_text)
                else:
                    # Простий віджет без підтримки виділення
                    widget.insert(tk.INSERT, clipboard_text)
    except Exception as e:
        print(f"Помилка вставки з буфера: {e}")

def select_all(widget):
    """Виділення всього тексту"""
    try:
        if hasattr(widget, 'tag_add'):  # Text widget
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, "1.0")
            widget.see(tk.INSERT)
        elif hasattr(widget, 'select_range'):  # Entry widget
            widget.select_range(0, tk.END)
    except tk.TclError:
        pass

def auto_paste_if_valid(widget, clipboard_manager: ClipboardManager, validator=None):
    """Автоматична вставка з буфера обміну при фокусі, якщо поле порожнє"""
    def on_focus_in(event):
        try:
            # Перевіряємо чи поле порожнє
            current_content = ""
            if hasattr(widget, 'get'):
                if callable(widget.get):
                    if hasattr(widget, 'index'):  # Text widget
                        current_content = widget.get("1.0", tk.END).strip()
                    else:  # Entry widget
                        current_content = widget.get().strip()
            
            # Якщо поле порожнє і в буфері є текст
            if not current_content:
                clipboard_text = clipboard_manager.get_text()
                if clipboard_text:
                    # Застосовуємо валідатор якщо він є
                    if validator is None or validator(clipboard_text.strip()):
                        paste_text(widget, clipboard_manager)
        except Exception as e:
            print(f"Помилка автовставки: {e}")
    
    widget.bind("<FocusIn>", on_focus_in)

# Валідатори для автовставки
def is_url(text: str) -> bool:
    """Перевірка чи є текст URL"""
    text = text.strip().lower()
    return (text.startswith(('http://', 'https://', 'ftp://')) or 
            '.' in text and ' ' not in text)

def is_email(text: str) -> bool:
    """Перевірка чи є текст email"""
    import re
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(text.strip()))

def is_phone(text: str) -> bool:
    """Перевірка чи є текст телефоном"""
    import re
    phone_clean = re.sub(r'[^\d+]', '', text.strip())
    return phone_clean.startswith('+') and len(phone_clean) >= 10
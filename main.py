#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QR Code Generator Pro v2.0
Головний файл додатку
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Додаємо src папку до шляху
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ui.main_window import QRCodeGenerator
except ImportError as e:
    print(f"Помилка імпорту: {e}")
    print("Переконайтесь, що всі необхідні модулі встановлені:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def main():
    """Головна функція додатку"""
    try:
        # Створення головного вікна
        root = tk.Tk()
        
        # Ініціалізація додатку
        app = QRCodeGenerator(root)
        
        # Обробка закриття додатку
        def on_closing():
            app.save_settings()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Запуск головного циклу
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Критична помилка", f"Не вдалося запустити додаток:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
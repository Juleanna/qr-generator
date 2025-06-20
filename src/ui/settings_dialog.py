#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Діалог налаштувань програми
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Optional

class SettingsDialog:
    """Діалог налаштувань програми"""
    
    def __init__(self, parent: tk.Tk, settings):
        self.parent = parent
        self.settings = settings
        self.result = False
        
        # Створення діалогового вікна
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Налаштування")
        self.dialog.geometry("650x550")
        self.dialog.resizable(False, False)
        
        # Центрування вікна
        self.center_window()
        
        # Модальність
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Змінні для налаштувань
        self.setup_variables()
        
        # Створення інтерфейсу
        self.create_widgets()
        
        # Завантаження поточних налаштувань
        self.load_current_settings()
        
        # Очікування закриття діалогу
        self.dialog.wait_window()
    
    def center_window(self):
        """Центрування вікна відносно батьківського"""
        self.dialog.update_idletasks()
        
        # Розміри вікон
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Розрахунок позиції
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def setup_variables(self):
        """Налаштування змінних для віджетів"""
        self.folder_var = tk.StringVar()
        self.error_var = tk.StringVar()
        self.box_size_var = tk.IntVar()
        self.border_var = tk.IntVar()
        self.default_type_var = tk.StringVar()
        self.auto_save_var = tk.BooleanVar()
        self.show_tips_var = tk.BooleanVar()
        self.language_var = tk.StringVar()
    
    def create_widgets(self):
        """Створення віджетів діалогу"""
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.pack(fill='both', expand=True)
        
        # Створення notebook для вкладок
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(0, 15))
        
        # Вкладки
        self.create_general_tab(notebook)
        self.create_qr_tab(notebook)
        self.create_advanced_tab(notebook)
        
        # Кнопки
        self.create_buttons(main_frame)
    
    def create_general_tab(self, notebook):
        """Створення вкладки загальних налаштувань"""
        general_frame = ttk.Frame(notebook, padding="10")
        notebook.add(general_frame, text="Загальні")
        
        # Папка збереження
        ttk.Label(general_frame, text="Папка для збереження QR-кодів:").pack(anchor='w', pady=(0, 5))
        
        folder_frame = ttk.Frame(general_frame)
        folder_frame.pack(fill='x', pady=(0, 15))
        
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=50)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        ttk.Button(folder_frame, text="Огляд...", command=self.browse_folder).pack(side='right')
        
        # Тип QR-коду за замовчуванням
        ttk.Label(general_frame, text="Тип QR-коду за замовчуванням:").pack(anchor='w', pady=(0, 5))
        
        default_combo = ttk.Combobox(general_frame, textvariable=self.default_type_var, state="readonly")
        default_combo['values'] = ['text', 'url', 'email', 'phone', 'sms', 'wifi', 'vcard']
        default_combo.pack(fill='x', pady=(0, 15))
        
        # Мова інтерфейсу
        ttk.Label(general_frame, text="Мова інтерфейсу:").pack(anchor='w', pady=(0, 5))
        
        language_combo = ttk.Combobox(general_frame, textvariable=self.language_var, state="readonly")
        language_combo['values'] = [
            ('uk', 'Українська'),
            ('en', 'English'),
            ('ru', 'Русский')
        ]
        language_combo.pack(fill='x', pady=(0, 15))
        
        # Додаткові опції
        options_frame = ttk.LabelFrame(general_frame, text="Додаткові опції", padding="5")
        options_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Checkbutton(
            options_frame,
            text="Автоматично зберігати QR-коди при генерації",
            variable=self.auto_save_var
        ).pack(anchor='w', pady=2)
        
        ttk.Checkbutton(
            options_frame,
            text="Показувати підказки та поради",
            variable=self.show_tips_var
        ).pack(anchor='w', pady=2)
    
    def create_qr_tab(self, notebook):
        """Створення вкладки налаштувань QR-коду"""
        qr_frame = ttk.Frame(notebook, padding="10")
        notebook.add(qr_frame, text="QR-код")
        
        # Рівень корекції помилок
        ttk.Label(qr_frame, text="Рівень корекції помилок:").pack(anchor='w', pady=(0, 5))
        
        error_frame = ttk.Frame(qr_frame)
        error_frame.pack(fill='x', pady=(0, 15))
        
        error_levels = [
            ('L', 'L (~7%) - Низький'),
            ('M', 'M (~15%) - Середній (рекомендується)'),
            ('Q', 'Q (~25%) - Високий'),
            ('H', 'H (~30%) - Максимальний')
        ]
        
        for i, (value, text) in enumerate(error_levels):
            ttk.Radiobutton(
                error_frame,
                text=text,
                variable=self.error_var,
                value=value
            ).grid(row=i//2, column=i%2, sticky='w', padx=(0, 15), pady=2)
        
        # Розмір блоку
        ttk.Label(qr_frame, text="Розмір блоку (пікселів):").pack(anchor='w', pady=(20, 5))
        
        box_size_frame = ttk.Frame(qr_frame)
        box_size_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Scale(
            box_size_frame,
            from_=5,
            to=20,
            variable=self.box_size_var,
            orient='horizontal'
        ).pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.box_size_label = ttk.Label(box_size_frame, text="10", width=3)
        self.box_size_label.pack(side='right')
        
        # Оновлення лейблу
        def update_box_size_label(*args):
            self.box_size_label.config(text=str(self.box_size_var.get()))
        self.box_size_var.trace('w', update_box_size_label)
        
        # Розмір границі
        ttk.Label(qr_frame, text="Розмір границі (блоків):").pack(anchor='w', pady=(0, 5))
        
        border_frame = ttk.Frame(qr_frame)
        border_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Scale(
            border_frame,
            from_=1,
            to=10,
            variable=self.border_var,
            orient='horizontal'
        ).pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.border_label = ttk.Label(border_frame, text="4", width=3)
        self.border_label.pack(side='right')
        
        # Оновлення лейблу границі
        def update_border_label(*args):
            self.border_label.config(text=str(self.border_var.get()))
        self.border_var.trace('w', update_border_label)
        
        # Інформація про налаштування
        info_frame = ttk.LabelFrame(qr_frame, text="Інформація", padding="5")
        info_frame.pack(fill='x', pady=(10, 0))
        
        info_text = ("• Вищий рівень корекції дозволяє сканувати пошкоджені QR-коди\n"
                    "• Більший розмір блоку створює більші QR-коди\n"
                    "• Границя допомагає сканерам краще розпізнавати QR-код")
        
        ttk.Label(info_frame, text=info_text, font=('Arial', 9), justify='left').pack(anchor='w')
    
    def create_advanced_tab(self, notebook):
        """Створення вкладки розширених налаштувань"""
        advanced_frame = ttk.Frame(notebook, padding="10")
        notebook.add(advanced_frame, text="Розширені")
        
        # Продуктивність
        performance_frame = ttk.LabelFrame(advanced_frame, text="Продуктивність", padding="5")
        performance_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(performance_frame, text="Ці налаштування будуть додані в майбутніх версіях:").pack(anchor='w')
        ttk.Label(performance_frame, text="• Кешування QR-кодів").pack(anchor='w', padx=(20, 0))
        ttk.Label(performance_frame, text="• Пакетна генерація").pack(anchor='w', padx=(20, 0))
        ttk.Label(performance_frame, text="• Оптимізація пам'яті").pack(anchor='w', padx=(20, 0))
        
        # Експорт/Імпорт налаштувань
        backup_frame = ttk.LabelFrame(advanced_frame, text="Резервне копіювання", padding="5")
        backup_frame.pack(fill='x', pady=(0, 10))
        
        backup_buttons_frame = ttk.Frame(backup_frame)
        backup_buttons_frame.pack(fill='x')
        
        ttk.Button(
            backup_buttons_frame,
            text="Експорт налаштувань",
            command=self.export_settings
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            backup_buttons_frame,
            text="Імпорт налаштувань",
            command=self.import_settings
        ).pack(side='left')
        
        # Скидання
        reset_frame = ttk.LabelFrame(advanced_frame, text="Скидання", padding="5")
        reset_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(reset_frame, text="Увага: ця дія незворотна!").pack(anchor='w', pady=(0, 5))
        
        ttk.Button(
            reset_frame,
            text="Скинути всі налаштування",
            command=self.reset_all_settings
        ).pack(anchor='w')
        
        # Інформація про програму
        about_frame = ttk.LabelFrame(advanced_frame, text="Про програму", padding="5")
        about_frame.pack(fill='x', pady=(10, 0))
        
        about_text = ("QR Code Generator Pro v2.0\n"
                     "Розробник: Juleanna\n"
                     "Ліцензія: MIT\n"
                     "GitHub: github.com/Juleanna/qr-generator")
        
        ttk.Label(about_frame, text=about_text, font=('Arial', 9), justify='left').pack(anchor='w')
    
    def create_buttons(self, parent):
        """Створення кнопок діалогу"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(
            button_frame,
            text="За замовчуванням",
            command=self.reset_to_defaults
        ).pack(side='left')
        
        ttk.Button(
            button_frame,
            text="Скасувати",
            command=self.cancel
        ).pack(side='right', padx=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Зберегти",
            command=self.save_settings
        ).pack(side='right')
    
    def load_current_settings(self):
        """Завантаження поточних налаштувань"""
        self.folder_var.set(self.settings.get('save_folder', ''))
        self.error_var.set(self.settings.get('error_correction', 'M'))
        self.box_size_var.set(self.settings.get('box_size', 10))
        self.border_var.set(self.settings.get('border', 4))
        self.default_type_var.set(self.settings.get('last_qr_type', 'text'))
        self.auto_save_var.set(self.settings.get('auto_save', False))
        self.show_tips_var.set(self.settings.get('show_tips', True))
        self.language_var.set(self.settings.get('language', 'uk'))
    
    def browse_folder(self):
        """Вибір папки для збереження"""
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)
    
    def export_settings(self):
        """Експорт налаштувань у файл"""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Зберегти налаштування"
            )
            
            if filepath:
                import json
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.settings.settings, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Успіх", f"Налаштування експортовано у:\n{filepath}")
        
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося експортувати налаштування:\n{str(e)}")
    
    def import_settings(self):
        """Імпорт налаштувань з файлу"""
        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Завантажити налаштування"
            )
            
            if filepath:
                import json
                with open(filepath, 'r', encoding='utf-8') as f:
                    imported_settings = json.load(f)
                
                # Оновлення налаштувань
                self.settings.settings.update(imported_settings)
                self.load_current_settings()
                
                messagebox.showinfo("Успіх", "Налаштування успішно імпортовано")
        
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося імпортувати налаштування:\n{str(e)}")
    
    def reset_all_settings(self):
        """Скидання всіх налаштувань"""
        result = messagebox.askyesno(
            "Підтвердження",
            "Скинути ВСІ налаштування до значень за замовчуванням?\n"
            "Ця дія незворотна!"
        )
        
        if result:
            self.settings.reset_to_defaults()
            self.load_current_settings()
            messagebox.showinfo("Виконано", "Всі налаштування скинуто до значень за замовчуванням")
    
    def reset_to_defaults(self):
        """Скидання до значень за замовчуванням"""
        result = messagebox.askyesno(
            "Підтвердження",
            "Скинути всі налаштування до значень за замовчуванням?"
        )
        
        if result:
            self.folder_var.set(os.path.expanduser("~/Desktop/QR_Codes"))
            self.error_var.set("M")
            self.box_size_var.set(10)
            self.border_var.set(4)
            self.default_type_var.set("text")
            self.auto_save_var.set(False)
            self.show_tips_var.set(True)
            self.language_var.set("uk")
    
    def save_settings(self):
        """Збереження налаштувань"""
        try:
            # Валідація папки збереження
            save_folder = self.folder_var.get().strip()
            if not save_folder:
                messagebox.showerror("Помилка", "Будь ласка, вкажіть папку для збереження")
                return
            
            # Спроба створити папку якщо не існує
            try:
                os.makedirs(save_folder, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося створити папку:\n{str(e)}")
                return
            
            # Збереження налаштувань
            self.settings.set('save_folder', save_folder)
            self.settings.set('error_correction', self.error_var.get())
            self.settings.set('box_size', self.box_size_var.get())
            self.settings.set('border', self.border_var.get())
            self.settings.set('last_qr_type', self.default_type_var.get())
            self.settings.set('auto_save', self.auto_save_var.get())
            self.settings.set('show_tips', self.show_tips_var.get())
            self.settings.set('language', self.language_var.get())
            
            # Збереження у файл
            if self.settings.save_settings():
                self.result = True
                self.dialog.destroy()
                messagebox.showinfo("Успіх", "Налаштування збережено")
            else:
                messagebox.showerror("Помилка", "Не вдалося зберегти налаштування")
        
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка збереження налаштувань:\n{str(e)}")
    
    def cancel(self):
        """Скасування змін"""
        self.result = False
        self.dialog.destroy()
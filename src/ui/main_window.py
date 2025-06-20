#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Головне вікно QR Code Generator
"""

import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
from PIL import Image, ImageTk
import os
from datetime import datetime

# Імпорти модулів
from ..config.settings import app_settings
from ..utils.clipboard import ClipboardManager
from ..qr_types.base import get_all_qr_types, get_qr_type
from ..design.export import QRExporter
from .design_tab import DesignTab
from .settings_dialog import SettingsDialog

# Імпорт всіх типів QR-кодів для їх реєстрації
from ..qr_types import text_qr, url_qr, email_qr

class QRCodeGenerator:
    """Головний клас додатку QR Code Generator"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.setup_window()
        
        # Ініціалізація компонентів
        self.clipboard_manager = ClipboardManager(root)
        self.qr_exporter = QRExporter()
        
        # QR код змінні
        self.current_qr_image = None
        self.qr_photo = None
        self.current_qr_type = app_settings.get("last_qr_type", "text")
        
        # Отримання всіх доступних типів QR-кодів
        self.qr_types = get_all_qr_types()
        self.current_qr_instance = None
        
        # Створення інтерфейсу
        self.create_widgets()
        
        # Встановлення поточного типу
        self.set_qr_type(self.current_qr_type)
    
    def setup_window(self):
        """Налаштування головного вікна"""
        self.root.title("QR Code Generator Pro v2.0")
        
        # Розмір з налаштувань або за замовчуванням
        geometry = app_settings.get("window_geometry", "1200x900")
        self.root.geometry(geometry)
        self.root.minsize(800, 600)
        
        # Збереження розміру вікна при зміні
        def save_geometry(event=None):
            app_settings.set("window_geometry", self.root.geometry())
        
        self.root.bind('<Configure>', save_geometry)
        
        # Іконка (якщо є)
        try:
            # Тут можна встановити іконку
            pass
        except:
            pass
    
    def create_widgets(self):
        """Створення основних віджетів"""
        # Головний контейнер з Notebook
        self.main_notebook = ttk.Notebook(self.root, padding="5")
        self.main_notebook.pack(fill='both', expand=True)
        
        # Вкладка створення QR-коду
        self.create_tab_frame = ttk.Frame(self.main_notebook, padding="10")
        self.main_notebook.add(self.create_tab_frame, text="Створення QR-коду")
        
        # Вкладка дизайну
        self.design_tab = DesignTab(self.main_notebook, self)
        self.main_notebook.add(self.design_tab.frame, text="Дизайн")
        
        # Створення основної вкладки
        self.create_main_tab()
        
        # Статус бар
        self.create_status_bar()
    
    def create_main_tab(self):
        """Створення основної вкладки"""
        # Налаштування сітки
        self.create_tab_frame.columnconfigure(1, weight=1)
        self.create_tab_frame.rowconfigure(4, weight=1)
        
        # Вибір типу QR-коду
        self.create_type_selector()
        
        # Контейнер для полів вводу
        self.create_input_container()
        
        # Кнопки управління
        self.create_control_buttons()
        
        # Область відображення QR-коду
        self.create_qr_display()
        
        # Інформаційна панель
        self.create_info_panel()
    
    def create_type_selector(self):
        """Створення селектора типу QR-коду"""
        # Лейбл
        ttk.Label(self.create_tab_frame, text="Оберіть тип QR-коду:").grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )
        
        # Фрейм для комбобоксу
        type_frame = ttk.Frame(self.create_tab_frame)
        type_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        type_frame.columnconfigure(0, weight=1)
        
        # Комбобокс типів
        self.qr_type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(
            type_frame, 
            textvariable=self.qr_type_var, 
            state="readonly", 
            width=40
        )
        
        # Заповнення значеннями
        type_names = [qr_type.display_name for qr_type in self.qr_types.values()]
        self.type_combo['values'] = type_names
        self.type_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Кнопка швидкого очищення
        ttk.Button(type_frame, text="Очистити", command=self.clear_fields).grid(
            row=0, column=1, sticky=tk.E
        )
        
        # Прив'язка зміни типу
        self.type_combo.bind('<<ComboboxSelected>>', self.on_type_change)
    
    def create_input_container(self):
        """Створення контейнера для полів вводу"""
        self.input_container = ttk.LabelFrame(
            self.create_tab_frame, 
            text="Введіть дані:", 
            padding="10"
        )
        self.input_container.grid(
            row=2, column=0, columnspan=2, 
            sticky=(tk.W, tk.E, tk.N, tk.S), 
            pady=(0, 10)
        )
        self.input_container.columnconfigure(0, weight=1)
        self.input_container.rowconfigure(0, weight=1)
    
    def create_control_buttons(self):
        """Створення кнопок управління"""
        buttons_frame = ttk.Frame(self.create_tab_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Налаштування колонок
        for i in range(4):
            buttons_frame.columnconfigure(i, weight=1)
        
        # Кнопка генерації
        self.generate_btn = ttk.Button(
            buttons_frame, 
            text="🎯 Згенерувати QR-код", 
            command=self.generate_qr
        )
        self.generate_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        # Кнопка збереження
        self.save_btn = ttk.Button(
            buttons_frame, 
            text="💾 Зберегти QR-код", 
            command=self.save_qr, 
            state='disabled'
        )
        self.save_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        # Кнопка копіювання
        self.copy_btn = ttk.Button(
            buttons_frame,
            text="📋 Копіювати",
            command=self.copy_qr_to_clipboard,
            state='disabled'
        )
        self.copy_btn.grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E))
        
        # Кнопка налаштувань
        self.settings_btn = ttk.Button(
            buttons_frame, 
            text="⚙️ Налаштування", 
            command=self.open_settings
        )
        self.settings_btn.grid(row=0, column=3, padx=(5, 0), sticky=(tk.W, tk.E))
    
    def create_qr_display(self):
        """Створення області відображення QR-коду"""
        qr_frame = ttk.LabelFrame(
            self.create_tab_frame, 
            text="Згенерований QR-код", 
            padding="10"
        )
        qr_frame.grid(
            row=4, column=0, columnspan=2, 
            sticky=(tk.W, tk.E, tk.N, tk.S), 
            pady=(0, 10)
        )
        
        self.qr_label = ttk.Label(
            qr_frame, 
            text="QR-код з'явиться тут після генерації",
            relief='sunken', 
            anchor='center'
        )
        self.qr_label.pack(expand=True, fill='both')
        
        # Мінімальний розмір
        qr_frame.configure(height=300)
    
    def create_info_panel(self):
        """Створення інформаційної панелі"""
        self.info_frame = ttk.LabelFrame(
            self.create_tab_frame, 
            text="Інформація", 
            padding="5"
        )
        self.info_frame.grid(
            row=5, column=0, columnspan=2, 
            sticky=(tk.W, tk.E), 
            pady=(0, 10)
        )
        
        self.info_label = ttk.Label(
            self.info_frame, 
            text="", 
            wraplength=600, 
            justify='left'
        )
        self.info_label.pack(fill='x')
    
    def create_status_bar(self):
        """Створення статус бару"""
        self.status_var = tk.StringVar()
        self.status_var.set(f"Папка збереження: {app_settings.get('save_folder')}")
        
        status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief='sunken'
        )
        status_bar.pack(side='bottom', fill='x')
    
    def set_qr_type(self, type_key: str):
        """Встановлення типу QR-коду"""
        if type_key in self.qr_types:
            self.current_qr_type = type_key
            self.current_qr_instance = get_qr_type(type_key)
            
            # Встановлення значення в комбобоксі
            display_name = self.qr_types[type_key].display_name
            self.qr_type_var.set(display_name)
            
            # Створення полів вводу
            self.create_input_fields()
            
            # Оновлення інформації
            self.update_info_text()
    
    def on_type_change(self, event=None):
        """Обробка зміни типу QR-коду"""
        selected_name = self.qr_type_var.get()
        
        # Знаходження ключа за відображуваним ім'ям
        for key, qr_type in self.qr_types.items():
            if qr_type.display_name == selected_name:
                self.set_qr_type(key)
                break
        
        # Очищення поточного QR-коду
        self.clear_qr_display()
    
    def create_input_fields(self):
        """Створення полів вводу для поточного типу"""
        if self.current_qr_instance:
            self.current_qr_instance.create_input_fields(
                self.input_container, 
                self.clipboard_manager
            )
    
    def clear_fields(self):
        """Очищення всіх полів вводу"""
        if self.current_qr_instance:
            self.current_qr_instance.clear_input_fields()
    
    def clear_qr_display(self):
        """Очищення відображення QR-коду"""
        self.current_qr_image = None
        self.qr_photo = None
        self.qr_label.configure(image='', text="QR-код з'явиться тут після генерації")
        self.save_btn.configure(state='disabled')
        self.copy_btn.configure(state='disabled')
        
        # Очищення превью в дизайні
        self.design_tab.clear_preview()
    
    def update_info_text(self):
        """Оновлення інформаційного тексту"""
        if self.current_qr_instance:
            info_text = self.current_qr_instance.get_info_text()
            self.info_label.config(text=info_text)
    
    def generate_qr(self):
        """Генерація QR-коду"""
        if not self.current_qr_instance:
            messagebox.showerror("Помилка", "Тип QR-коду не вибрано")
            return
        
        try:
            # Отримання даних з полів
            input_data = self.current_qr_instance.get_input_data()
            
            # Валідація
            is_valid, result = self.current_qr_instance.validate_input(input_data)
            if not is_valid:
                messagebox.showwarning("Помилка валідації", result)
                return
            
            # Генерація тексту для QR-коду
            qr_text = self.current_qr_instance.generate_qr_data(input_data)
            
            # Створення QR-коду
            error_levels = {
                'L': qrcode.constants.ERROR_CORRECT_L,
                'M': qrcode.constants.ERROR_CORRECT_M,
                'Q': qrcode.constants.ERROR_CORRECT_Q,
                'H': qrcode.constants.ERROR_CORRECT_H
            }
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=error_levels.get(
                    app_settings.get('error_correction', 'M'), 
                    qrcode.constants.ERROR_CORRECT_M
                ),
                box_size=app_settings.get('box_size', 10),
                border=app_settings.get('border', 4),
            )
            
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            # Створення базового зображення
            self.current_qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Відображення QR-коду
            self.display_qr_image()
            
            # Оновлення превью в дизайні
            self.design_tab.update_preview(self.current_qr_image)
            
            # Активація кнопок
            self.save_btn.configure(state='normal')
            self.copy_btn.configure(state='normal')
            
            # Оновлення статусу
            data_length = len(qr_text.encode('utf-8'))
            type_name = self.current_qr_instance.name
            self.status_var.set(
                f"QR-код згенеровано ({type_name}) | Розмір даних: {data_length} байт"
            )
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при генерації QR-коду:\n{str(e)}")
    
    def display_qr_image(self):
        """Відображення QR-коду в основному вікні"""
        if not self.current_qr_image:
            return
        
        try:
            # Створення стилізованого зображення для відображення
            styled_image = self.design_tab.create_styled_qr_image(self.current_qr_image)
            
            # Зміна розміру для відображення
            display_size = (300, 300)
            display_image = styled_image.resize(display_size, Image.Resampling.LANCZOS)
            
            # Конвертація для tkinter
            self.qr_photo = ImageTk.PhotoImage(display_image)
            self.qr_label.configure(image=self.qr_photo, text="")
            
        except Exception as e:
            print(f"Помилка відображення QR-коду: {e}")
    
    def save_qr(self):
        """Збереження QR-коду"""
        if not self.current_qr_image:
            messagebox.showwarning("Попередження", "Спочатку згенеруйте QR-код")
            return
        
        try:
            # Створення папки якщо не існує
            save_folder = app_settings.get('save_folder')
            os.makedirs(save_folder, exist_ok=True)
            
            # Генерація імені файлу
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            type_name = self.current_qr_type.upper()
            export_format = self.design_tab.get_export_format()
            
            filename = f"QR_{type_name}_{timestamp}.{export_format.lower()}"
            filepath = os.path.join(save_folder, filename)
            
            # Експорт через дизайн модуль
            success = self.qr_exporter.export_qr(
                self.current_qr_image,
                filepath,
                self.design_tab.get_export_settings()
            )
            
            if success:
                self.status_var.set(f"QR-код збережено: {filename}")
                messagebox.showinfo("Успіх", f"QR-код збережено як:\n{filepath}")
            else:
                messagebox.showerror("Помилка", "Не вдалося зберегти QR-код")
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при збереженні:\n{str(e)}")
    
    def copy_qr_to_clipboard(self):
        """Копіювання QR-коду в буфер обміну"""
        if not self.current_qr_image:
            messagebox.showwarning("Попередження", "Спочатку згенеруйте QR-код")
            return
        
        try:
            # Створення стилізованого зображення
            styled_image = self.design_tab.create_styled_qr_image(self.current_qr_image)
            
            # Збереження у тимчасовий файл для буфера обміну
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                styled_image.save(tmp_file.name, 'PNG')
                
                # Копіювання в буфер обміну (Windows)
                try:
                    import win32clipboard
                    from PIL import Image
                    
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    
                    # Конвертація в формат буфера обміну
                    output = io.BytesIO()
                    styled_image.convert('RGB').save(output, 'BMP')
                    data = output.getvalue()[14:]  # Видаляємо BMP заголовок
                    
                    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                    win32clipboard.CloseClipboard()
                    
                    self.status_var.set("QR-код скопійовано в буфер обміну")
                    messagebox.showinfo("Успіх", "QR-код скопійовано в буфер обміну")
                    
                except ImportError:
                    # Альтернативний метод без win32clipboard
                    self.clipboard_manager.set_text(f"QR код збережено у: {tmp_file.name}")
                    messagebox.showinfo("Інформація", 
                                      f"QR-код збережено у тимчасовий файл:\n{tmp_file.name}")
                
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка копіювання в буфер:\n{str(e)}")
    
    def open_settings(self):
        """Відкриття вікна налаштувань"""
        dialog = SettingsDialog(self.root, app_settings)
        if dialog.result:
            # Оновлення статусу після зміни налаштувань
            self.status_var.set(f"Папка збереження: {app_settings.get('save_folder')}")
            
            # Перегенерація QR-коду якщо змінились базові параметри
            if self.current_qr_image:
                self.generate_qr()
    
    def save_settings(self):
        """Збереження налаштувань при закритті"""
        # Збереження поточного типу QR-коду
        app_settings.set("last_qr_type", self.current_qr_type)
        
        # Збереження налаштувань дизайну
        design_settings = self.design_tab.get_current_settings()
        app_settings.update(design_settings)
        
        # Збереження в файл
        app_settings.save_settings()
    
    def on_closing(self):
        """Обробка закриття додатку"""
        self.save_settings()
        self.root.destroy()

# Імпортуємо io для роботи з буфером обміну
import io
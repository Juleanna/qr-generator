#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Вкладка дизайну QR-коду
"""

import tkinter as tk
from tkinter import ttk, colorchooser
from PIL import Image, ImageTk
from typing import Dict, Any, Optional

from ..config.settings import app_settings

class DesignTab:
    """Клас для управління вкладкою дизайну"""
    
    def __init__(self, parent: ttk.Notebook, main_window):
        self.parent = parent
        self.main_window = main_window
        
        # Створення фрейму
        self.frame = ttk.Frame(parent, padding="10")
        
        # Предустановлені кольори
        self.color_presets = {
            "Класичний": {"fg": "#000000", "bg": "#FFFFFF"},
            "Синій": {"fg": "#1E3A8A", "bg": "#FFFFFF"},
            "Зелений": {"fg": "#166534", "bg": "#FFFFFF"},
            "Червоний": {"fg": "#991B1B", "bg": "#FFFFFF"},
            "Фіолетовий": {"fg": "#7C3AED", "bg": "#FFFFFF"},
            "Темна тема": {"fg": "#FFFFFF", "bg": "#1F2937"},
            "Градація синього": {"fg": "#1E40AF", "bg": "#DBEAFE"},
            "Зелена градація": {"fg": "#059669", "bg": "#D1FAE5"}
        }
        
        # Стилі модулів
        self.module_styles = {
            "square": "Квадратні",
            "circle": "Круглі",
            "rounded": "Закруглені"
        }
        
        # Поточний QR код для превью
        self.current_qr_image = None
        self.preview_qr = None
        
        # Створення UI
        self.create_widgets()
        
        # Завантаження збережених налаштувань
        self.load_settings()
    
    def create_widgets(self):
        """Створення віджетів вкладки дизайну"""
        # Налаштування сітки
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # Ліва панель - налаштування
        self.create_settings_panel()
        
        # Права панель - превью
        self.create_preview_panel()
    
    def create_settings_panel(self):
        """Створення панелі налаштувань"""
        left_frame = ttk.Frame(self.frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Секція кольорів
        self.create_colors_section(left_frame)
        
        # Секція стилів
        self.create_styles_section(left_frame)
        
        # Секція експорту
        self.create_export_section(left_frame)
        
        # Кнопки
        self.create_design_buttons(left_frame)
    
    def create_colors_section(self, parent):
        """Створення секції налаштування кольорів"""
        colors_frame = ttk.LabelFrame(parent, text="Кольори", padding="10")
        colors_frame.pack(fill='x', pady=(0, 10))
        
        # Предустановлені схеми
        ttk.Label(colors_frame, text="Готові схеми:").pack(anchor='w', pady=(0, 5))
        
        self.color_preset_var = tk.StringVar(value="Класичний")
        preset_combo = ttk.Combobox(
            colors_frame,
            textvariable=self.color_preset_var,
            values=list(self.color_presets.keys()),
            state="readonly"
        )
        preset_combo.pack(fill='x', pady=(0, 10))
        preset_combo.bind('<<ComboboxSelected>>', self.on_preset_change)
        
        # Колір переднього плану
        fg_frame = ttk.Frame(colors_frame)
        fg_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(fg_frame, text="Колір QR-коду:").pack(side='left')
        self.fg_color_var = tk.StringVar(value="#000000")
        self.fg_color_btn = tk.Button(
            fg_frame,
            text="   ",
            bg=self.fg_color_var.get(),
            width=3,
            command=self.choose_fg_color
        )
        self.fg_color_btn.pack(side='right')
        
        # Колір фону
        bg_frame = ttk.Frame(colors_frame)
        bg_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(bg_frame, text="Колір фону:").pack(side='left')
        self.bg_color_var = tk.StringVar(value="#FFFFFF")
        self.bg_color_btn = tk.Button(
            bg_frame,
            text="   ",
            bg=self.bg_color_var.get(),
            width=3,
            command=self.choose_bg_color
        )
        self.bg_color_btn.pack(side='right')
        
        # Прозорий фон
        self.transparent_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            colors_frame,
            text="Прозорий фон (PNG)",
            variable=self.transparent_var,
            command=self.update_preview
        ).pack(anchor='w')
    
    def create_styles_section(self, parent):
        """Створення секції стилів"""
        style_frame = ttk.LabelFrame(parent, text="Стиль модулів", padding="10")
        style_frame.pack(fill='x', pady=(0, 10))
        
        self.module_style_var = tk.StringVar(value="square")
        
        for style_key, style_name in self.module_styles.items():
            ttk.Radiobutton(
                style_frame,
                text=style_name,
                variable=self.module_style_var,
                value=style_key,
                command=self.update_preview
            ).pack(anchor='w')
    
    def create_export_section(self, parent):
        """Створення секції експорту"""
        export_frame = ttk.LabelFrame(parent, text="Формат експорту", padding="10")
        export_frame.pack(fill='x', pady=(0, 10))
        
        self.export_format_var = tk.StringVar(value="PNG")
        
        # Доступні формати
        formats = ['PNG', 'JPG', 'SVG']
        
        for fmt in formats:
            ttk.Radiobutton(
                export_frame,
                text=fmt,
                variable=self.export_format_var,
                value=fmt,
                command=self.update_export_options
            ).pack(anchor='w')
        
        # Опції якості
        quality_frame = ttk.Frame(export_frame)
        quality_frame.pack(fill='x', pady=(10, 0))
        
        self.high_quality_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            quality_frame,
            text="Висока якість (800x800)",
            variable=self.high_quality_var
        ).pack(anchor='w')
        
        # Розмір файлу
        size_frame = ttk.Frame(export_frame)
        size_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(size_frame, text="Розмір (пікселі):").pack(side='left')
        self.size_var = tk.IntVar(value=400)
        size_scale = ttk.Scale(
            size_frame,
            from_=200,
            to=1200,
            variable=self.size_var,
            orient='horizontal'
        )
        size_scale.pack(side='left', fill='x', expand=True, padx=(10, 5))
        
        self.size_label = ttk.Label(size_frame, text="400")
        self.size_label.pack(side='right')
        
        # Оновлення лейблу розміру
        def update_size_label(*args):
            self.size_label.config(text=str(self.size_var.get()))
        
        self.size_var.trace('w', update_size_label)
    
    def create_design_buttons(self, parent):
        """Створення кнопок дизайну"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(
            buttons_frame,
            text="🔄 Оновити превью",
            command=self.update_preview
        ).pack(fill='x', pady=(0, 5))
        
        ttk.Button(
            buttons_frame,
            text="↻ Скинути до стандартних",
            command=self.reset_design
        ).pack(fill='x')
    
    def create_preview_panel(self):
        """Створення панелі превью"""
        right_frame = ttk.LabelFrame(self.frame, text="Попередній перегляд", padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Область превью
        self.preview_label = ttk.Label(
            right_frame,
            text="Превью з'явиться після генерації QR-коду",
            relief='sunken',
            anchor='center'
        )
        self.preview_label.pack(expand=True, fill='both')
        
        # Інформація про превью
        preview_info = ttk.Frame(right_frame)
        preview_info.pack(fill='x', pady=(10, 0))
        
        self.preview_info_label = ttk.Label(preview_info, text="", justify='center')
        self.preview_info_label.pack()
    
    def load_settings(self):
        """Завантаження збережених налаштувань"""
        self.fg_color_var.set(app_settings.get('fg_color', '#000000'))
        self.bg_color_var.set(app_settings.get('bg_color', '#FFFFFF'))
        self.module_style_var.set(app_settings.get('module_style', 'square'))
        self.export_format_var.set(app_settings.get('export_format', 'PNG'))
        self.high_quality_var.set(app_settings.get('high_quality', True))
        self.transparent_var.set(app_settings.get('transparent_bg', False))
        
        # Оновлення кнопок кольорів
        self.fg_color_btn.config(bg=self.fg_color_var.get())
        self.bg_color_btn.config(bg=self.bg_color_var.get())
    
    def on_preset_change(self, event=None):
        """Обробка зміни кольорової схеми"""
        preset_name = self.color_preset_var.get()
        if preset_name in self.color_presets:
            colors = self.color_presets[preset_name]
            
            self.fg_color_var.set(colors['fg'])
            self.bg_color_var.set(colors['bg'])
            
            self.fg_color_btn.config(bg=colors['fg'])
            self.bg_color_btn.config(bg=colors['bg'])
            
            self.update_preview()
    
    def choose_fg_color(self):
        """Вибір кольору переднього плану"""
        color = colorchooser.askcolor(initialcolor=self.fg_color_var.get())
        if color[1]:
            self.fg_color_var.set(color[1])
            self.fg_color_btn.config(bg=color[1])
            self.color_preset_var.set("Власний")
            self.update_preview()
    
    def choose_bg_color(self):
        """Вибір кольору фону"""
        color = colorchooser.askcolor(initialcolor=self.bg_color_var.get())
        if color[1]:
            self.bg_color_var.set(color[1])
            self.bg_color_btn.config(bg=color[1])
            self.color_preset_var.set("Власний")
            self.update_preview()
    
    def update_export_options(self):
        """Оновлення опцій експорту"""
        fmt = self.export_format_var.get()
        if fmt == 'SVG':
            self.high_quality_var.set(False)  # SVG не потребує високої роздільності
    
    def reset_design(self):
        """Скидання дизайну до стандартних налаштувань"""
        self.fg_color_var.set("#000000")
        self.bg_color_var.set("#FFFFFF")
        self.fg_color_btn.config(bg="#000000")
        self.bg_color_btn.config(bg="#FFFFFF")
        self.module_style_var.set("square")
        self.export_format_var.set("PNG")
        self.transparent_var.set(False)
        self.high_quality_var.set(True)
        self.color_preset_var.set("Класичний")
        self.size_var.set(400)
        self.update_preview()
    
    def update_preview(self, qr_image: Optional[Image.Image] = None):
        """Оновлення превью QR-коду"""
        if qr_image:
            self.current_qr_image = qr_image
        
        if not self.current_qr_image:
            return
        
        try:
            # Створення стилізованого зображення
            preview_image = self.create_styled_qr_image(self.current_qr_image, preview=True)
            
            # Зміна розміру для превью
            display_size = (250, 250)
            preview_display = preview_image.resize(display_size, Image.Resampling.LANCZOS)
            
            # Конвертація для tkinter
            self.preview_qr = ImageTk.PhotoImage(preview_display)
            self.preview_label.configure(image=self.preview_qr, text="")
            
            # Оновлення інформації
            self.update_preview_info()
            
            # Оновлення основного відображення
            if hasattr(self.main_window, 'display_qr_image'):
                self.main_window.display_qr_image()
            
        except Exception as e:
            print(f"Помилка оновлення превью: {e}")
    
    def update_preview_info(self):
        """Оновлення інформації про превью"""
        style_name = self.module_styles[self.module_style_var.get()]
        colors_info = f"Кольори: {self.fg_color_var.get()} / {self.bg_color_var.get()}"
        format_info = f"Формат: {self.export_format_var.get()}"
        size_info = f"Розмір: {self.size_var.get()}x{self.size_var.get()}"
        
        info_text = f"{style_name}\n{colors_info}\n{format_info}\n{size_info}"
        self.preview_info_label.config(text=info_text)
    
    def clear_preview(self):
        """Очищення превью"""
        self.current_qr_image = None
        self.preview_qr = None
        self.preview_label.configure(
            image='',
            text="Превью з'явиться після генерації QR-коду"
        )
        self.preview_info_label.config(text="")
    
    def create_styled_qr_image(self, base_qr_image: Image.Image, preview: bool = False) -> Image.Image:
        """Створення стилізованого QR-коду"""
        # Отримання кольорів
        fg_color = self.fg_color_var.get()
        bg_color = self.bg_color_var.get() if not self.transparent_var.get() else None
        
        # Копіювання базового зображення
        styled_image = base_qr_image.copy()
        
        # Застосування кольорів
        if fg_color != "#000000" or bg_color != "#FFFFFF" or self.transparent_var.get():
            styled_image = styled_image.convert("RGBA")
            data = styled_image.getdata()
            
            new_data = []
            for item in data:
                # Заміна чорного на вибраний колір переднього плану
                if item[:3] == (0, 0, 0):  # чорний піксель
                    rgb = tuple(int(fg_color[i:i+2], 16) for i in (1, 3, 5))
                    new_data.append(rgb + (255,))
                # Заміна білого на колір фону або прозорий
                elif item[:3] == (255, 255, 255):  # білий піксель
                    if self.transparent_var.get():
                        new_data.append((255, 255, 255, 0))  # прозорий
                    else:
                        rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                        new_data.append(rgb + (255,))
                else:
                    new_data.append(item)
            
            styled_image.putdata(new_data)
            
            # Конвертація назад в RGB якщо фон не прозорий
            if not self.transparent_var.get():
                styled_image = styled_image.convert("RGB")
        
        return styled_image
    
    def get_export_format(self) -> str:
        """Отримання формату експорту"""
        return self.export_format_var.get().lower()
    
    def get_export_settings(self) -> Dict[str, Any]:
        """Отримання налаштувань експорту"""
        return {
            'fg_color': self.fg_color_var.get(),
            'bg_color': self.bg_color_var.get(),
            'transparent_bg': self.transparent_var.get(),
            'module_style': self.module_style_var.get(),
            'format': self.export_format_var.get(),
            'high_quality': self.high_quality_var.get(),
            'size': self.size_var.get()
        }
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Отримання поточних налаштувань для збереження"""
        return {
            'fg_color': self.fg_color_var.get(),
            'bg_color': self.bg_color_var.get(),
            'transparent_bg': self.transparent_var.get(),
            'module_style': self.module_style_var.get(),
            'export_format': self.export_format_var.get(),
            'high_quality': self.high_quality_var.get()
        }
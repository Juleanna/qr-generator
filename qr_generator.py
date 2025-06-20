import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, colorchooser
import qrcode
from PIL import Image, ImageTk, ImageDraw
import os
import json
from datetime import datetime
import re
import urllib.parse
import io
import base64

# Для SVG експорту
try:
    import svgwrite
    SVG_AVAILABLE = True
except ImportError:
    SVG_AVAILABLE = False

class QRCodeGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator Pro v2.0")
        self.root.geometry("1100x900")
        self.root.resizable(True, True)
        
        # Загрузка настроек
        self.settings_file = "qr_settings.json"
        self.load_settings()
        
        # QR код переменные
        self.current_qr_image = None
        self.qr_photo = None
        self.current_qr_type = "text"
        self.preview_qr = None
        
        # Типи QR-кодів та їх генератори
        self.qr_types = {
            "text": {
                "name": "📝 Звичайний текст",
                "generator": self.generate_text_qr,
                "validator": self.validate_text
            },
            "url": {
                "name": "🌐 Веб-сайт (URL)",
                "generator": self.generate_url_qr,
                "validator": self.validate_url
            },
            "email": {
                "name": "📧 Email",
                "generator": self.generate_email_qr,
                "validator": self.validate_email
            },
            "phone": {
                "name": "📞 Телефон",
                "generator": self.generate_phone_qr,
                "validator": self.validate_phone
            },
            "sms": {
                "name": "💬 SMS",
                "generator": self.generate_sms_qr,
                "validator": self.validate_sms
            },
            "wifi": {
                "name": "📶 WiFi",
                "generator": self.generate_wifi_qr,
                "validator": self.validate_wifi
            },
            "vcard": {
                "name": "👤 Візитка (vCard)",
                "generator": self.generate_vcard_qr,
                "validator": self.validate_vcard
            }
        }
        
        # Предустановленные цвета
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
        
        # Стили модулів QR-коду
        self.module_styles = {
            "square": "Квадратні",
            "circle": "Круглі", 
            "rounded": "Закруглені"
        }
        
        # Создание интерфейса
        self.create_widgets()
        
    def load_settings(self):
        """Загрузка настроек из файла"""
        default_settings = {
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
            "transparent_bg": False
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                for key, value in default_settings.items():
                    if key not in self.settings:
                        self.settings[key] = value
            else:
                self.settings = default_settings
        except:
            self.settings = default_settings
            
    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            self.settings["last_qr_type"] = self.current_qr_type
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти налаштування: {str(e)}")
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Главный контейнер с Notebook
        main_notebook = ttk.Notebook(self.root, padding="5")
        main_notebook.pack(fill='both', expand=True)
        
        # Вкладка "Создание QR-кода"
        create_frame = ttk.Frame(main_notebook, padding="10")
        main_notebook.add(create_frame, text="Створення QR-коду")
        
        # Вкладка "Дизайн"
        design_frame = ttk.Frame(main_notebook, padding="10")
        main_notebook.add(design_frame, text="Дизайн")
        
        # Настройка весов для адаптивности
        create_frame.columnconfigure(1, weight=1)
        design_frame.columnconfigure(1, weight=1)
        
        # === ВКЛАДКА СОЗДАНИЯ ===
        self.create_main_tab(create_frame)
        
        # === ВКЛАДКА ДИЗАЙНА ===
        self.create_design_tab(design_frame)
        
    def create_main_tab(self, parent):
        """Создание основной вкладки"""
        # Выбор типа QR-кода
        ttk.Label(parent, text="Оберіть тип QR-коду:").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        self.qr_type_var = tk.StringVar(value=self.settings.get("last_qr_type", "text"))
        self.current_qr_type = self.qr_type_var.get()
        
        type_frame = ttk.Frame(parent)
        type_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.type_combo = ttk.Combobox(type_frame, textvariable=self.qr_type_var, state="readonly", width=30)
        self.type_combo['values'] = [self.qr_types[key]["name"] for key in self.qr_types.keys()]
        self.type_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.type_combo.bind('<<ComboboxSelected>>', self.on_type_change)
        
        # Установка текущего значения
        current_type_name = self.qr_types[self.current_qr_type]["name"]
        self.type_combo.set(current_type_name)
        
        type_frame.columnconfigure(0, weight=1)
        
        # Контейнер для полей ввода
        self.input_container = ttk.LabelFrame(parent, text="Введіть дані:", padding="10")
        self.input_container.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Создание полей для текущего типа
        self.create_input_fields()
        
        # Кнопки управления
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        
        self.generate_btn = ttk.Button(buttons_frame, text="Згенерувати QR-код", command=self.generate_qr)
        self.generate_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        self.save_btn = ttk.Button(buttons_frame, text="Зберегти QR-код", command=self.save_qr, state='disabled')
        self.save_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.settings_btn = ttk.Button(buttons_frame, text="Налаштування", command=self.open_settings)
        self.settings_btn.grid(row=0, column=2, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # Фрейм для отображения QR-кода
        qr_frame = ttk.LabelFrame(parent, text="Згенерований QR-код", padding="10")
        qr_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        parent.rowconfigure(4, weight=1)
        
        self.qr_label = ttk.Label(qr_frame, text="QR-код з'явиться тут після генерації", 
                                 relief='sunken', anchor='center')
        self.qr_label.pack(expand=True, fill='both')
        
        # Информация о типе
        self.info_frame = ttk.LabelFrame(parent, text="Інформація", padding="5")
        self.info_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.info_label = ttk.Label(self.info_frame, text="", wraplength=600, justify='left')
        self.info_label.pack(fill='x')
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set(f"Папка збереження: {self.settings['save_folder']}")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief='sunken')
        status_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Обновляем информацию о текущем типе
        self.update_type_info()
        
    def create_design_tab(self, parent):
        """Создание вкладки дизайна"""
        # Левая панель - настройки
        left_frame = ttk.Frame(parent)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Правая панель - превью
        right_frame = ttk.LabelFrame(parent, text="Попередній перегляд", padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # === НАСТРОЙКИ ЦВЕТОВ ===
        colors_frame = ttk.LabelFrame(left_frame, text="Кольори", padding="10")
        colors_frame.pack(fill='x', pady=(0, 10))
        
        # Предустановленные цвета
        ttk.Label(colors_frame, text="Готові схеми:").pack(anchor='w', pady=(0, 5))
        
        self.color_preset_var = tk.StringVar(value="Класичний")
        preset_combo = ttk.Combobox(colors_frame, textvariable=self.color_preset_var, 
                                   values=list(self.color_presets.keys()), state="readonly")
        preset_combo.pack(fill='x', pady=(0, 10))
        preset_combo.bind('<<ComboboxSelected>>', self.on_preset_change)
        
        # Цвет переднего плана
        fg_frame = ttk.Frame(colors_frame)
        fg_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(fg_frame, text="Колір QR-коду:").pack(side='left')
        self.fg_color_var = tk.StringVar(value=self.settings.get('fg_color', '#000000'))
        self.fg_color_btn = tk.Button(fg_frame, text="   ", bg=self.fg_color_var.get(), 
                                     width=3, command=self.choose_fg_color)
        self.fg_color_btn.pack(side='right')
        
        # Цвет фона
        bg_frame = ttk.Frame(colors_frame)
        bg_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(bg_frame, text="Колір фону:").pack(side='left')
        self.bg_color_var = tk.StringVar(value=self.settings.get('bg_color', '#FFFFFF'))
        self.bg_color_btn = tk.Button(bg_frame, text="   ", bg=self.bg_color_var.get(), 
                                     width=3, command=self.choose_bg_color)
        self.bg_color_btn.pack(side='right')
        
        # Прозрачный фон
        self.transparent_var = tk.BooleanVar(value=self.settings.get('transparent_bg', False))
        ttk.Checkbutton(colors_frame, text="Прозорий фон (PNG)", 
                       variable=self.transparent_var, command=self.update_preview).pack(anchor='w')
        
        # === СТИЛЬ МОДУЛЕЙ ===
        style_frame = ttk.LabelFrame(left_frame, text="Стиль модулів", padding="10")
        style_frame.pack(fill='x', pady=(0, 10))
        
        self.module_style_var = tk.StringVar(value=self.settings.get('module_style', 'square'))
        
        for style_key, style_name in self.module_styles.items():
            ttk.Radiobutton(style_frame, text=style_name, variable=self.module_style_var, 
                           value=style_key, command=self.update_preview).pack(anchor='w')
        
        # === ФОРМАТ ЕКСПОРТУ ===
        export_frame = ttk.LabelFrame(left_frame, text="Формат експорту", padding="10")
        export_frame.pack(fill='x', pady=(0, 10))
        
        self.export_format_var = tk.StringVar(value=self.settings.get('export_format', 'PNG'))
        
        formats = ['PNG', 'JPG', 'SVG']
        if not SVG_AVAILABLE:
            formats.remove('SVG')
            
        for fmt in formats:
            ttk.Radiobutton(export_frame, text=fmt, variable=self.export_format_var, 
                           value=fmt, command=self.update_export_options).pack(anchor='w')
        
        # Опції якості
        quality_frame = ttk.Frame(export_frame)
        quality_frame.pack(fill='x', pady=(10, 0))
        
        self.high_quality_var = tk.BooleanVar(value=self.settings.get('high_quality', True))
        ttk.Checkbutton(quality_frame, text="Висока якість (800x800)", 
                       variable=self.high_quality_var).pack(anchor='w')
        
        # === КНОПКИ ДИЗАЙНА ===
        design_buttons_frame = ttk.Frame(left_frame)
        design_buttons_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(design_buttons_frame, text="Оновити превью", 
                  command=self.update_preview).pack(fill='x', pady=(0, 5))
        ttk.Button(design_buttons_frame, text="Скинути до стандартних", 
                  command=self.reset_design).pack(fill='x')
        
        # === ПРЕВЬЮ ===
        self.preview_label = ttk.Label(right_frame, text="Превью з'явиться після генерації QR-коду", 
                                      relief='sunken', anchor='center')
        self.preview_label.pack(expand=True, fill='both')
        
        # Информация о превью
        preview_info = ttk.Frame(right_frame)
        preview_info.pack(fill='x', pady=(10, 0))
        
        self.preview_info_label = ttk.Label(preview_info, text="", justify='center')
        self.preview_info_label.pack()
        
    def on_preset_change(self, event=None):
        """Обработка изменения цветовой схемы"""
        preset_name = self.color_preset_var.get()
        if preset_name in self.color_presets:
            colors = self.color_presets[preset_name]
            
            self.fg_color_var.set(colors['fg'])
            self.bg_color_var.set(colors['bg'])
            
            self.fg_color_btn.config(bg=colors['fg'])
            self.bg_color_btn.config(bg=colors['bg'])
            
            self.update_preview()
    
    def choose_fg_color(self):
        """Выбор цвета переднего плана"""
        color = colorchooser.askcolor(initialcolor=self.fg_color_var.get())
        if color[1]:
            self.fg_color_var.set(color[1])
            self.fg_color_btn.config(bg=color[1])
            self.color_preset_var.set("Власний")
            self.update_preview()
    
    def choose_bg_color(self):
        """Выбор цвета фона"""
        color = colorchooser.askcolor(initialcolor=self.bg_color_var.get())
        if color[1]:
            self.bg_color_var.set(color[1])
            self.bg_color_btn.config(bg=color[1])
            self.color_preset_var.set("Власний")
            self.update_preview()
    
    def update_export_options(self):
        """Обновление опций экспорта"""
        fmt = self.export_format_var.get()
        if fmt == 'SVG':
            self.high_quality_var.set(False)  # SVG не нуждается в высоком разрешении
    
    def reset_design(self):
        """Сброс дизайна к стандартным настройкам"""
        self.fg_color_var.set("#000000")
        self.bg_color_var.set("#FFFFFF")
        self.fg_color_btn.config(bg="#000000")
        self.bg_color_btn.config(bg="#FFFFFF")
        self.module_style_var.set("square")
        self.export_format_var.set("PNG")
        self.transparent_var.set(False)
        self.high_quality_var.set(True)
        self.color_preset_var.set("Класичний")
        self.update_preview()
    
    def update_preview(self):
        """Обновление превью QR-кода"""
        if not self.current_qr_image:
            return
            
        try:
            # Создаем превью с текущими настройками дизайна
            preview_image = self.create_styled_qr_image(self.current_qr_image, preview=True)
            
            # Изменяем размер для превью
            display_size = (250, 250)
            preview_display = preview_image.resize(display_size, Image.Resampling.LANCZOS)
            
            # Конвертация для tkinter
            self.preview_qr = ImageTk.PhotoImage(preview_display)
            self.preview_label.configure(image=self.preview_qr, text="")
            
            # Обновляем информацию
            style_name = self.module_styles[self.module_style_var.get()]
            colors_info = f"Кольори: {self.fg_color_var.get()} / {self.bg_color_var.get()}"
            format_info = f"Формат: {self.export_format_var.get()}"
            self.preview_info_label.config(text=f"{style_name}\n{colors_info}\n{format_info}")
            
        except Exception as e:
            print(f"Помилка оновлення превью: {e}")
    
    def create_styled_qr_image(self, base_qr_image, preview=False):
        """Создание стилизованного QR-кода"""
        # Получаем цвета
        fg_color = self.fg_color_var.get()
        bg_color = self.bg_color_var.get() if not self.transparent_var.get() else None
        
        # Для простоты пока используем стандартные цвета
        # В будущих версиях можно добавить более сложную стилизацию
        styled_image = base_qr_image.copy()
        
        # Применяем цвета
        if fg_color != "#000000" or bg_color != "#FFFFFF":
            # Конвертируем в RGBA для работы с цветами
            styled_image = styled_image.convert("RGBA")
            data = styled_image.getdata()
            
            new_data = []
            for item in data:
                # Заменяем черный на выбранный цвет переднего плана
                if item[:3] == (0, 0, 0):  # черный пиксель
                    rgb = tuple(int(fg_color[i:i+2], 16) for i in (1, 3, 5))
                    new_data.append(rgb + (255,))
                # Заменяем белый на цвет фона или делаем прозрачным
                elif item[:3] == (255, 255, 255):  # белый пиксель
                    if self.transparent_var.get():
                        new_data.append((255, 255, 255, 0))  # прозрачный
                    else:
                        rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                        new_data.append(rgb + (255,))
                else:
                    new_data.append(item)
            
            styled_image.putdata(new_data)
            
            # Конвертируем обратно в RGB если фон не прозрачный
            if not self.transparent_var.get():
                styled_image = styled_image.convert("RGB")
        
        return styled_image
    
    def on_type_change(self, event=None):
        """Обработка изменения типа QR-кода"""
        selected_name = self.qr_type_var.get()
        
        # Находим ключ по имени
        for key, value in self.qr_types.items():
            if value["name"] == selected_name:
                self.current_qr_type = key
                break
        
        # Пересоздаем поля ввода
        self.create_input_fields()
        self.update_type_info()
        
        # Очищаем QR-код
        self.current_qr_image = None
        self.qr_photo = None
        self.preview_qr = None
        self.qr_label.configure(image='', text="QR-код з'явиться тут після генерації")
        self.preview_label.configure(image='', text="Превью з'явиться після генерації QR-коду")
        self.save_btn.configure(state='disabled')
    
    def create_input_fields(self):
        """Создание полей ввода в зависимости от типа QR-кода"""
        # Очищаем контейнер
        for widget in self.input_container.winfo_children():
            widget.destroy()
        
        self.input_widgets = {}
        
        if self.current_qr_type == "text":
            self.create_text_fields()
        elif self.current_qr_type == "url":
            self.create_url_fields()
        elif self.current_qr_type == "email":
            self.create_email_fields()
        elif self.current_qr_type == "phone":
            self.create_phone_fields()
        elif self.current_qr_type == "sms":
            self.create_sms_fields()
        elif self.current_qr_type == "wifi":
            self.create_wifi_fields()
        elif self.current_qr_type == "vcard":
            self.create_vcard_fields()
    
    def create_text_fields(self):
        """Поля для обычного текста"""
        ttk.Label(self.input_container, text="Текст:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['text'] = scrolledtext.ScrolledText(self.input_container, width=60, height=6, wrap=tk.WORD)
        self.input_widgets['text'].pack(fill='both', expand=True)
    
    def create_url_fields(self):
        """Поля для URL"""
        ttk.Label(self.input_container, text="URL веб-сайту:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['url'] = tk.Entry(self.input_container, width=60)
        self.input_widgets['url'].pack(fill='x', pady=(0, 5))
        self.input_widgets['url'].insert(0, "https://")
        
        ttk.Label(self.input_container, text="Приклад: https://www.google.com").pack(anchor='w')
    
    def create_email_fields(self):
        """Поля для email"""
        ttk.Label(self.input_container, text="Email адреса:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['email'] = tk.Entry(self.input_container, width=60)
        self.input_widgets['email'].pack(fill='x', pady=(0, 10))
        
        ttk.Label(self.input_container, text="Тема листа (необов'язково):").pack(anchor='w', pady=(0, 5))
        self.input_widgets['subject'] = tk.Entry(self.input_container, width=60)
        self.input_widgets['subject'].pack(fill='x', pady=(0, 10))
        
        ttk.Label(self.input_container, text="Текст листа (необов'язково):").pack(anchor='w', pady=(0, 5))
        self.input_widgets['body'] = scrolledtext.ScrolledText(self.input_container, width=60, height=4, wrap=tk.WORD)
        self.input_widgets['body'].pack(fill='both', expand=True)
    
    def create_phone_fields(self):
        """Поля для телефона"""
        ttk.Label(self.input_container, text="Номер телефону:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['phone'] = tk.Entry(self.input_container, width=60)
        self.input_widgets['phone'].pack(fill='x', pady=(0, 5))
        self.input_widgets['phone'].insert(0, "+380")
        
        ttk.Label(self.input_container, text="Приклад: +380123456789").pack(anchor='w')
    
    def create_sms_fields(self):
        """Поля для SMS"""
        ttk.Label(self.input_container, text="Номер телефону:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['phone'] = tk.Entry(self.input_container, width=60)
        self.input_widgets['phone'].pack(fill='x', pady=(0, 10))
        self.input_widgets['phone'].insert(0, "+380")
        
        ttk.Label(self.input_container, text="Текст повідомлення:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['message'] = scrolledtext.ScrolledText(self.input_container, width=60, height=4, wrap=tk.WORD)
        self.input_widgets['message'].pack(fill='both', expand=True)
    
    def create_wifi_fields(self):
        """Поля для WiFi"""
        ttk.Label(self.input_container, text="Назва мережі (SSID):").pack(anchor='w', pady=(0, 5))
        self.input_widgets['ssid'] = tk.Entry(self.input_container, width=60)
        self.input_widgets['ssid'].pack(fill='x', pady=(0, 10))
        
        ttk.Label(self.input_container, text="Пароль:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['password'] = tk.Entry(self.input_container, width=60, show="*")
        self.input_widgets['password'].pack(fill='x', pady=(0, 10))
        
        ttk.Label(self.input_container, text="Тип шифрування:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['security'] = ttk.Combobox(self.input_container, values=['WPA', 'WEP', 'nopass'], state="readonly")
        self.input_widgets['security'].set('WPA')
        self.input_widgets['security'].pack(fill='x', pady=(0, 10))
        
        self.input_widgets['hidden'] = tk.BooleanVar()
        ttk.Checkbutton(self.input_container, text="Прихована мережа", variable=self.input_widgets['hidden']).pack(anchor='w')
    
    def create_vcard_fields(self):
        """Поля для vCard"""
        # Основна інформація
        ttk.Label(self.input_container, text="Ім'я:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['first_name'] = tk.Entry(self.input_container, width=60)
        self.input_widgets['first_name'].pack(fill='x', pady=(0, 5))
        
        ttk.Label(self.input_container, text="Прізвище:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['last_name'] = tk.Entry(self.input_container, width=60)
        self.input_widgets['last_name'].pack(fill='x', pady=(0, 10))
        
        # Контактна інформація
        contact_frame = ttk.LabelFrame(self.input_container, text="Контактна інформація", padding="5")
        contact_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(contact_frame, text="Організація:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['organization'] = tk.Entry(contact_frame, width=60)
        self.input_widgets['organization'].pack(fill='x', pady=(0, 5))
        
        ttk.Label(contact_frame, text="Посада:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['title'] = tk.Entry(contact_frame, width=60)
        self.input_widgets['title'].pack(fill='x', pady=(0, 5))
        
        ttk.Label(contact_frame, text="Телефон:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['phone'] = tk.Entry(contact_frame, width=60)
        self.input_widgets['phone'].pack(fill='x', pady=(0, 5))
        
        ttk.Label(contact_frame, text="Email:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['email'] = tk.Entry(contact_frame, width=60)
        self.input_widgets['email'].pack(fill='x', pady=(0, 5))
        
        ttk.Label(contact_frame, text="Веб-сайт:").pack(anchor='w', pady=(0, 5))
        self.input_widgets['website'] = tk.Entry(contact_frame, width=60)
        self.input_widgets['website'].pack(fill='x')
    
    def update_type_info(self):
        """Обновление информации о типе QR-кода"""
        info_texts = {
            "text": "Звичайний текст - найпростіший тип QR-коду. Може містити будь-який текст до 4296 символів.",
            "url": "URL QR-код - перенаправляє користувача на веб-сайт при скануванні. Не забудьте включити http:// або https://",
            "email": "Email QR-код - створює новий лист з вказаною адресою, темою та текстом в поштовому клієнті користувача.",
            "phone": "Телефонний QR-код - дозволяє користувачеві зателефонувати на вказаний номер одним дотиком.",
            "sms": "SMS QR-код - відкриває додаток повідомлень з заповненим номером та текстом повідомлення.",
            "wifi": "WiFi QR-код - автоматично підключає пристрій до WiFi мережі без ручного введення паролю.",
            "vcard": "vCard (Візитка) - зберігає контактну інформацію в телефонну книгу користувача при скануванні."
        }
        
        self.info_label.config(text=info_texts.get(self.current_qr_type, ""))
    
    # Валідатори
    def validate_text(self, data):
        """Валідація звичайного тексту"""
        text = data.get('text', '').strip()
        if not text:
            return False, "Будь ласка, введіть текст"
        if len(text) > 4296:
            return False, "Текст занадто довгий (максимум 4296 символів)"
        return True, text
    
    def validate_url(self, data):
        """Валідація URL"""
        url = data.get('url', '').strip()
        if not url:
            return False, "Будь ласка, введіть URL"
        
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url
        
        # Спрощена валідація URL
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False, "Невірний формат URL"
        except:
            return False, "Невірний формат URL"
        
        return True, url
    
    def validate_email(self, data):
        """Валідація email"""
        email = data.get('email', '').strip()
        if not email:
            return False, "Будь ласка, введіть email адресу"
        
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$')
        if not email_pattern.match(email):
            return False, "Невірний формат email адреси"
        
        return True, email
    
    def validate_phone(self, data):
        """Валідація телефону"""
        phone = data.get('phone', '').strip()
        if not phone:
            return False, "Будь ласка, введіть номер телефону"
        
        phone_clean = re.sub(r'[^\d+]', '', phone)
        
        if not phone_clean.startswith('+'):
            return False, "Номер телефону повинен починатися з +"
        
        if len(phone_clean) < 10 or len(phone_clean) > 15:
            return False, "Невірна довжина номера телефону"
        
        return True, phone_clean
    
    def validate_sms(self, data):
        """Валідація SMS"""
        phone_valid, phone_result = self.validate_phone(data)
        if not phone_valid:
            return False, phone_result
        
        message = data.get('message', '').strip()
        if len(message) > 160:
            return False, "Повідомлення занадто довге (максимум 160 символів)"
        
        return True, (phone_result, message)
    
    def validate_wifi(self, data):
        """Валідація WiFi"""
        ssid = data.get('ssid', '').strip()
        if not ssid:
            return False, "Будь ласка, введіть назву мережі (SSID)"
        
        password = data.get('password', '').strip()
        security = data.get('security', 'WPA')
        
        if security != 'nopass' and not password:
            return False, "Будь ласка, введіть пароль для захищеної мережі"
        
        return True, (ssid, password, security)
    
    def validate_vcard(self, data):
        """Валідація vCard"""
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        if not first_name and not last_name:
            return False, "Будь ласка, введіть хоча б ім'я або прізвище"
        
        return True, data
    
    # Генератори для різних типів
    def generate_text_qr(self, data):
        """Генерація QR для звичайного тексту"""
        return data.get('text', '').strip()
    
    def generate_url_qr(self, data):
        """Генерація QR для URL"""
        return data.get('url', '').strip()
    
    def generate_email_qr(self, data):
        """Генерація QR для email"""
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        body = data.get('body', '').strip()
        
        mailto_url = f"mailto:{email}"
        params = []
        
        if subject:
            params.append(f"subject={urllib.parse.quote(subject)}")
        if body:
            params.append(f"body={urllib.parse.quote(body)}")
        
        if params:
            mailto_url += "?" + "&".join(params)
        
        return mailto_url
    
    def generate_phone_qr(self, data):
        """Генерація QR для телефону"""
        phone = data.get('phone', '').strip()
        return f"tel:{phone}"
    
    def generate_sms_qr(self, data):
        """Генерація QR для SMS"""
        phone = data.get('phone', '').strip()
        message = data.get('message', '').strip()
        
        sms_url = f"sms:{phone}"
        if message:
            sms_url += f"?body={urllib.parse.quote(message)}"
        
        return sms_url
    
    def generate_wifi_qr(self, data):
        """Генерація QR для WiFi"""
        ssid = data.get('ssid', '').strip()
        password = data.get('password', '').strip()
        security = data.get('security', 'WPA')
        hidden = data.get('hidden', False)
        
        wifi_string = f"WIFI:T:{security};S:{ssid};P:{password};H:{'true' if hidden else 'false'};;"
        return wifi_string
    
    def generate_vcard_qr(self, data):
        """Генерація QR для vCard"""
        vcard_lines = ["BEGIN:VCARD", "VERSION:3.0"]
        
        # Ім'я
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        if first_name or last_name:
            vcard_lines.append(f"FN:{first_name} {last_name}".strip())
            vcard_lines.append(f"N:{last_name};{first_name};;;")
        
        # Організація та посада
        organization = data.get('organization', '').strip()
        if organization:
            vcard_lines.append(f"ORG:{organization}")
        
        title = data.get('title', '').strip()
        if title:
            vcard_lines.append(f"TITLE:{title}")
        
        # Контакти
        phone = data.get('phone', '').strip()
        if phone:
            vcard_lines.append(f"TEL:{phone}")
        
        email = data.get('email', '').strip()
        if email:
            vcard_lines.append(f"EMAIL:{email}")
        
        website = data.get('website', '').strip()
        if website:
            if not website.startswith(('http://', 'https://')):
                website = 'https://' + website
            vcard_lines.append(f"URL:{website}")
        
        vcard_lines.append("END:VCARD")
        return "\n".join(vcard_lines)
    
    def get_input_data(self):
        """Получение данных из полей ввода"""
        data = {}
        
        for key, widget in self.input_widgets.items():
            if isinstance(widget, (tk.Entry, ttk.Combobox)):
                data[key] = widget.get()
            elif isinstance(widget, scrolledtext.ScrolledText):
                data[key] = widget.get(1.0, tk.END).strip()
            elif isinstance(widget, tk.BooleanVar):
                data[key] = widget.get()
        
        return data
    
    def generate_qr(self):
        """Генерация QR-кода"""
        try:
            # Получаем данные из полей
            input_data = self.get_input_data()
            
            # Валидация
            is_valid, result = self.qr_types[self.current_qr_type]["validator"](input_data)
            if not is_valid:
                messagebox.showwarning("Помилка валідації", result)
                return
            
            # Генерация текста для QR-кода
            qr_text = self.qr_types[self.current_qr_type]["generator"](input_data)
            
            # Создание QR-кода
            error_levels = {
                'L': qrcode.constants.ERROR_CORRECT_L,
                'M': qrcode.constants.ERROR_CORRECT_M,
                'Q': qrcode.constants.ERROR_CORRECT_Q,
                'H': qrcode.constants.ERROR_CORRECT_H
            }
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=error_levels.get(self.settings['error_correction'], qrcode.constants.ERROR_CORRECT_M),
                box_size=self.settings['box_size'],
                border=self.settings['border'],
            )
            
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            # Создание базового изображения
            self.current_qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Создание стилизованного изображения для отображения
            styled_image = self.create_styled_qr_image(self.current_qr_image)
            
            # Изменение размера для отображения в основной вкладке
            display_size = (300, 300)
            display_image = styled_image.resize(display_size, Image.Resampling.LANCZOS)
            
            # Конвертация для tkinter
            self.qr_photo = ImageTk.PhotoImage(display_image)
            self.qr_label.configure(image=self.qr_photo, text="")
            
            # Обновляем превью в дизайне
            self.update_preview()
            
            # Активация кнопки сохранения
            self.save_btn.configure(state='normal')
            
            # Информация о размере данных
            data_length = len(qr_text.encode('utf-8'))
            type_name = self.qr_types[self.current_qr_type]["name"]
            self.status_var.set(f"QR-код згенеровано ({type_name}) | Розмір даних: {data_length} байт")
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при генерації QR-коду: {str(e)}")
    
    def save_qr(self):
        """Сохранение QR-кода"""
        if not self.current_qr_image:
            messagebox.showwarning("Попередження", "Спочатку згенеруйте QR-код")
            return
        
        try:
            # Создание папки если она не существует
            os.makedirs(self.settings['save_folder'], exist_ok=True)
            
            # Генерация имени файла с типом и временной меткой
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            type_name = self.current_qr_type.upper()
            export_format = self.export_format_var.get().lower()
            
            filename = f"QR_{type_name}_{timestamp}.{export_format}"
            filepath = os.path.join(self.settings['save_folder'], filename)
            
            # Создание финального изображения
            final_image = self.create_styled_qr_image(self.current_qr_image)
            
            # Определение размера
            if self.high_quality_var.get() and export_format != 'svg':
                final_size = (800, 800)
                final_image = final_image.resize(final_size, Image.Resampling.LANCZOS)
            
            # Сохранение в зависимости от формата
            if export_format == 'svg':
                self.save_as_svg(filepath)
            elif export_format == 'png':
                final_image.save(filepath, 'PNG', optimize=True)
            elif export_format == 'jpg':
                # JPG не поддерживает прозрачность
                if final_image.mode == 'RGBA':
                    # Создаем белый фон
                    jpg_image = Image.new('RGB', final_image.size, 'white')
                    jpg_image.paste(final_image, mask=final_image.split()[-1])
                    final_image = jpg_image
                final_image.save(filepath, 'JPEG', quality=95, optimize=True)
            
            self.status_var.set(f"QR-код збережено: {filename}")
            messagebox.showinfo("Успіх", f"QR-код збережено як:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при збереженні: {str(e)}")
    
    def save_as_svg(self, filepath):
        """Сохранение в формате SVG"""
        if not SVG_AVAILABLE:
            messagebox.showerror("Помилка", "SVG експорт недоступний. Встановіть svgwrite: pip install svgwrite")
            return
        
        try:
            # Создаем базовый QR-код для получения матрицы
            input_data = self.get_input_data()
            qr_text = self.qr_types[self.current_qr_type]["generator"](input_data)
            
            error_levels = {
                'L': qrcode.constants.ERROR_CORRECT_L,
                'M': qrcode.constants.ERROR_CORRECT_M,
                'Q': qrcode.constants.ERROR_CORRECT_Q,
                'H': qrcode.constants.ERROR_CORRECT_H
            }
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=error_levels.get(self.settings['error_correction'], qrcode.constants.ERROR_CORRECT_M),
                box_size=1,  # Для SVG используем размер 1
                border=self.settings['border'],
            )
            
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            # Получаем матрицу
            matrix = qr.get_matrix()
            
            # Создаем SVG
            module_size = 10  # Размер одного модуля в SVG
            border_size = self.settings['border'] * module_size
            svg_size = len(matrix) * module_size + 2 * border_size
            
            dwg = svgwrite.Drawing(filepath, size=(svg_size, svg_size))
            
            # Фон
            if not self.transparent_var.get():
                dwg.add(dwg.rect(insert=(0, 0), size=(svg_size, svg_size), 
                               fill=self.bg_color_var.get()))
            
            # Модули QR-кода
            fg_color = self.fg_color_var.get()
            
            for row in range(len(matrix)):
                for col in range(len(matrix[row])):
                    if matrix[row][col]:
                        x = col * module_size + border_size
                        y = row * module_size + border_size
                        
                        if self.module_style_var.get() == "circle":
                            # Круглые модули
                            dwg.add(dwg.circle(center=(x + module_size/2, y + module_size/2), 
                                             r=module_size/2, fill=fg_color))
                        elif self.module_style_var.get() == "rounded":
                            # Закругленные модули
                            dwg.add(dwg.rect(insert=(x, y), size=(module_size, module_size), 
                                           fill=fg_color, rx=module_size/4, ry=module_size/4))
                        else:
                            # Квадратные модули
                            dwg.add(dwg.rect(insert=(x, y), size=(module_size, module_size), 
                                           fill=fg_color))
            
            dwg.save()
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка збереження SVG: {str(e)}")
    
    def open_settings(self):
        """Открытие окна настроек"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Налаштування")
        settings_window.geometry("600x500")
        settings_window.resizable(False, False)
        
        # Центрирование окна
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        main_frame = ttk.Frame(settings_window, padding="15")
        main_frame.pack(fill='both', expand=True)
        
        # Создание notebook для вкладок
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(0, 15))
        
        # Вкладка "Общие"
        general_frame = ttk.Frame(notebook, padding="10")
        notebook.add(general_frame, text="Загальні")
        
        # Папка сохранения
        ttk.Label(general_frame, text="Папка для збереження QR-кодів:").pack(anchor='w', pady=(0, 5))
        
        folder_frame = ttk.Frame(general_frame)
        folder_frame.pack(fill='x', pady=(0, 15))
        
        self.folder_var = tk.StringVar(value=self.settings['save_folder'])
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=50)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        ttk.Button(folder_frame, text="Огляд...", command=self.browse_folder).pack(side='right')
        
        # Тип QR-кода по умолчанию
        ttk.Label(general_frame, text="Тип QR-коду за замовчуванням:").pack(anchor='w', pady=(0, 5))
        
        self.default_type_var = tk.StringVar(value=self.current_qr_type)
        default_type_combo = ttk.Combobox(general_frame, textvariable=self.default_type_var, state="readonly")
        default_type_combo['values'] = list(self.qr_types.keys())
        default_type_combo.pack(fill='x', pady=(0, 15))
        
        # Вкладка "QR-код"
        qr_frame = ttk.Frame(notebook, padding="10")
        notebook.add(qr_frame, text="QR-код")
        
        # Уровень коррекции ошибок
        ttk.Label(qr_frame, text="Рівень корекції помилок:").pack(anchor='w', pady=(0, 5))
        
        self.error_var = tk.StringVar(value=self.settings['error_correction'])
        error_frame = ttk.Frame(qr_frame)
        error_frame.pack(fill='x', pady=(0, 15))
        
        error_levels = [
            ('L (~7%) - Низький', 'L'),
            ('M (~15%) - Середній', 'M'),
            ('Q (~25%) - Високий', 'Q'),
            ('H (~30%) - Максимальний', 'H')
        ]
        
        for i, (text, value) in enumerate(error_levels):
            ttk.Radiobutton(error_frame, text=text, variable=self.error_var, 
                           value=value).grid(row=i//2, column=i%2, sticky='w', padx=(0, 15), pady=2)
        
        # Размер блока
        ttk.Label(qr_frame, text="Розмір блоку (пікселів):").pack(anchor='w', pady=(20, 5))
        
        self.box_size_var = tk.IntVar(value=self.settings['box_size'])
        box_size_frame = ttk.Frame(qr_frame)
        box_size_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Scale(box_size_frame, from_=5, to=20, variable=self.box_size_var, 
                 orient='horizontal').pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Label(box_size_frame, textvariable=self.box_size_var, width=3).pack(side='right')
        
        # Граница
        ttk.Label(qr_frame, text="Розмір границі (блоків):").pack(anchor='w', pady=(0, 5))
        
        self.border_var = tk.IntVar(value=self.settings['border'])
        border_frame = ttk.Frame(qr_frame)
        border_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Scale(border_frame, from_=1, to=10, variable=self.border_var, 
                 orient='horizontal').pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Label(border_frame, textvariable=self.border_var, width=3).pack(side='right')
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Зберегти", 
                  command=lambda: self.save_settings_dialog(settings_window)).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Скасувати", 
                  command=settings_window.destroy).pack(side='right')
        ttk.Button(button_frame, text="За замовчуванням", 
                  command=lambda: self.reset_to_defaults(settings_window)).pack(side='left')
    
    def reset_to_defaults(self, window):
        """Сброс настроек к значениям по умолчанию"""
        result = messagebox.askyesno("Підтвердження", 
                                   "Скинути всі налаштування до значень за замовчуванням?")
        if result:
            self.folder_var.set(os.path.expanduser("~/Desktop/QR_Codes"))
            self.error_var.set("M")
            self.box_size_var.set(10)
            self.border_var.set(4)
            self.default_type_var.set("text")
    
    def browse_folder(self):
        """Выбор папки для сохранения"""
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)
    
    def save_settings_dialog(self, window):
        """Сохранение настроек из диалога"""
        self.settings['save_folder'] = self.folder_var.get()
        self.settings['error_correction'] = self.error_var.get()
        self.settings['box_size'] = self.box_size_var.get()
        self.settings['border'] = self.border_var.get()
        self.settings['last_qr_type'] = self.default_type_var.get()
        
        # Сохраняем настройки дизайна
        self.settings['fg_color'] = self.fg_color_var.get()
        self.settings['bg_color'] = self.bg_color_var.get()
        self.settings['module_style'] = self.module_style_var.get()
        self.settings['export_format'] = self.export_format_var.get()
        self.settings['high_quality'] = self.high_quality_var.get()
        self.settings['transparent_bg'] = self.transparent_var.get()
        
        self.save_settings()
        self.status_var.set(f"Папка збереження: {self.settings['save_folder']}")
        
        window.destroy()
        messagebox.showinfo("Успіх", "Налаштування збережено")

def main():
    root = tk.Tk()
    app = QRCodeGenerator(root)
    
    # Обработка закрытия приложения
    def on_closing():
        app.save_settings()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
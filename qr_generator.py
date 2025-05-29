import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import qrcode
from PIL import Image, ImageTk
import os
import json
from datetime import datetime

class QRCodeGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Загрузка настроек
        self.settings_file = "qr_settings.json"
        self.load_settings()
        
        # Создание интерфейса
        self.create_widgets()
        
        # QR код переменные
        self.current_qr_image = None
        self.qr_photo = None
        
    def load_settings(self):
        """Загрузка настроек из файла"""
        default_settings = {
            "save_folder": os.path.expanduser("~/Desktop/QR_Codes"),
            "error_correction": "M",
            "border": 4,
            "box_size": 10
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                # Проверяем наличие всех необходимых ключей
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
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для адаптивности
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Поле для ввода текста
        ttk.Label(main_frame, text="Введите текст для QR-кода:").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        self.text_area = scrolledtext.ScrolledText(main_frame, width=60, height=8, wrap=tk.WORD)
        self.text_area.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Кнопки управления
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        
        self.generate_btn = ttk.Button(buttons_frame, text="Сгенерировать QR-код", command=self.generate_qr)
        self.generate_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        self.save_btn = ttk.Button(buttons_frame, text="Сохранить QR-код", command=self.save_qr, state='disabled')
        self.save_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.settings_btn = ttk.Button(buttons_frame, text="Настройки", command=self.open_settings)
        self.settings_btn.grid(row=0, column=2, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # Фрейм для отображения QR-кода
        qr_frame = ttk.LabelFrame(main_frame, text="Сгенерированный QR-код", padding="10")
        qr_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(3, weight=1)
        
        self.qr_label = ttk.Label(qr_frame, text="QR-код появится здесь после генерации", 
                                 relief='sunken', anchor='center')
        self.qr_label.pack(expand=True, fill='both')
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set(f"Папка сохранения: {self.settings['save_folder']}")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief='sunken')
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
    def generate_qr(self):
        """Генерация QR-кода"""
        text = self.text_area.get(1.0, tk.END).strip()
        
        if not text:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите текст для генерации QR-кода")
            return
        
        try:
            # Настройки уровня коррекции ошибок
            error_levels = {
                'L': qrcode.constants.ERROR_CORRECT_L,
                'M': qrcode.constants.ERROR_CORRECT_M,
                'Q': qrcode.constants.ERROR_CORRECT_Q,
                'H': qrcode.constants.ERROR_CORRECT_H
            }
            
            # Создание QR-кода
            qr = qrcode.QRCode(
                version=1,
                error_correction=error_levels.get(self.settings['error_correction'], qrcode.constants.ERROR_CORRECT_M),
                box_size=self.settings['box_size'],
                border=self.settings['border'],
            )
            
            qr.add_data(text)
            qr.make(fit=True)
            
            # Создание изображения
            self.current_qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Изменение размера для отображения
            display_size = (300, 300)
            display_image = self.current_qr_image.resize(display_size, Image.Resampling.LANCZOS)
            
            # Конвертация для tkinter
            self.qr_photo = ImageTk.PhotoImage(display_image)
            self.qr_label.configure(image=self.qr_photo, text="")
            
            # Активация кнопки сохранения
            self.save_btn.configure(state='normal')
            
            self.status_var.set("QR-код успешно сгенерирован")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при генерации QR-кода: {str(e)}")
    
    def save_qr(self):
        """Сохранение QR-кода"""
        if not self.current_qr_image:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте QR-код")
            return
        
        try:
            # Создание папки если она не существует
            os.makedirs(self.settings['save_folder'], exist_ok=True)
            
            # Генерация имени файла с временной меткой
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"QR_Code_{timestamp}.png"
            filepath = os.path.join(self.settings['save_folder'], filename)
            
            # Сохранение изображения
            self.current_qr_image.save(filepath)
            
            self.status_var.set(f"QR-код сохранен: {filename}")
            messagebox.showinfo("Успех", f"QR-код сохранен как:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def open_settings(self):
        """Открытие окна настроек"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки")
        settings_window.geometry("500x400")
        settings_window.resizable(False, False)
        
        # Центрирование окна
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        main_frame = ttk.Frame(settings_window, padding="15")
        main_frame.pack(fill='both', expand=True)
        
        # Папка сохранения
        ttk.Label(main_frame, text="Папка для сохранения QR-кодов:").pack(anchor='w', pady=(0, 5))
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill='x', pady=(0, 15))
        
        self.folder_var = tk.StringVar(value=self.settings['save_folder'])
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=50)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        ttk.Button(folder_frame, text="Обзор...", command=self.browse_folder).pack(side='right')
        
        # Уровень коррекции ошибок
        ttk.Label(main_frame, text="Уровень коррекции ошибок:").pack(anchor='w', pady=(0, 5))
        
        self.error_var = tk.StringVar(value=self.settings['error_correction'])
        error_frame = ttk.Frame(main_frame)
        error_frame.pack(fill='x', pady=(0, 15))
        
        error_levels = [
            ('L (~7%)', 'L'),
            ('M (~15%)', 'M'),
            ('Q (~25%)', 'Q'),
            ('H (~30%)', 'H')
        ]
        
        for text, value in error_levels:
            ttk.Radiobutton(error_frame, text=text, variable=self.error_var, 
                           value=value).pack(side='left', padx=(0, 15))
        
        # Размер блока
        ttk.Label(main_frame, text="Размер блока (пикселей):").pack(anchor='w', pady=(0, 5))
        
        self.box_size_var = tk.IntVar(value=self.settings['box_size'])
        box_size_frame = ttk.Frame(main_frame)
        box_size_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Scale(box_size_frame, from_=1, to=20, variable=self.box_size_var, 
                 orient='horizontal').pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Label(box_size_frame, textvariable=self.box_size_var).pack(side='right')
        
        # Граница
        ttk.Label(main_frame, text="Размер границы (блоков):").pack(anchor='w', pady=(0, 5))
        
        self.border_var = tk.IntVar(value=self.settings['border'])
        border_frame = ttk.Frame(main_frame)
        border_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Scale(border_frame, from_=1, to=10, variable=self.border_var, 
                 orient='horizontal').pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Label(border_frame, textvariable=self.border_var).pack(side='right')
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Сохранить", 
                  command=lambda: self.save_settings_dialog(settings_window)).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Отмена", 
                  command=settings_window.destroy).pack(side='right')
    
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
        
        self.save_settings()
        self.status_var.set(f"Папка сохранения: {self.settings['save_folder']}")
        
        window.destroy()
        messagebox.showinfo("Успех", "Настройки сохранены")

def main():
    root = tk.Tk()
    app = QRCodeGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
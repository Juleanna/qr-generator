#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль експорту QR-кодів у різні формати
"""

import os
from typing import Dict, Any
from PIL import Image

# Спроба імпорту для SVG
try:
    import svgwrite
    SVG_AVAILABLE = True
except ImportError:
    SVG_AVAILABLE = False

class QRExporter:
    """Клас для експорту QR-кодів у різні формати"""
    
    def __init__(self):
        self.supported_formats = ['png', 'jpg', 'jpeg']
        if SVG_AVAILABLE:
            self.supported_formats.append('svg')
    
    def export_qr(self, qr_image: Image.Image, filepath: str, settings: Dict[str, Any]) -> bool:
        """
        Експорт QR-коду з налаштуваннями дизайну
        
        Args:
            qr_image: Базове зображення QR-коду
            filepath: Шлях для збереження
            settings: Налаштування дизайну
            
        Returns:
            True якщо експорт успішний
        """
        try:
            # Визначення формату з розширення файлу
            format_ext = os.path.splitext(filepath)[1].lower().lstrip('.')
            
            if format_ext not in self.supported_formats:
                print(f"Непідтримуваний формат: {format_ext}")
                return False
            
            # Створення стилізованого зображення
            styled_image = self._apply_styling(qr_image, settings)
            
            # Визначення розміру
            target_size = self._get_target_size(settings)
            if target_size != styled_image.size:
                styled_image = styled_image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Експорт у відповідному форматі
            if format_ext == 'svg':
                return self._export_svg(filepath, qr_image, settings)
            elif format_ext in ['jpg', 'jpeg']:
                return self._export_jpg(styled_image, filepath, settings)
            elif format_ext == 'png':
                return self._export_png(styled_image, filepath, settings)
            
            return False
            
        except Exception as e:
            print(f"Помилка експорту: {e}")
            return False
    
    def _apply_styling(self, qr_image: Image.Image, settings: Dict[str, Any]) -> Image.Image:
        """Застосування стилізації до QR-коду"""
        styled_image = qr_image.copy()
        
        fg_color = settings.get('fg_color', '#000000')
        bg_color = settings.get('bg_color', '#FFFFFF')
        transparent_bg = settings.get('transparent_bg', False)
        
        # Застосування кольорів
        if fg_color != "#000000" or bg_color != "#FFFFFF" or transparent_bg:
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
                    if transparent_bg:
                        new_data.append((255, 255, 255, 0))  # прозорий
                    else:
                        rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                        new_data.append(rgb + (255,))
                else:
                    new_data.append(item)
            
            styled_image.putdata(new_data)
            
            # Конвертація назад в RGB якщо фон не прозорий
            if not transparent_bg:
                styled_image = styled_image.convert("RGB")
        
        return styled_image
    
    def _get_target_size(self, settings: Dict[str, Any]) -> tuple:
        """Визначення цільового розміру зображення"""
        if settings.get('high_quality', True):
            return (800, 800)
        else:
            custom_size = settings.get('size', 400)
            return (custom_size, custom_size)
    
    def _export_png(self, image: Image.Image, filepath: str, settings: Dict[str, Any]) -> bool:
        """Експорт у PNG формат"""
        try:
            # PNG підтримує прозорість
            image.save(filepath, 'PNG', optimize=True)
            return True
        except Exception as e:
            print(f"Помилка збереження PNG: {e}")
            return False
    
    def _export_jpg(self, image: Image.Image, filepath: str, settings: Dict[str, Any]) -> bool:
        """Експорт у JPG формат"""
        try:
            # JPG не підтримує прозорість
            if image.mode == 'RGBA':
                # Створюємо білий фон
                jpg_image = Image.new('RGB', image.size, 'white')
                jpg_image.paste(image, mask=image.split()[-1] if len(image.split()) == 4 else None)
                image = jpg_image
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            quality = 95 if settings.get('high_quality', True) else 85
            image.save(filepath, 'JPEG', quality=quality, optimize=True)
            return True
        except Exception as e:
            print(f"Помилка збереження JPG: {e}")
            return False
    
    def _export_svg(self, filepath: str, qr_image: Image.Image, settings: Dict[str, Any]) -> bool:
        """Експорт у SVG формат"""
        if not SVG_AVAILABLE:
            print("SVG експорт недоступний. Встановіть svgwrite: pip install svgwrite")
            return False
        
        try:
            # Отримання матриці QR-коду
            # Для цього потрібно пересоздати QR-код, але поки використаємо простий підхід
            
            # Параметри
            fg_color = settings.get('fg_color', '#000000')
            bg_color = settings.get('bg_color', '#FFFFFF')
            transparent_bg = settings.get('transparent_bg', False)
            module_style = settings.get('module_style', 'square')
            
            # Визначення розміру
            qr_size = qr_image.size[0]
            module_size = 10  # Розмір одного модуля в SVG
            border_size = 40  # Розмір границі
            svg_size = qr_size * module_size + 2 * border_size
            
            # Створення SVG
            dwg = svgwrite.Drawing(filepath, size=(svg_size, svg_size))
            
            # Фон
            if not transparent_bg:
                dwg.add(dwg.rect(
                    insert=(0, 0),
                    size=(svg_size, svg_size),
                    fill=bg_color
                ))
            
            # Конвертація зображення в матрицю
            qr_bw = qr_image.convert('L')  # Чорно-біле
            pixels = list(qr_bw.getdata())
            
            # Створення модулів
            for y in range(qr_size):
                for x in range(qr_size):
                    pixel_index = y * qr_size + x
                    if pixel_index < len(pixels) and pixels[pixel_index] < 128:  # Чорний піксель
                        svg_x = x * module_size + border_size
                        svg_y = y * module_size + border_size
                        
                        if module_style == "circle":
                            # Круглі модулі
                            dwg.add(dwg.circle(
                                center=(svg_x + module_size/2, svg_y + module_size/2),
                                r=module_size/2,
                                fill=fg_color
                            ))
                        elif module_style == "rounded":
                            # Закруглені модулі
                            dwg.add(dwg.rect(
                                insert=(svg_x, svg_y),
                                size=(module_size, module_size),
                                fill=fg_color,
                                rx=module_size/4,
                                ry=module_size/4
                            ))
                        else:
                            # Квадратні модулі
                            dwg.add(dwg.rect(
                                insert=(svg_x, svg_y),
                                size=(module_size, module_size),
                                fill=fg_color
                            ))
            
            dwg.save()
            return True
            
        except Exception as e:
            print(f"Помилка збереження SVG: {e}")
            return False
    
    def get_supported_formats(self) -> list:
        """Отримання списку підтримуваних форматів"""
        return self.supported_formats.copy()
    
    def is_format_supported(self, format_name: str) -> bool:
        """Перевірка підтримки формату"""
        return format_name.lower() in self.supported_formats

class QRStyler:
    """Клас для додаткової стилізації QR-кодів"""
    
    @staticmethod
    def add_logo(qr_image: Image.Image, logo_path: str, logo_size_percent: int = 20) -> Image.Image:
        """
        Додавання логотипу до QR-коду
        
        Args:
            qr_image: Зображення QR-коду
            logo_path: Шлях до логотипу
            logo_size_percent: Розмір логотипу у відсотках від QR-коду
            
        Returns:
            QR-код з логотипом
        """
        try:
            if not os.path.exists(logo_path):
                return qr_image
            
            # Відкриття логотипу
            logo = Image.open(logo_path)
            
            # Розрахунок розміру логотипу
            qr_width, qr_height = qr_image.size
            logo_size = int(min(qr_width, qr_height) * logo_size_percent / 100)
            
            # Зміна розміру логотипу
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Створення білого фону для логотипу
            logo_bg_size = int(logo_size * 1.2)
            logo_bg = Image.new('RGB', (logo_bg_size, logo_bg_size), 'white')
            
            # Позиціонування логотипу на фоні
            logo_bg_pos = ((logo_bg_size - logo_size) // 2, (logo_bg_size - logo_size) // 2)
            if logo.mode == 'RGBA':
                logo_bg.paste(logo, logo_bg_pos, logo)
            else:
                logo_bg.paste(logo, logo_bg_pos)
            
            # Копіювання QR-коду
            result_image = qr_image.copy()
            
            # Позиціонування логотипу в центрі QR-коду
            logo_pos = (
                (qr_width - logo_bg_size) // 2,
                (qr_height - logo_bg_size) // 2
            )
            
            result_image.paste(logo_bg, logo_pos)
            
            return result_image
            
        except Exception as e:
            print(f"Помилка додавання логотипу: {e}")
            return qr_image
    
    @staticmethod
    def add_frame(qr_image: Image.Image, frame_width: int = 20, frame_color: str = "#000000") -> Image.Image:
        """
        Додавання рамки до QR-коду
        
        Args:
            qr_image: Зображення QR-коду
            frame_width: Товщина рамки
            frame_color: Колір рамки
            
        Returns:
            QR-код з рамкою
        """
        try:
            # Створення нового зображення з рамкою
            qr_width, qr_height = qr_image.size
            new_width = qr_width + 2 * frame_width
            new_height = qr_height + 2 * frame_width
            
            # Конвертація кольору
            if frame_color.startswith('#'):
                rgb = tuple(int(frame_color[i:i+2], 16) for i in (1, 3, 5))
            else:
                rgb = (0, 0, 0)  # За замовчуванням чорний
            
            # Створення зображення з рамкою
            framed_image = Image.new('RGB', (new_width, new_height), rgb)
            
            # Вставка QR-коду в центр
            framed_image.paste(qr_image, (frame_width, frame_width))
            
            return framed_image
            
        except Exception as e:
            print(f"Помилка додавання рамки: {e}")
            return qr_image
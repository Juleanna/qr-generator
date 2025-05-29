@echo off
echo Компиляция QR Generator...
echo.

REM Проверка наличия PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Установка PyInstaller...
    pip install pyinstaller
)

REM Очистка предыдущих сборок
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del "*.spec"

REM Компиляция
echo Создание исполняемого файла...
pyinstaller --onefile --windowed --name "QR_Generator" --version-file=version_info.txt qr_generator.py

REM Проверка результата
if exist "dist\QR_Generator.exe" (
    echo.
    echo Успешно! Исполняемый файл создан: dist\QR_Generator.exe
    echo Размер файла:
    dir "dist\QR_Generator.exe" | find "QR_Generator.exe"
    echo.
    echo Хотите запустить программу? (y/n)
    set /p choice=
    if /i "%choice%"=="y" start "" "dist\QR_Generator.exe"
) else (
    echo.
    echo Ошибка при создании исполняемого файла!
)

pause
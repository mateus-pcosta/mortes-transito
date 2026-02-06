@echo off
echo ========================================
echo   Build Sistema Mortes no Transito
echo   SSP-PI
echo ========================================
echo.

echo [1/4] Instalando PyInstaller...
pip install pyinstaller

echo.
echo [2/4] Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Sistema_Mortes_Transito.spec" del "Sistema_Mortes_Transito.spec"

echo.
echo [3/4] Criando executavel...
pyinstaller --name="Sistema_Mortes_Transito" ^
            --onefile ^
            --windowed ^
            --icon=NONE ^
            --add-data "credentials;credentials" ^
            --add-data "config_sheets.txt;." ^
            --hidden-import=gspread ^
            --hidden-import=google.auth ^
            --hidden-import=openpyxl ^
            main.py

echo.
echo [4/4] Build concluido!
echo.
echo Executavel gerado em: dist\Sistema_Mortes_Transito.exe
echo.
pause

@echo off
echo ================================================
echo  Instalando dependencias do sistema
echo ================================================
echo.

python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ================================================
echo  Instalacao concluida!
echo ================================================
echo.
echo Execute: python main.py
echo.
pause

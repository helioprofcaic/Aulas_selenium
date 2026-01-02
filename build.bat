@echo off

cd /d "%~dp0"

:: Verifica e ativa o ambiente virtual se existir
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

echo Limpando builds anteriores...
rmdir /s /q build
rmdir /s /q dist
del /q *.spec

echo Construindo o executavel com PyInstaller...

pyinstaller --onefile --name "AssistenteAulas" ^
    --add-data "tools;tools" ^
    --add-data "interfaces;interfaces" ^
    --add-data "data;data" ^
    app.py

echo.
echo Build concluido! O executavel esta em 'dist/AssistenteAulas.exe'.
@echo off

cd /d "%~dp0"

:: Verifica e ativa o ambiente virtual se existir
if exist ".venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual ^(.venv^)...
    call ".venv\Scripts\activate.bat"
)

echo Limpando builds anteriores...
rmdir /s /q build
rmdir /s /q dist
del /q *.spec

echo Construindo o executavel com PyInstaller...

:: Verifica se o PyInstaller esta instalado no ambiente e o executa via modulo
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller nao encontrado no ambiente virtual. Instalando...
    pip install pyinstaller
)

:: Garante que as bibliotecas do setup.py (selenium, etc) estao instaladas
echo Verificando dependencias do projeto...
pip install .

python -m PyInstaller --onefile --name "AssistenteAulas" ^
    --hidden-import=selenium ^
    --hidden-import=webdriver_manager ^
    --hidden-import=webdriver_manager.chrome ^
    --hidden-import=dateutil ^
    --hidden-import=pyautogui ^
    --hidden-import=cv2 ^
    --add-data "tools;tools" ^
    --add-data "interfaces;interfaces" ^
    --add-data "data;data" ^
    app.py

echo.
echo Build concluido! O executavel esta em 'dist/AssistenteAulas.exe'.
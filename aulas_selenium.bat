@echo off

cd /d "%~dp0"

:: Verifica e ativa o ambiente virtual se existir
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

:: Executa o script 'app.py' e passa todos os argumentos recebidos (%*)
python app.py %*
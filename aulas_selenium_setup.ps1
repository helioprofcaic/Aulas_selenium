# setup.ps1
# Script de Instalação "Mágico" - Gera todo o projeto do zero.
# Este script contém todo o código fonte necessário embutido.
# Ao executar, ele recria a estrutura de arquivos, pastas e ambiente virtual.

$ErrorActionPreference = "Stop"

# --- Funções Auxiliares ---

function Write-Color {
    param([string]$Text, [ConsoleColor]$Color)
    Write-Host $Text -ForegroundColor $Color
}

function Create-File {
    param(
        [string]$Path,
        [string]$Content
    )
    $Dir = Split-Path -Parent $Path
    if (-not (Test-Path $Dir)) { 
        New-Item -ItemType Directory -Path $Dir -Force | Out-Null 
    }
    
    # Normaliza quebras de linha para Windows
    $Content = $Content -replace "`r`n", "`n" -replace "`n", "`r`n"
    
    if (-not (Test-Path $Path)) {
        # Usa UTF8 sem BOM para compatibilidade máxima com Python/JSON
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
        Write-Color "  [+] Criado: $Path" -Color Cyan
    } else {
        Write-Color "  [=] Já existe (mantido): $Path" -Color DarkGray
    }
}

# --- Início do Script ---

$RootPath = Join-Path $PSScriptRoot "Aulas_selenium"
if (-not (Test-Path $RootPath)) {
    New-Item -ItemType Directory -Path $RootPath -Force | Out-Null
}

Write-Color "=== Iniciando Setup do Projeto Aulas Selenium ===" -Color Green
Write-Color "Diretório Raiz: $RootPath" -Color Gray

# 1. Verificação Python
Write-Color "`n[1/5] Verificando instalação do Python..." -Color Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Color "ERRO: Python não encontrado. Instale o Python 3.8+ e adicione ao PATH." -Color Red
    exit 1
}
Write-Color "Python encontrado." -Color Green

# 2. Criação da Estrutura de Diretórios
Write-Color "`n[2/5] Criando estrutura de pastas..." -Color Yellow
$directories = @(
    "data", 
    "data\_modelo",
    "aulas", 
    "aulas\inputs", 
    "aulas\inputs\_modelo",
    "aulas\logs",
    "tools", 
    "interfaces",
    "docs", 
    "screenshots"
)

foreach ($dir in $directories) {
    $dirPath = Join-Path $RootPath $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath | Out-Null
        Write-Color "  [+] Pasta criada: $dir" -Color Cyan
    }
}

# 3. Gerando Arquivos do Projeto
Write-Color "`n[3/5] Gerando arquivos do projeto..." -Color Yellow

# --- ARQUIVOS RAIZ ---

$Content_Req = @'
selenium
webdriver-manager>=4.0.0
notebook
pandas
plotly_express
nbformat
python-dateutil
Jinja2
opencv-python
pyautogui
Pillow
pyscreeze
python-dotenv
google-generativeai
setuptools
'@
Create-File (Join-Path $RootPath "requirements.txt") $Content_Req

$Content_GitIgnore = @'
# Conteúdo sensível e dados
aulas/*
data/*
!data/_modelo/
!aulas/_modelo/
!aulas/inputs/_modelo/
screenshots/*
.env
logs/

# Ambientes virtuais
.venv/
venv/
env/

# IDEs e arquivos temporários Python
.idea/
__pycache__/
*.pyc
*.ipynb_checkpoints
'@
Create-File (Join-Path $RootPath ".gitignore") $Content_GitIgnore

$Content_Readme = @'
# 🤖 Automação de Aulas e Planos de Ensino

Bem-vindo ao **Assistente de Aulas**! Este projeto é uma suíte completa de automação para professores, projetada para coletar dados do portal da Seduc, gerar planos de aula inteligentes e realizar o registro automático de aulas.

Agora com uma **Interface Gráfica (GUI)** amigável!

## 🚀 Configuração Inicial (Ambiente)

### 1. Instalação

Certifique-se de ter o Python instalado.

```bash
# Crie um ambiente virtual
python -m venv .venv

# Ative o ambiente
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 2. Configurando a pasta `data/`

Para garantir a segurança, as pastas com dados sensíveis são ignoradas pelo Git. Configure-as usando os modelos:

1.  Execute o assistente de configuração:
    ```bash
    python tools/setup_wizard.py
    ```
2.  Escolha a opção **1** para gerar os arquivos modelo.
3.  Edite os arquivos gerados em `data/` com suas informações reais.
4.  Execute novamente e escolha a opção **2** para criar as pastas de input automaticamente.

## 🖥️ Como Usar

O projeto possui um ponto de entrada único que facilita a execução:

### Interface Gráfica (Recomendado)
Basta executar o arquivo `app.py`:
```bash
python app.py
```
Uma janela abrirá com botões para cada etapa do processo (Coleta, Planejamento, Preenchimento, Registro).

### Linha de Comando (CLI)
Se preferir usar o terminal ou estiver em um servidor sem interface gráfica:
```bash
python app.py --cli
```

## 📚 Documentação

*   📖 Tutorial de Uso: Guia passo a passo para o professor.
*   🏗️ Arquitetura Técnica: Para desenvolvedores entenderem a estrutura do código.
*   🤖 Detalhes do Scraper: Como funciona a coleta de dados.
*   🛠️ **Ferramentas Secundárias**: Documentação dos utilitários de análise e gestão de conteúdo (CSV, PDFs, Relatórios).
'@
Create-File (Join-Path $RootPath "README.md") $Content_Readme

# --- ARQUIVOS DE INICIALIZAÇÃO E BUILD ---

$Content_App = @'
import sys
import os
import runpy

def get_base_path():
    """Retorna o caminho base para persistencia de dados."""
    if getattr(sys, 'frozen', False):
        # Se for executavel, usa a pasta onde o .exe esta
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# --- DEPENDÊNCIAS PARA O PYINSTALLER ---
# Como os scripts da pasta 'tools/' são executados dinamicamente via runpy/subprocess,
# o PyInstaller não detecta automaticamente que essas bibliotecas são necessárias.
# Importamos aqui explicitamente (dentro de um if False para não pesar na inicialização)
# para garantir que sejam empacotadas no executável final.
if False:
    import selenium
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait, Select
    import webdriver_manager
    from webdriver_manager.chrome import ChromeDriverManager
    import dateutil
    import pyautogui
    import cv2
# ---------------------------------------

def main():
    """
    Ponto de entrada principal da aplicação (Âncora).
    Tenta carregar a interface gráfica (GUI) para o usuário.
    Se falhar ou se solicitado via argumento '--cli', carrega o menu de linha de comando (CLI).
    """
    
    # --- FIX PARA PYINSTALLER (Execução de Scripts) ---
    # Quando congelado, o sys.executable aponta para o executável.
    # O subprocess.Popen chama [exe, script.py].
    # Precisamos interceptar isso e rodar o script em vez de abrir a GUI novamente.
    if getattr(sys, 'frozen', False) and len(sys.argv) > 1 and sys.argv[1].endswith('.py'):
        script_path = sys.argv[1]
        # Remove o executável dos argumentos para o script
        sys.argv = sys.argv[1:]
        
        # Garante que o diretório do script está no path (comportamento padrão do python)
        sys.path.insert(0, os.path.dirname(os.path.abspath(script_path)))
        
        try:
            runpy.run_path(script_path, run_name="__main__")
        except Exception as e:
            print(f"Erro fatal ao executar script interno: {e}")
            input("Pressione ENTER para fechar...")
        return
    # --------------------------------------------------

    # Garante que a raiz do projeto está no PYTHONPATH para importações funcionarem
    # Nota: Para importacoes (sys.path), usamos a localizacao do script/temp
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Define o diretório de trabalho para a pasta do EXECUTAVEL (para dados persistentes)
    raiz = get_base_path()
    os.chdir(raiz)

    # Verifica argumento de linha de comando para forçar modo texto
    if "--cli" in sys.argv:
        iniciar_cli()
        return

    try:
        iniciar_gui()
    except Exception as e:
        print(f"\n[AVISO] Não foi possível iniciar a interface gráfica: {e}")
        print("Alternando para o modo de linha de comando (CLI)...\n")
        iniciar_cli()

def iniciar_gui():
    import tkinter as tk
    from interfaces.gui_app import AppAutomação
    
    root = tk.Tk()
    root.title("Assistente de Aulas")

    # Configuração do ícone da janela principal
    try:
        icone_path = os.path.join(get_base_path(), "recursos", "icone_app.png")
        if os.path.exists(icone_path):
            icon_img = tk.PhotoImage(file=icone_path)
            root.iconphoto(True, icon_img)
    except Exception as e:
        print(f"Erro ao carregar ícone da janela: {e}")
    
    app = AppAutomação(root)
    root.mainloop()

def iniciar_cli():
    from interfaces.cli_menu import menu_principal
    menu_principal()

if __name__ == "__main__":
    main()
'@
Create-File (Join-Path $RootPath "app.py") $Content_App

$Content_AppSpec = @'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('docs', 'docs'),
        ('tools', 'tools'),
        ('recursos', 'recursos'),
        ('data', 'data'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'selenium', 'webdriver_manager', 'PIL', 'cv2', 'pyautogui', 'tkinter', 
        'dateutil', 'markdown', 'weasyprint', 'interfaces.gui_app', 'interfaces.cli_menu',
        'interfaces.assets'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AssistenteAulas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='recursos/icone.ico', # Descomente se converter o png para ico
)
'@
Create-File (Join-Path $RootPath "app.spec") $Content_AppSpec

$Content_SetupPy = @'
from setuptools import setup, find_packages

setup(
    name='assistente-aulas',
    version='1.0.0',
    author='Seu Nome',
    author_email='seu_email@exemplo.com',
    description='Ferramenta de linha de comando para automação e gerenciamento de aulas.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    py_modules=['app'],
    include_package_data=True,
    install_requires=[
        'pyautogui',
        'opencv-python',
    ],
    entry_points={
        'console_scripts': [
            'assistente-aulas=app:main',
        ],
    },
)
'@
Create-File (Join-Path $RootPath "setup.py") $Content_SetupPy

$Content_BuildBat = @'
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
:: Não deletar o .spec, pois agora usamos ele para configuração
:: del /q *.spec

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

if exist app.spec (
    echo Usando arquivo de especificacao: app.spec
    python -m PyInstaller app.spec
) else (
    echo ERRO: Arquivo app.spec nao encontrado!
    exit /b 1
)

echo.
echo Build concluido! O executavel esta em 'dist/AssistenteAulas.exe'.
'@
Create-File (Join-Path $RootPath "build.bat") $Content_BuildBat

$Content_Manifest = @'
include README.md
recursive-include docs *
recursive-include tools *
recursive-include recursos *
recursive-include interfaces *
'@
Create-File (Join-Path $RootPath "MANIFEST.in") $Content_Manifest

$Content_RunBat = @'
@echo off

cd /d "%~dp0"

:: Verifica e ativa o ambiente virtual se existir
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

:: Executa o script 'app.py' e passa todos os argumentos recebidos (%*)
python app.py %*
'@
Create-File (Join-Path $RootPath "aulas_selenium.bat") $Content_RunBat

# --- INTERFACES ---

Create-File (Join-Path $RootPath "interfaces\__init__.py") ""

$Content_GuiStats = @'
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Adiciona a raiz ao path para importar tools
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from tools import ver_aulas_por_disciplina as stats_tool

class StatsViewer(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("📊 Estatísticas de Aulas")
        self.geometry("800x600")
        self.configure(bg="#f0f4f8")

        # Carregar dados
        data_path = os.path.join(PROJECT_ROOT, 'data')
        self.aulas, self.turmas_disciplinas, self.mapa_turmas = stats_tool.carregar_dados(data_path)

        if not self.aulas:
            messagebox.showerror("Erro", "Não foi possível carregar os dados. Execute o Scraper primeiro.")
            self.destroy()
            return

        # Notebook (Abas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.criar_aba_disciplina()
        self.criar_aba_turma()
        self.criar_aba_data()

    def criar_treeview(self, parent, colunas):
        tree = ttk.Treeview(parent, columns=colunas, show='headings')
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    def criar_aba_disciplina(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Por Disciplina")
        
        dados = stats_tool.obter_resumo_disciplina(self.aulas, self.turmas_disciplinas)
        
        cols = ('Código', 'Nome da Disciplina', 'Aulas Registradas')
        tree = self.criar_treeview(frame, cols)
        tree.column('Nome da Disciplina', width=300)
        
        for item in dados:
            tree.insert('', tk.END, values=item)

    def criar_aba_turma(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Por Turma")
        
        dados = stats_tool.obter_resumo_turma_dados(self.aulas, self.mapa_turmas)
        
        cols = ('Nome Curto', 'Nome Completo', 'Aulas Registradas')
        tree = self.criar_treeview(frame, cols)
        tree.column('Nome Completo', width=300)
        
        for item in dados:
            tree.insert('', tk.END, values=item)

    def criar_aba_data(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Por Data")
        
        dados = stats_tool.obter_resumo_data_dados(self.aulas)
        
        cols = ('Data', 'Aulas Registradas')
        tree = self.criar_treeview(frame, cols)
        
        for data_obj, count in dados:
            tree.insert('', tk.END, values=(data_obj.strftime('%d/%m/%Y'), count))
'@
Create-File (Join-Path $RootPath "interfaces\gui_stats.py") $Content_GuiStats

$Content_GuiPreenchedor = @'
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os
import threading

if getattr(sys, 'frozen', False):
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from tools import preenchedor_planos as filler_tool

class PreenchedorViewer(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("📝 Preenchedor de Conteúdos")
        self.geometry("700x600")
        self.configure(bg="#f0f4f8")

        self.aulas_dir = os.path.join(PROJECT_ROOT, 'aulas')
        self.inputs_dir = os.path.join(self.aulas_dir, 'inputs')
        self.data_dir = os.path.join(PROJECT_ROOT, 'data')

        # Carregar dados
        self.grouped_files = filler_tool.find_plan_files(self.aulas_dir)
        self.links_recursos = filler_tool.carregar_links_recursos(self.data_dir)

        # Layout
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(top_frame, text="Selecione as disciplinas para preencher:", font=('Segoe UI', 10, 'bold')).pack(anchor='w')

        # Lista com Checkboxes
        self.check_vars = {}
        
        canvas = tk.Canvas(top_frame, bg="#ffffff", highlightthickness=1, highlightbackground="#ccc")
        scrollbar = ttk.Scrollbar(top_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        if not self.grouped_files:
            ttk.Label(self.scrollable_frame, text="Nenhum plano pendente encontrado.").pack(padx=10, pady=10)
        else:
            for key in sorted(self.grouped_files.keys()):
                turma, disciplina = key
                count = len(self.grouped_files[key])
                var = tk.BooleanVar()
                chk = ttk.Checkbutton(self.scrollable_frame, text=f"{turma} - {disciplina} ({count} arquivos)", variable=var)
                chk.pack(anchor='w', padx=5, pady=2)
                self.check_vars[key] = var

        # Botões
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Preencher Selecionados", command=self.iniciar_preenchimento).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="Selecionar Todos", command=self.selecionar_todos).pack(side=tk.LEFT)

        # Log
        log_frame = ttk.LabelFrame(self, text="Log de Processamento", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, state='disabled', font=('Consolas', 9))
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def selecionar_todos(self):
        for var in self.check_vars.values():
            var.set(True)

    def log(self, msg):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def iniciar_preenchimento(self):
        files_to_process = []
        for key, var in self.check_vars.items():
            if var.get():
                files_to_process.extend(self.grouped_files[key])
        
        if not files_to_process:
            messagebox.showwarning("Aviso", "Nenhuma disciplina selecionada.")
            return

        self.log("-" * 40)
        self.log(f"Iniciando preenchimento de {len(files_to_process)} arquivos...")
        
        # Thread para não travar GUI
        threading.Thread(target=self.processar_arquivos, args=(files_to_process,)).start()

    def processar_arquivos(self, files):
        sucessos = 0
        falhas = 0
        
        for txt_path in files:
            success, msg = filler_tool.preencher_arquivo_plano(txt_path, self.inputs_dir, self.links_recursos)
            if success:
                self.log(f"✅ {os.path.basename(txt_path)}: {msg}")
                sucessos += 1
            else:
                self.log(f"❌ {os.path.basename(txt_path)}: {msg}")
                falhas += 1
        
        self.log("-" * 40)
        self.log(f"Concluído. Sucessos: {sucessos}, Falhas: {falhas}")
        messagebox.showinfo("Concluído", f"Processamento finalizado.\nSucessos: {sucessos}\nFalhas: {falhas}")
        
        # Atualizar lista (recarregar janela seria ideal, mas vamos apenas avisar)
        self.log("Nota: Feche e reabra esta janela para atualizar a lista de pendências.")
'@
Create-File (Join-Path $RootPath "interfaces\gui_preenchedor.py") $Content_GuiPreenchedor

$Content_Assets = @'
import os
from PIL import Image, ImageTk # Requer: pip install Pillow

# Cache para evitar que o Garbage Collector do Python apague as imagens
_cache_icones = {}

def get_icon(nome, tamanho=(32, 32)):
    """
    Carrega um ícone da pasta 'recursos', redimensiona e retorna um objeto PhotoImage.
    
    Args:
        nome (str): Nome lógico do ícone ('app', 'scraper', 'planejamento', etc.)
        tamanho (tuple): Tamanho desejado (largura, altura). Padrão 32x32.
    """
    global _cache_icones
    
    # Mapeamento dos nomes lógicos para os arquivos gerados
    mapa_arquivos = {
        'app': 'icone_app.png',
        'scraper': 'icone_scraper.png',
        'planejamento': 'icone_planejamento.png',
        'preenchimento': 'icone_preenchimento.png',
        'registro': 'icone_registro.png',
        'config': 'icone_config.png'
    }
    
    filename = mapa_arquivos.get(nome, f"{nome}.png")
    chave_cache = (filename, tamanho)
    
    if chave_cache in _cache_icones:
        return _cache_icones[chave_cache]

    # Define o caminho da pasta recursos (assumindo estrutura: projeto/interfaces/assets.py)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_img = os.path.join(base_dir, 'recursos', filename)
    
    if not os.path.exists(caminho_img):
        print(f"⚠️ Ícone não encontrado: {caminho_img}")
        return None
        
    try:
        pil_img = Image.open(caminho_img)
        pil_img = pil_img.resize(tamanho, Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(pil_img)
        _cache_icones[chave_cache] = tk_img
        return tk_img
    except Exception as e:
        print(f"❌ Erro ao carregar ícone {filename}: {e}")
        return None
'@
Create-File (Join-Path $RootPath "interfaces\assets.py") $Content_Assets

$Content_GuiApp = @'
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import os
import sys
import subprocess
import threading
import json
import re
# --- Bloco de Resiliência de Importação ---
# Permite que o script seja executado diretamente (python interfaces/gui_app.py)
# ou como um módulo importado (por app.py).
try:
    from interfaces.assets import get_icon
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from interfaces.assets import get_icon
    
# Importações das novas interfaces gráficas
from interfaces.gui_stats import StatsViewer
from interfaces.gui_preenchedor import PreenchedorViewer


class AppAutomação:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Assistente")
        # Configuração para ocupar ~25% da tela 720p (aprox 340px largura) e ficar à esquerda
        self.root.geometry("400x720+0+0")
        self.root.configure(bg="#f0f4f8") # Fundo Azul-Cinza muito suave

        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        
        # Paleta de Cores "Bluish Tone"
        bg_color = "#f0f4f8"       # Fundo da janela
        primary_blue = "#0077b6"   # Azul principal (texto botões/ícones)
        dark_blue = "#023e8a"      # Azul escuro (títulos)
        hover_blue = "#e0f2fe"     # Azul claro (hover)
        text_gray = "#486581"      # Cinza azulado (descrições)

        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, font=('Segoe UI', 9), foreground=text_gray)
        
        # Botões com estilo "Card" (Branco com texto Azul)
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=8, background="#ffffff", foreground=primary_blue, borderwidth=1, bordercolor="#bcccdc", focuscolor=hover_blue)
        style.map('TButton', background=[('active', hover_blue)], foreground=[('active', dark_blue)], bordercolor=[('active', primary_blue)])
        
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), background=bg_color, foreground=dark_blue)
        style.configure('Desc.TLabel', font=('Segoe UI', 8), background=bg_color, foreground=text_gray)
        style.configure('TLabelframe', background=bg_color, bordercolor="#bcccdc")
        style.configure('TLabelframe.Label', background=bg_color, foreground=dark_blue, font=('Segoe UI', 9, 'bold'))

        # --- Layout Dividido (70% / 30%) ---
        # Container Superior (Header + Botões)
        top_container = ttk.Frame(root)
        top_container.place(relx=0, rely=0, relwidth=1.0, relheight=0.7)

        # Container Inferior (Logs)
        bottom_container = ttk.Frame(root)
        bottom_container.place(relx=0, rely=0.7, relwidth=1.0, relheight=0.3)

        # Cabeçalho
        header_frame = ttk.Frame(top_container, padding="10")
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Painel do Professor", style='Header.TLabel').pack(anchor='w')
        ttk.Label(header_frame, text="Automação de Aulas", style='Desc.TLabel').pack(anchor='w')

        # Botões de Ação
        btn_frame = ttk.Frame(top_container, padding="5")
        btn_frame.pack(fill=tk.BOTH, expand=True)

        self.criar_botao(btn_frame, "1. Atualizar Dados", 
                         "Baixa os registros atuais do portal.", 
                         "scraper.py", 0, icon_name="scraper")
        
        self.criar_botao(btn_frame, "2. Planejar Aulas", 
                         "Gera arquivos de plano vazios.", 
                         "preparar_planos.py", 1, icon_name="planejamento")
        
        self.criar_botao(btn_frame, "3. Preencher Conteúdos", 
                         "Insere conteúdo nos planos.", 
                         "GUI_PREENCHEDOR", 2, icon_name="preenchimento")
        
        self.criar_botao(btn_frame, "4. Registrar no Portal", 
                         "Lança as aulas no sistema.", 
                         "registrar_aulas.py", 3, icon_name="registro")
        
        self.criar_botao(btn_frame, "5. Configurações", 
                         "Assistente de configuração inicial.", 
                         "WIZARD", 4, icon_name="config")

        # Área de Log/Console
        log_frame = ttk.LabelFrame(bottom_container, text="Log de Execução", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=8, state='disabled', font=('Consolas', 8))
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.configure(bg="#ffffff", fg="#486581", relief="flat", highlightthickness=0, padx=5, pady=5)

        # Botão Sair
        # ttk.Button(root, text="Sair", command=root.quit).pack(pady=5) # Removido para limpar visual

        # Verificação inicial de credenciais
        self.root.after(1000, self.verificar_credenciais)

    def criar_botao(self, parent, texto, descricao, script, row, icon_name=None):
        # Frame container para o "Card" do botão
        frame = ttk.Frame(parent, padding="0")
        frame.pack(fill=tk.X, pady=2)
        
        # Carrega o ícone se fornecido
        image = None
        if icon_name:
            image = get_icon(icon_name, tamanho=(32, 32))

        # Botão principal ocupando toda a largura
        if script == "WIZARD":
            btn = ttk.Button(frame, text=f" {texto}", command=self.abrir_wizard, image=image, compound="left")
        elif script == "GUI_PREENCHEDOR":
            btn = ttk.Button(frame, text=f" {texto}", command=self.abrir_preenchedor, image=image, compound="left")
        else:
            btn = ttk.Button(frame, text=f" {texto}", command=lambda: self.iniciar_script(script), image=image, compound="left")
        
        btn.pack(fill=tk.X, ipady=2)
        
        # Descrição logo abaixo, discreta
        lbl = ttk.Label(frame, text=descricao, style='Desc.TLabel', wraplength=300)
        lbl.pack(fill=tk.X, padx=2, pady=(1, 3))

    def log(self, mensagem):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, mensagem + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def obter_raiz(self):
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def abrir_wizard(self):
        WizardDialog(self.root, self)

    def abrir_preenchedor(self):
        PreenchedorViewer(self.root)

    def iniciar_script(self, script_name):
        # Executa em uma thread separada para não travar a interface
        thread = threading.Thread(target=self.executar_processo, args=(script_name,))
        thread.start()

    def executar_processo(self, script_name):
        raiz = self.obter_raiz()
        
        # Se estiver rodando como EXE, os scripts estão na pasta temporária interna (_MEIPASS)
        # mas o diretório de trabalho (cwd) deve ser a pasta do executável (raiz)
        base_scripts = sys._MEIPASS if getattr(sys, 'frozen', False) else raiz
        
        caminho_script = os.path.join(base_scripts, 'tools', script_name)
        
        self.log("-" * 40)
        self.log(f"Iniciando: {script_name}...")
        
        try:
            # No Windows, precisamos configurar o startupinfo para esconder a janela do console extra
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen(
                [sys.executable, caminho_script],
                cwd=raiz,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                startupinfo=startupinfo
            )

            # Ler a saída em tempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())
            
            # Capturar erros se houver
            stderr = process.stderr.read()
            if stderr:
                self.log(f"ERRO: {stderr}")

            if process.returncode == 0:
                self.log(f"✅ {script_name} finalizado com sucesso.")
                messagebox.showinfo("Sucesso", f"O script {script_name} foi concluído.")
            else:
                self.log(f"❌ {script_name} finalizado com erros.")
                messagebox.showerror("Erro", f"Ocorreu um erro ao executar {script_name}.")

        except Exception as e:
            self.log(f"Erro crítico: {str(e)}")
            messagebox.showerror("Erro Crítico", str(e))

    def verificar_credenciais(self):
        raiz = self.obter_raiz()
        creds_path = os.path.join(raiz, 'data', 'credentials.json')
        
        abrir_wizard = False
        if not os.path.exists(creds_path):
            abrir_wizard = True
        else:
            try:
                with open(creds_path, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    # Verifica se são os dados de exemplo ou vazios
                    if dados.get('username') in ["12345678900", "seu_usuario", ""] or dados.get('password') in ["senha_secreta", "sua_senha", ""]:
                        abrir_wizard = True
            except:
                pass
        
        if abrir_wizard:
            if messagebox.askyesno("Configuração Inicial", "Suas credenciais de acesso (CPF/Senha) parecem não estar configuradas.\n\nO robô precisa delas para funcionar.\nDeseja abrir o Assistente para configurá-las agora?"):
                self.abrir_wizard()

class MarkdownViewer(tk.Toplevel):
    """Visualizador simples de Markdown nativo em Tkinter."""
    def __init__(self, parent, title, file_path):
        super().__init__(parent)
        self.title(title)
        self.geometry("700x600")
        self.configure(bg="#ffffff")

        # Configuração da área de texto
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Segoe UI", 10), padx=20, pady=20, bd=0)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Tags de formatação (Estilo visual do Markdown)
        self.text_area.tag_config("h1", font=("Segoe UI", 20, "bold"), foreground="#023e8a", spacing1=15, spacing3=5)
        self.text_area.tag_config("h2", font=("Segoe UI", 16, "bold"), foreground="#0077b6", spacing1=10, spacing3=5)
        self.text_area.tag_config("h3", font=("Segoe UI", 12, "bold"), foreground="#486581", spacing1=5)
        self.text_area.tag_config("bold", font=("Segoe UI", 10, "bold"))
        self.text_area.tag_config("bullet", lmargin1=20, lmargin2=30)
        self.text_area.tag_config("code", font=("Consolas", 9), background="#f5f5f5", foreground="#d63384")
        self.text_area.tag_config("normal", font=("Segoe UI", 10))

        self.load_file(file_path)
        self.text_area.configure(state='disabled') # Apenas leitura

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            in_code = False
            for line in lines:
                line_strip = line.strip()
                if line_strip.startswith('```'):
                    in_code = not in_code
                    continue
                
                if in_code:
                    self.text_area.insert(tk.END, line, "code")
                else:
                    self.parse_line(line)
        except Exception as e:
            self.text_area.insert(tk.END, f"Erro ao ler arquivo: {e}")

    def parse_line(self, line):
        if line.startswith('# '):
            self.text_area.insert(tk.END, line[2:], "h1")
        elif line.startswith('## '):
            self.text_area.insert(tk.END, line[3:], "h2")
        elif line.startswith('### '):
            self.text_area.insert(tk.END, line[4:], "h3")
        elif line.strip().startswith('* ') or line.strip().startswith('- '):
            self.insert_formatted(line.strip()[2:] + "\n", "bullet")
        else:
            self.insert_formatted(line, "normal")

    def insert_formatted(self, text, base_tag):
        # Detecta negrito **texto**
        parts = re.split(r'(\*\*.*?\*\*)', text)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                self.text_area.insert(tk.END, part[2:-2], (base_tag, "bold"))
            else:
                self.text_area.insert(tk.END, part, base_tag)

class WizardDialog:
    def __init__(self, parent, app_instance):
        self.top = tk.Toplevel(parent)
        self.top.title("🧙 Assistente de Configuração")
        self.top.configure(bg="#f0f4f8") # Mesmo fundo da janela principal
        
        # Geometria e Centralização
        largura = 460
        altura = 750
        pos_x = parent.winfo_x() + (parent.winfo_width() // 2) - (largura // 2)
        pos_y = parent.winfo_y() + (parent.winfo_height() // 2) - (altura // 2)

        # Correção: Garante que a janela não inicie fora da tela (coordenadas negativas)
        pos_x = max(0, pos_x)
        pos_y = max(0, pos_y)

        self.top.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        
        # Comportamento Modal (Harmonização de Navegabilidade)
        self.top.transient(parent) # Mantém sempre acima da janela pai
        self.top.grab_set()        # Bloqueia interação com a janela pai
        
        self.app = app_instance
        
        # Importa o módulo de wizard dinamicamente
        sys.path.append(self.app.obter_raiz())
        import tools.setup_wizard as wizard_module
        self.wizard = wizard_module

        # --- NOTEBOOK (ABAS) ---
        self.notebook = ttk.Notebook(self.top)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # === ABA 1: CONFIGURAÇÃO ===
        self.tab_config = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_config, text=" Configuração ")

        ttk.Label(self.tab_config, text="Configuração Inicial", style='Header.TLabel').pack(anchor='w')
        ttk.Label(self.tab_config, text="Prepare o ambiente para o robô.", style='Desc.TLabel').pack(anchor='w', pady=(0, 10))

        config_frame = ttk.Frame(self.tab_config)
        config_frame.pack(fill=tk.BOTH, expand=True)

        # Opção 0: Credenciais
        self.criar_secao(config_frame, "0. Credenciais de Acesso", 
                         "Configure seu CPF, Senha e Nome.", 
                         "Configurar Login", self.configurar_login)

        # Opção 1: Reset
        self.criar_secao(config_frame, "1. Arquivos Iniciais", 
                         "Gera modelos JSON em data/ (Reset).", 
                         "Gerar Modelos", self.gerar_modelos)

        # Opção 2: Pastas
        self.criar_secao(config_frame, "2. Estrutura de Pastas", 
                         "Cria pastas em aulas/inputs/.", 
                         "Criar Pastas", self.criar_pastas)

        # Opção 3: Auto Config
        self.criar_secao(config_frame, "3. Configuração Automática", 
                         "Lê histórico e configura turmas (Recomendado).", 
                         "Executar Auto Config", self.auto_config)

        # Opção 4: Calendário
        self.criar_secao(config_frame, "4. Disciplinas Anuais/Mensais", 
                         "Defina quais disciplinas usam unidades.", 
                         "Configurar Disciplinas", self.configurar_disciplinas)

        # === ABA 2: FERRAMENTAS ===
        self.tab_tools = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_tools, text=" Ferramentas ")

        ttk.Label(self.tab_tools, text="Ferramentas de Apoio", style='Header.TLabel').pack(anchor='w')
        ttk.Label(self.tab_tools, text="Utilitários para gestão e análise.", style='Desc.TLabel').pack(anchor='w', pady=(0, 10))

        tools_frame = ttk.Frame(self.tab_tools)
        tools_frame.pack(fill=tk.BOTH, expand=True)

        self.criar_secao(tools_frame, "Análise de Grade", "Relatório de horas registradas vs necessárias.", "Executar Analisador", lambda: self.app.iniciar_script("analisador_de_grade.py"))
        self.criar_secao(tools_frame, "Estatísticas", "Visualizar contagem de aulas por turma/disciplina.", "Ver Estatísticas", self.abrir_stats)
        self.criar_secao(tools_frame, "Conversor PDF", "Converter planos Markdown para PDF.", "Converter MD -> PDF", lambda: self.app.iniciar_script("converter_md_para_pdf.py"))

        frame_files = ttk.LabelFrame(tools_frame, text="Gestão de Arquivos", padding="10")
        frame_files.pack(fill=tk.X, pady=5)
        ttk.Button(frame_files, text="📂 Abrir Pasta de Aulas", command=lambda: self.abrir_pasta("aulas")).pack(fill=tk.X, pady=2)
        ttk.Button(frame_files, text="📂 Abrir Pasta de Logs", command=lambda: self.abrir_pasta("aulas/logs")).pack(fill=tk.X, pady=2)

        # === ABA 3: AJUDA ===
        self.tab_help = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_help, text=" Ajuda ")

        ttk.Label(self.tab_help, text="Documentação", style='Header.TLabel').pack(anchor='w')
        ttk.Label(self.tab_help, text="Acesse os guias do sistema.", style='Desc.TLabel').pack(anchor='w', pady=(0, 10))

        help_frame = ttk.Frame(self.tab_help)
        help_frame.pack(fill=tk.BOTH, expand=True)

        self.criar_secao(help_frame, "Tutorial de Uso", "Guia passo a passo para o professor.", "Ler Tutorial", lambda: self.abrir_documento("tutorial_uso.md"))
        self.criar_secao(help_frame, "Arquitetura Técnica", "Documentação para desenvolvedores.", "Ler Arquitetura", lambda: self.abrir_documento("arquitetura_tecnica.md"))
        self.criar_secao(help_frame, "Leia-me", "Informações gerais do projeto.", "Ler README", lambda: self.abrir_documento("README.md"))

    def criar_secao(self, parent, titulo, descricao, texto_botao, comando):
        frame = ttk.LabelFrame(parent, text=titulo, padding="10")
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text=descricao, wraplength=350).pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(frame, text=texto_botao, command=comando).pack(fill=tk.X)

    def abrir_stats(self):
        StatsViewer(self.top)

    def abrir_pasta(self, path_rel):
        raiz = self.app.obter_raiz()
        path = os.path.join(raiz, path_rel)
        os.makedirs(path, exist_ok=True)
        if os.name == 'nt':
            os.startfile(path)
        else:
            try: subprocess.Popen(['xdg-open', path])
            except: pass

    def abrir_documento(self, filename):
        raiz = self.app.obter_raiz()
        path = os.path.join(raiz, 'docs', filename)
        if not os.path.exists(path): path = os.path.join(raiz, filename)
        if os.path.exists(path):
            MarkdownViewer(self.top, f"Ajuda - {filename}", path)
        else:
            messagebox.showerror("Erro", f"Arquivo não encontrado: {filename}")

    def log_gui(self, msg):
        self.app.log(f"[Wizard] {msg}")

    def configurar_login(self):
        cpf = simpledialog.askstring("Login", "Digite seu Usuário (CPF):", parent=self.top)
        if not cpf: return
        senha = simpledialog.askstring("Login", "Digite sua Senha do Portal:", show="*", parent=self.top)
        if not senha: return
        prof = simpledialog.askstring("Configuração", "Nome do Professor (conforme horário):", parent=self.top)
        
        raiz = self.app.obter_raiz()
        data_dir = os.path.join(raiz, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Salvar credentials.json
        with open(os.path.join(data_dir, 'credentials.json'), 'w', encoding='utf-8') as f:
            json.dump({"username": cpf, "password": senha}, f, indent=4)
            
        # Salvar config.json se professor foi informado
        if prof:
            cfg_path = os.path.join(data_dir, 'config.json')
            cfg = {}
            if os.path.exists(cfg_path):
                try: 
                    with open(cfg_path, 'r', encoding='utf-8') as f: cfg = json.load(f)
                except: pass
            cfg['professor'] = prof
            with open(cfg_path, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=4, ensure_ascii=False)
        
        messagebox.showinfo("Sucesso", "Credenciais salvas com sucesso!")
        self.log_gui("Credenciais e Configurações atualizadas.")

    def gerar_modelos(self):
        if messagebox.askyesno("Confirmar", "Isso irá sobrescrever arquivos de configuração em 'data/'. Continuar?"):
            self.wizard.gerar_modelos_ficticios()
            self.log_gui("Modelos gerados com sucesso.")
            messagebox.showinfo("Sucesso", "Arquivos de modelo gerados em data/.")

    def criar_pastas(self):
        self.wizard.gerar_estrutura_inputs()
        self.log_gui("Estrutura de pastas verificada/criada.")
        messagebox.showinfo("Sucesso", "Pastas criadas em aulas/inputs/.")

    def auto_config(self):
        if not messagebox.askyesno("Confirmar", "Isso irá analisar seu histórico e reconfigurar turmas. Continuar?"):
            return
        
        sobrescrever = messagebox.askyesno("Sobrescrever", "Deseja sobrescrever nomes curtos de turmas existentes?\n\nSim: Recria nomes (ex: '1º A')\nNão: Mantém seus nomes personalizados")
        
        def resolver_conflito(turma_completa, sugestao_atual, conflito_com):
            msg = f"Conflito detectado!\n\nO nome curto '{sugestao_atual}' já é usado por:\n'{conflito_com}'\n\nMas a turma atual é:\n'{turma_completa}'\n\nDigite um novo nome curto para a turma atual:"
            novo = simpledialog.askstring("Conflito de Nomes", msg, parent=self.top)
            return novo if novo else sugestao_atual + "_X"

        try:
            self.wizard.gerar_configuracao_via_historico(sobrescrever=sobrescrever, callback_conflito=resolver_conflito)
            self.log_gui("Configuração automática concluída.")
            messagebox.showinfo("Sucesso", "Configuração automática finalizada! Verifique a pasta 'data/'.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def configurar_disciplinas(self):
        disciplinas, calendario, path = self.wizard.obter_dados_disciplinas_calendario()
        if not disciplinas:
            messagebox.showwarning("Aviso", "Nenhuma disciplina encontrada ou arquivos de configuração ausentes.")
            return

        # Janela de diálogo customizada para as disciplinas
        diag = tk.Toplevel(self.top)
        diag.title("Configurar Disciplinas")
        diag.geometry("600x640")

        vars_dict = {}
        anuais_atuais = set(calendario.get('disciplinas_config', {}).get('anuais', []))

        def salvar():
            novas_anuais = [code for code, var in vars_dict.items() if var.get()]
            novas_mensais = [code for code, var in vars_dict.items() if not var.get()]
            
            calendario['disciplinas_config']['anuais'] = sorted(novas_anuais)
            calendario['disciplinas_config']['mensais'] = sorted(novas_mensais)
            
            self.wizard.save_json(path, calendario)
            self.log_gui(f"Disciplinas atualizadas: {len(novas_anuais)} anuais, {len(novas_mensais)} mensais.")
            messagebox.showinfo("Sucesso", "Configuração de disciplinas salva!")
            diag.destroy()

        ttk.Button(diag, text="Salvar Configuração", command=salvar).pack(side="bottom", pady=10)

        canvas = tk.Canvas(diag)
        scrollbar = ttk.Scrollbar(diag, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(scrollable_frame, text="Marque as disciplinas ANUAIS:", font=('bold')).pack(pady=5)

        for disc in sorted(list(disciplinas)):
            codigo = "".join(c for c in disc if c.isalnum()).upper()
            var = tk.BooleanVar(value=(codigo in anuais_atuais))
            chk = ttk.Checkbutton(scrollable_frame, text=f"{disc} ({codigo})", variable=var)
            chk.pack(anchor='w', padx=5)
            vars_dict[codigo] = var

if __name__ == "__main__":
    root = tk.Tk()
    # Tenta definir um ícone se existir (opcional)
    # try: root.iconbitmap("icone.ico")
    # except: pass
    
    app = AppAutomação(root)
    root.mainloop()

'@
Create-File (Join-Path $RootPath "interfaces\gui_app.py") $Content_GuiApp

$Content_CliMenu = @'
import os
import sys
import subprocess
import time
import json

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def obter_caminho_raiz():
    # Assume que este script está em /interfaces e a raiz é o pai
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def executar_script(caminho_relativo, descricao):
    raiz = obter_caminho_raiz()
    caminho_script = os.path.join(raiz, caminho_relativo)
    
    print(f"\n{'='*50}")
    print(f"INICIANDO: {descricao}")
    print(f"{'='*50}\n")
    
    # Executa o script definindo o diretório de trabalho como a raiz do projeto
    # Isso é crucial para que os scripts encontrem a pasta 'data/' e 'aulas/'
    try:
        subprocess.run([sys.executable, caminho_script], cwd=raiz, check=True)
        print(f"\n[SUCESSO] {descricao} finalizado.")
    except subprocess.CalledProcessError:
        print(f"\n[ERRO] Falha ao executar {descricao}.")
    except KeyboardInterrupt:
        print(f"\n[CANCELADO] Operação interrompida pelo usuário.")
    
    input("\nPressione ENTER para voltar ao menu...")

def verificar_credenciais_ok():
    raiz = obter_caminho_raiz()
    creds_path = os.path.join(raiz, 'data', 'credentials.json')
    if not os.path.exists(creds_path): return False
    try:
        with open(creds_path, 'r', encoding='utf-8') as f:
            d = json.load(f)
            if d.get('username') in ["12345678900", "seu_usuario", ""] or d.get('password') in ["senha_secreta", "sua_senha", ""]:
                return False
    except: return False
    return True

def menu_principal():
    while True:
        limpar_tela()
        
        aviso = "" if verificar_credenciais_ok() else " [⚠️ Configuração Pendente]"

        print("==========================================")
        print(f"   🤖 ASSISTENTE DE AULAS - MENU PRINCIPAL{aviso}")
        print("==========================================")
        print("1. [COLETAR]   Atualizar base de dados (Scraper)")
        print("2. [ANALISAR]  Verificar grade e pendências")
        print("3. [PLANEJAR]  Gerar esqueletos de planos")
        print("4. [PREENCHER] Inserir conteúdo nos planos")
        print("5. [REGISTRAR] Enviar aulas para o portal")
        print("6. [CONFIGURAR] Assistente de Configuração (Wizard)")
        print("------------------------------------------")
        print("0. Sair")
        print("==========================================")
        
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            executar_script(os.path.join('tools', 'scraper.py'), "Coleta de Dados")
        elif opcao == '2':
            executar_script(os.path.join('tools', 'analisador_de_grade.py'), "Análise de Grade")
        elif opcao == '3':
            executar_script(os.path.join('tools', 'preparar_planos.py'), "Preparação de Planos")
        elif opcao == '4':
            executar_script(os.path.join('tools', 'preenchedor_planos.py'), "Preenchimento de Conteúdo")
        elif opcao == '5':
            executar_script(os.path.join('tools', 'registrar_aulas.py'), "Registro Automático")
        elif opcao == '6':
            executar_script(os.path.join('tools', 'setup_wizard.py'), "Assistente de Configuração")
        elif opcao == '0':
            print("Saindo...")
            break
        else:
            print("Opção inválida!")
            time.sleep(1)

if __name__ == "__main__":
    menu_principal()
'@
Create-File (Join-Path $RootPath "interfaces\cli_menu.py") $Content_CliMenu

# --- TOOLS (Scripts Python) ---

$Content_Scraper = @'
import json
import os
import time
import sys
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

class Scraper:
    """
    Um scraper em Python usando Selenium para automatizar a coleta de dados de aulas
    de um portal educacional, replicando a funcionalidade de um script Puppeteer.
    """

    def __init__(self, project_root):
        self.project_root = project_root
        self.data_path = os.path.join(self.project_root, 'data')
        self.driver = None
        self.wait = None
        self.mapeamento_turmas = {}
        self.mapa_turmas_reverso = {} # NOVO: Para mapear nome curto -> nome completo
        self.turmas_para_coletar = []
        self.nome_professor = ""

        # NOVO: Para filtrar disciplinas já completas
        self.disciplinas_completas = set()
        self.dados_antigos_completos = []

    def _initialize_driver(self):
        """Inicializa o WebDriver do Selenium."""
        print("[Scraper] Inicializando o WebDriver do Chrome...")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        # options.add_argument("--headless") # Descomente para rodar em segundo plano
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20) # Timeout padrão de 20 segundos
        except Exception as e:
            raise RuntimeError(f"Falha ao inicializar o WebDriver: {e}")

    def _analisar_aulas_existentes(self):
        """
        Lê 'aulas_coletadas.json', identifica disciplinas com 40h ou mais,
        e as adiciona à lista de exclusão para a coleta.
        """
        aulas_existentes_path = os.path.join(self.data_path, 'aulas_coletadas.json')
        if not os.path.exists(aulas_existentes_path):
            print("[Análise Prévia] Arquivo 'aulas_coletadas.json' não encontrado. Todas as disciplinas serão coletadas.")
            return

        print("[Análise Prévia] Lendo 'aulas_coletadas.json' para otimizar a coleta...")
        with open(aulas_existentes_path, 'r', encoding='utf-8') as f:
            aulas_existentes = json.load(f)

        # Contagem de aulas por (turma, disciplina)
        contagem = {}
        for aula in aulas_existentes:
            chave = (aula.get('turma'), aula.get('componenteCurricular'))
            if all(chave):
                contagem[chave] = contagem.get(chave, 0) + 1
        
        # Identifica disciplinas completas (>= 40h)
        for chave, total_aulas in contagem.items():
            if total_aulas >= 40:
                self.disciplinas_completas.add(chave)

        if not self.disciplinas_completas:
            print("[Análise Prévia] Nenhuma disciplina com 40h ou mais encontrada. Todas serão coletadas.")
            return

        print(f"[Análise Prévia] {len(self.disciplinas_completas)} disciplina(s) com carga horária completa serão ignoradas na coleta.")
        
        # Salva a lista de disciplinas ignoradas em um CSV
        csv_path = os.path.join(self.data_path, 'disciplinas_ignoradas_coleta.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            f.write("turma;disciplina\n")
            for turma, disciplina in sorted(list(self.disciplinas_completas)):
                f.write(f'"{turma}";"{disciplina}"\n')
        print(f"[Análise Prévia] Lista de disciplinas ignoradas salva em: {csv_path}")

        # Guarda os dados das disciplinas completas para adicionar ao resultado final
        self.dados_antigos_completos = [
            aula for aula in aulas_existentes if (aula.get('turma'), aula.get('componenteCurricular')) in self.disciplinas_completas
        ]
        print(f"[Análise Prévia] {len(self.dados_antigos_completos)} registros de aulas completas foram preservados.")

    def _load_configs(self):
        """Carrega os arquivos de configuração necessários."""
        print(f"[Scraper] Lendo configurações de: {self.data_path}")
        try:
            with open(os.path.join(self.data_path, 'config.json'), 'r', encoding='utf-8-sig') as f:
                config_data = json.load(f)
            with open(os.path.join(self.data_path, 'horarios_semanais_oficial.json'), 'r', encoding='utf-8-sig') as f:
                horarios_data = json.load(f)
            with open(os.path.join(self.data_path, 'turmas_com_disciplinas.json'), 'r', encoding='utf-8-sig') as f:
                self.mapeamento_turmas = json.load(f)
            with open(os.path.join(self.data_path, 'mapa_turmas.json'), 'r', encoding='utf-8-sig') as f:
                mapa_turmas_data = json.load(f)

            # Executa a análise das aulas existentes ANTES de prosseguir
            self._analisar_aulas_existentes()

            self.nome_professor = config_data.get('professor')
            if not self.nome_professor:
                raise ValueError('Nome do professor não encontrado em data/config.json')

            # CORREÇÃO: Acessa os dados de horário considerando que pode ser uma lista.
            # Baseado na lógica do scraper.js, que verifica se horariosData é um array.
            if isinstance(horarios_data, list) and horarios_data:
                # Pega o primeiro item da lista, que deve conter os dados dos professores.
                horarios_do_professor = horarios_data[0].get('professores', {}).get(self.nome_professor)
                if horarios_do_professor and 'turmas' in horarios_do_professor:
                    self.turmas_para_coletar = list(horarios_do_professor['turmas'].keys())
                else:
                    horarios_do_professor = None # Garante que não prossiga se não encontrar
            else:
                horarios_do_professor = None

            if not self.turmas_para_coletar or horarios_do_professor is None:
                 raise ValueError(f"Nenhuma turma encontrada para o professor '{self.nome_professor}' em horarios_semanais_oficial.json")
            
            # NOVO: Cria o mapa reverso para encontrar o nome completo a partir do nome curto
            # Ex: {'1º DS': 'EMI-INT CT DES SIST-1ª SÉRIE -I-A'}
            self.mapa_turmas_reverso = {v: k for k, v in mapa_turmas_data.items()}

            print(f"[Scraper] Turmas a serem coletadas: {', '.join(self.turmas_para_coletar)}")

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {e.filename}")
        except (json.JSONDecodeError, ValueError) as e:
            raise RuntimeError(f"Erro ao ler ou processar arquivos de configuração: {e}")


    def _take_screenshot(self, name):
        """Tira um screenshot da tela atual para depuração."""
        if not self.driver:
            print("AVISO: Não foi possível tirar screenshot porque o navegador não foi inicializado.")
            return

        # Cria o diretório de screenshots se ele não existir
        screenshots_dir = os.path.join(self.project_root, 'screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)

        safe_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        path = os.path.join(screenshots_dir, f"erro_{safe_name}.png")
        try:
            self.driver.save_screenshot(path)
            print(f"Screenshot de erro salvo em: {path}")
        except Exception as e:
            print(f"Falha ao salvar screenshot: {e}")

    def _login(self, url, credenciais):
        """Navega para a URL e realiza o login."""
        if not credenciais or not credenciais.get('username') or not credenciais.get('password'):
            raise ValueError('As credenciais (usuário/senha) não foram fornecidas.')

        print(f"Navegando para {url}...")
        self.driver.get(url)

        time.sleep(0.5) # Pausa para observação
        print("Preenchendo formulário de login...")
        self.wait.until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(credenciais['username'])
        time.sleep(0.5)
        self.driver.find_element(By.ID, 'password').send_keys(credenciais['password'])
        
        print("Clicando no botão de login...")        
        self.driver.find_element(By.CSS_SELECTOR, 'button[ng-click="logar(login)"]').click()

    def _select_profile_and_institution(self):
        """Seleciona o perfil de professor e a instituição."""
        try:
            # Etapa: Escolher Perfil
            print("Aguardando seleção de perfil 'Professor(a)'...")
            profile_selector = (By.CSS_SELECTOR, 'a.collection-item[ng-click="selecionarPerfil(perfil)"]')
            time.sleep(0.5)
            self.wait.until(EC.element_to_be_clickable(profile_selector)).click()
            print("Perfil 'Professor(a)' selecionado.")

            # Etapa: Escolher Instituição (dentro de um iframe)
            print("Aguardando iframe de seleção de instituição...")
            iframe_selector = (By.ID, 'iframe-container')
            self.wait.until(EC.frame_to_be_available_and_switch_to_it(iframe_selector))
            
            print("Dentro do iframe, clicando no botão 'ABRIR'...")
            # Em Selenium, usamos XPath para encontrar um elemento pelo texto contido nele
            open_button_selector = (By.XPATH, "//button[contains(., 'ABRIR')]")
            time.sleep(0.5)
            self.wait.until(EC.element_to_be_clickable(open_button_selector)).click()
            
            # Sair do iframe atual para o contexto da página principal
            self.driver.switch_to.default_content()
            print("Botão 'ABRIR' clicado. Retornando ao conteúdo principal.")

        except TimeoutException as e:
            self._take_screenshot("selecao_perfil_instituicao")
            raise TimeoutException(f"Tempo esgotado ao selecionar perfil ou instituição: {e.msg}")

    def _extract_table_data(self):
        """Extrai os dados da tabela de aulas na página atual."""
        try:
            # Espera o spinner de loading desaparecer
            spinner_selector = (By.CSS_SELECTOR, "svg.animate-spin")
            print("[Extração] Aguardando tabela carregar (spinner desaparecer)...")
            self.wait.until(EC.invisibility_of_element_located(spinner_selector))
        except TimeoutException:
            print("[Extração] AVISO: Spinner de loading não desapareceu no tempo esperado. A tabela pode estar vazia ou já carregada.")

        # Verifica se há a mensagem "Nenhum registro encontrado"
        try:
            if self.driver.find_element(By.XPATH, "//td[contains(., 'Nenhum registro encontrado')]" ).is_displayed():
                print("[Extração] Mensagem 'Nenhum registro encontrado' detectada.")
                return []
        except NoSuchElementException:
            pass # É o esperado, significa que a tabela tem dados

        # Extrai os dados
        linhas_dados = []
        # CORREÇÃO: Re-localiza a tabela a cada chamada para evitar StaleElementReferenceException.
        # A tabela é buscada aqui, e suas linhas e cabeçalhos são processados imediatamente.
        try:
            table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            headers = [th.text.strip() for th in table.find_elements(By.CSS_SELECTOR, "thead th")]
        except StaleElementReferenceException:
            print("[Extração] AVISO: A tabela ficou obsoleta durante a extração. Tentando novamente...")
            table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            headers = [th.text.strip() for th in table.find_elements(By.CSS_SELECTOR, "thead th")]
        header_map = {
            'Data da Aula': 'dataAula',
            'Horário (inicial ~ final)': 'horario',
            'Turma': 'turma',
            'Componente': 'componenteCurricular',
            'Data de Cadastro da Aula': 'data_cadastro',
            'Situação': 'status'
        }

        for linha in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
            celulas = linha.find_elements(By.TAG_NAME, "td")
            if not celulas: continue
            
            # Pula linhas que são apenas placeholders de "nenhum registro"
            if len(celulas) == 1 and "Nenhum registro encontrado" in celulas[0].text:
                continue

            linha_dict = {}
            for i, header_text in enumerate(headers):
                key = header_map.get(header_text)
                if key and i < len(celulas):
                    linha_dict[key] = celulas[i].text.strip()
            linhas_dados.append(linha_dict)
        
        return linhas_dados

    def _collect_with_pagination(self):
        """
        Coleta dados de todas as páginas da tabela, navegando pela paginação.
        """
        all_data = []
        page_count = 1
        
        # Otimização: Tenta configurar a paginação para 50 registros por página
        try:
            print("[Paginação] Tentando configurar para 50 registros por página...")
            # Encontra o botão do combobox que controla os registros por página
            registros_combobox = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@role='combobox' and contains(., 'Registros')]")
            ))
            
            # Só clica se não estiver já em 50
            if "50 Registros" not in registros_combobox.text:
                self.driver.execute_script("arguments[0].click();", registros_combobox)
                time.sleep(0.5) # Pausa para o dropdown abrir
                
                # Clica na opção "50"
                option_50 = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class, 'z-50')]//button[contains(., '50')]")
                ))
                self.driver.execute_script("arguments[0].click();", option_50)
                print("[Paginação] Configurado para 50 registros. Aguardando recarregamento...")
                # Espera a tabela recarregar após a mudança
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "svg.animate-spin")))
            else:
                print("[Paginação] Já está configurado para 50 registros por página.")
        except TimeoutException:
            print("[Paginação] AVISO: Não foi possível configurar para 50 registros. Continuando com o padrão.")

        while True:
            print(f"[Paginação] Coletando dados da página {page_count}...")
            
            # Extrai os dados da página atual
            data_on_page = self._extract_table_data()
            # CORREÇÃO: A condição foi simplificada para `if data_on_page:`
            # para garantir que qualquer dado retornado pela extração (incluindo aulas
            # com status "Excluída") seja contabilizado e processado.
            if data_on_page: 
                all_data.extend(data_on_page)
                print(f"[Paginação] {len(data_on_page)} aulas encontradas na página {page_count}. Total até agora: {len(all_data)}")
            else:
                print("[Paginação] Nenhuma aula encontrada na página atual.")

            # Verifica se o botão "Próxima" existe e está habilitado
            try:
                # Localiza o botão que contém o texto "Próxima"
                next_button_xpath = "//button[contains(., 'Próxima')]"
                next_button = self.wait.until(EC.presence_of_element_located((By.XPATH, next_button_xpath)))
                
                # O atributo 'disabled' determina se o botão está clicável
                is_disabled = next_button.get_attribute('disabled')
                
                if is_disabled:
                    print("[Paginação] Botão 'Próxima' está desabilitado. Fim da coleta.")
                    break
                
                # Se não estiver desabilitado, clica para ir para a próxima página
                print("[Paginação] Clicando no botão 'Próxima'...")
                time.sleep(0.5) # Pausa antes do clique para estabilidade
                self.driver.execute_script("arguments[0].click();", next_button)
                page_count += 1
                
                # Aguarda o recarregamento da tabela (o spinner é um bom indicador)
                # Esta espera é crucial para evitar coletar dados antigos antes da página atualizar
                spinner_selector = (By.CSS_SELECTOR, "svg.animate-spin")
                # Pausa após o clique para dar tempo do spinner aparecer
                time.sleep(1)
                self.wait.until(EC.invisibility_of_element_located(spinner_selector))

            except TimeoutException:
                # Se o botão "Próxima" não for encontrado, significa que não há mais páginas
                print("[Paginação] Botão 'Próxima' não encontrado. Fim da coleta.")
                break
            except Exception as e:
                print(f"[Paginação] Erro inesperado ao tentar paginar: {e}")
                break
        
        return all_data

    def _navigate_and_collect(self):
        """Navega pelas turmas e disciplinas, coletando os dados."""
        all_collected_data = []

        # Espera o iframe das turmas aparecer
        turmas_iframe_selector = (By.CSS_SELECTOR, 'iframe[src*="listagem-turmas"]')
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(turmas_iframe_selector))
        print("Iframe de listagem de turmas carregado.")

        for nome_turma_curto in self.turmas_para_coletar:
            print(f"\n--- [LOOP] Iniciando coleta para a turma: {nome_turma_curto} ---")
            
            # CORREÇÃO: Usa o mapa reverso para obter o nome completo da turma.
            nome_completo_turma = self.mapa_turmas_reverso.get(nome_turma_curto)
            if not nome_completo_turma:
                print(f"[LOOP] AVISO: Mapeamento não encontrado para a turma '{nome_turma_curto}'. Pulando...")
                continue

            print(f"[LOOP] Nome completo na página: '{nome_completo_turma}'")

            # Encontra as disciplinas para a turma atual usando o nome completo
            # CORREÇÃO 1: Usar "nomeTurma" para corresponder ao JSON.
            turma_disciplinas_info = next((turma for turma in self.mapeamento_turmas if turma.get("nomeTurma") == nome_completo_turma), None)
            
            # CORREÇÃO 2: Extrair apenas o nome da disciplina do objeto.
            disciplinas_da_turma = [d.get('nomeDisciplina') for d in turma_disciplinas_info.get('disciplinas', [])] if turma_disciplinas_info else []

            print(f"[LOOP] Disciplinas a coletar: {', '.join(disciplinas_da_turma)}")
            
            # A cada iteração de disciplina, a página recarrega.
            # Então, para cada disciplina, precisamos re-localizar o card correto.
            for i, nome_disciplina in enumerate(disciplinas_da_turma):
                print(f"\n--- [SUB-LOOP] Processando disciplina: '{nome_disciplina}' ({i+1}/{len(disciplinas_da_turma)}) ---")

                # NOVO: Verifica se a disciplina está na lista de exclusão
                chave_disciplina = (nome_completo_turma, nome_disciplina)
                if chave_disciplina in self.disciplinas_completas:
                    print(f"[SUB-LOOP] IGNORANDO: A disciplina '{nome_disciplina}' da turma '{nome_turma_curto}' já possui 40h ou mais.")
                    continue # Pula para a próxima disciplina

                
                try:
                    # Re-localiza todos os cards da turma e seleciona o da disciplina atual
                    card_xpath = f"//div[div/h3[normalize-space()='{nome_completo_turma}'] and div/p[normalize-space()='{nome_disciplina}']]"
                    card = self.wait.until(EC.presence_of_element_located((By.XPATH, card_xpath)))

                    # Clica em "Registro de aulas" dentro do card correto
                    time.sleep(0.5)
                    registro_aulas_link = card.find_element(By.XPATH, ".//p[normalize-space()='Registro de aulas']")
                    self.driver.execute_script("arguments[0].click();", registro_aulas_link) # Click com JS para evitar problemas de visibilidade
                    print("[SUB-LOOP] Clicou em 'Registro de aulas'.")

                    # Coleta com paginação
                    dados_disciplina = self._collect_with_pagination() # SUBSTITUÍDO
                    all_collected_data.extend(dados_disciplina)
                    print(f"[SUB-LOOP] {len(dados_disciplina)} aulas coletadas para '{nome_disciplina}'.")

                    # Voltar para a lista de disciplinas
                    print("[SUB-LOOP] Voltando para a lista de turmas/disciplinas...")
                    time.sleep(0.5)
                    voltar_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Voltar"]')))
                    self.driver.execute_script("arguments[0].click();", voltar_btn)
                    
                    # Espera a lista de cards recarregar
                    self.wait.until(EC.presence_of_element_located((By.XPATH, f"//h3[normalize-space()='{nome_completo_turma}']")))
                    print("[SUB-LOOP] Retornou à lista.")

                except (TimeoutException, StaleElementReferenceException) as e:
                    print(f"[SUB-LOOP] Erro ao processar a disciplina '{nome_disciplina}': {e}")
                    self._take_screenshot(f"erro_disciplina_{nome_turma_curto}_{nome_disciplina}")
                    
                    # Tenta voltar para a lista para continuar com a próxima disciplina/turma
                    try:
                        print("[SUB-LOOP] Tentando voltar para a lista (após erro)...")
                        time.sleep(0.5)
                        voltar_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Voltar"]')))
                        self.driver.execute_script("arguments[0].click();", voltar_btn)
                        self.wait.until(EC.presence_of_element_located((By.XPATH, f"//h3[normalize-space()='{nome_completo_turma}']")))
                        print("[SUB-LOOP] Retornou à lista (após erro).")
                    except Exception as nav_error:
                        print(f"Falha crítica ao tentar voltar para a lista após erro: {nav_error}. Interrompendo o scraper.")
                        raise
                    continue # Pula para a próxima disciplina
        
        # Ao final, retorna para o contexto principal para que o chamador possa continuar
        self.driver.switch_to.default_content()
        return all_collected_data
    
    def capturar_dados(self, url, credenciais, disciplina_alvo=None):
        """
Método principal que orquestra todo o processo de scraping.
        """
        # MODIFICAÇÃO: Não carrega mais configs nem inicializa o driver aqui.
        # Isso será feito pelo script que o chama.
        try:
            self._login(url, credenciais)
            self._select_profile_and_institution()

            # Se uma disciplina específica for fornecida, a lógica de navegação mudará.
            # Esta parte pode ser expandida se a navegação direta for necessária.
            # Por enquanto, a lógica principal de coleta já itera sobre as turmas.
            collected_data = self._navigate_and_collect()
            
            # NOVO: Adiciona os dados das disciplinas que já estavam completas de volta ao resultado
            if self.dados_antigos_completos:
                print(f"\n[Consolidação] Adicionando {len(self.dados_antigos_completos)} registros de aulas (que foram ignoradas na coleta) ao resultado final.")
                collected_data.extend(self.dados_antigos_completos)

            print(f"\n--- FIM DO SCRAPING ---")
            print(f"Total de aulas coletadas de todas as turmas: {len(collected_data)}")
            return collected_data

        except Exception as e:
            print(f"Ocorreu um erro fatal durante o scraping: {e}")
            self._take_screenshot("erro_fatal")
            # Re-lança a exceção para que o chamador saiba que algo deu errado
            raise

        # MODIFICAÇÃO: A responsabilidade de fechar o driver passa a ser do chamador.
        # finally:
        #     if self.driver:
        #         print("Fechando o navegador.")
        #         self.driver.quit()

    def coletar_dados_disciplina(self, nome_turma_completo, nome_disciplina_completo):
        """
        Coleta dados de uma única disciplina específica. Assume que o driver já está logado.
        """
        try:
            # O login e a seleção de perfil/instituição agora são feitos pelo chamador.

            # Espera o iframe das turmas aparecer
            turmas_iframe_selector = (By.CSS_SELECTOR, 'iframe[src*="listagem-turmas"]')
            self.wait.until(EC.frame_to_be_available_and_switch_to_it(turmas_iframe_selector))
            print(f"Iframe de listagem de turmas carregado. Navegando para a disciplina '{nome_disciplina_completo}'...")

            # OTIMIZAÇÃO: Verifica primeiro o cartão de resumo de aulas pendentes.
            try:
                # XPath para encontrar o número dentro do card "Aulas aguardando confirmação"
                pending_count_xpath = "//div[div[normalize-space()='Aulas aguardando confirmação']]//div[contains(@class, 'font-bold')]"
                pending_count_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, pending_count_xpath)))
                pending_count = int(pending_count_element.text.strip())
                
                print(f"  -> Verificação rápida: Encontradas {pending_count} aulas aguardando confirmação no resumo.")

                # Se não houver aulas pendentes, não há necessidade de varrer a tabela.
                if pending_count == 0:
                    print("  -> Nenhuma aula pendente encontrada. Retornando lista vazia para economizar tempo.")
                    self.driver.switch_to.default_content()
                    return []
            except (TimeoutException, ValueError) as e:
                # Se os cartões de resumo não forem encontrados ou o valor não for um número,
                # o script continua com a varredura completa da tabela como fallback.
                print(f"  -> AVISO: Não foi possível verificar o resumo de aulas pendentes (erro: {e}).")
                print("     -> Prosseguindo com a varredura completa da tabela como garantia.")
                pass


            # Navega para a disciplina e coleta os dados
            card_xpath = f"//div[div/h3[normalize-space()='{nome_turma_completo}'] and div/p[normalize-space()='{nome_disciplina_completo}']]"
            card = self.wait.until(EC.presence_of_element_located((By.XPATH, card_xpath)))

            registro_aulas_link = card.find_element(By.XPATH, ".//p[normalize-space()='Registro de aulas']")
            self.driver.execute_script("arguments[0].click();", registro_aulas_link)
            print("Clicou em 'Registro de aulas'.")

            dados_disciplina = self._collect_with_pagination()
            print(f"{len(dados_disciplina)} aulas coletadas para '{nome_disciplina_completo}'.")

            # Volta para a lista de disciplinas para a próxima iteração do loop no planejador
            print("  -> Voltando para a lista de turmas/disciplinas...")
            voltar_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Voltar"]')))
            self.driver.execute_script("arguments[0].click();", voltar_btn)
            self.wait.until(EC.presence_of_element_located((By.XPATH, f"//h3[normalize-space()='{nome_turma_completo}']")))
            print("  -> Retornou à lista.")

            # CORREÇÃO: Sai do iframe para o contexto principal, preparando para a próxima iteração do loop.
            self.driver.switch_to.default_content()

            return dados_disciplina

        except Exception as e:
            print(f"Ocorreu um erro fatal durante a coleta da disciplina: {e}")
            self._take_screenshot(f"erro_coleta_disciplina_{nome_turma_completo}")
            raise





# Exemplo de como usar a classe (pode ser chamado por outro script)
if __name__ == '__main__':
    # Este bloco agora serve apenas para execução direta e independente do scraper.
    # A lógica principal foi movida para ser reutilizável.
    # Este bloco só será executado se você rodar o script diretamente
    # Ex: python tools/scraper.py
    
    if getattr(sys, 'frozen', False):
        PROJECT_ROOT = os.path.dirname(sys.executable)
    else:
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Carrega credenciais de um arquivo (mais seguro do que colocar no código)
    try:
        with open(os.path.join(PROJECT_ROOT, 'data', 'credentials.json'), 'r') as f:
            creds = json.load(f)
    except FileNotFoundError:
        print("ERRO: Arquivo 'data/credentials.json' não encontrado.")
        print("Crie o arquivo com o formato: {\"username\": \"seu_usuario\", \"password\": \"sua_senha\"}")
        exit(1)
    except json.JSONDecodeError:
        print("ERRO: O arquivo 'data/credentials.json' está mal formatado.")
        exit(1)

    TARGET_URL = "https://portal.seduc.pi.gov.br/#!/turmas" # Substitua se necessário

    scraper_instance = Scraper(project_root=PROJECT_ROOT)    
    try:
        # A inicialização e carregamento de configs agora acontecem aqui para execução direta
        scraper_instance._load_configs()
        scraper_instance._initialize_driver()

        final_data = scraper_instance.capturar_dados(TARGET_URL, creds)
        
        # Salva os dados coletados em um arquivo JSON
        output_path = os.path.join(PROJECT_ROOT, 'data', 'aulas_coletadas.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        
        print(f"\nDados salvos com sucesso em: {output_path}")

    except Exception as e:
        print(f"\nO processo de scraping falhou. Causa: {e}")
    finally:
        # Garante que o driver seja fechado ao executar diretamente
        if scraper_instance and scraper_instance.driver:
            print("Fechando o navegador.")
            scraper_instance.driver.quit()
'@
Create-File (Join-Path $RootPath "tools\scraper.py") $Content_Scraper

$Content_SetupWizard = @'
import json
import os
import sys
import re

def get_root():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Arquivo salvo: {os.path.basename(filepath)}")

def _gerar_conteudo_json(data_dir, sobrescrever_sensiveis=False):
    os.makedirs(data_dir, exist_ok=True)

    # 1. config.json
    config_path = os.path.join(data_dir, 'config.json')
    # Só cria/sobrescreve se o arquivo não existir, ou se estivermos na pasta _modelo
    if not os.path.exists(config_path) or '_modelo' in data_dir:
        save_json(config_path, {
            "professor": "João da Silva"
        })

    # 2. credentials.json
    if sobrescrever_sensiveis or not os.path.exists(os.path.join(data_dir, 'credentials.json')):
        save_json(os.path.join(data_dir, 'credentials.json'), {
            "username": "12345678900",
            "password": "senha_secreta"
        })

    # 3. mapa_turmas.json (Nome Completo -> Nome Curto)
    save_json(os.path.join(data_dir, 'mapa_turmas.json'), {
        "ESCOLA ESTADUAL EXEMPLO - 1 SERIE A": "1º A",
        "ESCOLA ESTADUAL EXEMPLO - 2 SERIE B": "2º B"
    })

    # 4. turmas_com_disciplinas.json (Estrutura das disciplinas)
    save_json(os.path.join(data_dir, 'turmas_com_disciplinas.json'), [
        {
            "nomeTurma": "ESCOLA ESTADUAL EXEMPLO - 1 SERIE A",
            "disciplinas": [
                {"codigoDisciplina": "MAT", "nomeDisciplina": "Matemática"},
                {"codigoDisciplina": "PORT", "nomeDisciplina": "Português"}
            ]
        },
        {
            "nomeTurma": "ESCOLA ESTADUAL EXEMPLO - 2 SERIE B",
            "disciplinas": [
                {"codigoDisciplina": "HIST", "nomeDisciplina": "História"}
            ]
        }
    ])

    # 5. horarios_semanais_oficial.json (A grade horária complexa)
    save_json(os.path.join(data_dir, 'horarios_semanais_oficial.json'), [
        {
            "professores": {
                "João da Silva": {
                    "turmas": {
                        "1º A": {
                            "MAT": [
                                {"dia_semana_nome": "segunda-feira", "label_horario": "07:30 - 08:20"},
                                {"dia_semana_nome": "quarta-feira", "label_horario": "09:10 - 10:00"}
                            ],
                            "PORT": [
                                {"dia_semana_nome": "terça-feira", "label_horario": "07:30 - 08:20"}
                            ]
                        },
                        "2º B": {
                            "HIST": [
                                {"dia_semana_nome": "sexta-feira", "label_horario": "10:00 - 10:50"}
                            ]
                        }
                    }
                }
            }
        }
    ])
    
    # 6. calendario_letivo.json
    save_json(os.path.join(data_dir, 'calendario_letivo.json'), {
        "ano": 2025,
        "data_inicio": "03/02/2025",
        "data_fim": "12/12/2025",
        "carga_horaria_padrao_disciplina": 40,
        "disciplinas_config": {
            "anuais": [
                "PENSAMENTO_COMPUTACIONAL_DES_SIST", 
                "MENTORIAS_TEC_DES_SIST",
                "PROGRAMACAO_JOGOS_II",
                "MENTORIAS_TEC_JOGOS"
            ],
            "mensais": ["COMPUT"]
        },
        "restricoes_planejamento": {
            "COMPUT": {
                "data_inicio": "01/08/2025",
                "data_fim": "31/08/2025"
            }
        }
    })

    # 7. feriados.json
    save_json(os.path.join(data_dir, 'feriados.json'), {
        "feriados": [
            { "data": "03/03/2025", "descricao": "Carnaval" },
            { "data": "04/03/2025", "descricao": "Carnaval" },
            { "data": "18/04/2025", "descricao": "Sexta-feira Santa" }
        ]
    })

    # 8. .env (Configuração de Ambiente / IA)
    env_path = os.path.join(data_dir, '.env')
    if sobrescrever_sensiveis or not os.path.exists(env_path):
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("GEMINI_API_KEY=sua_chave_aqui\n")
        print(f"  [OK] Arquivo salvo: .env")

    # 9. aulas_coletadas.json (vazio por padrão)
    if not os.path.exists(os.path.join(data_dir, 'aulas_coletadas.json')):
        save_json(os.path.join(data_dir, 'aulas_coletadas.json'), [])

    # 10. recursos_links.json (com exemplo)
    if not os.path.exists(os.path.join(data_dir, 'recursos_links.json')):
        save_json(os.path.join(data_dir, 'recursos_links.json'), {
            "('1º DS', 'PENSAMENTO_COMPUTACIONAL_DES_SIST', 1)": "https://link.para.aula1.com/slide.pdf"
        })

def gerar_modelos_ficticios():
    """Gera arquivos JSON com dados de exemplo na pasta data/."""
    root = get_root()
    data_dir = os.path.join(root, 'data')
    print("\n--- Gerando Modelos JSON (Dados Fictícios) em data/ ---")
    _gerar_conteudo_json(data_dir, sobrescrever_sensiveis=False)
    print("\n✅ Modelos gerados! Edite os arquivos em 'data/' com seus dados reais.")

def gerar_espelho_modelo():
    """Gera uma cópia dos modelos fictícios na pasta data/_modelo."""
    root = get_root()
    modelo_dir = os.path.join(root, 'data', '_modelo')
    print(f"\n--- Gerando Espelho Fictício em {modelo_dir} ---")
    _gerar_conteudo_json(modelo_dir, sobrescrever_sensiveis=True)
    print("\n✅ Espelho de modelos gerado em data/_modelo/.")

def obter_dados_disciplinas_calendario():
    """
    Retorna as disciplinas encontradas no histórico e a configuração atual do calendário.
    Útil para interfaces gráficas construírem seus próprios menus.
    Retorna: (disciplinas_encontradas (set), calendario_data (dict), calendario_path (str))
    """
    root = get_root()
    data_dir = os.path.join(root, 'data')
    aulas_json_path = os.path.join(data_dir, 'aulas_coletadas.json')
    calendario_path = os.path.join(data_dir, 'calendario_letivo.json')

    if not os.path.exists(aulas_json_path):
        print("❌ Erro: 'data/aulas_coletadas.json' não encontrado.")
        print("   Execute o 'scraper.py' (Opção 1 do menu principal) para baixar seu histórico primeiro.")
        return None, None, None

    if not os.path.exists(calendario_path):
        print("❌ Erro: 'data/calendario_letivo.json' não encontrado. Execute a opção 1 ou 3 primeiro.")
        return None, None, None

    try:
        with open(aulas_json_path, 'r', encoding='utf-8-sig') as f:
            aulas = json.load(f)
        with open(calendario_path, 'r', encoding='utf-8-sig') as f:
            calendario = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler arquivos: {e}")
        return None, None, None

    disciplinas_encontradas = set()
    for aula in aulas:
        if aula.get('componenteCurricular'):
            disciplinas_encontradas.add(aula['componenteCurricular'])
    
    if not disciplinas_encontradas:
        print("⚠️ Nenhuma disciplina encontrada no histórico.")
        return None, None, None

    if 'disciplinas_config' not in calendario:
        calendario['disciplinas_config'] = {'anuais': [], 'mensais': []}
        
    return disciplinas_encontradas, calendario, calendario_path

def configurar_disciplinas_calendario():
    """Versão interativa (CLI) para configurar disciplinas."""
    disciplinas_encontradas, calendario, calendario_path = obter_dados_disciplinas_calendario()
    if not disciplinas_encontradas: return

    config_disciplinas = calendario.get('disciplinas_config', {})
    anuais = set(config_disciplinas.get('anuais', []))
    mensais = set(config_disciplinas.get('mensais', []))

    print("\n--- Configuração de Disciplinas (Anual vs Mensal) ---")
    print("Para cada disciplina, digite 'a' para Anual ou 'm' para Mensal.")
    print("Pressione ENTER para manter a configuração atual (se existir) ou definir como Mensal (padrão).")

    novas_anuais = set(anuais)
    novas_mensais = set(mensais)

    for disc in sorted(list(disciplinas_encontradas)):
        # Gera o código usado nas pastas (mesma lógica do gerar_estrutura_inputs)
        codigo = "".join(c for c in disc if c.isalnum()).upper()
        
        tipo_atual = "Novo/Padrão (Mensal)"
        if codigo in anuais: tipo_atual = "Anual"
        elif codigo in mensais: tipo_atual = "Mensal"
        
        print(f"\nDisciplina: {disc}")
        print(f"  -> Código Interno: {codigo}")
        print(f"  -> Status Atual: {tipo_atual}")
        
        escolha = input("  [A]nual ou [M]ensal? ").strip().lower()
        
        if escolha == 'a':
            novas_anuais.add(codigo)
            if codigo in novas_mensais: novas_mensais.remove(codigo)
        elif escolha == 'm':
            novas_mensais.add(codigo)
            if codigo in novas_anuais: novas_anuais.remove(codigo)
        else:
            # Se não escolher nada e for novo, vai para mensal
            if codigo not in novas_anuais and codigo not in novas_mensais:
                novas_mensais.add(codigo)

    # Atualiza o calendário
    calendario['disciplinas_config']['anuais'] = sorted(list(novas_anuais))
    calendario['disciplinas_config']['mensais'] = sorted(list(novas_mensais))
    
    save_json(calendario_path, calendario)
    print("\n✅ Calendário letivo atualizado com as classificações de disciplinas.")

def gerar_configuracao_via_historico(sobrescrever=None, callback_conflito=None):
    """
    Lê 'data/aulas_coletadas.json', extrai turmas e disciplinas reais,
    atualiza 'mapa_turmas.json' e 'turmas_com_disciplinas.json',
    e cria a estrutura de pastas.
    :param sobrescrever: True/False para forçar decisão, None para perguntar (CLI).
    :param callback_conflito: Função(nome_turma, sugestao_atual) -> nova_sugestao. Se None, usa input (CLI).
    """
    root = get_root()
    data_dir = os.path.join(root, 'data')
    aulas_json_path = os.path.join(data_dir, 'aulas_coletadas.json')

    if not os.path.exists(aulas_json_path):
        print("❌ Erro: 'data/aulas_coletadas.json' não encontrado.")
        print("   Execute o 'scraper.py' (Opção 1 do menu principal) para baixar seu histórico primeiro.")
        return

    print("\n--- Analisando Histórico (aulas_coletadas.json) ---")
    try:
        with open(aulas_json_path, 'r', encoding='utf-8-sig') as f:
            aulas = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler JSON: {e}")
        return

    if not aulas:
        print("⚠️ O arquivo de histórico está vazio.")
        return

    # 1. Extrair Turmas e Disciplinas únicas
    # Estrutura: { "Nome Turma Completo": { "Nome Disciplina" } }
    dados_extraidos = {}
    
    for aula in aulas:
        turma = aula.get('turma')
        disciplina = aula.get('componenteCurricular')
        
        if turma and disciplina:
            if turma not in dados_extraidos:
                dados_extraidos[turma] = set()
            dados_extraidos[turma].add(disciplina)

    print(f"  -> Encontradas {len(dados_extraidos)} turmas no histórico.")

    # 1.5 Garantir existência de arquivos essenciais (Calendário e Feriados)
    # Isso evita que a geração de pastas falhe ou crie apenas estruturas mensais por falta de config
    if not os.path.exists(os.path.join(data_dir, 'calendario_letivo.json')):
        print("  [!] 'calendario_letivo.json' não encontrado. Criando modelo padrão...")
        save_json(os.path.join(data_dir, 'calendario_letivo.json'), {
            "ano": 2025,
            "data_inicio": "03/02/2025",
            "data_fim": "12/12/2025",
            "carga_horaria_padrao_disciplina": 40,
            "disciplinas_config": {
                "anuais": ["COMPUT", "PROJETO_VIDA"],
                "mensais": ["DISC_MENSAL"]
            },
            "restricoes_planejamento": {}
        })

    if not os.path.exists(os.path.join(data_dir, 'feriados.json')):
        save_json(os.path.join(data_dir, 'feriados.json'), {
            "feriados": [
                { "data": "24/02/2025", "descricao": "Carnaval" },
                { "data": "25/02/2025", "descricao": "Carnaval" }
            ]
        })

    # 2. Atualizar mapa_turmas.json
    mapa_path = os.path.join(data_dir, 'mapa_turmas.json')
    mapa_turmas = {}
    
    # Mapa reverso temporário para detectar colisões: ShortName -> FullName
    nomes_curtos_usados = {}
    
    sobrescrever_local = False
    if os.path.exists(mapa_path):
        with open(mapa_path, 'r', encoding='utf-8-sig') as f:
            mapa_turmas = json.load(f)
        
        if mapa_turmas:
            if sobrescrever is None:
                print(f"  [i] Encontrados {len(mapa_turmas)} mapeamentos de turmas existentes.")
                resp = input("  [?] Deseja sobrescrever os nomes curtos existentes (s) ou apenas adicionar novos (n)? (s/n): ").strip().lower()
                sobrescrever_local = (resp == 's')
            else:
                sobrescrever_local = sobrescrever
            
            if not sobrescrever_local:
                # Se não for sobrescrever, carregamos os existentes para respeitar e verificar colisão
                for full, short in mapa_turmas.items():
                    nomes_curtos_usados[short] = full

    print("\n--- Atualizando Configurações ---")
    
    # Gera nomes curtos se não existirem ou se for sobrescrever
    for turma_completa in dados_extraidos:
        if sobrescrever_local or turma_completa not in mapa_turmas:
            # Tenta criar um nome curto simples (ex: pega as últimas palavras ou siglas)
            # Tenta padrões comuns: "1ª SÉRIE ... A", "9º ANO ... B" usando Regex
            match = re.search(r'(\d+)[ºªa-z]*\s*(?:SÉRIE|ANO|SERIE).*?([A-Z])(?:\s*$|$)', turma_completa, re.IGNORECASE)
            if match:
                mapa_turmas[turma_completa] = f"{match.group(1)}º {match.group(2)}"
            else:
                partes = turma_completa.split('-') # fallback
                sugestao = partes[-1].strip()
                # Evita nomes muito curtos como "A" ou "B" pegando contexto anterior se possível
                if len(sugestao) <= 2 and len(partes) > 1:
                    sugestao = f"{partes[-2].strip()} {sugestao}"
                
                mapa_turmas[turma_completa] = sugestao[:20] if len(sugestao) > 0 else turma_completa[:20]
            
            # Verificação de colisão de nomes curtos
            sugestao_atual = mapa_turmas[turma_completa]
            while sugestao_atual in nomes_curtos_usados and nomes_curtos_usados[sugestao_atual] != turma_completa:
                conflito_com = nomes_curtos_usados[sugestao_atual]
                
                if callback_conflito:
                    nova_sugestao = callback_conflito(turma_completa, sugestao_atual, conflito_com)
                else:
                    print(f"\n⚠️  CONFLITO DETECTADO para o nome curto: '{sugestao_atual}'")
                    print(f"  1. Turma já mapeada: '{conflito_com}' -> '{sugestao_atual}'")
                    print(f"  2. Turma atual:      '{turma_completa}'")
                    print("  Precisamos de nomes distintos para criar pastas separadas.")
                    nova_sugestao = input(f"  Digite um novo nome curto para a turma atual ('{turma_completa}'): ").strip()
                
                if nova_sugestao:
                    sugestao_atual = nova_sugestao
                    mapa_turmas[turma_completa] = sugestao_atual
                else:
                    print("  Nome inválido. Tente novamente.")
            
            nomes_curtos_usados[sugestao_atual] = turma_completa
            print(f"  [+] Mapeado: '{turma_completa}' -> '{mapa_turmas[turma_completa]}'")
    
    save_json(mapa_path, mapa_turmas)

    # 3. Gerar turmas_com_disciplinas.json
    turmas_config_path = os.path.join(data_dir, 'turmas_com_disciplinas.json')
    nova_config_turmas = []

    for turma_completa, disciplinas_set in dados_extraidos.items():
        lista_disciplinas = []
        for nome_disc in sorted(list(disciplinas_set)):
            # Gera um código simples para a pasta (ex: MATEMATICA)
            codigo = "".join(c for c in nome_disc if c.isalnum()).upper()
            lista_disciplinas.append({
                "codigoDisciplina": codigo,
                "nomeDisciplina": nome_disc
            })
        
        nova_config_turmas.append({
            "nomeTurma": turma_completa,
            "disciplinas": lista_disciplinas
        })
    
    save_json(turmas_config_path, nova_config_turmas)
    print("  -> 'turmas_com_disciplinas.json' recriado com base no histórico.")

    # 4. Criar pastas
    print("\n--- Criando Pastas de Input ---")
    gerar_estrutura_inputs()

def gerar_estrutura_inputs():
    """Lê os JSONs de configuração e cria as pastas correspondentes em aulas/inputs."""
    root = get_root()
    data_dir = os.path.join(root, 'data')
    inputs_dir = os.path.join(root, 'aulas', 'inputs')
    
    print("\n--- Gerando Estrutura de Pastas em aulas/inputs/ ---")

    try:
        with open(os.path.join(data_dir, 'turmas_com_disciplinas.json'), 'r', encoding='utf-8') as f:
            turmas = json.load(f)
        with open(os.path.join(data_dir, 'mapa_turmas.json'), 'r', encoding='utf-8') as f:
            mapa = json.load(f)
        
        # Tenta carregar calendário para saber quais disciplinas são anuais
        anuais = set()
        if os.path.exists(os.path.join(data_dir, 'calendario_letivo.json')):
            with open(os.path.join(data_dir, 'calendario_letivo.json'), 'r', encoding='utf-8-sig') as f:
                cal = json.load(f)
                anuais = set(d.upper() for d in cal.get('disciplinas_config', {}).get('anuais', []))
    except FileNotFoundError:
        print("❌ Erro: Arquivos de configuração não encontrados em 'data/'. Execute a opção 1 primeiro.")
        return

    count = 0
    for turma in turmas:
        nome_completo = turma['nomeTurma']
        # Tenta obter o nome curto, se não existir, usa o completo sanitizado
        nome_curto = mapa.get(nome_completo, nome_completo).replace(' ', '_').replace('º', '')
        
        for disciplina in turma['disciplinas']:
            # Usa o código da disciplina para a pasta (mais seguro que nome longo)
            nome_disc_pasta = disciplina['codigoDisciplina']
            
            caminho = os.path.join(inputs_dir, nome_curto, nome_disc_pasta)
            os.makedirs(caminho, exist_ok=True)
            
            # Cria subpastas baseadas no tipo (Anual vs Mensal)
            if disciplina['codigoDisciplina'].upper() in anuais:
                subpastas = ["Unidade_I", "Unidade_II", "Unidade_III", "Unidade_IV"]
            else:
                subpastas = ["Semana_01", "Semana_02", "Semana_03", "Semana_04"]
            
            for sub in subpastas:
                os.makedirs(os.path.join(caminho, sub), exist_ok=True)

            # Cria um arquivo de exemplo para orientar o usuário
            exemplo_md = os.path.join(caminho, subpastas[0], '_exemplo_aula.md')
            if not os.path.exists(exemplo_md):
                with open(exemplo_md, 'w', encoding='utf-8') as f:
                    f.write(f"# Aula 01 - {disciplina['nomeDisciplina']}\n\n### Objetivos da Aula\n* Objetivo 1\n* Objetivo 2\n\n### Conteúdo\nDescreva o conteúdo aqui...")
            
            print(f"  [+] Criado: aulas/inputs/{nome_curto}/{nome_disc_pasta}/")
            count += 1
            
    print(f"\n✅ Estrutura criada com sucesso! {count} pastas de disciplinas verificadas.")

def menu():
    while True:
        print("\n=== 🧙 ASSISTENTE DE CONFIGURAÇÃO ===")
        print("1. [RESET] Gerar JSONs de Exemplo em data/ (Sobrescreve configurações!)")
        print("2. [PASTAS] Criar pastas em aulas/inputs/ baseadas na configuração atual")
        print("3. [AUTO] Gerar configuração e pastas a partir do histórico (aulas_coletadas.json)")
        print("4. [CALENDARIO] Configurar Disciplinas (Anual/Mensal)")
        print("5. [MODELO] Gerar espelho fictício em data/_modelo/")
        print("0. Sair")
        op = input("Escolha uma opção: ")
        if op == '1':
            gerar_modelos_ficticios()
        elif op == '2':
            gerar_estrutura_inputs()
        elif op == '3':
            gerar_configuracao_via_historico()
        elif op == '4':
            configurar_disciplinas_calendario()
        elif op == '5':
            gerar_espelho_modelo()
        elif op == '0':
            break

if __name__ == "__main__":
    menu()

'@
Create-File (Join-Path $RootPath "tools\setup_wizard.py") $Content_SetupWizard

$Content_CortarIcones = @'
import os
import sys

def slice_image(image_path, output_dir, rows=2, cols=3):
    """
    Corta uma imagem de grade (sprite sheet) em ícones individuais.
    Requer: pip install Pillow
    """
    try:
        from PIL import Image
    except ImportError:
        print("❌ Erro: A biblioteca Pillow (PIL) é necessária.")
        print("   Instale rodando: pip install Pillow")
        return

    if not os.path.exists(image_path):
        print(f"❌ Arquivo não encontrado: {image_path}")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    print(f"--- Processando: {image_path} ---")
    img = Image.open(image_path)
    w, h = img.size
    
    # Calcula o tamanho de cada célula
    icon_w = w // cols
    icon_h = h // rows
    
    names = ["icone_app", "icone_scraper", "icone_planejamento", "icone_preenchimento", "icone_registro", "icone_config"]
    
    count = 0
    for r in range(rows):
        for c in range(cols):
            if count >= len(names): break
            
            left = c * icon_w
            top = r * icon_h
            right = left + icon_w
            bottom = top + icon_h
            
            crop = img.crop((left, top, right, bottom))
            output_filename = f"{names[count]}.png"
            save_path = os.path.join(output_dir, output_filename)
            crop.save(save_path)
            print(f"  ✅ Salvo: {output_filename}")
            count += 1
    
    print(f"\nÍcones extraídos para a pasta: {output_dir}")

if __name__ == "__main__":
    # Uso: python tools/cortar_icones.py caminho/para/sua_imagem_grade.png
    if len(sys.argv) < 2:
        print("Uso: python tools/cortar_icones.py <caminho_da_imagem_grade.png>")
    else:
        # Define a pasta de saída como 'recursos' na raiz do projeto
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output = os.path.join(root, 'recursos')
        slice_image(sys.argv[1], output)
'@
Create-File (Join-Path $RootPath "tools\cortar_icones.py") $Content_CortarIcones


$Content_VerAulas = @'
import json
import os
import sys
from collections import defaultdict
from datetime import datetime

def carregar_dados(data_path):
    """Carrega os arquivos JSON necessários."""
    try:
        with open(os.path.join(data_path, 'aulas_coletadas.json'), 'r', encoding='utf-8-sig') as f:
            aulas_coletadas = json.load(f)
        with open(os.path.join(data_path, 'turmas_com_disciplinas.json'), 'r', encoding='utf-8-sig') as f:
            turmas_disciplinas = json.load(f)
        with open(os.path.join(data_path, 'mapa_turmas.json'), 'r', encoding='utf-8-sig') as f:
            mapa_turmas = json.load(f)
        return aulas_coletadas, turmas_disciplinas, mapa_turmas
    except FileNotFoundError as e:
        print(f"ERRO: Arquivo de dados não encontrado: {e.filename}")
        print("Por favor, execute o 'scraper.py' primeiro para gerar o 'aulas_coletadas.json'.")
        return None, None, None
    except Exception as e:
        print(f"ERRO ao carregar arquivos de dados: {e}")
        return None, None, None

def obter_resumo_disciplina(aulas_coletadas, turmas_disciplinas):
    """Retorna lista de tuplas (codigo, nome, contagem) para disciplinas."""
    # 1. Criar um mapa de nome completo da disciplina para seu código curto
    mapa_disciplinas = {}
    for turma in turmas_disciplinas:
        for disciplina in turma.get('disciplinas', []):
            nome_completo = disciplina.get('nomeDisciplina')
            codigo_curto = disciplina.get('codigoDisciplina')
            if nome_completo and codigo_curto:
                mapa_disciplinas[nome_completo] = {
                    "codigo": codigo_curto,
                    "nome": nome_completo
                }

    # 2. Contar aulas por nome completo da disciplina
    contagem_disciplinas = defaultdict(int)
    for aula in aulas_coletadas:
        # Considera apenas aulas com status que indicam que a aula foi dada
        if aula.get('status') in ['Aula confirmada', 'Aguardando confirmação']:
            nome_disciplina = aula.get('componenteCurricular')
            if nome_disciplina:
                contagem_disciplinas[nome_disciplina] += 1

    # 3. Preparar dados para exibição
    dados_tabela = []
    for nome_completo, contagem in contagem_disciplinas.items():
        info_disciplina = mapa_disciplinas.get(nome_completo, {"codigo": "N/A", "nome": nome_completo})
        dados_tabela.append((info_disciplina['codigo'], info_disciplina['nome'], contagem))

    # Ordena por nome do código da disciplina para consistência
    dados_tabela.sort()
    return dados_tabela

def ver_por_disciplina(aulas_coletadas, turmas_disciplinas):
    """Conta as aulas por disciplina e exibe um resumo."""
    if not aulas_coletadas:
        print("Nenhuma aula coletada para analisar.")
        return
    dados_tabela = obter_resumo_disciplina(aulas_coletadas, turmas_disciplinas)

    # 4. Exibir a tabela formatada
    print("\n--- Resumo de Aulas Registradas por Disciplina ---")
    # Encontra a largura máxima para o nome da disciplina para alinhar a tabela
    max_len_nome = max(len(row[1]) for row in dados_tabela) if dados_tabela else 30
    
    header = f"{'Código':<15} | {'Nome da Disciplina':<{max_len_nome}} | {'Aulas Registradas'}"
    print(header)
    print("-" * len(header))

    for codigo, nome, contagem in dados_tabela:
        print(f"{codigo:<15} | {nome:<{max_len_nome}} | {contagem}")
    
    print("-" * len(header))
    print(f"Total de disciplinas encontradas: {len(dados_tabela)}")

def obter_resumo_turma_dados(aulas_coletadas, mapa_turmas):
    """Retorna lista de tuplas (nome_curto, nome_completo, contagem) para turmas."""
    contagem_turmas = defaultdict(int)
    for aula in aulas_coletadas:
        if aula.get('status') in ['Aula confirmada', 'Aguardando confirmação']:
            nome_turma = aula.get('turma')
            if nome_turma:
                contagem_turmas[nome_turma] += 1

    dados_tabela = []
    for nome_completo, contagem in contagem_turmas.items():
        nome_curto = mapa_turmas.get(nome_completo, "N/A")
        dados_tabela.append((nome_curto, nome_completo, contagem))

    dados_tabela.sort()
    return dados_tabela

def ver_por_turma(aulas_coletadas, mapa_turmas):
    """Conta as aulas por turma e exibe um resumo."""
    if not aulas_coletadas:
        print("Nenhuma aula coletada para analisar.")
        return
    dados_tabela = obter_resumo_turma_dados(aulas_coletadas, mapa_turmas)

    print("\n--- Resumo de Aulas Registradas por Turma ---")
    max_len_nome = max(len(row[1]) for row in dados_tabela) if dados_tabela else 30
    
    header = f"{'Nome Curto':<15} | {'Nome Completo da Turma':<{max_len_nome}} | {'Aulas Registradas'}"
    print(header)
    print("-" * len(header))

    for nome_curto, nome_completo, contagem in dados_tabela:
        print(f"{nome_curto:<15} | {nome_completo:<{max_len_nome}} | {contagem}")
    
    print("-" * len(header))
    print(f"Total de turmas encontradas: {len(dados_tabela)}")

def obter_resumo_data_dados(aulas_coletadas):
    """Retorna lista de tuplas (data_obj, contagem) para datas."""
    contagem_data = defaultdict(int)
    for aula in aulas_coletadas:
        if aula.get('status') in ['Aula confirmada', 'Aguardando confirmação']:
            data_aula = aula.get('dataAula')
            if data_aula:
                contagem_data[data_aula] += 1

    dados_tabela = []
    for data_str, contagem in contagem_data.items():
        try:
            data_obj = datetime.strptime(data_str, "%d/%m/%Y")
            dados_tabela.append((data_obj, contagem))
        except ValueError:
            continue # Ignora datas mal formatadas

    dados_tabela.sort()
    return dados_tabela

def ver_por_data(aulas_coletadas):
    """Conta as aulas por data e exibe um resumo."""
    if not aulas_coletadas:
        print("Nenhuma aula coletada para analisar.")
        return
    dados_tabela = obter_resumo_data_dados(aulas_coletadas)

    print("\n--- Resumo de Aulas Registradas por Data ---")
    header = f"{'Data':<15} | {'Aulas Registradas'}"
    print(header)
    print("-" * len(header))

    for data_obj, contagem in dados_tabela:
        print(f"{data_obj.strftime('%d/%m/%Y'):<15} | {contagem}")
    
    print("-" * len(header))
    print(f"Total de dias com aulas: {len(dados_tabela)}")

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_PATH = os.path.join(PROJECT_ROOT, 'data')

    aulas, disciplinas_map, turmas_map = carregar_dados(DATA_PATH)

    if aulas:
        # Verifica se está rodando em um terminal interativo
        if not sys.stdin.isatty():
            print("\n[Modo não-interativo detectado - Execução via Interface Gráfica]")
            print("Exibindo resumo geral das disciplinas...")
            ver_por_disciplina(aulas, disciplinas_map)
            print("\nPara ver outros relatórios (Turma/Data), execute este script via terminal (CMD).")
            sys.exit(0)

        while True:
            print("\n--- Menu de Visualização ---")
            print("1. Ver por Disciplina")
            print("2. Ver por Turma")
            print("3. Ver por Data")
            print("0. Sair")
            
            escolha = input("Escolha uma opção: ")

            if escolha == '1':
                ver_por_disciplina(aulas, disciplinas_map)
            elif escolha == '2':
                ver_por_turma(aulas, turmas_map)
            elif escolha == '3':
                ver_por_data(aulas)
            elif escolha == '0':
                print("Saindo...")
                break
            else:
                print("Opção inválida. Tente novamente.")
'@
Create-File (Join-Path $RootPath "tools\ver_aulas_por_disciplina.py") $Content_VerAulas

$Content_Registrar = @'
import json, os, re, time, sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
from webdriver_manager.chrome import ChromeDriverManager

class Registrador:
    def __init__(self, project_root):
        self.project_root = project_root
        self.driver = None
        self.wait = None

    # Mapeamento reverso para meses (para navegação no calendário)
    MESES_MAP_REVERSE = {
        "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
        "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
        "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12 # Corrigido o mapeamento de novembro
    }

    def _initialize_driver(self):
        print("[Registrador] Inicializando o WebDriver...")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized") # Iniciar maximizado
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 30)
        # REMOVIDO: set_window_size, pois --start-maximized já cuida disso
        print("  -> Navegador iniciado maximizado.")
        self.driver.execute_script("document.body.style.zoom = '80%'") # Mantendo o zoom
        print("  -> Zoom da página definido para 80%.")


    def _take_screenshot(self, name):
        try:
            screenshots_dir = os.path.join(self.project_root, 'screenshots')
            os.makedirs(screenshots_dir, exist_ok=True)
            path = os.path.join(screenshots_dir, f"registro_erro_{name}.png")
            self.driver.save_screenshot(path)
            print(f"  -> Screenshot de erro salvo em: {path}")
        except NoSuchWindowException:
            print("  -> ERRO: Não foi possível tirar screenshot porque a janela do navegador já foi fechada.")

    def _login_and_navigate_to_turmas(self, url, credenciais):
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(credenciais['username'])
        self.driver.find_element(By.ID, 'password').send_keys(credenciais['password'])
        self.driver.find_element(By.CSS_SELECTOR, 'button[ng-click="logar(login)"]').click()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.collection-item[ng-click="selecionarPerfil(perfil)"]'))).click()
        self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'iframe-container')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'ABRIR')]"))).click()
        self.driver.switch_to.default_content()

    def _navigate_to_disciplina(self, turma, disciplina):
        print(f"\n--- Navegando para: {turma} / {disciplina} ---")
        try:
            # Garante que o driver está no contexto principal antes de tentar mudar para o iframe
            self.driver.switch_to.default_content()
            turmas_iframe_selector = (By.CSS_SELECTOR, 'iframe[src*="listagem-turmas"]')
            self.wait.until(EC.frame_to_be_available_and_switch_to_it(turmas_iframe_selector))
            
            # Espera por um elemento genérico dentro do iframe para garantir que o conteúdo carregou
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[div/h3]"))) # Espera por qualquer card de turma
            
            card_xpath = f"//div[div/h3[normalize-space()='{turma}'] and div/p[normalize-space()='{disciplina}']]"
            card = self.wait.until(EC.presence_of_element_located((By.XPATH, card_xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
            registro_aulas_link = card.find_element(By.XPATH, ".//p[normalize-space()='Registro de aulas']")
            self.driver.execute_script("arguments[0].click();", registro_aulas_link)
            time.sleep(1)
            print("[Navegação] Acessou a página de 'Registro de aulas'.")
            return True
        except TimeoutException:
            print(f"ERRO: Não foi possível encontrar o card para a disciplina '{disciplina}' na turma '{turma}'.")
            self._take_screenshot(f"card_nao_encontrado_{turma}_{disciplina}")
            return False

    def _navigate_back_to_turmas(self):
        try:
            print("[Recuperação] Tentando voltar para a lista de turmas para continuar...")
            if not self.driver.window_handles:
                print("ERRO CRÍTICO: A janela do navegador não está mais disponível.")
                return

            print("  -> Usando o comando 'voltar' do navegador...")
            self.driver.back()
            time.sleep(2)

            print("  -> Verificando se o iframe da lista de turmas recarregou...")
            self.driver.switch_to.default_content()
            turmas_iframe_selector = (By.CSS_SELECTOR, 'iframe[src*="listagem-turmas"]')
            self.wait.until(EC.frame_to_be_available_and_switch_to_it(turmas_iframe_selector))
            
            print("[Recuperação] Retorno à lista de turmas bem-sucedido.")

        except Exception as e:
            print(f"ERRO CRÍTICO: O comando 'voltar' falhou. Tentando URL direta como fallback. Erro: {e}")
            self._take_screenshot("erro_fatal_navegar_voltar")
            try:
                self.driver.get("https://portal.seduc.pi.gov.br/#!/turmas")
                # Após um hard reload, precisamos passar pela dança inicial do iframe novamente
                self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'iframe-container')))
                self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'ABRIR')]"))).click()
                self.driver.switch_to.default_content()
                print("[Recuperação] Fallback para URL direta parece ter funcionado.")
            except Exception as e2:
                print(f"ERRO CRÍTICO: Fallback para URL direta também falhou. O script pode não conseguir continuar. Erro: {e2}")
                raise e2

    def _click_save_and_next(self):
        """Encontra o botão 'Salvar e Avançar' visível, rola até ele e clica."""
        try:
            save_button_xpath = "//button[contains(normalize-space(), 'Salvar e Avançar')]"
            save_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, save_button_xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", save_button)
            return True
        except (TimeoutException, NoSuchElementException):
            print("ERRO: Botão 'Salvar e Avançar' não foi encontrado ou não é clicável.")
            return False
            
    def _wait_for_active_step(self, step_text):
        """Espera a etapa na barra de progresso se tornar ativa."""
        print(f"[Formulário] Esperando pela Aba '{step_text}' se tornar ativa na barra de progresso...")
        step_xpath = f"//nav[@aria-label='Progress']//div[@aria-current='step' and contains(., '{step_text}')]"
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, step_xpath)))
            print(f"  -> Aba '{step_text}' está ativa.")
            return True
        except TimeoutException:
            print(f"ERRO: A Aba '{step_text}' não se tornou ativa a tempo.")
            return False

    def _select_date_from_picker(self, target_date_str):
        """
        Abre o date picker e seleciona a data desejada.
        target_date_str format: YYYY-MM-DD
        """
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        target_day = target_date.day
        target_month = target_date.month
        target_year = target_date.year

        print(f"  -> Automatizando seleção de data: {target_date.strftime('%d/%m/%Y')}")

        # 1. Clicar no botão que abre o calendário (o que exibe a data atual)
        date_input_button_xpath = "//button[@type='button' and @aria-haspopup='dialog' and .//span[normalize-space()='Escolha uma data']]"
        date_input_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, date_input_button_xpath)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", date_input_button)
        self.driver.execute_script("arguments[0].click();", date_input_button) # Clicar via JS
        print("    -> Calendário aberto.")

        # 2. Navegar para o mês/ano correto
        calendar_dialog_xpath = "//div[@role='dialog' and contains(@id, 'radix-')]"
        self.wait.until(EC.visibility_of_element_located((By.XPATH, calendar_dialog_xpath)))

        while True:
            current_month_year_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, f"{calendar_dialog_xpath}//div[@class='text-sm font-medium']")))
            current_month_year_text = current_month_year_element.text
            
            # Parse current month and year from text like "setembro 2025"
            parts = current_month_year_text.split()
            current_month_name = parts[0].lower()
            current_year = int(parts[1])
            current_month = self.MESES_MAP_REVERSE[current_month_name]

            print(f"    -> Calendário atual: {current_month_year_text}. Alvo: {target_date.strftime('%B %Y')}")

            if current_year == target_year and current_month == target_month:
                print("    -> Mês e ano corretos encontrados.")
                break
            elif target_date < datetime(current_year, current_month, 1):
                # Target date is in the past relative to current calendar view
                prev_month_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"{calendar_dialog_xpath}//button[@name='previous-month']")))
                self.driver.execute_script("arguments[0].click();", prev_month_button) # Clicar via JS
                print("    -> Clicando no mês anterior.")
            else:
                # Target date is in the future relative to current calendar view
                next_month_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"{calendar_dialog_xpath}//button[@name='next-month']")))
                self.driver.execute_script("arguments[0].click();", next_month_button) # Clicar via JS
                print("    -> Clicando no próximo mês.")
            time.sleep(0.5) # Pequena pausa entre cliques de mês

        # 3. Selecionar o dia
        day_button_xpath = f"{calendar_dialog_xpath}//button[@name='day' and normalize-space()='{target_day}']"
        time.sleep(0.5) # Pausa adicional para a interface estabilizar antes de clicar no dia
        try:
            day_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, day_button_xpath)))
            self.driver.execute_script("arguments[0].click();", day_button) # Clicar via JS
            print(f"    -> Dia {target_day} selecionado automaticamente.")
            time.sleep(1) # Pausa após selecionar o dia
        except (TimeoutException, NoSuchElementException):
            print("\n" + "!"*15 + " AÇÃO MANUAL NECESSÁRIA " + "!"*15)
            print(f"    -> Não foi possível selecionar o dia {target_day} automaticamente.")
            print(f"    -> Por favor, selecione o dia {target_day} no calendário do navegador.")
            input("    -> Após selecionar, pressione ENTER para continuar...")
            print("!"*55)
            time.sleep(1) # Pausa após a ação manual


    def registrar_aula(self, aula_info, plano_de_aula):
        if not self._navigate_to_disciplina(aula_info['turma'], aula_info['disciplina']):
            return False # Retorna False para que o loop principal possa tentar a recuperação

        try:
            print("[Formulário] Procurando e clicando em 'Adicionar aula'...")
            # Espera o overlay de carregamento desaparecer antes de clicar em 'Adicionar aula'
            loading_overlay_xpath = "//div[contains(@class, 'flex justify-center items-center mt-[50vh]')]"
            self.wait.until(EC.invisibility_of_element_located((By.XPATH, loading_overlay_xpath)))
            
            add_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Adicionar aula')]")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
            add_button.click()
            print("  -> Botão 'Adicionar aula' clicado.")

            self.driver.switch_to.default_content()
            # CORREÇÃO: Fechar o colchete corretamente
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe[src*="listagem-turmas"]')))
            
            if not self._wait_for_active_step("1 - Conteúdo"): raise Exception("Aba 1 não carregou.")

            # --- AUTOMAÇÃO DA SELEÇÃO DE DATA ---
            self._select_date_from_picker(aula_info['data'])
            # --- FIM DA AUTOMAÇÃO DA SELEÇÃO DE DATA ---

            print("\n" + "!"*15 + " AÇÃO MANUAL NECESSÁRIA " + "!"*15)
            print(f"Por favor, selecione o HORÁRIO ({aula_info['horario']}) da aula.")
            input("Após selecionar, pressione ENTER para continuar...")
            print("!"*55 + "\n  -> Retomando automação...")

            print("[Formulário] Preenchendo campos da Aba 1...")
            self.driver.find_element(By.XPATH, "//label[contains(., 'Conteúdo abordado')]/following-sibling::textarea").send_keys(plano_de_aula.get('conteudo', ''))
            self.driver.find_element(By.XPATH, "//label[contains(., 'Estratégia metodológica')]/following-sibling::textarea").send_keys(plano_de_aula.get('estrategia', ''))
            print("  -> Campos preenchidos.")

            if not self._click_save_and_next(): raise Exception("Falha ao salvar Aba 1.")
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Sim']"))).click()
            print("[Formulário] Aba 1 (Criação da Aula) salva com sucesso.")

            if not self._wait_for_active_step("2 - Plano de aula"): raise Exception("Aba 2 não ativou.")
            if not self._click_save_and_next(): raise Exception("Falha ao salvar Aba 2.")
            print("[Formulário] Aba 2 salva.")

            if not self._wait_for_active_step("3 - Frequência"): raise Exception("Aba 3 não ativou.")
            if not self._click_save_and_next(): raise Exception("Falha ao salvar Aba 3.")
            print("[Formulário] Aba 3 salva.")

            if not self._wait_for_active_step("4 - Recursos didáticos"): raise Exception("Aba 4 não ativou.")
            link_recurso = plano_de_aula.get('recurso_link')
            if link_recurso:
                print("  -> Clicando em 'Adicionar novo recurso didático'...")
                add_recurso_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Adicionar novo recurso didático')]")))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_recurso_button)
                add_recurso_button.click()
                
                dialog_xpath = "//div[@role='dialog' and .//h2[normalize-space()='Adicionar/Editar recurso didático']]"
                self.wait.until(EC.visibility_of_element_located((By.XPATH, dialog_xpath)))
                print("  -> Formulário de recurso aberto. Aguardando estabilização...")
                time.sleep(1)
                print("  -> Preenchendo campos...")
                
                resource_type = "Arquivo PDF"
                print(f"    -> Selecionando tipo de recurso: '{resource_type}'.")
                
                combobox_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"{dialog_xpath}//button[@role='combobox']")))
                combobox_button.click()
                
                option_xpath = f"//div[normalize-space()='{resource_type}']"
                link_option = self.wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
                link_option.click()
                print(f"    -> Opção '{resource_type}' selecionada.")

                recurso_titulo = plano_de_aula.get('recurso_titulo', '')
                self.driver.find_element(By.XPATH, f"{dialog_xpath}//label[contains(.,'Nome do recurso')]/following-sibling::div/input").send_keys(recurso_titulo)
                self.driver.find_element(By.XPATH, f"{dialog_xpath}//label[contains(.,'URL do recurso')]/following-sibling::div/input").send_keys(plano_de_aula.get('recurso_link', ''))
                self.driver.find_element(By.XPATH, f"{dialog_xpath}//textarea").send_keys(plano_de_aula.get('recurso_comentario', ''))
                
                print("  -> Clicando em 'Salvar' para confirmar o recurso...")
                confirm_add_button_xpath = f"{dialog_xpath}//button[contains(@class, 'bg-[#007521]')]"
                save_button_dialog = self.wait.until(EC.element_to_be_clickable((By.XPATH, confirm_add_button_xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button_dialog)
                self.driver.execute_script("arguments[0].click();", save_button_dialog)
                
                print("  -> Aguardando o formulário de recurso fechar...")
                self.wait.until(EC.invisibility_of_element_located((By.XPATH, dialog_xpath)))
                
                print(f"  -> Verificando se o recurso '{recurso_titulo}' apareceu na lista...")
                recurso_adicionado_xpath = f"//td[normalize-space()='{recurso_titulo}']"
                self.wait.until(EC.visibility_of_element_located((By.XPATH, recurso_adicionado_xpath)))
                print("  -> Recurso confirmado na lista. Aguardando 2 segundos...")
                time.sleep(2)

            if not self._click_save_and_next(): raise Exception("Falha ao salvar Aba 4.")
            print("[Formulário] Aba 4 salva.")

            if not self._wait_for_active_step("5 - Atividade"): raise Exception("Aba 5 não ativou.")
            final_button_xpath = "//button[contains(normalize-space(), 'Salvar e Finalizar')]"
            final_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, final_button_xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", final_button)
            final_button.click()
            print("[Formulário] Aba 5 finalizada.")

            print("[Formulário] Aguardando o balão de confirmação final 'Atenção'...")
            modal_atencao_xpath = "//div[@role='dialog' and .//h2[normalize-space()='Atenção']]" # Usando normalize-space()
            self.wait.until(EC.visibility_of_element_located((By.XPATH, modal_atencao_xpath)))
            
            print("  -> Balão 'Atenção' apareceu. Clicando em 'Fechar'...")
            fechar_button_xpath = f"{modal_atencao_xpath}//button[normalize-space()='Fechar']"
            fechar_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, fechar_button_xpath)))
            self.driver.execute_script("arguments[0].click();", fechar_button)
            print("  -> Botão 'Fechar' clicado. Balão de confirmação fechado.")

            print(f"SUCESSO: Aula de {aula_info['disciplina']} em {aula_info['data']} registrada!")
            
            self._navigate_back_to_turmas()
            return True

        except Exception as e:
            print(f"\nERRO INESPERADO: Ocorreu uma falha durante o registro da aula.")
            print(f"  -> Detalhe: {e}")
            self._take_screenshot(f"{aula_info['turma']}_{aula_info['data']}")
            self._navigate_back_to_turmas()
            return False

# --- Funções de Parsing (sem alterações) ---
def parse_plan_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
    except FileNotFoundError: return None
    plan_data = {}
    for line in content.splitlines():
        if line.startswith('# Data:'): plan_data['data'] = line.split(':', 1)[1].strip()
        elif line.startswith('# Horário:'): plan_data['horario'] = line.split(':', 1)[1].strip()
    blocos = ['[CONTEUDO]', '[ESTRATEGIA]', '[RECURSO_TITULO]', '[RECURSO_LINK]', '[RECURSO_COMENTARIO]']
    for i, bloco_atual in enumerate(blocos):
        try:
            start_index = content.index(bloco_atual) + len(bloco_atual)
            end_index = len(content)
            if i + 1 < len(blocos):
                next_block_start = content.find(blocos[i+1], start_index)
                if next_block_start != -1: end_index = next_block_start
            valor = content[start_index:end_index].strip()
            if bloco_atual in ['[CONTEUDO]', '[ESTRATEGIA]'] and (not valor or "Preencher" in valor): return None
            plan_data[bloco_atual.strip('[]').lower()] = valor
        except ValueError: continue
    return plan_data if 'data' in plan_data and 'horario' in plan_data else None

def find_plans_to_register(project_root, mapa_turmas, turmas_disciplinas):
    aulas_para_registrar = []
    aulas_dir = os.path.join(project_root, 'aulas')
    mapa_turmas_reverso = {v.replace(' ', ''): k for k, v in mapa_turmas.items()}
    mapa_disciplinas_reverso = {disc['codigoDisciplina']: disc['nomeDisciplina'] for turma in turmas_disciplinas for disc in turma['disciplinas']}
    if not os.path.exists(aulas_dir): return []
    for nome_pasta_turma in sorted(os.listdir(aulas_dir)):
        caminho_pasta_turma = os.path.join(aulas_dir, nome_pasta_turma)
        # Ignora arquivos de log e outros diretórios especiais como 'inputs'
        if not os.path.isdir(caminho_pasta_turma) or nome_pasta_turma == 'inputs':
            continue

        for nome_arquivo in sorted(os.listdir(caminho_pasta_turma)):
            if not nome_arquivo.endswith('.txt'): continue
            caminho_arquivo = os.path.join(caminho_pasta_turma, nome_arquivo)
            plano = parse_plan_file(caminho_arquivo)
            if plano:
                # CORREÇÃO: Atualiza a regex para corresponder ao novo formato de nome de arquivo
                # que inclui o horário (ex: DISC_AAAAMMDD_HHMM.txt).
                match = re.match(r'(.+)_(\d{8})_\d{4}\.txt$', nome_arquivo)
                if not match: continue
                disciplina_curta = match.group(1)
                nome_curto_turma_normalizado = nome_pasta_turma.replace('_', 'º').replace(' ', '')
                turma_completa = mapa_turmas_reverso.get(nome_curto_turma_normalizado)
                disciplina_completa = mapa_disciplinas_reverso.get(disciplina_curta)
                if not turma_completa or not disciplina_completa:
                    print(f"AVISO: Mapeamento não encontrado para '{nome_pasta_turma}/{disciplina_curta}'. Pulando.")
                    continue
                aula_info = {'data': datetime.strptime(plano['data'], "%d/%m/%Y").strftime("%Y-%m-%d"), 'horario': plano['horario'], 'turma': turma_completa, 'disciplina': disciplina_completa, 'caminho_arquivo': caminho_arquivo}
                aulas_para_registrar.append({'info': aula_info, 'plano': plano})
            else:
                print(f"INFO: Plano '{nome_arquivo}' ignorado por estar incompleto (contém 'Preencher').")
    return aulas_para_registrar

class Logger:
    """Redireciona a saída do console (stdout) para um arquivo de log e para o terminal."""
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.log = open(filepath, "a", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

if __name__ == '__main__':
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_PATH = os.path.join(PROJECT_ROOT, 'data')
    try:
        with open(os.path.join(DATA_PATH, 'credentials.json'), 'r', encoding='utf-8-sig') as f: creds = json.load(f)
        with open(os.path.join(DATA_PATH, 'mapa_turmas.json'), 'r', encoding='utf-8-sig') as f: mapa_turmas = json.load(f)
        with open(os.path.join(DATA_PATH, 'turmas_com_disciplinas.json'), 'r', encoding='utf-8-sig') as f: turmas_disciplinas = json.load(f)
    except FileNotFoundError as e:
        print(f"ERRO: Arquivo de configuração não encontrado: {e.filename}")
        exit(1)

    # --- Configuração do Log ---
    AULAS_DIR = os.path.join(PROJECT_ROOT, 'aulas')
    LOGS_DIR = os.path.join(AULAS_DIR, 'logs') # Diretório específico para logs
    os.makedirs(LOGS_DIR, exist_ok=True)

    log_filename = f"log_registro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    log_filepath = os.path.join(LOGS_DIR, log_filename)
    sys.stdout = Logger(log_filepath)
    print(f"--- Log de execução iniciado. Salvo em: {log_filepath} ---")

    aulas_para_registrar = find_plans_to_register(PROJECT_ROOT, mapa_turmas, turmas_disciplinas)
    if not aulas_para_registrar:
        print("\nNenhum plano de aula encontrado para registrar.")
        exit(0)

    print(f"\nEncontradas {len(aulas_para_registrar)} aulas para registrar.")
    
    registrador = Registrador(project_root=PROJECT_ROOT)
    registrador._initialize_driver()
    registrador._login_and_navigate_to_turmas("https://portal.seduc.pi.gov.br/#!/turmas", creds)
    
    try:
        for i, item in enumerate(aulas_para_registrar):
            info = item['info']
            print(f"\n>>> Próxima aula a registrar ({i+1}/{len(aulas_para_registrar)}):")
            print(f"  - Data:      {info['data']}")
            print(f"  - Horário:   {info['horario']}")
            print(f"  - Turma:     {info['turma']}")
            print(f"  - Disciplina: {info['disciplina']}")
            
            user_choice = input("Deseja registrar esta aula? (s = sim / n = pular / parar = encerrar): ").lower()

            if user_choice == 'n':
                print("  -> Aula pulada pelo usuário. O arquivo será mantido.")
                continue
            elif user_choice == 'parar':
                print("  -> Processo encerrado pelo usuário.")
                break
            elif user_choice != 's':
                print("  -> Opção inválida. Pulando aula por segurança.")
                continue

            if registrador.registrar_aula(info, item['plano']):
                print(f"SUCESSO: Aula registrada. Removendo arquivo: {info['caminho_arquivo']}")
                os.remove(info['caminho_arquivo'])
            else:
                print(f"FALHA: O registro da aula falhou. O arquivo será mantido para nova tentativa.")
            
            time.sleep(2)
    finally:
        if registrador.driver and registrador.driver.window_handles:
            registrador.driver.quit()
            print("\nProcesso finalizado.")
        else:
            print("\nProcesso finalizado. O navegador parece já ter sido fechado.")
        
        if isinstance(sys.stdout, Logger):
            sys.stdout.close()
            sys.stdout = sys.stdout.terminal
'@
Create-File (Join-Path $RootPath "tools\registrar_aulas.py") $Content_Registrar

$Content_Analisador = @'
import json
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def carregar_dados(data_path):
    """Carrega todos os arquivos JSON necessários para a análise."""
    arquivos = [
        'aulas_coletadas.json', 'turmas_com_disciplinas.json', 'calendario_letivo.json',
        'horarios_semanais_oficial.json', 'mapa_turmas.json', 'feriados.json', 'config.json'
    ]
    dados = {}
    try:
        for arquivo in arquivos:
            with open(os.path.join(data_path, arquivo), 'r', encoding='utf-8-sig') as f:
                # Caso especial para horarios_semanais_oficial que é uma lista
                if arquivo == 'horarios_semanais_oficial.json':
                    dados[arquivo] = json.load(f)[0]
                else:
                    dados[arquivo] = json.load(f)
        return dados
    except FileNotFoundError as e:
        print(f"ERRO: Arquivo de configuração não encontrado: {e.filename}")
        exit(1)
    except Exception as e:
        print(f"ERRO ao carregar arquivos de configuração: {e}")
        exit(1)

def analisar_aulas_registradas(aulas_coletadas):
    """Conta as horas (aulas) já registradas para cada disciplina de cada turma."""
    contagem = {}
    for aula in aulas_coletadas:
        turma = aula.get('turma')
        disciplina = aula.get('componenteCurricular')
        if turma and disciplina:
            chave = (turma, disciplina)
            contagem[chave] = contagem.get(chave, 0) + 1
    return contagem

def encontrar_proxima_disciplina_a_registrar(turma_info, contagem_horas, carga_horaria_padrao, disciplinas_anuais):
    """Encontra a primeira disciplina que ainda não completou a carga horária."""
    nome_turma_completo = turma_info['nomeTurma']
    for disciplina_info in turma_info['disciplinas']:
        nome_disciplina_completo = disciplina_info['nomeDisciplina']
        horas_registradas = contagem_horas.get((nome_turma_completo, nome_disciplina_completo), 0)
        
        is_anual = nome_disciplina_completo.upper() in disciplinas_anuais
        
        if horas_registradas < carga_horaria_padrao:
            # Para disciplinas anuais, sempre mostramos. Para mensais, só se for a primeira incompleta.
            if is_anual or not any(
                contagem_horas.get((nome_turma_completo, d['nomeDisciplina']), 0) < carga_horaria_padrao 
                for d in turma_info['disciplinas'][:turma_info['disciplinas'].index(disciplina_info)] 
                if d['nomeDisciplina'].upper() not in disciplinas_anuais
            ):
                 return disciplina_info
    return None

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_PATH = os.path.join(PROJECT_ROOT, 'data')

    # 1. Carregar todos os dados
    print("Carregando arquivos de configuração...")
    dados = carregar_dados(DATA_PATH)
    
    # 2. Preparar estruturas de dados para análise
    mapa_turmas_reverso = {v: k for k, v in dados['mapa_turmas.json'].items()}
    carga_horaria_padrao = dados['calendario_letivo.json'].get('carga_horaria_padrao_disciplina', 40)
    disciplinas_anuais_config = set(d.upper() for d in dados['calendario_letivo.json'].get('disciplinas_config', {}).get('anuais', []))
    
    print("\nUsando 'aulas_coletadas.json' para a análise de grade.")
    contagem_horas = analisar_aulas_registradas(dados['aulas_coletadas.json'])
    
    slots_ocupados = {
        (datetime.strptime(aula['dataAula'], "%d/%m/%Y").date(), aula['horario'].replace("às", "-").replace(" ", ""), aula['turma'])
        for aula in dados['aulas_coletadas.json']
        if aula.get('status') == 'Aula confirmada'
    }
    
    print("\n--- RELATÓRIO DE ANÁLISE DE GRADE ---\n")
    
    # 3. Iterar sobre as turmas para gerar o relatório
    for turma_info in dados['turmas_com_disciplinas.json']:
        nome_turma_completo = turma_info['nomeTurma']
        nome_turma_curto = dados['mapa_turmas.json'].get(nome_turma_completo)
        if not nome_turma_curto:
            continue

        print(f"TURMA: {nome_turma_curto} ({nome_turma_completo})")
        print("-" * 40)

        # Relatório de Carga Horária
        for disciplina_info in turma_info['disciplinas']:
            nome_disciplina = disciplina_info['nomeDisciplina']
            horas_registradas = contagem_horas.get((nome_turma_completo, nome_disciplina), 0)
            status = "Completa" if horas_registradas >= carga_horaria_padrao else "Incompleta"
            print(f"  - {nome_disciplina:<45} | {horas_registradas:02d}/{carga_horaria_padrao}h | Status: {status}")

        # Análise de Próxima Ação
        proxima_disciplina = encontrar_proxima_disciplina_a_registrar(turma_info, contagem_horas, carga_horaria_padrao, disciplinas_anuais_config)

        if not proxima_disciplina:
            print("\n  >> AÇÃO: Todas as disciplinas parecem completas. Nenhuma ação necessária.\n")
            continue

        # Encontrar primeiro horário disponível para a próxima disciplina
        horarios_turma = dados['horarios_semanais_oficial.json'].get('professores', {}).get('Hélio', {}).get('turmas', {}).get(nome_turma_curto, {})
        horarios_disciplina = horarios_turma.get(proxima_disciplina['codigoDisciplina']) or horarios_turma.get('DISC_MENSAL', [])
        
        primeiro_slot_livre = None
        if horarios_disciplina:
            data_inicio_ano = datetime.strptime(dados['calendario_letivo.json']['data_inicio'], "%d/%m/%Y")
            data_fim_ano = datetime.strptime(dados['calendario_letivo.json']['data_fim'], "%d/%m/%Y")
            feriados_set = {datetime.strptime(f['data'], "%d/%m/%Y").date() for f in dados['feriados.json'].get('feriados', [])}
            
            data_atual = data_inicio_ano
            while data_atual <= data_fim_ano:
                if data_atual.weekday() < 5 and data_atual.date() not in feriados_set:
                    for horario_info in horarios_disciplina:
                        dia_semana_map = {"segunda-feira": 0, "terça-feira": 1, "quarta-feira": 2, "quinta-feira": 3, "sexta-feira": 4}
                        if data_atual.weekday() == dia_semana_map.get(horario_info['dia_semana_nome']):
                            chave_slot = (data_atual.date(), horario_info['label_horario'].replace(" ", ""), nome_turma_completo)
                            if chave_slot not in slots_ocupados:
                                primeiro_slot_livre = data_atual
                                break
                if primeiro_slot_livre:
                    break
                data_atual += timedelta(days=1)

        print(f"\n  >> PRÓXIMA AÇÃO PARA ESTA TURMA:")
        print(f"     Disciplina a registrar: '{proxima_disciplina['nomeDisciplina']}'")
        if primeiro_slot_livre:
            print(f"     Primeiro horário livre encontrado a partir de: {primeiro_slot_livre.strftime('%d/%m/%Y')}")
        else:
            print("     AVISO: Nenhum horário livre encontrado no calendário para a grade desta disciplina.")
        print("\n" + "="*60 + "\n")

    print("Análise concluída. Para gerar os arquivos de planejamento, execute 'preparar_planos.py'.")
'@
Create-File (Join-Path $RootPath "tools\analisador_de_grade.py") $Content_Analisador

$Content_Preparar = @'
import json
import os
import re
from dateutil.relativedelta import relativedelta
import sys
from datetime import datetime, timedelta

def normalizar_horario(horario_str):
    """Normaliza a string de horário para um formato consistente 'HH:MM-HH:MM'."""
    if not isinstance(horario_str, str):
        horario_str = str(horario_str)
    
    numeros = re.findall(r'\d+', horario_str)
    if len(numeros) == 4:
        return f"{numeros[0]}:{numeros[1]}-{numeros[2]}:{numeros[3]}"
    
    return horario_str.replace("às", "-").replace(" ", "")

def carregar_dados(data_path):
    """Carrega todos os arquivos JSON necessários."""
    try:
        with open(os.path.join(data_path, 'turmas_com_disciplinas.json'), 'r', encoding='utf-8-sig') as f:
            turmas_disciplinas = json.load(f)
        with open(os.path.join(data_path, 'calendario_letivo.json'), 'r', encoding='utf-8-sig') as f:
            calendario = json.load(f)
        with open(os.path.join(data_path, 'horarios_semanais_oficial.json'), 'r', encoding='utf-8-sig') as f:
            horarios_oficiais = json.load(f)[0]
        with open(os.path.join(data_path, 'mapa_turmas.json'), 'r', encoding='utf-8-sig') as f:
            mapa_turmas = json.load(f)
        with open(os.path.join(data_path, 'feriados.json'), 'r', encoding='utf-8-sig') as f:
            feriados_data = json.load(f)
        with open(os.path.join(data_path, 'config.json'), 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
        return turmas_disciplinas, calendario, horarios_oficiais, mapa_turmas, feriados_data, config
    except FileNotFoundError as e:
        print(f"ERRO: Arquivo de configuração não encontrado: {e.filename}")
        exit(1)
    except Exception as e:
        print(f"ERRO ao carregar arquivos de configuração: {e}")
        exit(1)

def get_slots_ocupados(data_path, mapa_turmas):
    """Lê todas as fontes e retorna um conjunto de slots ocupados."""
    slots_ocupados = set()
    
    # Fonte 1: JSON de aulas coletadas
    json_path = os.path.join(data_path, 'aulas_coletadas.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                aulas_coletadas = json.load(f)
            for aula in aulas_coletadas:
                if aula.get('status') == 'Aula confirmada':
                    data_obj = datetime.strptime(aula['dataAula'], "%d/%m/%Y").date()
                    horario_normalizado = normalizar_horario(aula['horario'])
                    # Adiciona a turma à chave para evitar conflitos entre turmas
                    nome_turma_completo = aula.get('turma')
                    nome_turma_curto = mapa_turmas.get(nome_turma_completo)
                    if nome_turma_curto:
                        slots_ocupados.add((data_obj, horario_normalizado, nome_turma_curto))
        except Exception as e:
            print(f"AVISO: Não foi possível processar o arquivo JSON '{json_path}': {e}")

    # Fonte 2: Arquivos .txt de planos de aula já gerados na pasta 'aulas'
    aulas_path = os.path.join(os.path.dirname(data_path), 'aulas')
    if os.path.exists(aulas_path):
        for turma_folder in os.listdir(aulas_path):
            turma_path = os.path.join(aulas_path, turma_folder)
            if not os.path.isdir(turma_path) or turma_folder in ['inputs', 'logs', 'backups']:
                continue
            
            for filename in os.listdir(turma_path):
                if filename.endswith('.txt'):
                    file_path = os.path.join(turma_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        data_match = re.search(r'# Data: (\d{2}/\d{2}/\d{4})', content)
                        horario_match = re.search(r'# Horário: (.+)', content)
                        
                        if data_match and horario_match:
                            data_obj = datetime.strptime(data_match.group(1), "%d/%m/%Y").date()
                            horario_normalizado = normalizar_horario(horario_match.group(1))
                            nome_turma_curto = turma_folder.replace('_', 'º ')
                            slots_ocupados.add((data_obj, horario_normalizado, nome_turma_curto))
                            
                    except Exception as e:
                        print(f"AVISO: Não foi possível processar o arquivo de plano '{filename}': {e}")

    return slots_ocupados

def get_datas_disciplina(aulas_coletadas, nome_turma_completo, nome_disciplina_completo):
    """Encontra a primeira e a última data de aula para uma disciplina específica."""
    datas_aulas = []
    for aula in aulas_coletadas:
        if aula.get('turma') == nome_turma_completo and aula.get('componenteCurricular') == nome_disciplina_completo:
            try:
                # Considera apenas aulas com status que conta como hora/aula
                if aula.get('status') in ['Aula confirmada', 'Aguardando confirmação']:
                    datas_aulas.append(datetime.strptime(aula['dataAula'], "%d/%m/%Y").date())
            except (ValueError, TypeError):
                continue
    if not datas_aulas:
        return None, None
    
    return min(datas_aulas), max(datas_aulas)

def gerar_arquivos_esqueleto(project_root, aulas_a_preparar):
    if not aulas_a_preparar:
        print("\nNenhum arquivo de plano de aula a ser gerado.")
        return
    print("\nGerando arquivos de plano de aula...")
    arquivos_gerados_nesta_execucao = set()

    for aula in aulas_a_preparar:
        nome_pasta_turma = aula['nome_curto_turma'].replace('º', '_').replace(' ', '')
        data_obj = datetime.strptime(aula['data'], "%Y-%m-%d")
        # CORREÇÃO: Adiciona o horário ao nome do arquivo para garantir unicidade
        # quando há múltiplas aulas da mesma disciplina no mesmo dia.
        horario_para_nome_arquivo = aula['horario'].split('-')[0].replace(':', '') # Pega 'HHMM' do início do horário
        nome_arquivo = f"{aula['nome_curto_disciplina']}_{data_obj.strftime('%Y%m%d')}_{horario_para_nome_arquivo}.txt"
        caminho_pasta = os.path.join(project_root, 'aulas', nome_pasta_turma)
        os.makedirs(caminho_pasta, exist_ok=True)
        caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
        caminho_relativo = os.path.join('aulas', nome_pasta_turma, nome_arquivo)

        conteudo_esqueleto = (
            f"# Data: {data_obj.strftime('%d/%m/%Y')}\n"
            f"# Aula: {aula['numero_aula']:02d}\n"
            f"# Horário: {aula['horario']}\n\n"
            "[CONTEUDO]\nPreencher o conteúdo abordado aqui.\n\n"
            "[ESTRATEGIA]\nPreencher a estratégia metodológica aqui.\n\n"
            "[RECURSO_TITULO]\n\n\n"
            "[RECURSO_LINK]\n\n\n"
            "[RECURSO_COMENTARIO]\n\n"
        )
        
        # Só escreve no arquivo e exibe "Criado" se for a primeira vez para este arquivo.
        # Para as demais aulas do mesmo dia, apenas informa que foi agrupado.
        if caminho_arquivo not in arquivos_gerados_nesta_execucao:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo_esqueleto)
            print(f"  -> Criado: {caminho_relativo}")
            arquivos_gerados_nesta_execucao.add(caminho_arquivo)
        else:
            print(f"  -> Agrupado: Aula {aula['numero_aula']} no arquivo {os.path.basename(caminho_arquivo)}")

def salvar_manifesto_preenchimento(data_path, aulas_a_preparar):
    """Salva um manifesto JSON com os detalhes das aulas a serem preenchidas."""
    manifesto_path = os.path.join(data_path, 'manifesto_preenchimento.json')
    manifesto_data = []
    for aula in aulas_a_preparar:
        nome_pasta_turma = aula['nome_curto_turma'].replace('º', '_').replace(' ', '')
        data_obj = datetime.strptime(aula['data'], "%Y-%m-%d")
        horario_para_nome_arquivo = aula['horario'].split('-')[0].replace(':', '')
        nome_arquivo = f"{aula['nome_curto_disciplina']}_{data_obj.strftime('%Y%m%d')}_{horario_para_nome_arquivo}.txt"
        caminho_arquivo_relativo = os.path.join('aulas', nome_pasta_turma, nome_arquivo)
        
        aula_info = aula.copy()
        aula_info['caminho_arquivo'] = caminho_arquivo_relativo
        manifesto_data.append(aula_info)

    with open(manifesto_path, 'w', encoding='utf-8') as f:
        json.dump(manifesto_data, f, indent=4)
    print(f"\nINFO: Manifesto de preenchimento salvo em '{manifesto_path}'.")

def limpar_planos_antigos(aulas_dir):
    """
    Apaga todos os arquivos .txt de planos de aula existentes no diretório 'aulas'.
    Ignora subdiretórios como 'inputs' e arquivos de log.
    """
    print("\nLimpando arquivos de plano de aula (.txt) pendentes...")
    arquivos_deletados = 0
    for root, dirs, files in os.walk(aulas_dir):
        # Ignora os diretórios especiais para não apagar arquivos neles
        dirs[:] = [d for d in dirs if d not in ['inputs', 'logs', 'backups']]
        
        files_to_delete = []
        for file in files:
            if file.endswith('.txt') and 'backups' not in root:
                file_path = os.path.join(root, file)
                try:
                    # Primeiro, verifica se o arquivo deve ser deletado
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if 'Preencher' in content:
                        files_to_delete.append(file_path)
                except Exception as e:
                    print(f"  -> ERRO ao ler o arquivo '{file_path}' para verificação: {e}")

        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                arquivos_deletados += 1
            except Exception as e:
                print(f"  -> ERRO ao tentar deletar '{file_path}': {e}")

    print(f"  -> {arquivos_deletados} arquivo(s) de plano pendente(s) foram removidos.")

class Logger:
    """Redireciona a saída do console (stdout) para um arquivo de log e para o terminal."""
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.log = open(filepath, "a", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

def planejar_e_preparar_aulas(dados_carregados, aulas_coletadas, aulas_dir):
    """
    Função principal que executa a lógica de planejamento e preparação dos arquivos.
    Agora pode ser chamada por outros scripts.
    """
    turmas_disciplinas, calendario, horarios, mapa_turmas, feriados_data, config = dados_carregados
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    LOGS_DIR = os.path.join(aulas_dir, 'logs') # Diretório específico para logs
    os.makedirs(LOGS_DIR, exist_ok=True)

    log_filename = f"log_preparacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    log_filepath = os.path.join(LOGS_DIR, log_filename)
    sys.stdout = Logger(log_filepath)
    print(f"--- Log de preparação de planos iniciado. Salvo em: {log_filepath} ---")

    try:
        # 1. Contagem de horas para saber o progresso de cada disciplina
        # Mapeamento para forçar disciplinas anuais a usarem um horário genérico.
        # Isso evita que caiam na lógica de 'DISC_MENSAL' ou fiquem sem horário.
        mapa_disciplinas_para_anual = {
            "COMPUT": "DISC_ANUAL",
            "PENSAMENTO_COMPUTACIONAL_DES_SIST": "DISC_ANUAL",
            "MENTORIAS_TEC_DES_SIST": "DISC_ANUAL",
            "PENSAMENTO_COMPUTACIONAL_JOGOS": "DISC_ANUAL",
            "MENTORIAS_TEC_JOGOS": "DISC_ANUAL"
            # Adicione outros códigos de disciplina anuais aqui se necessário
        }

        contagem_horas = {}
        for aula in aulas_coletadas:
            # CORREÇÃO: Contar aulas confirmadas e pendentes para a carga horária.
            if aula.get('status') in ['Aula confirmada', 'Aguardando confirmação']:
                chave_contagem = (aula['turma'], aula['componenteCurricular'])
                contagem_horas[chave_contagem] = contagem_horas.get(chave_contagem, 0) + 1

        # 2. Obter todos os slots já ocupados para evitar conflitos
        DATA_PATH = os.path.join(PROJECT_ROOT, 'data')
        slots_ocupados = get_slots_ocupados(DATA_PATH, mapa_turmas)
        print(f"\nEncontrados {len(slots_ocupados)} slots de horário já ocupados (de JSON e planos .txt).")

        # 3. Lógica de planejamento
        aulas_a_preparar = []
        carga_horaria_padrao = calendario.get('carga_horaria_padrao_disciplina', 40)
        disciplinas_anuais_config = set(d.upper() for d in calendario.get('disciplinas_config', {}).get('anuais', []))

        for turma_info in turmas_disciplinas:
            nome_turma_completo = turma_info['nomeTurma']
            nome_turma_curto = mapa_turmas.get(nome_turma_completo)
            if not nome_turma_curto: continue

            print(f"\n--- Verificando Turma: {nome_turma_curto} ({nome_turma_completo}) ---")

            for disciplina_info in turma_info['disciplinas']:
                nome_disciplina_completo = disciplina_info['nomeDisciplina']
                horas_registradas = contagem_horas.get((nome_turma_completo, nome_disciplina_completo), 0)

                if horas_registradas >= carga_horaria_padrao:
                    print(f"  - '{nome_disciplina_completo}': Completa ({horas_registradas}/{carga_horaria_padrao}h).")
                    continue

                print(f"  - '{nome_disciplina_completo}': Incompleta ({horas_registradas}/{carga_horaria_padrao}h). Planejando aulas...")

                # Carrega a lista de disciplinas mensais para a lógica de seleção de horário
                disciplinas_mensais_config = set(d.upper() for d in calendario.get('disciplinas_config', {}).get('mensais', []))

                horarios_turma = horarios.get('professores', {}).get('Hélio', {}).get('turmas', {}).get(nome_turma_curto, {})
                codigo_disciplina_completo = disciplina_info['codigoDisciplina']
                
                # Lógica de busca de horário com fallback
                # 1. Tenta encontrar pelo código específico da disciplina (ex: 'COMPUT')
                horarios_disciplina = horarios_turma.get(codigo_disciplina_completo)

                # 2. Se não encontrou, e a disciplina está no mapa de anuais, tenta pelo genérico 'DISC_ANUAL'
                if not horarios_disciplina and codigo_disciplina_completo in mapa_disciplinas_para_anual:
                    horarios_disciplina = horarios_turma.get(mapa_disciplinas_para_anual[codigo_disciplina_completo])
                
                # 3. Se ainda não encontrou e é uma disciplina mensal, tenta pelo genérico 'DISC_MENSAL'
                if not horarios_disciplina and nome_disciplina_completo.upper() in disciplinas_mensais_config:
                    print(f"    -> Disciplina '{nome_disciplina_completo}' é mensal. Usando horários de 'DISC_MENSAL'.") # Sem 'and not horarios_disciplina'
                    horarios_disciplina = horarios_turma.get('DISC_MENSAL')
                if not horarios_disciplina:
                    print(f"    -> AVISO: Nenhum horário encontrado para esta disciplina. Pulando.")
                    continue

                data_inicio_ano = datetime.strptime(calendario['data_inicio'], "%d/%m/%Y").date()
                data_fim_ano = datetime.strptime(calendario['data_fim'], "%d/%m/%Y").date()
                feriados_set = {datetime.strptime(f['data'], "%d/%m/%Y").date() for f in feriados_data.get('feriados', [])}
                dias_semana_map = {"segunda-feira": 0, "terça-feira": 1, "quarta-feira": 2, "quinta-feira": 3, "sexta-feira": 4}
                
                primeira_data_registrada, ultima_data_registrada = get_datas_disciplina(aulas_coletadas, nome_turma_completo, nome_disciplina_completo)

                # --- LÓGICA DE RESTRIÇÃO DE DATAS ---
                # Verifica se há uma restrição de planejamento para a disciplina
                restricoes = calendario.get('restricoes_planejamento', {}).get(disciplina_info['codigoDisciplina'])
                
                data_inicio_planejamento = data_inicio_ano
                data_fim_planejamento = data_fim_ano

                if restricoes:
                    data_inicio_planejamento = datetime.strptime(restricoes['data_inicio'], "%d/%m/%Y").date()
                    data_fim_planejamento = datetime.strptime(restricoes['data_fim'], "%d/%m/%Y").date()
                    print(f"    -> APLICANDO RESTRIÇÃO DE PLANEJAMENTO: De {data_inicio_planejamento.strftime('%d/%m/%Y')} a {data_fim_planejamento.strftime('%d/%m/%Y')}.")

                aulas_a_planejar_contador = horas_registradas
                
                # --- NOVA LÓGICA UNIFICADA ---
                # 1. Gerar todos os slots possíveis para a disciplina no ano letivo.
                slots_potenciais = []
                data_atual = data_inicio_planejamento
                print(f"    -> Mapeando todos os horários possíveis de {data_inicio_planejamento.strftime('%d/%m/%Y')} a {data_fim_planejamento.strftime('%d/%m/%Y')}.")
                
                while data_atual <= data_fim_planejamento:
                    if data_atual.weekday() >= 5 or data_atual in feriados_set:
                        data_atual += timedelta(days=1)
                        continue
                    
                    dia_semana_nome = list(dias_semana_map.keys())[data_atual.weekday()]
                    for horario_info in horarios_disciplina:
                        if horario_info['dia_semana_nome'] == dia_semana_nome:
                            horario_normalizado = normalizar_horario(horario_info['label_horario'])
                            chave_slot = (data_atual, horario_normalizado, nome_turma_curto)
                            slots_potenciais.append(chave_slot)
                    data_atual += timedelta(days=1)

                # 2. Filtrar os slots que já estão ocupados.
                slots_livres = [slot for slot in slots_potenciais if slot not in slots_ocupados]
                
                # CORREÇÃO: Ordenar os slots livres por data e depois por horário.
                # Isso garante que o planejamento preencha todos os horários de um dia antes de passar para o próximo.
                slots_livres.sort(key=lambda x: (x[0], x[1]))
                print(f"    -> Encontrados {len(slots_potenciais)} slots potenciais. Destes, {len(slots_livres)} estão livres.")

                # 3. Preencher as aulas necessárias usando os slots livres.
                aulas_necessarias = carga_horaria_padrao - horas_registradas
                for i in range(min(aulas_necessarias, len(slots_livres))):
                    slot_livre = slots_livres[i]
                    data_aula, horario_aula, _ = slot_livre
                    aulas_a_planejar_contador += 1
                    
                    aulas_a_preparar.append({
                        "data": data_aula.strftime("%Y-%m-%d"),
                        "horario": horario_aula, # Mantém o formato normalizado HH:MM-HH:MM
                        "nome_curto_turma": nome_turma_curto,
                        "nome_curto_disciplina": disciplina_info['codigoDisciplina'],
                        "numero_aula": aulas_a_planejar_contador
                    })
                    slots_ocupados.add(slot_livre) # Adiciona ao conjunto de ocupados para não ser usado por outra disciplina no mesmo run

        # 4. Confirmar e gerar os arquivos .txt
        if not aulas_a_preparar:
            print("\nNenhuma aula nova a ser planejada. A grade parece estar em dia.")
        else:
            print(f"\nResumo: {len(aulas_a_preparar)} arquivos de plano de aula prontos para serem gerados.")
            # A entrada do usuário virá do terminal real, não do log
            confirmacao = input("Deseja criar estes arquivos .txt? (s/n): ").lower()
            if confirmacao == 's':
                # Limpa os arquivos pendentes ANTES de gerar os novos, usando o caminho recebido
                limpar_planos_antigos(aulas_dir)
                salvar_manifesto_preenchimento(DATA_PATH, aulas_a_preparar)
                gerar_arquivos_esqueleto(PROJECT_ROOT, aulas_a_preparar)
                print("\nPreparação concluída. Preencha os arquivos gerados na pasta 'aulas' antes de executar o 'registrar_aulas.py'.")
            else:
                print("\nOperação cancelada pelo usuário. Nenhum arquivo foi gerado.")


    finally:
        # Garante que o log seja fechado e o stdout restaurado, mesmo se ocorrer um erro
        if isinstance(sys.stdout, Logger):
            # Adiciona uma linha final ao log antes de fechar
            print("\n--- Fim do log de preparação ---")
            sys.stdout.close()
            sys.stdout = sys.stdout.terminal

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_PATH = os.path.join(PROJECT_ROOT, 'data')
    AULAS_DIR = os.path.join(PROJECT_ROOT, 'aulas')

    # Carrega os dados da forma tradicional
    dados_carregados = carregar_dados(DATA_PATH)
    with open(os.path.join(DATA_PATH, 'aulas_coletadas.json'), 'r', encoding='utf-8') as f:
        aulas_coletadas_offline = json.load(f)
    
    # Executa a lógica de planejamento
    planejar_e_preparar_aulas(dados_carregados, aulas_coletadas_offline, AULAS_DIR)
'@
Create-File (Join-Path $RootPath "tools\preparar_planos.py") $Content_Preparar

$Content_Preenchedor = @'
import os
import re
import sys
import json
import ast # Usar ast.literal_eval em vez de eval para segurança

def find_plan_files(aulas_dir):
    """
    Escaneia o diretório 'aulas', encontra arquivos .txt pendentes (com 'Preencher')
    e os agrupa por (turma, disciplina).
    Retorna um dicionário: {(turma, disciplina): [lista_de_arquivos]}
    """
    grouped_files = {}
    total_txt_files = 0
    if not os.path.exists(aulas_dir):
        return grouped_files

    for turma_folder in sorted(os.listdir(aulas_dir)):
        turma_path = os.path.join(aulas_dir, turma_folder)
        # Ignora diretórios especiais que não contêm planos de aula
        if not os.path.isdir(turma_path) or turma_folder in ['inputs', 'logs', 'backups']:
            continue

        for filename in sorted(os.listdir(turma_path)):
            if not filename.endswith('.txt'):
                continue
            total_txt_files += 1

            file_path = os.path.join(turma_path, filename)
            # CORREÇÃO: Atualiza a regex para corresponder ao novo formato de nome de arquivo
            # que inclui o horário (ex: DISC_AAAAMMDD_HHMM.txt).
            match = re.match(r'(.+)_(\d{8})_\d{4}\.txt$', filename)
            if not match:
                continue
            
            disciplina_curto = match.group(1)
            chave_grupo = (turma_folder, disciplina_curto)

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'Preencher' in content:
                    if chave_grupo not in grouped_files:
                        grouped_files[chave_grupo] = []
                    grouped_files[chave_grupo].append(file_path)
    
    print(f"INFO: Encontrados {total_txt_files} arquivos .txt no total. Destes, os seguintes grupos contêm arquivos pendentes:")
    return grouped_files

def display_menu_and_get_choice(grouped_files):
    """
    Exibe um menu com as disciplinas pendentes e retorna a lista de arquivos a serem processados.
    """
    if not grouped_files:
        return []

    print("Disciplinas com planos de aula pendentes:\n")
    options = list(grouped_files.keys())
    for i, (turma, disciplina) in enumerate(options):
        file_count = len(grouped_files[(turma, disciplina)])
        print(f"  {i+1}) {turma} / {disciplina} ({file_count} arquivo(s))")
    
    print(f"\n  {len(options) + 1}) Processar todas as disciplinas")
    print("  0) Sair")

    while True:
        try:
            choice = int(input("\nEscolha uma opção para preencher: "))
            if 0 <= choice <= len(options) + 1:
                if choice == 0: return []
                if choice == len(options) + 1: return [file for files in grouped_files.values() for file in files]
                selected_key = options[choice - 1]
                return grouped_files[selected_key]
            else:
                print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")

def parse_md_content(md_path):
    """
    Extrai o título (primeira linha H1) e os objetivos de um arquivo Markdown.
    Os objetivos são considerados o texto entre "### Objetivos da Aula" e a próxima seção H3.
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        title = ""
        objectives = []
        in_objectives_section = False

        for line in lines:
            if line.strip().startswith('#'):
                if not title:
                    title = line.strip().lstrip('#').strip()
            
            # Regex para encontrar o início da seção de objetivos de forma flexível
            # Procura por "objetivo(s)" no início da linha, ignorando formatação como '##', '*', emojis, etc.
            if re.match(r'^[#\s*🎯]*\s*objetivos?(:|\s+da\s+aula)', line.strip(), re.IGNORECASE):
                in_objectives_section = True
                continue

            if in_objectives_section:
                if line.strip().startswith('#') or line.strip().lower().startswith('**conteúdo'):
                    break
                if line.strip():
                    objectives.append(line.strip())

        return title, "\n".join(objectives)

    except FileNotFoundError:
        return None, None
    except Exception as e:
        print(f"  -> ERRO ao ler o arquivo MD '{os.path.basename(md_path)}': {e}")
        return None, None

def carregar_links_recursos(data_path):
    """
    Carrega um arquivo JSON centralizado que mapeia (turma, disciplina, aula) para um link.
    """
    links_recursos = {}
    caminho_arquivo = os.path.join(data_path, 'recursos_links.json')
    if not os.path.exists(caminho_arquivo):
        print("AVISO: Arquivo 'recursos_links.json' não encontrado. Nenhum link de recurso será adicionado automaticamente.")
        return links_recursos
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Converte a chave string para tupla de forma segura usando ast.literal_eval
        for k, v in data.items():
            try:
                links_recursos[ast.literal_eval(k)] = v
            except (ValueError, SyntaxError):
                print(f"AVISO: Chave JSON inválida ignorada: {k}")
    return links_recursos

def update_plan_file(txt_path, title, objectives, link):
    """
    Atualiza o arquivo .txt com o título, objetivos e link extraídos,
    respeitando o limite de caracteres para o comentário.
    """
    try:
        # Mapeamento de conteúdos e estratégias para aulas especiais
        conteudos_especiais = {
            "revisao av1": ("Revisão de Conteúdo para a Avaliação 1 (AV1)", "Aula expositiva e resolução de exercícios preparatórios para a avaliação."),
            "av1": ("Aplicação da Avaliação 1 (AV1)", "Realização de avaliação individual escrita para verificação da aprendizagem."),
            "revisao av2": ("Revisão de Conteúdo para a Avaliação 2 (AV2)", "Aula expositiva e resolução de exercícios preparatórios para a avaliação."),
            "av2": ("Aplicação da Avaliação 2 (AV2)", "Realização de avaliação individual escrita para verificação da aprendizagem."),
            "atividades praticas": ("Desenvolvimento de Atividades Práticas", "Execução de atividades práticas em laboratório para consolidar o conhecimento.")
        }

        with open(txt_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        conteudo_final = title
        estrategia_final = "Aula expositiva com uso de projetor e internet"
        recurso_titulo_final = title
        recurso_link_final = link or ""
        recurso_comentario_final = objectives

        # Verifica se o título corresponde a uma aula especial
        title_lower = title.lower()
        for key, (conteudo_esp, estrategia_esp) in conteudos_especiais.items():
            if key in title_lower:
                print(f"  -> INFO: Detectada aula especial '{key}'. Usando conteúdo padrão.")
                conteudo_final = conteudo_esp
                estrategia_final = estrategia_esp
                recurso_titulo_final = "" # Limpa para não ter recurso
                recurso_link_final = ""
                recurso_comentario_final = "" # Limpa para não ter comentário
                break

        # Trunca o comentário do recurso se não for uma aula especial
        if recurso_comentario_final:
            char_limit = 150
            if len(recurso_comentario_final) > char_limit:
                recurso_comentario_final = recurso_comentario_final[:char_limit - 3] + "..."

        # Substitui os blocos no arquivo com os conteúdos finais
        new_content = re.sub(r'(\[CONTEUDO\]\n)[\s\S]*?(\n\n\[ESTRATEGIA\])', f'\\1{conteudo_final}\\2', original_content)
        new_content = re.sub(r'(\[ESTRATEGIA\]\n)[\s\S]*?(\n\n\[RECURSO_TITULO\])', f'\\1{estrategia_final}\\2', new_content)
        new_content = re.sub(r'(\[RECURSO_TITULO\]\n)[\s\S]*?(\n\n\[RECURSO_LINK\])', f'\\1{recurso_titulo_final}\\2', new_content)
        new_content = re.sub(r'(\[RECURSO_LINK\]\n)[\s\S]*?(\n\n\[RECURSO_COMENTARIO\])', f'\\1{recurso_link_final}\\2', new_content)
        new_content = re.sub(r'(\[RECURSO_COMENTARIO\]\n)[\s\S]*', f'\\1{recurso_comentario_final}', new_content)

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  -> SUCESSO: Arquivo '{os.path.basename(txt_path)}' preenchido.")

    except Exception as e:
        print(f"  -> ERRO ao atualizar o arquivo '{os.path.basename(txt_path)}': {e}")

def preencher_arquivo_plano(txt_path, inputs_dir, links_recursos_globais):
    """
    Lógica encapsulada para preencher um único arquivo de plano.
    Retorna (sucesso: bool, mensagem: str)
    """
    path_parts = txt_path.split(os.sep)
    turma_folder = path_parts[-2]
    txt_filename = path_parts[-1]

    match = re.match(r'(.+)_(\d{8})_\d{4}\.txt$', txt_filename)
    disciplina_curto = match.group(1) if match else None

    aula_num = None
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('# Aula:'):
                    aula_num = int(line.split(':')[1].strip())
                    break
    except Exception as e:
        return False, f"Erro ao ler arquivo: {e}"
    
    if not disciplina_curto:
        return False, f"Não foi possível extrair disciplina de '{txt_filename}'"

    if aula_num is None:
        return False, f"Número da aula não encontrado em '{txt_filename}'"

    source_turma_folder = turma_folder
    source_disciplina_curto = disciplina_curto

    # Redirecionamentos (Hardcoded rules)
    if turma_folder == '1_PJ' and disciplina_curto == 'MENTORIAS_TEC_JOGOS':
        source_turma_folder = '1_DS'
        source_disciplina_curto = 'MENTORIAS_TEC_DES_SIST'
    if turma_folder == '1_PJ' and disciplina_curto == 'PROGRAMACAO_JOGOS_II':
        source_disciplina_curto = 'PROGRAMACAO_JOGOS_II'

    md_input_folder = os.path.join(inputs_dir, source_turma_folder, source_disciplina_curto)
    md_filename_prefix = f"aula_{aula_num:02d}"
    md_path = None
    
    if os.path.exists(md_input_folder):
        for root, _, files in os.walk(md_input_folder):
            if md_path: break
            for file in files:
                if file.startswith(md_filename_prefix) and file.endswith('.md'):
                    md_path = os.path.join(root, file)
                    break

    chave_link = (turma_folder.replace('_', 'º '), disciplina_curto, aula_num)
    recurso_link = links_recursos_globais.get(chave_link)

    if not md_path:
        title = disciplina_curto.replace('_', ' ').title()
        objectives = ""
        msg_extra = " (Sem MD, usando padrão)"
    else:
        title, objectives = parse_md_content(md_path)
        msg_extra = ""

    if not title:
        return False, "Título não encontrado ou gerado."
    
    update_plan_file(txt_path, title, objectives, recurso_link)
    return True, f"Preenchido{msg_extra}"

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    AULAS_DIR = os.path.join(PROJECT_ROOT, 'aulas')
    INPUTS_DIR = os.path.join(AULAS_DIR, 'inputs')
    DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

    print("\n--- Assistente Automatizado de Preenchimento de Planos ---")
    
    grouped_plan_files = find_plan_files(AULAS_DIR)
    plan_files_to_fill = display_menu_and_get_choice(grouped_plan_files)
    links_recursos_globais = carregar_links_recursos(DATA_DIR)

    if not plan_files_to_fill:
        print("\nNenhum plano de aula selecionado ou pendente. Encerrando.")
    else:
        print(f"\nIniciando preenchimento para {len(plan_files_to_fill)} arquivo(s) selecionado(s)...\n")

    plan_files_to_fill.sort() # Garante uma ordem consistente de processamento

    for txt_path in plan_files_to_fill:
        success, msg = preencher_arquivo_plano(txt_path, INPUTS_DIR, links_recursos_globais)
        if success:
            print(f"  -> SUCESSO: {os.path.basename(txt_path)} - {msg}")
        else:
            print(f"  -> FALHA: {os.path.basename(txt_path)} - {msg}")

    print("\nPreenchimento finalizado.")
'@
Create-File (Join-Path $RootPath "tools\preenchedor_planos.py") $Content_Preenchedor


$Content_ConverterMD = @'
import os
import markdown
from weasyprint import HTML, CSS
import sys

def converter_md_para_pdf(caminho_arquivo_md):
    """
    Converte um único arquivo Markdown para PDF, aplicando um estilo CSS.
    """
    try:
        print(f"  -> Convertendo: {os.path.basename(caminho_arquivo_md)}")

        # 1. Ler o conteúdo do arquivo Markdown
        with open(caminho_arquivo_md, 'r', encoding='utf-8') as f:
            texto_md = f.read()

        # 2. Converter Markdown para HTML
        html_texto = markdown.markdown(texto_md, extensions=['fenced_code', 'tables'])

        # 3. Definir um estilo CSS para deixar o PDF mais legível e profissional
        # Este CSS pode ser customizado como você preferir.
        estilo_css = """
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        h1, h2, h3 {
            font-family: 'Segoe UI Light', Arial, sans-serif;
            color: #005a9e;
            border-bottom: 2px solid #005a9e;
            padding-bottom: 5px;
            margin-top: 24px;
        }
        h1 { font-size: 24pt; }
        h2 { font-size: 18pt; }
        h3 { font-size: 14pt; }
        strong {
            color: #000;
        }
        code {
            font-family: 'Consolas', 'Courier New', monospace;
            background-color: #f0f0f0;
            padding: 2px 5px;
            border-radius: 4px;
            font-size: 0.9em;
        }
        pre {
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
            white-space: pre-wrap; /* Quebra de linha no código */
        }
        """

        # 4. Gerar o PDF a partir do HTML e CSS
        caminho_arquivo_pdf = os.path.splitext(caminho_arquivo_md)[0] + '.pdf'
        HTML(string=html_texto).write_pdf(caminho_arquivo_pdf, stylesheets=[CSS(string=estilo_css)])

        print(f"     -> PDF salvo em: {os.path.basename(caminho_arquivo_pdf)}")
        return True

    except Exception as e:
        print(f"     -> ERRO ao converter '{os.path.basename(caminho_arquivo_md)}': {e}")
        return False

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUTS_DIR = os.path.join(PROJECT_ROOT, 'aulas', 'inputs')
    print(f"--- Iniciando conversão de Markdown para PDF na pasta: {INPUTS_DIR} ---")
    for root, _, files in os.walk(INPUTS_DIR):
        for file in files:
            if file.endswith('.md'):
                caminho_completo = os.path.join(root, file)
                converter_md_para_pdf(caminho_completo)
    print("\n--- Conversão concluída. ---")

'@
Create-File (Join-Path $RootPath "tools\converter_md_para_pdf.py") $Content_ConverterMD


# --- DOCS ---

$Content_DocScraper = @'
# Documentação do Scraper
O script `scraper.py` conecta no portal, navega pelas turmas e baixa o histórico.
'@
Create-File (Join-Path $RootPath "docs\scrapper.md") $Content_DocScraper

$Content_DocTutorial = @'
# Tutorial Completo
1. Rode `scraper.py` para atualizar dados.
2. Rode `analisador_de_grade.py` para ver o que falta.
3. Rode `preparar_planos.py` para gerar os .txt.
4. Rode `preenchedor_planos.py` para colocar conteúdo.
5. Rode `registrar_aulas.py` para enviar ao portal.
'@
Create-File (Join-Path $RootPath "docs\tutorial_completo.md") $Content_DocTutorial

$Content_DocUso = @'
# 📖 Tutorial de Uso: Assistente de Aulas

Este guia explica como utilizar a interface gráfica do Assistente de Aulas para automatizar sua rotina, desde a coleta de dados até o registro no portal.

## 1. Iniciando o Aplicativo

1.  Abra a pasta do projeto.
2.  Certifique-se de que seu ambiente virtual está ativo (se estiver rodando via terminal) ou que você configurou o Python corretamente.
3.  Execute o arquivo `app.py`:
    ```bash
    python app.py
    ```
4.  A janela **"Painel de Controle do Professor"** será aberta.

---

## 2. O Fluxo de Trabalho

O sistema foi desenhado para funcionar em 4 etapas sequenciais. Recomenda-se seguir a ordem dos botões na interface.

### Passo 1: Atualizar Dados (Scraper) 📥
*   **O que faz:** O robô entra no portal da Seduc, navega por todas as suas turmas e baixa o histórico do que **já foi registrado**.
*   **Por que usar:** Isso evita que o sistema tente registrar aulas duplicadas ou em dias que você já preencheu manualmente.
*   **Resultado:** Atualiza o arquivo `data/aulas_coletadas.json`.
*   **Tempo estimado:** 2 a 5 minutos (depende da velocidade do portal).

### Passo 2: Planejar Aulas 🗓️
*   **O que faz:** Analisa sua grade horária (`horarios_semanais_oficial.json`) e o calendário letivo. Ele identifica os "buracos" futuros e cria arquivos de texto vazios (esqueletos) na pasta `aulas/`.
*   **Exemplo:** Se você tem aula de "Matemática" na próxima segunda-feira, ele cria um arquivo `2023-10-23_Matematica_TurmaA.txt`.
*   **Ação do Professor:** Após rodar este passo, você pode verificar a pasta `aulas/` para ver os arquivos criados.

### Passo 3: Preencher Conteúdos 📝
*   **O que faz:** Esta é a mágica. O sistema lê os arquivos "esqueletos" criados no passo anterior e procura conteúdo correspondente na pasta `aulas/inputs/`.
*   **Como funciona:** Se o esqueleto pede a "Aula 05" de "História", o sistema busca nos seus materiais (PDFs, Markdowns) o conteúdo dessa aula e preenche automaticamente os campos:
    *   Conteúdo Programático
    *   Estratégia Metodológica
    *   Recursos
*   **Resultado:** Os arquivos `.txt` na pasta `aulas/` agora estão completos e prontos para envio.

### Passo 4: Registrar no Portal 🚀
*   **O que faz:** O robô abre o navegador, faz login e começa a lançar as aulas que estão prontas na pasta `aulas/`.
*   **Importante:**
    *   Não mexa no mouse ou teclado enquanto o robô trabalha (a menos que ele peça).
    *   Acompanhe o progresso na área de "Logs" da janela do aplicativo.
*   **Sucesso:** Quando uma aula é registrada com sucesso, o arquivo `.txt` correspondente é movido/deletado da pasta de pendências.

---

## 3. Dicas e Solução de Problemas

*   **O aplicativo travou?**
    A interface gráfica roda os processos em segundo plano. Se parecer travada, verifique a janela de "Logs". Se houver um erro vermelho, leia a mensagem para entender o que houve (geralmente é senha errada ou portal fora do ar).

*   **Preciso parar o robô!**
    Feche a janela do aplicativo ou o terminal preto que se abriu junto com o navegador.

*   **Modo Texto (CLI)**
    Se preferir usar o teclado, você pode rodar `python app.py --cli` para ver um menu numérico simples no terminal.

## 4. Organização das Pastas

*   Coloque seus materiais de aula em: `aulas/inputs/SuaTurma/SuaDisciplina/`.
*   Verifique os planos gerados em: `aulas/`.
'@
Create-File (Join-Path $RootPath "docs\tutorial_uso.md") $Content_DocUso

$Content_DocArq = @'
# 🏗️ Arquitetura Técnica do Projeto

Este documento descreve a estrutura de software, as decisões de design e o fluxo de dados do projeto **Assistente de Aulas**.

## Visão Geral

O projeto é uma aplicação Python modular que utiliza automação de navegador (Selenium) e processamento de texto para gerenciar registros escolares. A arquitetura segue uma separação clara entre **Interface (Frontend)**, **Lógica de Negócio (Tools)** e **Dados**.

## Estrutura de Diretórios

```text
Aulas_selenium/
├── app.py                  # Entry Point (Padrão Facade/Âncora)
├── interfaces/             # Camada de Apresentação
│   ├── gui_app.py          # Interface Gráfica (Tkinter)
│   └── cli_menu.py         # Interface de Linha de Comando
├── tools/                  # Camada de Lógica de Negócio (Scripts Independentes)
│   ├── scraper.py          # Coleta de dados (Selenium)
│   ├── preparar_planos.py  # Lógica de calendário e geração de arquivos
│   ├── registrar_aulas.py  # Automação de input (Selenium)
│   └── ...
├── core/                   # Bibliotecas Compartilhadas
│   └── gemini_client.py    # Integração com LLMs
├── data/                   # Camada de Persistência (JSON/Flat files)
└── aulas/                  # Área de Staging (Arquivos de trabalho)
```

## Componentes Principais

### 1. Âncora (`app.py`)
Atua como o ponto de entrada único. Sua função é detectar o ambiente e decidir qual interface carregar.
*   Configura o `PYTHONPATH` e o diretório de trabalho (`CWD`) para garantir que as importações relativas funcionem.
*   Trata exceções de inicialização da GUI (ex: falta de display no Linux) e faz *fallback* para CLI.

### 2. Interfaces (`interfaces/`)
A camada de apresentação é desacoplada da lógica.
*   **GUI (`gui_app.py`)**: Utiliza `tkinter` (nativo do Python). Implementa *Threading* para executar os scripts da pasta `tools/` sem congelar a interface. Captura `stdout` e `stderr` dos subprocessos para exibir logs em tempo real na janela.
*   **CLI (`cli_menu.py`)**: Um loop simples de menu para execução rápida em terminais.

### 3. Ferramentas (`tools/`)
Cada script nesta pasta é uma unidade lógica independente que pode ser executada isoladamente.
*   **Design Pattern**: Scripts de execução direta. Eles não dependem da interface para funcionar, apenas dos arquivos de configuração em `data/`.
*   **Comunicação**: A comunicação entre as ferramentas ocorre via sistema de arquivos (JSONs em `data/` e TXTs em `aulas/`).
    *   *Exemplo*: O `scraper.py` escreve em `aulas_coletadas.json`, que é lido pelo `analisador_de_grade.py`.

### 4. Persistência de Dados
O projeto não utiliza banco de dados relacional (SQL) para manter a portabilidade e simplicidade.
*   **Configuração**: Arquivos JSON (`config.json`, `credentials.json`).
*   **Estado**: O estado do sistema é determinado pela presença ou ausência de arquivos na pasta `aulas/`. Se um arquivo `.txt` existe, é uma aula pendente. Se não existe, foi registrada.

## Fluxo de Execução (Pipeline)

1.  **Usuário** aciona `app.py`.
2.  **Interface** chama `subprocess.Popen(['python', 'tools/script.py'])`.
3.  **Tool** carrega configurações de `data/`.
4.  **Tool** executa lógica (ex: Selenium abre Chrome).
5.  **Tool** lê/escreve em `aulas/` ou `data/`.
6.  **Interface** captura o output e mostra ao usuário.
'@
Create-File (Join-Path $RootPath "docs\arquitetura_tecnica.md") $Content_DocArq

$Content_DocFerramentas = @'
# 🛠️ Ferramentas Secundárias e Utilitários

Além do fluxo principal de automação, a pasta `tools/` contém diversos scripts utilitários projetados para tarefas específicas de análise, gestão de conteúdo e manutenção.

Este guia explica o propósito e o uso de cada um.

## 📊 Análise e Relatórios

### `analisador_de_grade.py`
*   **Função:** Gera um relatório detalhado no terminal comparando as horas registradas versus a carga horária obrigatória de cada disciplina.
*   **Quando usar:** Para saber exatamente quantas aulas faltam para completar a grade de uma turma específica.
*   **Uso:** Executado automaticamente pela **Opção 2** do menu principal, ou via terminal:
    ```bash
    python tools/analisador_de_grade.py
    ```

### `ver_aulas_por_disciplina.py`
*   **Função:** Oferece um menu interativo para visualizar estatísticas das aulas já coletadas (arquivo `aulas_coletadas.json`).
*   **Modos de Visualização:**
    1.  Por Disciplina (contagem total).
    2.  Por Turma.
    3.  Por Data (útil para verificar dias com muitas aulas).
*   **Uso:**
    ```bash
    python tools/ver_aulas_por_disciplina.py
    ```

### `utils_files.py` (Exportar CSV)
*   **Função:** Converte o banco de dados JSON (`aulas_coletadas.json`) para um arquivo Excel/CSV (`aulas_coletadas.csv`).
*   **Quando usar:** Se você quiser abrir seus dados no Excel para criar gráficos ou relatórios personalizados.
*   **Uso:**
    ```bash
    python tools/utils_files.py
    ```

---

## 📝 Gestão de Conteúdo Didático

### `gerar_json_recursos.py`
*   **Função:** Varre todos os arquivos Markdown (`.md`) na pasta `aulas/inputs/`, procura por links de materiais (ex: `* Aula 01`) e cria um índice centralizado em `data/recursos_links.json`.
*   **Por que é importante:** O script de preenchimento usa esse índice para inserir automaticamente os links dos slides/PDFs nos planos de aula.
*   **Uso:** Execute sempre que adicionar novos links nos seus resumos.
    ```bash
    python tools/gerar_json_recursos.py
    ```

### `converter_md_para_pdf.py`
*   **Função:** Converte seus resumos de aula em Markdown para arquivos PDF formatados profissionalmente.
*   **Requisito:** Requer a biblioteca `weasyprint` e `markdown`.
*   **Uso:**
    ```bash
    python tools/converter_md_para_pdf.py
    ```

### `setup_wizard.py` (Assistente de Configuração)
*   **Função:** Resolve o problema da "tela em branco".
    1.  Gera arquivos JSON de exemplo em `data/` com a estrutura correta preenchida.
    2.  Lê suas configurações e cria automaticamente a árvore de pastas em `aulas/inputs/` para você colocar seus materiais.
*   **Quando usar:** Na primeira vez que instalar o projeto ou quando adicionar novas turmas.
*   **Uso:**
    ```bash
    python tools/setup_wizard.py
    ```
'@
Create-File (Join-Path $RootPath "docs\ferramentas_secundarias.md") $Content_DocFerramentas

# --- DATA MODELS (Templates) ---

$Content_ConfigJson = @'
{
  "professor": "Nome do Professor"
}
'@
Create-File (Join-Path $RootPath "data\_modelo\config.json") $Content_ConfigJson

$Content_CredsJson = @'
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
'@
Create-File (Join-Path $RootPath "data\_modelo\credentials.json") $Content_CredsJson

$Content_HorariosJson = @'
[
  {
    "professores": {
      "Nome do Professor": {
        "turmas": {
          "1º A": {
            "DISCIPLINA_EXEMPLO": [
              { "dia_semana_nome": "segunda-feira", "label_horario": "07:30 - 08:20" }
            ]
          }
        }
      }
    }
  }
]
'@
Create-File (Join-Path $RootPath "data\_modelo\horarios_semanais_oficial.json") $Content_HorariosJson

$Content_CalendarioJson = @'
{
  "ano": 2025,
  "data_inicio": "03/02/2025",
  "data_fim": "12/12/2025",
  "carga_horaria_padrao_disciplina": 40,
  "disciplinas_config": {
    "anuais": ["COMPUT", "PROJETO_VIDA"],
    "mensais": ["DISC_MENSAL"]
  },
  "restricoes_planejamento": {}
}
'@
Create-File (Join-Path $RootPath "data\_modelo\calendario_letivo.json") $Content_CalendarioJson

$Content_FeriadosJson = @'
{
  "feriados": [
    { "data": "24/02/2025", "descricao": "Carnaval" },
    { "data": "25/02/2025", "descricao": "Carnaval" }
  ]
}
'@
Create-File (Join-Path $RootPath "data\_modelo\feriados.json") $Content_FeriadosJson

$Content_RecursosJson = @'
{
    "('1º A', 'DISCIPLINA_EXEMPLO', 1)": "https://link.exemplo.com"
}
'@
Create-File (Join-Path $RootPath "data\_modelo\recursos_links.json") $Content_RecursosJson

Create-File (Join-Path $RootPath "data\_modelo\aulas_coletadas.json") "[]"

$Content_MapaTurmas = @'
{
  "NOME COMPLETO DA TURMA NO PORTAL": "1º A"
}
'@
Create-File (Join-Path $RootPath "data\_modelo\mapa_turmas.json") $Content_MapaTurmas

Create-File (Join-Path $RootPath "data\_modelo\turmas_com_disciplinas.json") "[]"
Create-File (Join-Path $RootPath "data\_modelo\.env") "GEMINI_API_KEY=sua_chave_aqui"

# 4. Copiar Modelos para Data (Inicialização)
Write-Color "`n[4/5] Inicializando configurações em data/..." -Color Yellow

$filesToCopy = @(
    "config.json",
    "credentials.json",
    ".env",
    "calendario_letivo.json",
    "horarios_semanais_oficial.json",
    "feriados.json",
    "recursos_links.json",
    "aulas_coletadas.json",
    "mapa_turmas.json",
    "turmas_com_disciplinas.json"
)

foreach ($file in $filesToCopy) {
    $model = Join-Path (Join-Path $RootPath "data\_modelo") $file
    $dest = Join-Path (Join-Path $RootPath "data") $file
    
    if (Test-Path $model) {
        if (-not (Test-Path $dest)) {
            Copy-Item -Path $model -Destination $dest
            Write-Color "  [+] Configuração inicial criada: $file" -Color Cyan
        } else {
            Write-Color "  [=] Configuração já existe: $file" -Color DarkGray
        }
    }
}

# 5. Configuração do Ambiente Virtual e Dependências
Write-Color "`n[5/5] Configurando ambiente virtual e dependências..." -Color Yellow

if (-not (Test-Path (Join-Path $RootPath ".venv"))) {
    Write-Color "  [+] Criando ambiente virtual (.venv)..." -Color Cyan
    python -m venv (Join-Path $RootPath ".venv")
} else {
    Write-Color "  [=] Ambiente virtual já existe." -Color DarkGray
}

$pipPath = Join-Path $RootPath ".venv\Scripts\pip.exe"
$reqPath = Join-Path $RootPath "requirements.txt"

if (Test-Path $pipPath) {
    if (Test-Path $reqPath) {
        Write-Color "  [+] Instalando dependências (pode demorar)..." -Color Cyan
        & $pipPath install -r $reqPath | Out-Null
        Write-Color "  [+] Dependências instaladas com sucesso." -Color Green
    } else {
        Write-Color "  [!] requirements.txt não encontrado." -Color Red
    }
} else {
    Write-Color "ERRO: Pip não encontrado em $pipPath" -Color Red
}

Write-Color "`n=== Setup Concluído! ===" -Color Green
Write-Color "Para iniciar o trabalho:" -Color White
Write-Color "  1. Configure seus dados em: data\credentials.json e data\config.json" -Color Magenta

$activateScript = Join-Path $RootPath ".venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Color "  2. Entrando no diretório e ativando ambiente virtual..." -Color Cyan
    Set-Location $RootPath
    . $activateScript
    Write-Color "  [+] Ambiente ativado!" -Color Green
}

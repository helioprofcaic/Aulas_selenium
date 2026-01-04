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
def _force_hidden_imports():
    import selenium
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait, Select
    import webdriver_manager
    from webdriver_manager.chrome import ChromeDriverManager
    import dateutil
    import pyautogui
    import cv2
    import pandas
    import markdown
    import weasyprint
    import tinycss2
    # Submódulos específicos que o PyInstaller pode perder
    import tinycss2.color3
    import tinycss2.nth
    import tinycss2.parser
    import tinycss2.tokenizer
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
        # O caminho recebido do subprocess é inválido quando congelado.
        # Usamos apenas o nome do arquivo para encontrá-lo dentro do _MEIPASS.
        script_name = os.path.basename(sys.argv[1])
        script_path = os.path.join(sys._MEIPASS, 'tools', script_name)

        if not os.path.exists(script_path):
            print(f"Erro fatal: Script interno '{script_name}' não encontrado em '{os.path.join(sys._MEIPASS, 'tools')}'")
            input("Pressione ENTER para fechar...")
            return
        
        # Ajusta sys.argv para que o script executado veja seu próprio caminho como argv[0]
        sys.argv = [script_path] + sys.argv[2:]

        # Garante que o diretório do script está no path (comportamento padrão do python)
        sys.path.insert(0, os.path.dirname(script_path))
        
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
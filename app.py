import sys
import os
import runpy

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
    raiz = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(raiz)
    # Define o diretório de trabalho para a raiz, para que ferramentas (tools/) encontrem seus arquivos
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
    # Configuração opcional de ícone, se houver
    # try: root.iconbitmap("recursos/icone.ico")
    # except: pass
    
    app = AppAutomação(root)
    root.mainloop()

def iniciar_cli():
    from interfaces.cli_menu import menu_principal
    menu_principal()

if __name__ == "__main__":
    main()

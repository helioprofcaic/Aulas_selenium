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
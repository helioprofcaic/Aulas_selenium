import os
import json
from scraper import Scraper
from preparar_planos import carregar_dados as carregar_dados_preparador, planejar_e_preparar_aulas
from datetime import datetime

def main():
    """
    Orquestra o processo de planejamento de aulas de forma online.
    1. Pede ao usuário para selecionar uma disciplina.
    2. Identifica aulas "Aguardando confirmação" para essa disciplina no JSON local.
    3. Usa o Scraper para coletar dados atualizados APENAS para as turmas/disciplinas relevantes.
    4. Atualiza o `aulas_coletadas.json` local com os novos status.
    5. Usa a lógica do `preparar_planos` para gerar os arquivos .txt necessários com base nos dados atualizados.
    """
    print("\n--- INICIANDO PLANEJADOR ONLINE ---")
    print("Este script irá verificar o status de aulas pendentes no portal antes de planejar.\n")

    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_PATH = os.path.join(PROJECT_ROOT, 'data')
    AULAS_COLETADAS_PATH = os.path.join(DATA_PATH, 'aulas_coletadas.json')
    AULAS_DIR = os.path.join(PROJECT_ROOT, 'aulas') # <-- ADICIONADO: Define o caminho para a pasta 'aulas'

    # 1. Carregar configurações e credenciais locais
    try:
        print("[Passo 1/3] Carregando configurações locais...")
        dados_locais_preparador = carregar_dados_preparador(DATA_PATH)
        turmas_disciplinas, _, _, mapa_turmas, _, _ = dados_locais_preparador
        with open(os.path.join(DATA_PATH, 'credentials.json'), 'r') as f:
            creds = json.load(f)
        with open(AULAS_COLETADAS_PATH, 'r', encoding='utf-8') as f:
            aulas_coletadas_local = json.load(f)
        print("  -> Configurações carregadas com sucesso.")
    except Exception as e:
        print(f"ERRO CRÍTICO ao carregar arquivos locais: {e}")
        return

    # Mapeia nome da disciplina para as turmas que a possuem
    disciplina_para_turmas = {}
    for turma in turmas_disciplinas:
        nome_turma_completo = turma['nomeTurma']
        for disciplina in turma['disciplinas']:
            nome_disciplina = disciplina['nomeDisciplina']
            if nome_disciplina not in disciplina_para_turmas:
                disciplina_para_turmas[nome_disciplina] = []
            disciplina_para_turmas[nome_disciplina].append(nome_turma_completo)

    disciplinas_disponiveis = sorted(list(disciplina_para_turmas.keys()))

    print("\nDisciplinas disponíveis para planejamento:")
    for i, nome_disciplina in enumerate(disciplinas_disponiveis):
        print(f"  {i + 1}. {nome_disciplina}")

    while True:
        try:
            escolha = int(input("\nDigite o número da disciplina que deseja planejar/verificar: "))
            if 1 <= escolha <= len(disciplinas_disponiveis):
                disciplina_selecionada = disciplinas_disponiveis[escolha - 1]
                break
            else:
                print("Opção inválida. Por favor, digite um número da lista.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")

    print(f"\nVocê selecionou a disciplina: '{disciplina_selecionada}'")
    turmas_da_disciplina = disciplina_para_turmas[disciplina_selecionada]

    # 2. Verificar aulas "Aguardando confirmação" e atualizar status online
    print("\n[Passo 2/3] Verificando status de aulas pendentes no portal...")
    aulas_para_verificar = [
        aula for aula in aulas_coletadas_local
        if aula.get('componenteCurricular') == disciplina_selecionada and aula.get('status') == 'Aguardando confirmação'
    ]

    if not aulas_para_verificar:
        print(f"  -> Nenhuma aula 'Aguardando confirmação' encontrada para '{disciplina_selecionada}'. O planejamento usará os dados locais.")
        aulas_atualizadas = aulas_coletadas_local
    else:
        print(f"  -> Encontradas {len(aulas_para_verificar)} aulas 'Aguardando confirmação' para '{disciplina_selecionada}'. Conectando ao portal para verificar...")
        
        aulas_online_disciplina = {} # Dicionário para acesso rápido: (turma, data, horario) -> status
        scraper_instance = Scraper(project_root=PROJECT_ROOT)
        try:
            # --- NOVA LÓGICA DE LOGIN ÚNICO ---
            scraper_instance._initialize_driver()
            target_url = "https://portal.seduc.pi.gov.br/#!/turmas"
            scraper_instance._login(target_url, creds)
            scraper_instance._select_profile_and_institution()
            # ------------------------------------

            for nome_turma_completo in turmas_da_disciplina:
                print(f"    -> Coletando dados da turma: {mapa_turmas.get(nome_turma_completo, nome_turma_completo)}")
                dados_online = scraper_instance.coletar_dados_disciplina(nome_turma_completo=nome_turma_completo, nome_disciplina_completo=disciplina_selecionada)
                for aula in dados_online:
                    chave = (aula['turma'], aula['dataAula'], aula['horario'])
                    aulas_online_disciplina[chave] = aula['status']
            
            print(" -> Coleta online concluída.")

        except Exception as e:
            print(f"ERRO CRÍTICO durante a coleta de dados online: {e}")
            print("O planejamento será abortado.")
            return
        finally:
            if scraper_instance and scraper_instance.driver:
                scraper_instance.driver.quit()
                print(" -> Navegador do scraper fechado.")

        # Atualiza a lista de aulas local com os status online
        aulas_atualizadas = list(aulas_coletadas_local) # Cria uma cópia
        atualizacoes = 0
        for i, aula_local in enumerate(aulas_atualizadas):
            if aula_local.get('componenteCurricular') == disciplina_selecionada and aula_local.get('status') == 'Aguardando confirmação':
                chave_online = (aula_local['turma'], aula_local['dataAula'], aula_local['horario'])
                status_online = aulas_online_disciplina.get(chave_online)
                if status_online and status_online != aula_local['status']:
                    print(f"    -> ATUALIZANDO: Aula de {aula_local['dataAula']} na turma {mapa_turmas.get(aula_local['turma'])} mudou para '{status_online}'")
                    aulas_atualizadas[i]['status'] = status_online
                    atualizacoes += 1
        
        if atualizacoes > 0:
            print(f"  -> {atualizacoes} aulas foram atualizadas. Salvando em '{AULAS_COLETADAS_PATH}'...")
            with open(AULAS_COLETADAS_PATH, 'w', encoding='utf-8') as f:
                json.dump(aulas_atualizadas, f, indent=4, ensure_ascii=False)
            print("  -> Arquivo 'aulas_coletadas.json' atualizado com sucesso.")
        else:
            print("  -> Nenhum status de aula pendente foi alterado no portal.")

    # 3. Chamar a lógica de planejamento com os dados atualizados
    try:
        if aulas_atualizadas:
            print("\n[Passo 3/3] Iniciando o planejamento com base nos dados atualizados...")
            # Passa os dados locais e os dados online recém-coletados/atualizados
            planejar_e_preparar_aulas(dados_locais_preparador, aulas_atualizadas, AULAS_DIR) # <-- CORRIGIDO: Passa o caminho para a função
        else:
            print("\nAVISO: Nenhuma aula foi coletada do portal. O planejamento não pode continuar.")
    except Exception as e:
        print(f"\nERRO INESPERADO durante a fase de planejamento: {e}")

if __name__ == '__main__':

    main()
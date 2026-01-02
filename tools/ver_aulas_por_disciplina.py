import json
import os
from collections import defaultdict
from datetime import datetime

def carregar_dados(data_path):
    """Carrega os arquivos JSON necessários."""
    try:
        with open(os.path.join(data_path, 'aulas_coletadas.json'), 'r', encoding='utf-8') as f:
            aulas_coletadas = json.load(f)
        with open(os.path.join(data_path, 'turmas_com_disciplinas.json'), 'r', encoding='utf-8') as f:
            turmas_disciplinas = json.load(f)
        with open(os.path.join(data_path, 'mapa_turmas.json'), 'r', encoding='utf-8') as f:
            mapa_turmas = json.load(f)
        return aulas_coletadas, turmas_disciplinas, mapa_turmas
    except FileNotFoundError as e:
        print(f"ERRO: Arquivo de dados não encontrado: {e.filename}")
        print("Por favor, execute o 'scraper.py' primeiro para gerar o 'aulas_coletadas.json'.")
        return None, None, None
    except Exception as e:
        print(f"ERRO ao carregar arquivos de dados: {e}")
        return None, None, None

def ver_por_disciplina(aulas_coletadas, turmas_disciplinas):
    """Conta as aulas por disciplina e exibe um resumo."""
    if not aulas_coletadas:
        print("Nenhuma aula coletada para analisar.")
        return

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

def ver_por_turma(aulas_coletadas, mapa_turmas):
    """Conta as aulas por turma e exibe um resumo."""
    if not aulas_coletadas:
        print("Nenhuma aula coletada para analisar.")
        return

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

    print("\n--- Resumo de Aulas Registradas por Turma ---")
    max_len_nome = max(len(row[1]) for row in dados_tabela) if dados_tabela else 30
    
    header = f"{'Nome Curto':<15} | {'Nome Completo da Turma':<{max_len_nome}} | {'Aulas Registradas'}"
    print(header)
    print("-" * len(header))

    for nome_curto, nome_completo, contagem in dados_tabela:
        print(f"{nome_curto:<15} | {nome_completo:<{max_len_nome}} | {contagem}")
    
    print("-" * len(header))
    print(f"Total de turmas encontradas: {len(dados_tabela)}")

def ver_por_data(aulas_coletadas):
    """Conta as aulas por data e exibe um resumo."""
    if not aulas_coletadas:
        print("Nenhuma aula coletada para analisar.")
        return

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
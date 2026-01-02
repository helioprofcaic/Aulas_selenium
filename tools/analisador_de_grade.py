import json
import os
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
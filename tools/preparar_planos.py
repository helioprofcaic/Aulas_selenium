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
            with open(json_path, 'r', encoding='utf-8-sig') as f:
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
    with open(os.path.join(DATA_PATH, 'aulas_coletadas.json'), 'r', encoding='utf-8-sig') as f:
        aulas_coletadas_offline = json.load(f)
    
    # Executa a lógica de planejamento
    planejar_e_preparar_aulas(dados_carregados, aulas_coletadas_offline, AULAS_DIR)

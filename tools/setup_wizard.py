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
        "EMI-INT CT DES SIST-1ª SÉRIE -I-A": "1º DS",
        "EMI-INT CT PROG JOGOS DIG-1ª SÉRIE-I-A": "1º PJ",
        "ENS FUND II-9º ANO-I-B": "9º B"
    })

    # 4. turmas_com_disciplinas.json (Estrutura das disciplinas)
    save_json(os.path.join(data_dir, 'turmas_com_disciplinas.json'), [
        {
            "nomeTurma": "EMI-INT CT DES SIST-1ª SÉRIE -I-A",
            "disciplinas": [
                {"codigoDisciplina": "PENSAMENTO_COMPUTACIONAL_DES_SIST", "nomeDisciplina": "Pensamento Computacional"},
                {"codigoDisciplina": "MENTORIAS_TEC_DES_SIST", "nomeDisciplina": "Mentorias Tecnológicas I"}
            ]
        },
        {
            "nomeTurma": "EMI-INT CT PROG JOGOS DIG-1ª SÉRIE-I-A",
            "disciplinas": [
                {"codigoDisciplina": "PROGRAMACAO_JOGOS_II", "nomeDisciplina": "Programação de Jogos II"},
                {"codigoDisciplina": "MENTORIAS_TEC_JOGOS", "nomeDisciplina": "Mentorias Tecnológicas I (Jogos)"}
            ]
        },
        {
            "nomeTurma": "ENS FUND II-9º ANO-I-B",
            "disciplinas": [
                {"codigoDisciplina": "COMPUT", "nomeDisciplina": "Computação"}
            ]
        }
    ])

    # 5. horarios_semanais_oficial.json (A grade horária complexa)
    save_json(os.path.join(data_dir, 'horarios_semanais_oficial.json'), [
        {
            "professores": {
                "Hélio Lima": {
                    "turmas": {
                        "1º DS": {
                            "PENSAMENTO_COMPUTACIONAL_DES_SIST": [
                                {"dia_semana_nome": "segunda-feira", "label_horario": "07:30 - 08:20"},
                                {"dia_semana_nome": "quarta-feira", "label_horario": "09:10 - 10:00"}
                            ],
                            "MENTORIAS_TEC_DES_SIST": [
                                {"dia_semana_nome": "sexta-feira", "label_horario": "10:50 - 11:40"}
                            ]
                        },
                        "1º PJ": {
                            "PROGRAMACAO_JOGOS_II": [
                                {"dia_semana_nome": "terça-feira", "label_horario": "13:20 - 14:10"},
                                {"dia_semana_nome": "terça-feira", "label_horario": "14:10 - 15:00"}
                            ]
                        },
                        "9º B": {
                            "DISC_MENSAL": [
                                {"dia_semana_nome": "quinta-feira", "label_horario": "07:30 - 08:20"}
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
        save_json(os.path.join(data_dir, 'aulas_coletadas.json'), [
            {
                "dataAula": "03/02/2025",
                "horario": "07:30 - 08:20",
                "turma": "EMI-INT CT DES SIST-1ª SÉRIE -I-A",
                "componenteCurricular": "Pensamento Computacional",
                "data_cadastro": "03/02/2025",
                "status": "Aula confirmada"
            },
            {
                "dataAula": "04/02/2025",
                "horario": "13:20 - 14:10",
                "turma": "EMI-INT CT PROG JOGOS DIG-1ª SÉRIE-I-A",
                "componenteCurricular": "Programação de Jogos II",
                "data_cadastro": "04/02/2025",
                "status": "Aula confirmada"
            }
        ])

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
        with open(aulas_json_path, 'r', encoding='utf-8') as f:
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

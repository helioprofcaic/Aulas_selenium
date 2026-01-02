import os
import re
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
        path_parts = txt_path.split(os.sep)
        turma_folder = path_parts[-2]
        txt_filename = path_parts[-1]

        # CORREÇÃO: Usa a regex correta que considera o horário no nome do arquivo.
        # Isso extrai 'PROGRAMACAO_JOGOS_II' de 'PROGRAMACAO_JOGOS_II_20251114_1340.txt'.
        match = re.match(r'(.+)_(\d{8})_\d{4}\.txt$', txt_filename)
        disciplina_curto = match.group(1) if match else None

        aula_num = None
        with open(txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('# Aula:'):
                    aula_num = int(line.split(':')[1].strip())
                    break
        
        if not disciplina_curto:
            print(f"  -> AVISO: Não foi possível extrair o nome da disciplina do arquivo '{txt_filename}'. Pulando.")
            continue

        if aula_num is None:
            print(f"  -> AVISO: Não foi possível encontrar o número da aula em '{txt_filename}'. Pulando.")
            continue

        source_turma_folder = turma_folder
        source_disciplina_curto = disciplina_curto

        if turma_folder == '1_PJ' and disciplina_curto == 'MENTORIAS_TEC_JOGOS':
            print(f"  -> INFO: Redirecionando para usar material de '1_DS/MENTORIAS_TEC_DES_SIST' para a turma {turma_folder}.")
            source_turma_folder = '1_DS'
            source_disciplina_curto = 'MENTORIAS_TEC_DES_SIST'

        # CORREÇÃO: Aponta para o diretório correto onde os MDs de PJD II estão
        if turma_folder == '1_PJ' and disciplina_curto == 'PROGRAMACAO_JOGOS_II':
            print(f"  -> INFO: Redirecionando para usar material de 'PROGRAMACAO_DE_JOGOS_II' para a disciplina {disciplina_curto}.")
            source_disciplina_curto = 'PROGRAMACAO_JOGOS_II'

        md_input_folder = os.path.join(INPUTS_DIR, source_turma_folder, source_disciplina_curto)
        md_filename_prefix = f"aula_{aula_num:02d}" # Ex: "aula_01"
        md_path = None
        
        if os.path.exists(md_input_folder):
            # Procura o arquivo .md da aula recursivamente
            for root, _, files in os.walk(md_input_folder):
                if md_path: break
                for file in files:
                    if file.startswith(md_filename_prefix) and file.endswith('.md'):
                        md_path = os.path.join(root, file)
                        break

        # Lógica unificada para buscar o link do recurso
        chave_link = (turma_folder.replace('_', 'º '), disciplina_curto, aula_num)
        recurso_link = links_recursos_globais.get(chave_link)

        title, objectives = None, None
        if not md_path:
            print(f"  -> AVISO: Arquivo MD correspondente a '{md_filename_prefix}' não encontrado em '{md_input_folder}' ou subpastas.")
            # Se não há MD, usa o nome da disciplina como título e preenche mesmo assim
            title = disciplina_curto.replace('_', ' ').title()
            objectives = ""
        else:
            title, objectives = parse_md_content(md_path)

        if not title:
            print(f"  -> AVISO: Não foi possível extrair título do MD '{os.path.basename(md_path)}' nem usar um padrão. Pulando.")
            continue
        
        update_plan_file(txt_path, title, objectives, recurso_link)

    print("\nPreenchimento finalizado.")
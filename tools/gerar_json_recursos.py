import os
import re
import json

def parse_links_md(links_path):
    """
    Analisa um arquivo de links em Markdown e retorna um dicionário mapeando
    o número da aula (int) para uma URL (string).
    O padrão esperado é: * [Aula XX](URL)
    """
    links_map = {}
    if not links_path or not os.path.exists(links_path):
        return links_map

    try:
        with open(links_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Padrão regex para encontrar links no formato "* [Aula XX](...)"
        pattern = re.compile(r'^\s*\*\s*\[Aula\s*(\d+)\]\((https?://[^\)]+)\)', re.MULTILINE)
        matches = pattern.findall(content)
        
        for match in matches:
            try:
                aula_num = int(match[0])
                url = match[1]
                links_map[aula_num] = url
            except (ValueError, IndexError):
                continue
            
    except Exception as e:
        print(f"  -> ERRO ao processar o arquivo de links '{os.path.basename(links_path)}': {e}")

    return links_map

def main():
    """
    Script principal para encontrar todos os arquivos de links, extrair os dados
    e gerar o arquivo 'recursos_links.json' centralizado.
    """
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUTS_DIR = os.path.join(PROJECT_ROOT, 'aulas', 'inputs')
    DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
    JSON_OUTPUT_PATH = os.path.join(DATA_DIR, 'recursos_links.json')

    print("\n--- Gerador de JSON de Recursos de Links ---")

    # Carrega o JSON existente para não sobrescrever dados manuais
    if os.path.exists(JSON_OUTPUT_PATH):
        with open(JSON_OUTPUT_PATH, 'r', encoding='utf-8') as f:
            links_globais = json.load(f)
        print(f"Arquivo existente '{JSON_OUTPUT_PATH}' carregado. {len(links_globais)} links encontrados.")
    else:
        links_globais = {}
        print("Nenhum arquivo 'recursos_links.json' existente. Um novo será criado.")

    links_encontrados = 0

    # Navega pela estrutura de pastas: /inputs/{turma}/{disciplina}
    for turma_folder in sorted(os.listdir(INPUTS_DIR)):
        turma_path = os.path.join(INPUTS_DIR, turma_folder)
        if not os.path.isdir(turma_path):
            continue

        for disciplina_folder in sorted(os.listdir(turma_path)):
            disciplina_path = os.path.join(turma_path, disciplina_folder)
            if not os.path.isdir(disciplina_path):
                continue

            # Procura recursivamente por arquivos de links na pasta da disciplina
            for root, _, files in os.walk(disciplina_path):
                for file in files:
                    if (file.startswith('links_mod_') or file.startswith('links_S')) and file.endswith('.md'):
                        caminho_arquivo_link = os.path.join(root, file)
                        print(f"\nAnalisando arquivo de link: {caminho_arquivo_link}")
                        
                        links_extraidos = parse_links_md(caminho_arquivo_link)
                        if not links_extraidos:
                            print("  -> Nenhum link no formato esperado encontrado.")
                            continue

                        # Converte o nome da pasta da turma para o formato do JSON
                        turma_curta_formatada = turma_folder.replace('_', 'º ')

                        for aula_num, url in links_extraidos.items():
                            # A chave é uma string de tupla para ser compatível com JSON
                            chave_json = str((turma_curta_formatada, disciplina_folder, aula_num))
                            
                            # Adiciona ou atualiza o link no dicionário global
                            if chave_json not in links_globais or links_globais[chave_json] != url:
                                print(f"  -> Adicionando/Atualizando link para Aula {aula_num}")
                                links_globais[chave_json] = url
                                links_encontrados += 1

    # Salva o dicionário atualizado de volta no arquivo JSON
    with open(JSON_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(links_globais, f, indent=2, ensure_ascii=False)

    print(f"\nProcesso finalizado. {links_encontrados} novos links foram adicionados/atualizados.")
    print(f"Total de {len(links_globais)} links no arquivo '{JSON_OUTPUT_PATH}'.")

if __name__ == "__main__":
    main()
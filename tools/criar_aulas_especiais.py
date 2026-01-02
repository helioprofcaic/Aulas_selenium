import os

# --- Configuração das Aulas Especiais ---
# Mapeia o número da aula para o título do arquivo .md
# Estes títulos serão usados pelo 'preenchedor_planos.py' para identificar e preencher
# o conteúdo padrão para revisões, avaliações e atividades práticas.
aulas_especiais = {
    33: "# Revisão AV2",
    34: "# Revisão AV2",
    35: "# AV2",
    36: "# Atividades Praticas",
    37: "# Atividades Praticas",
    38: "# Atividades Praticas",
    39: "# Atividades Praticas",
    40: "# Atividades Praticas",
}

def criar_arquivos_md_especiais():
    """
    Cria arquivos .md para aulas especiais (revisões, avaliações, etc.)
    que não possuem um PDF de origem.
    """
    # O diretório 'resumos' é onde os arquivos de aula .md são colocados
    # pelo script 'gerar_aulas_pdf.py'.
    resumos_dir = os.path.join(os.path.dirname(__file__), 'S04', 'resumos')
    os.makedirs(resumos_dir, exist_ok=True)
    print(f"Verificando e criando arquivos de aulas especiais em: {resumos_dir}")

    for numero_aula, titulo_md in aulas_especiais.items():
        nome_arquivo = f"aula_{numero_aula:02d}.md"
        caminho_arquivo = os.path.join(resumos_dir, nome_arquivo)

        if os.path.exists(caminho_arquivo):
            print(f"⏩ Arquivo já existe, pulando: {nome_arquivo}")
            continue

        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(titulo_md)
        print(f"✅ Arquivo de aula especial criado: {nome_arquivo}")

if __name__ == "__main__":
    criar_arquivos_md_especiais()
    print("\nCriação de arquivos para aulas especiais concluída.")
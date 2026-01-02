import os
import markdown
from weasyprint import HTML, CSS
import sys

def converter_md_para_pdf(caminho_arquivo_md):
    """
    Converte um único arquivo Markdown para PDF, aplicando um estilo CSS.
    """
    try:
        print(f"  -> Convertendo: {os.path.basename(caminho_arquivo_md)}")

        # 1. Ler o conteúdo do arquivo Markdown
        with open(caminho_arquivo_md, 'r', encoding='utf-8') as f:
            texto_md = f.read()

        # 2. Converter Markdown para HTML
        html_texto = markdown.markdown(texto_md, extensions=['fenced_code', 'tables'])

        # 3. Definir um estilo CSS para deixar o PDF mais legível e profissional
        # Este CSS pode ser customizado como você preferir.
        estilo_css = """
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        h1, h2, h3 {
            font-family: 'Segoe UI Light', Arial, sans-serif;
            color: #005a9e;
            border-bottom: 2px solid #005a9e;
            padding-bottom: 5px;
            margin-top: 24px;
        }
        h1 { font-size: 24pt; }
        h2 { font-size: 18pt; }
        h3 { font-size: 14pt; }
        strong {
            color: #000;
        }
        code {
            font-family: 'Consolas', 'Courier New', monospace;
            background-color: #f0f0f0;
            padding: 2px 5px;
            border-radius: 4px;
            font-size: 0.9em;
        }
        pre {
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
            white-space: pre-wrap; /* Quebra de linha no código */
        }
        """

        # 4. Gerar o PDF a partir do HTML e CSS
        caminho_arquivo_pdf = os.path.splitext(caminho_arquivo_md)[0] + '.pdf'
        HTML(string=html_texto).write_pdf(caminho_arquivo_pdf, stylesheets=[CSS(string=estilo_css)])

        print(f"     -> PDF salvo em: {os.path.basename(caminho_arquivo_pdf)}")
        return True

    except Exception as e:
        print(f"     -> ERRO ao converter '{os.path.basename(caminho_arquivo_md)}': {e}")
        return False

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUTS_DIR = os.path.join(PROJECT_ROOT, 'aulas', 'inputs')
    print(f"--- Iniciando conversão de Markdown para PDF na pasta: {INPUTS_DIR} ---")
    for root, _, files in os.walk(INPUTS_DIR):
        for file in files:
            if file.endswith('.md'):
                caminho_completo = os.path.join(root, file)
                converter_md_para_pdf(caminho_completo)
    print("\n--- Conversão concluída. ---")
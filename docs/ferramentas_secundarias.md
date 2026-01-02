# 🛠️ Ferramentas Secundárias e Utilitários

Além do fluxo principal de automação, a pasta `tools/` contém diversos scripts utilitários projetados para tarefas específicas de análise, gestão de conteúdo e manutenção.

Este guia explica o propósito e o uso de cada um.

## 📊 Análise e Relatórios

### `analisador_de_grade.py`
*   **Função:** Gera um relatório detalhado no terminal comparando as horas registradas versus a carga horária obrigatória de cada disciplina.
*   **Quando usar:** Para saber exatamente quantas aulas faltam para completar a grade de uma turma específica.
*   **Uso:** Executado automaticamente pela **Opção 2** do menu principal, ou via terminal:
    ```bash
    python tools/analisador_de_grade.py
    ```

### `ver_aulas_por_disciplina.py`
*   **Função:** Oferece um menu interativo para visualizar estatísticas das aulas já coletadas (arquivo `aulas_coletadas.json`).
*   **Modos de Visualização:**
    1.  Por Disciplina (contagem total).
    2.  Por Turma.
    3.  Por Data (útil para verificar dias com muitas aulas).
*   **Uso:**
    ```bash
    python tools/ver_aulas_por_disciplina.py
    ```

### `utils_files.py` (Exportar CSV)
*   **Função:** Converte o banco de dados JSON (`aulas_coletadas.json`) para um arquivo Excel/CSV (`aulas_coletadas.csv`).
*   **Quando usar:** Se você quiser abrir seus dados no Excel para criar gráficos ou relatórios personalizados.
*   **Uso:**
    ```bash
    python tools/utils_files.py
    ```

---

## 📝 Gestão de Conteúdo Didático

### `gerar_json_recursos.py`
*   **Função:** Varre todos os arquivos Markdown (`.md`) na pasta `aulas/inputs/`, procura por links de materiais (ex: `* Aula 01`) e cria um índice centralizado em `data/recursos_links.json`.
*   **Por que é importante:** O script de preenchimento usa esse índice para inserir automaticamente os links dos slides/PDFs nos planos de aula.
*   **Uso:** Execute sempre que adicionar novos links nos seus resumos.
    ```bash
    python tools/gerar_json_recursos.py
    ```

### `converter_md_para_pdf.py`
*   **Função:** Converte seus resumos de aula em Markdown para arquivos PDF formatados profissionalmente.
*   **Requisito:** Requer a biblioteca `weasyprint` e `markdown`.
*   **Uso:**
    ```bash
    python tools/converter_md_para_pdf.py
    ```

### `criar_aulas_especiais.py`
*   **Função:** Cria arquivos `.md` de placeholder para aulas que não possuem conteúdo teórico tradicional, como "Revisão AV1", "Prova", "Atividades Práticas".
*   **Configuração:** Edite o dicionário `aulas_especiais` dentro do script para definir quais aulas devem ser criadas.

---

## 🚀 Planejamento Avançado

### `planejador_online.py`
*   **Função:** Uma versão mais robusta do `preparar_planos.py`.
*   **Diferencial:** Antes de gerar os planos, ele conecta no portal da Seduc e verifica se as aulas que constam como "Aguardando confirmação" no seu computador já foram aceitas ou rejeitadas.
*   **Quando usar:** Se você trabalha em múltiplos computadores ou se a coordenação costuma alterar o status das suas aulas com frequência.
*   **Uso:**
    ```bash
    python tools/planejador_online.py
    ```

### `setup_wizard.py` (Assistente de Configuração)
*   **Função:** Resolve o problema da "tela em branco".
    1.  Gera arquivos JSON de exemplo em `data/` com a estrutura correta preenchida.
    2.  Lê suas configurações e cria automaticamente a árvore de pastas em `aulas/inputs/` para você colocar seus materiais.
*   **Quando usar:** Na primeira vez que instalar o projeto ou quando adicionar novas turmas.
*   **Uso:**
    ```bash
    python tools/setup_wizard.py
    ```

---

## 🧪 Experimentais

*   **`gerar_aulas_modelo.py`**: Um script esboço para integração futura com IA (Gemini) para gerar conteúdo de aulas do zero. Ainda em desenvolvimento.
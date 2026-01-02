# 🤖 Documentação: Assistente de Automação de Aulas

Este documento detalha o funcionamento dos componentes principais do projeto, que automatizam a coleta, preparação e registro de aulas.

## Fluxo de Trabalho Geral

O processo completo é dividido em várias fases, projetadas para serem executadas em sequência:

1.  **Coleta (`scraper.py`)**: O robô acessa o portal da Seduc, faz login e extrai todos os registros de aulas **já existentes**. Isso cria uma base de dados atualizada do que já foi feito, salvando tudo em `data/aulas_coletadas.json`.

2.  **Análise (`analisador_de_grade.py`)**: Este script lê os dados coletados e os compara com o seu cronograma (`horarios_semanais_oficial.json` e `calendario_letivo.json`). Ele gera um relatório no console mostrando o status de cada disciplina (quantas aulas foram dadas vs. a meta) e identifica qual a próxima disciplina a ser planejada para cada turma.

3.  **Preparação (`preparar_planos.py`)**: Com base na análise anterior, este script inteligente encontra os próximos horários vagos no calendário (pulando feriados e fins de semana) para a disciplina que precisa ser planejada. Ele então cria arquivos de texto "esqueleto" (`.txt`) na pasta `aulas/`, um para cada aula futura.

4.  **Preenchimento (`preenchedor_planos.py`)**: Este assistente automatiza a tarefa de preencher os planos. Ele lê os arquivos `.txt` gerados, encontra os materiais de aula correspondentes (`.md`) na pasta `aulas/inputs/` e preenche automaticamente os blocos `[CONTEUDO]`, `[ESTRATEGIA]` e `[RECURSO_LINK]`.

5.  **Validação (`validar_planos.ipynb`)**: Um notebook Jupyter que serve como um painel de controle para você revisar visualmente todos os planos de aula que estão prontos para serem registrados, garantindo que nenhum plano incompleto seja enviado.

6.  **Registro (`registrar_aulas.py`)**: O robô final. Ele lê os arquivos `.txt` preenchidos e validados, acessa o portal e cadastra cada aula, uma por uma, de forma totalmente automática. Se o registro for bem-sucedido, o arquivo `.txt` é excluído para evitar duplicidade.

Adicionalmente, o `analise_aulas.ipynb` pode ser usado a qualquer momento para validar a coleta e entender o panorama geral dos registros.

---

## 1. `scraper.py` - O Coletor de Dados

Este script utiliza a biblioteca **Selenium** para automatizar um navegador Chrome, simulando as ações de um usuário para coletar dados de forma estruturada.

### Funcionalidades Principais

-   **Inicialização e Login**: Configura o navegador e realiza o login no portal usando as credenciais fornecidas.
-   **Navegação Inteligente**: Seleciona o perfil de "Professor" e a instituição correta, lidando com a complexidade de `iframes` (páginas dentro de páginas).
-   **Mapeamento de Turmas**: Utiliza arquivos JSON para traduzir os nomes "curtos" das turmas (ex: `1º DS`) para os nomes completos encontrados no portal (ex: `EMI-INT CT DES SIST-1ª SÉRIE -I-A`).
-   **Coleta Cíclica**:
    1.  Itera sobre cada turma e, dentro dela, sobre cada disciplina associada.
    2.  Clica em "Registro de aulas" para cada disciplina.
    3.  Acessa a tabela de aulas registradas.
-   **Paginação**: Uma vez na tabela, o scraper navega por todas as páginas de resultados, clicando no botão "Próxima" até que não haja mais páginas, garantindo que **todos** os registros sejam coletados.
-   **Tratamento de Erros**: Tira screenshots automaticamente em caso de falhas e possui mecanismos para tentar se recuperar de erros de navegação.

### Estrutura de Arquivos Necessária

Para que o `scraper.py` funcione, os seguintes arquivos devem estar corretamente configurados no diretório `data/`:

-   `config.json`: Contém o nome do professor para o qual os dados serão coletados.
    ```json
    {
      "professor": "Nome Sobrenome"
    }
    ```
-   `credentials.json`: Armazena o usuário e a senha de acesso ao portal.
    ```json
    {
      "username": "seu_usuario",
      "password": "sua_senha"
    }
    ```
-   `horarios_semanais_oficial.json`: Define quais turmas pertencem ao professor. O scraper lê as chaves dentro do objeto do professor (ex: "1º DS", "1º PJ").
-   `mapa_turmas.json`: O "dicionário" que traduz o nome completo da turma (chave) para o nome curto (valor). Essencial para a navegação.
    ```json
    {
      "EMI-INT CT DES SIST-1ª SÉRIE -I-A": "1º DS",
      "ENS FUND II-9º ANO-I-B": "9º B"
    }
    ```
-   `turmas_com_disciplinas.json`: Mapeia o nome completo da turma às suas respectivas disciplinas.

### Como Executar

1.  Certifique-se de que todos os arquivos de configuração acima estão preenchidos.
2.  Abra o terminal na raiz do projeto (`B:\Dev\Aulas_pygui>`).
3.  Ative o ambiente virtual: `.venv\Scripts\activate`.
4.  Execute o script:
    ```shell
    python tools/scraper.py
    ```
5.  Ao final, o arquivo `data/aulas_coletadas.json` será criado ou atualizado com os dados coletados.

---

## 2. `analise_aulas.ipynb` - O Painel de Análise

Este é um Jupyter Notebook que serve como um dashboard interativo para explorar os dados coletados pelo scraper. Ele utiliza as bibliotecas **Pandas** para manipulação de dados e **Plotly** para visualização.

### Análises Geradas

1.  **Carregamento e Limpeza**:
    -   Lê o arquivo `aulas_coletadas.json`.
    -   Converte as colunas de data para um formato que permite análises temporais.

2.  **Estatísticas Gerais**:
    -   **Aulas por Disciplina**: Um gráfico de barras que mostra o total de aulas coletadas para cada disciplina. É a ferramenta mais importante para identificar falhas na coleta (ex: uma disciplina com muito menos aulas que as outras).
    -   **Aulas por Turma**: Um gráfico de pizza que mostra a proporção de aulas por turma.
    -   **Aulas ao Longo do Tempo**: Um gráfico de barras que agrupa as aulas por mês, ajudando a visualizar a distribuição ao longo do ano letivo.

3.  **Análise Detalhada**:
    -   **Tabela Cruzada e Mapa de Calor**: Mostra a quantidade exata de aulas coletadas para cada disciplina dentro de cada turma. É ideal para encontrar "buracos" específicos na coleta.

### Como Utilizar

1.  Certifique-se de que o `scraper.py` já foi executado e o arquivo `data/aulas_coletadas.json` existe.
2.  No terminal, com o ambiente virtual ativado, instale as dependências para análise:
    ```shell
    pip install notebook pandas plotly nbformat
    ```
3.  Inicie o servidor Jupyter:
    ```shell
    jupyter notebook
    ```
4.  Seu navegador abrirá uma nova aba. Navegue até `tools/` e clique em `analise_aulas.ipynb`.
5.  Dentro do notebook, você pode executar cada célula de código para gerar as tabelas e gráficos. Use o menu "Cell" > "Run All" para executar tudo de uma vez.

### Investigando Problemas

Se a análise revelar que o número de aulas coletadas (ex: 704) é menor que o esperado (ex: 780), use os gráficos para responder às seguintes perguntas:

-   **Qual disciplina tem menos aulas?** O gráfico de "Aulas por Disciplina" mostrará isso claramente.
-   **A coleta falhou em um mês específico?** O gráfico de "Distribuição por Mês" pode indicar isso.

Com essas informações, você pode focar a investigação, por exemplo, rodando o `scraper.py` novamente para uma única disciplina e observando o console em busca de erros de paginação ou `Timeout`.
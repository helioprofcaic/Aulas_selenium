# 🚀 Tutorial Completo: Do Planejamento ao Registro de Aulas

Este guia detalha o fluxo de trabalho completo para automatizar o registro de suas aulas, usando a suíte de scripts de automação. O processo foi dividido em três etapas principais, cada uma com seu próprio script, para garantir controle e flexibilidade.

## O Fluxo em 3 Passos

O processo completo segue a ordem:

1.  **Preparar**: O script `preparar_planos.py` analisa sua grade e o calendário para determinar quais aulas precisam ser planejadas. Ele cria os "esqueletos" dos planos de aula.
2.  **Preencher**: O script `preenchedor_planos.py` pega esses esqueletos e os preenche automaticamente com o conteúdo dos seus materiais de aula.
3.  **Registrar**: O script `registrar_aulas.py` usa os planos preenchidos para automatizar o registro no portal da Seduc.

---

## Passo 1: `preparar_planos.py` - O Planejador Inteligente

Este é o ponto de partida. A função deste script é olhar para o futuro e preparar o terreno para as próximas aulas.

### O que ele faz?

-   **Analisa o Cenário Atual**: Ele lê o arquivo `data/aulas_coletadas.json` (que contém todas as aulas que você já registrou) para saber onde parou em cada disciplina.
-   **Consulta o Calendário e Horários**: Ele verifica seu horário semanal (`horarios_semanais_oficial.json`) e o calendário letivo (`calendario_letivo.json`) para encontrar as próximas datas e horários disponíveis para cada disciplina, pulando feriados e fins de semana.
-   **Cria os Esqueletos**: Com base nessa análise, ele gera arquivos de texto (`.txt`) vazios na pasta `aulas/`, organizados por turma. Cada arquivo representa uma aula futura e já contém o cabeçalho com data, horário e número da aula.

### Como Executar

1.  Abra um terminal na raiz do projeto (`B:\Dev\Aulas_selenium`).
2.  Ative seu ambiente virtual (se aplicável): `.venv\Scripts\activate`.
3.  Execute o comando:
    ```shell
    python tools/preparar_planos.py
    ```
4.  O script mostrará um resumo de quantas aulas serão geradas e pedirá sua confirmação (`s/n`). Digite `s` e pressione Enter.

> **Resultado**: A pasta `aulas/` será populada com subpastas para cada turma, contendo os arquivos `.txt` prontos para a próxima etapa.

---

## Passo 2: `preenchedor_planos.py` - O Assistente de Conteúdo

Agora que os "esqueletos" estão criados, este script faz o trabalho de preenchê-los com o conteúdo real da aula.

### O que ele faz?

-   **Encontra Planos Pendentes**: Ele varre a pasta `aulas/` em busca de arquivos `.txt` que ainda contenham a marcação "Preencher".
-   **Busca o Material de Aula**: Para cada plano pendente, ele localiza o material de aula correspondente (arquivos `.md`) dentro da pasta `aulas/inputs/`. Ele é inteligente o suficiente para associar `METODOS_AGEIS_20250417.txt` com o material da aula 28 de Métodos Ágeis.
-   **Preenche Automaticamente**: Ele extrai o título, os objetivos e os links dos arquivos `.md` e os insere nos campos `[CONTEUDO]`, `[ESTRATEGIA]`, `[RECURSO_TITULO]`, `[RECURSO_LINK]` e `[RECURSO_COMENTARIO]` do arquivo `.txt`.

### Como Executar

1.  No mesmo terminal, execute o comando:
    ```shell
    python tools/preenchedor_planos.py
    ```
2.  Um menu interativo aparecerá, listando todas as disciplinas que têm planos pendentes.
3.  Você pode escolher preencher uma disciplina específica (digitando o número correspondente) ou todas de uma vez (digitando a opção "Processar todas").

> **Resultado**: Os arquivos `.txt` na pasta `aulas/` agora estarão completamente preenchidos e prontos para o registro.

---

## Passo 3: `registrar_aulas.py` - O Robô de Registro

Esta é a etapa final, onde a mágica acontece. O robô assume o controle e registra as aulas no portal.

### O que ele faz?

-   **Lê os Planos Prontos**: Ele encontra todos os arquivos `.txt` que foram preenchidos na etapa anterior.
-   **Automatiza o Navegador**: Usando Selenium, ele abre o navegador Chrome, faz o login no portal da Seduc e navega até a página de registro de cada turma/disciplina.
-   **Preenche o Formulário Web**: Para cada aula, ele preenche todos os campos do formulário online (data, conteúdo, estratégia, recursos) com as informações do arquivo `.txt`.
-   **Pausa para Ação Manual**: O script fará uma pausa e pedirá que você **selecione manualmente o horário da aula** na lista. Isso é necessário porque a lista de horários é dinâmica e depende da data selecionada.
-   **Confirma e Finaliza**: Após sua intervenção, ele continua o processo, salva o registro e avança para a próxima aula.

### Como Executar

1.  No terminal, execute o comando:
    ```shell
    python tools/registrar_aulas.py
    ```
2.  O script listará a primeira aula a ser registrada e pedirá sua confirmação (`s` para registrar, `n` para pular, `parar` para encerrar).
3.  Ao digitar `s`, o navegador será aberto e o processo de automação começará. Fique atento ao terminal para a solicitação de seleção do horário.

### Medidas de Segurança

-   **Confirmação Individual**: Ele pede permissão antes de registrar cada aula.
-   **Tratamento de Falhas**: Se um registro falhar, um *screenshot* do erro é salvo na pasta `screenshots/`, e o arquivo `.txt` **não é apagado**, permitindo que você tente novamente mais tarde.
-   **Limpeza Automática**: Se um registro for bem-sucedido, o arquivo `.txt` correspondente é automaticamente excluído para evitar registros duplicados.

---

## Resumo Rápido dos Comandos

```shell
# 1. Criar os planos de aula vazios
python tools/preparar_planos.py

# 2. Preencher os planos com o conteúdo das aulas
python tools/preenchedor_planos.py

# 3. Iniciar o robô para registrar as aulas preenchidas
python tools/registrar_aulas.py
```

Seguindo estes três passos, você pode manter seus registros de aula sempre em dia com o mínimo de esforço manual.
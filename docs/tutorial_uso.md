# 📖 Tutorial de Uso: Assistente de Aulas

Este guia explica como utilizar a interface gráfica do Assistente de Aulas para automatizar sua rotina, desde a coleta de dados até o registro no portal.

## 1. Iniciando o Aplicativo

1.  Abra a pasta do projeto.
2.  Certifique-se de que seu ambiente virtual está ativo (se estiver rodando via terminal) ou que você configurou o Python corretamente.
3.  Execute o arquivo `app.py`:
    ```bash
    python app.py
    ```
4.  A janela **"Painel de Controle do Professor"** será aberta.

---

## 2. O Fluxo de Trabalho

O sistema foi desenhado para funcionar em 4 etapas sequenciais. Recomenda-se seguir a ordem dos botões na interface.

### Passo 1: Atualizar Dados (Scraper) 📥
*   **O que faz:** O robô entra no portal da Seduc, navega por todas as suas turmas e baixa o histórico do que **já foi registrado**.
*   **Por que usar:** Isso evita que o sistema tente registrar aulas duplicadas ou em dias que você já preencheu manualmente.
*   **Resultado:** Atualiza o arquivo `data/aulas_coletadas.json`.
*   **Tempo estimado:** 2 a 5 minutos (depende da velocidade do portal).

### Passo 2: Planejar Aulas 🗓️
*   **O que faz:** Analisa sua grade horária (`horarios_semanais_oficial.json`) e o calendário letivo. Ele identifica os "buracos" futuros e cria arquivos de texto vazios (esqueletos) na pasta `aulas/`.
*   **Exemplo:** Se você tem aula de "Matemática" na próxima segunda-feira, ele cria um arquivo `2023-10-23_Matematica_TurmaA.txt`.
*   **Ação do Professor:** Após rodar este passo, você pode verificar a pasta `aulas/` para ver os arquivos criados.

### Passo 3: Preencher Conteúdos 📝
*   **O que faz:** Esta é a mágica. O sistema lê os arquivos "esqueletos" criados no passo anterior e procura conteúdo correspondente na pasta `aulas/inputs/`.
*   **Como funciona:** Se o esqueleto pede a "Aula 05" de "História", o sistema busca nos seus materiais (PDFs, Markdowns) o conteúdo dessa aula e preenche automaticamente os campos:
    *   Conteúdo Programático
    *   Estratégia Metodológica
    *   Recursos
*   **Resultado:** Os arquivos `.txt` na pasta `aulas/` agora estão completos e prontos para envio.

### Passo 4: Registrar no Portal 🚀
*   **O que faz:** O robô abre o navegador, faz login e começa a lançar as aulas que estão prontas na pasta `aulas/`.
*   **Importante:**
    *   Não mexa no mouse ou teclado enquanto o robô trabalha (a menos que ele peça).
    *   Acompanhe o progresso na área de "Logs" da janela do aplicativo.
*   **Sucesso:** Quando uma aula é registrada com sucesso, o arquivo `.txt` correspondente é movido/deletado da pasta de pendências.

---

## 3. Dicas e Solução de Problemas

*   **O aplicativo travou?**
    A interface gráfica roda os processos em segundo plano. Se parecer travada, verifique a janela de "Logs". Se houver um erro vermelho, leia a mensagem para entender o que houve (geralmente é senha errada ou portal fora do ar).

*   **Preciso parar o robô!**
    Feche a janela do aplicativo ou o terminal preto que se abriu junto com o navegador.

*   **Modo Texto (CLI)**
    Se preferir usar o teclado, você pode rodar `python app.py --cli` para ver um menu numérico simples no terminal.

## 4. Organização das Pastas

*   Coloque seus materiais de aula em: `aulas/inputs/SuaTurma/SuaDisciplina/`.
*   Verifique os planos gerados em: `aulas/`.
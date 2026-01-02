# 🏗️ Arquitetura Técnica do Projeto

Este documento descreve a estrutura de software, as decisões de design e o fluxo de dados do projeto **Assistente de Aulas**.

## Visão Geral

O projeto é uma aplicação Python modular que utiliza automação de navegador (Selenium) e processamento de texto para gerenciar registros escolares. A arquitetura segue uma separação clara entre **Interface (Frontend)**, **Lógica de Negócio (Tools)** e **Dados**.

## Estrutura de Diretórios

```text
Aulas_selenium/
├── app.py                  # Entry Point (Padrão Facade/Âncora)
├── interfaces/             # Camada de Apresentação
│   ├── gui_app.py          # Interface Gráfica (Tkinter)
│   └── cli_menu.py         # Interface de Linha de Comando
├── tools/                  # Camada de Lógica de Negócio (Scripts Independentes)
│   ├── scraper.py          # Coleta de dados (Selenium)
│   ├── preparar_planos.py  # Lógica de calendário e geração de arquivos
│   ├── registrar_aulas.py  # Automação de input (Selenium)
│   └── ...
├── core/                   # Bibliotecas Compartilhadas
│   └── gemini_client.py    # Integração com LLMs
├── data/                   # Camada de Persistência (JSON/Flat files)
└── aulas/                  # Área de Staging (Arquivos de trabalho)
```

## Componentes Principais

### 1. Âncora (`app.py`)
Atua como o ponto de entrada único. Sua função é detectar o ambiente e decidir qual interface carregar.
*   Configura o `PYTHONPATH` e o diretório de trabalho (`CWD`) para garantir que as importações relativas funcionem.
*   Trata exceções de inicialização da GUI (ex: falta de display no Linux) e faz *fallback* para CLI.

### 2. Interfaces (`interfaces/`)
A camada de apresentação é desacoplada da lógica.
*   **GUI (`gui_app.py`)**: Utiliza `tkinter` (nativo do Python). Implementa *Threading* para executar os scripts da pasta `tools/` sem congelar a interface. Captura `stdout` e `stderr` dos subprocessos para exibir logs em tempo real na janela.
*   **CLI (`cli_menu.py`)**: Um loop simples de menu para execução rápida em terminais.

### 3. Ferramentas (`tools/`)
Cada script nesta pasta é uma unidade lógica independente que pode ser executada isoladamente.
*   **Design Pattern**: Scripts de execução direta. Eles não dependem da interface para funcionar, apenas dos arquivos de configuração em `data/`.
*   **Comunicação**: A comunicação entre as ferramentas ocorre via sistema de arquivos (JSONs em `data/` e TXTs em `aulas/`).
    *   *Exemplo*: O `scraper.py` escreve em `aulas_coletadas.json`, que é lido pelo `analisador_de_grade.py`.

### 4. Persistência de Dados
O projeto não utiliza banco de dados relacional (SQL) para manter a portabilidade e simplicidade.
*   **Configuração**: Arquivos JSON (`config.json`, `credentials.json`).
*   **Estado**: O estado do sistema é determinado pela presença ou ausência de arquivos na pasta `aulas/`. Se um arquivo `.txt` existe, é uma aula pendente. Se não existe, foi registrada.

## Fluxo de Execução (Pipeline)

1.  **Usuário** aciona `app.py`.
2.  **Interface** chama `subprocess.Popen(['python', 'tools/script.py'])`.
3.  **Tool** carrega configurações de `data/`.
4.  **Tool** executa lógica (ex: Selenium abre Chrome).
5.  **Tool** lê/escreve em `aulas/` ou `data/`.
6.  **Interface** captura o output e mostra ao usuário.

## Decisões Técnicas

### Por que `subprocess` em vez de importar módulos?
Optou-se por executar as ferramentas via `subprocess` na interface gráfica por dois motivos:
1.  **Isolamento de Memória**: O Selenium consome muita memória e pode ter vazamentos (leaks). Ao rodar em um processo separado, o SO limpa toda a memória quando o script termina, mantendo a interface leve.
2.  **Estabilidade**: Se o script de automação falhar (crash), ele não derruba a interface principal.

### Por que arquivos de texto para planos de aula?
Para permitir que o professor edite manualmente o plano antes do envio, se desejar. Arquivos `.txt` são universais e fáceis de debugar.

## Guia para Desenvolvedores

Para adicionar uma nova funcionalidade:
1.  Crie o script lógico em `tools/nova_funcionalidade.py`.
2.  Garanta que ele leia as configs de `data/` e funcione via terminal.
3.  Adicione um botão em `interfaces/gui_app.py` apontando para esse script.
4.  Adicione uma entrada no menu de `interfaces/cli_menu.py`.

---
*Documento atualizado em: Janeiro/2026*
# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.0.0] - 2025-01-02

### 🚀 Lançamento Oficial: Assistente de Registro Seduc-PI

Primeira versão estável da ferramenta de automação para o Portal Seduc-PI.

### 🎯 Escopo Definido
- Foco total na **automação de registro** (interação com o portal).
- A geração de conteúdo pedagógico via IA foi removida do escopo principal; a ferramenta agora processa inputs fornecidos pelo professor.

### ✨ Funcionalidades
- **Interface Gráfica (GUI):** Painel de controle visual com Tkinter.
- **Scraper (Coleta):** Baixa histórico de aulas para evitar duplicidade.
- **Planejador:** Gera arquivos `.txt` (esqueletos) baseados na grade horária e calendário letivo.
- **Registrador:** Robô Selenium que preenche os formulários no portal automaticamente.
- **Suporte a CLI:** Modo de linha de comando (`--cli`) para servidores ou execução rápida.

### 📦 Estrutura
- Sistema de pastas `aulas/inputs` para organização de material.
- Scripts modulares em `tools/`.
- Configuração via `data/config.json` e `data/credentials.json`.
- Suporte a empacotamento via PyInstaller.


## [1.1.0] - 2025-01-04
### Adicionado
- Nova Interface Gráfica para Estatísticas (`gui_stats.py`).
- Nova Interface Gráfica para Preenchimento de Planos (`gui_preenchedor.py`).
- Suporte a codificação UTF-8-SIG para maior compatibilidade com Windows.

### Corrigido
- Correção de dependências ocultas no PyInstaller (`pandas`, `weasyprint`, `tinycss2`).
- Correção no `setup_wizard.py` para não sobrescrever o nome do professor ao regenerar modelos.
- Correção de encoding na leitura de arquivos JSON em todas as ferramentas.
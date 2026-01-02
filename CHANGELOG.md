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
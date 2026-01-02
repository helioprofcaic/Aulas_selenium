import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import os
import sys
import subprocess
import threading
import json
import re
# --- Bloco de Resiliência de Importação ---
# Permite que o script seja executado diretamente (python interfaces/gui_app.py)
# ou como um módulo importado (por app.py).
try:
    from interfaces.assets import get_icon
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from interfaces.assets import get_icon


class AppAutomação:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Assistente")
        # Configuração para ocupar ~25% da tela 720p (aprox 340px largura) e ficar à esquerda
        self.root.geometry("400x720+0+0")
        self.root.configure(bg="#f0f4f8") # Fundo Azul-Cinza muito suave

        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        
        # Paleta de Cores "Bluish Tone"
        bg_color = "#f0f4f8"       # Fundo da janela
        primary_blue = "#0077b6"   # Azul principal (texto botões/ícones)
        dark_blue = "#023e8a"      # Azul escuro (títulos)
        hover_blue = "#e0f2fe"     # Azul claro (hover)
        text_gray = "#486581"      # Cinza azulado (descrições)

        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, font=('Segoe UI', 9), foreground=text_gray)
        
        # Botões com estilo "Card" (Branco com texto Azul)
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=8, background="#ffffff", foreground=primary_blue, borderwidth=1, bordercolor="#bcccdc", focuscolor=hover_blue)
        style.map('TButton', background=[('active', hover_blue)], foreground=[('active', dark_blue)], bordercolor=[('active', primary_blue)])
        
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), background=bg_color, foreground=dark_blue)
        style.configure('Desc.TLabel', font=('Segoe UI', 8), background=bg_color, foreground=text_gray)
        style.configure('TLabelframe', background=bg_color, bordercolor="#bcccdc")
        style.configure('TLabelframe.Label', background=bg_color, foreground=dark_blue, font=('Segoe UI', 9, 'bold'))

        # --- Layout Dividido (70% / 30%) ---
        # Container Superior (Header + Botões)
        top_container = ttk.Frame(root)
        top_container.place(relx=0, rely=0, relwidth=1.0, relheight=0.7)

        # Container Inferior (Logs)
        bottom_container = ttk.Frame(root)
        bottom_container.place(relx=0, rely=0.7, relwidth=1.0, relheight=0.3)

        # Cabeçalho
        header_frame = ttk.Frame(top_container, padding="10")
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Painel do Professor", style='Header.TLabel').pack(anchor='w')
        ttk.Label(header_frame, text="Automação de Aulas", style='Desc.TLabel').pack(anchor='w')

        # Botões de Ação
        btn_frame = ttk.Frame(top_container, padding="5")
        btn_frame.pack(fill=tk.BOTH, expand=True)

        self.criar_botao(btn_frame, "1. Atualizar Dados", 
                         "Baixa os registros atuais do portal.", 
                         "scraper.py", 0, icon_name="scraper")
        
        self.criar_botao(btn_frame, "2. Planejar Aulas", 
                         "Gera arquivos de plano vazios.", 
                         "preparar_planos.py", 1, icon_name="planejamento")
        
        self.criar_botao(btn_frame, "3. Preencher Conteúdos", 
                         "Insere conteúdo nos planos.", 
                         "preenchedor_planos.py", 2, icon_name="preenchimento")
        
        self.criar_botao(btn_frame, "4. Registrar no Portal", 
                         "Lança as aulas no sistema.", 
                         "registrar_aulas.py", 3, icon_name="registro")
        
        self.criar_botao(btn_frame, "5. Configurações", 
                         "Assistente de configuração inicial.", 
                         "WIZARD", 4, icon_name="config")

        # Área de Log/Console
        log_frame = ttk.LabelFrame(bottom_container, text="Log de Execução", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.log_area = scrolledtext.ScrolledText(log_frame, height=8, state='disabled', font=('Consolas', 8))
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.configure(bg="#ffffff", fg="#486581", relief="flat", highlightthickness=0, padx=5, pady=5)

        # Botão Sair
        # ttk.Button(root, text="Sair", command=root.quit).pack(pady=5) # Removido para limpar visual

        # Verificação inicial de credenciais
        self.root.after(1000, self.verificar_credenciais)

    def criar_botao(self, parent, texto, descricao, script, row, icon_name=None):
        # Frame container para o "Card" do botão
        frame = ttk.Frame(parent, padding="0")
        frame.pack(fill=tk.X, pady=2)
        
        # Carrega o ícone se fornecido
        image = None
        if icon_name:
            image = get_icon(icon_name, tamanho=(32, 32))

        # Botão principal ocupando toda a largura
        if script == "WIZARD":
            btn = ttk.Button(frame, text=f" {texto}", command=self.abrir_wizard, image=image, compound="left")
        else:
            btn = ttk.Button(frame, text=f" {texto}", command=lambda: self.iniciar_script(script), image=image, compound="left")
        
        btn.pack(fill=tk.X, ipady=2)
        
        # Descrição logo abaixo, discreta
        lbl = ttk.Label(frame, text=descricao, style='Desc.TLabel', wraplength=300)
        lbl.pack(fill=tk.X, padx=2, pady=(1, 3))

    def log(self, mensagem):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, mensagem + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def obter_raiz(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def abrir_wizard(self):
        WizardDialog(self.root, self)

    def iniciar_script(self, script_name):
        # Executa em uma thread separada para não travar a interface
        thread = threading.Thread(target=self.executar_processo, args=(script_name,))
        thread.start()

    def executar_processo(self, script_name):
        raiz = self.obter_raiz()
        caminho_script = os.path.join(raiz, 'tools', script_name)
        
        self.log("-" * 40)
        self.log(f"Iniciando: {script_name}...")
        
        try:
            # No Windows, precisamos configurar o startupinfo para esconder a janela do console extra
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen(
                [sys.executable, caminho_script],
                cwd=raiz,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                startupinfo=startupinfo
            )

            # Ler a saída em tempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())
            
            # Capturar erros se houver
            stderr = process.stderr.read()
            if stderr:
                self.log(f"ERRO: {stderr}")

            if process.returncode == 0:
                self.log(f"✅ {script_name} finalizado com sucesso.")
                messagebox.showinfo("Sucesso", f"O script {script_name} foi concluído.")
            else:
                self.log(f"❌ {script_name} finalizado com erros.")
                messagebox.showerror("Erro", f"Ocorreu um erro ao executar {script_name}.")

        except Exception as e:
            self.log(f"Erro crítico: {str(e)}")
            messagebox.showerror("Erro Crítico", str(e))

    def verificar_credenciais(self):
        raiz = self.obter_raiz()
        creds_path = os.path.join(raiz, 'data', 'credentials.json')
        
        abrir_wizard = False
        if not os.path.exists(creds_path):
            abrir_wizard = True
        else:
            try:
                with open(creds_path, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    # Verifica se são os dados de exemplo ou vazios
                    if dados.get('username') in ["12345678900", "seu_usuario", ""] or dados.get('password') in ["senha_secreta", "sua_senha", ""]:
                        abrir_wizard = True
            except:
                pass
        
        if abrir_wizard:
            if messagebox.askyesno("Configuração Inicial", "Suas credenciais de acesso (CPF/Senha) parecem não estar configuradas.\n\nO robô precisa delas para funcionar.\nDeseja abrir o Assistente para configurá-las agora?"):
                self.abrir_wizard()

class MarkdownViewer(tk.Toplevel):
    """Visualizador simples de Markdown nativo em Tkinter."""
    def __init__(self, parent, title, file_path):
        super().__init__(parent)
        self.title(title)
        self.geometry("700x600")
        self.configure(bg="#ffffff")

        # Configuração da área de texto
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Segoe UI", 10), padx=20, pady=20, bd=0)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Tags de formatação (Estilo visual do Markdown)
        self.text_area.tag_config("h1", font=("Segoe UI", 20, "bold"), foreground="#023e8a", spacing1=15, spacing3=5)
        self.text_area.tag_config("h2", font=("Segoe UI", 16, "bold"), foreground="#0077b6", spacing1=10, spacing3=5)
        self.text_area.tag_config("h3", font=("Segoe UI", 12, "bold"), foreground="#486581", spacing1=5)
        self.text_area.tag_config("bold", font=("Segoe UI", 10, "bold"))
        self.text_area.tag_config("bullet", lmargin1=20, lmargin2=30)
        self.text_area.tag_config("code", font=("Consolas", 9), background="#f5f5f5", foreground="#d63384")
        self.text_area.tag_config("normal", font=("Segoe UI", 10))

        self.load_file(file_path)
        self.text_area.configure(state='disabled') # Apenas leitura

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            in_code = False
            for line in lines:
                line_strip = line.strip()
                if line_strip.startswith('```'):
                    in_code = not in_code
                    continue
                
                if in_code:
                    self.text_area.insert(tk.END, line, "code")
                else:
                    self.parse_line(line)
        except Exception as e:
            self.text_area.insert(tk.END, f"Erro ao ler arquivo: {e}")

    def parse_line(self, line):
        if line.startswith('# '):
            self.text_area.insert(tk.END, line[2:], "h1")
        elif line.startswith('## '):
            self.text_area.insert(tk.END, line[3:], "h2")
        elif line.startswith('### '):
            self.text_area.insert(tk.END, line[4:], "h3")
        elif line.strip().startswith('* ') or line.strip().startswith('- '):
            self.insert_formatted(line.strip()[2:] + "\n", "bullet")
        else:
            self.insert_formatted(line, "normal")

    def insert_formatted(self, text, base_tag):
        # Detecta negrito **texto**
        parts = re.split(r'(\*\*.*?\*\*)', text)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                self.text_area.insert(tk.END, part[2:-2], (base_tag, "bold"))
            else:
                self.text_area.insert(tk.END, part, base_tag)

class WizardDialog:
    def __init__(self, parent, app_instance):
        self.top = tk.Toplevel(parent)
        self.top.title("🧙 Assistente de Configuração")
        self.top.configure(bg="#f0f4f8") # Mesmo fundo da janela principal
        
        # Geometria e Centralização
        largura = 460
        altura = 750
        pos_x = parent.winfo_x() + (parent.winfo_width() // 2) - (largura // 2)
        pos_y = parent.winfo_y() + (parent.winfo_height() // 2) - (altura // 2)

        # Correção: Garante que a janela não inicie fora da tela (coordenadas negativas)
        pos_x = max(0, pos_x)
        pos_y = max(0, pos_y)

        self.top.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        
        # Comportamento Modal (Harmonização de Navegabilidade)
        self.top.transient(parent) # Mantém sempre acima da janela pai
        self.top.grab_set()        # Bloqueia interação com a janela pai
        
        self.app = app_instance
        
        # Importa o módulo de wizard dinamicamente
        sys.path.append(self.app.obter_raiz())
        import tools.setup_wizard as wizard_module
        self.wizard = wizard_module

        # --- NOTEBOOK (ABAS) ---
        self.notebook = ttk.Notebook(self.top)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # === ABA 1: CONFIGURAÇÃO ===
        self.tab_config = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_config, text=" Configuração ")

        ttk.Label(self.tab_config, text="Configuração Inicial", style='Header.TLabel').pack(anchor='w')
        ttk.Label(self.tab_config, text="Prepare o ambiente para o robô.", style='Desc.TLabel').pack(anchor='w', pady=(0, 10))

        config_frame = ttk.Frame(self.tab_config)
        config_frame.pack(fill=tk.BOTH, expand=True)

        # Opção 0: Credenciais
        self.criar_secao(config_frame, "0. Credenciais de Acesso", 
                         "Configure seu CPF, Senha e Nome.", 
                         "Configurar Login", self.configurar_login)

        # Opção 1: Reset
        self.criar_secao(config_frame, "1. Arquivos Iniciais", 
                         "Gera modelos JSON em data/ (Reset).", 
                         "Gerar Modelos", self.gerar_modelos)

        # Opção 2: Pastas
        self.criar_secao(config_frame, "2. Estrutura de Pastas", 
                         "Cria pastas em aulas/inputs/.", 
                         "Criar Pastas", self.criar_pastas)

        # Opção 3: Auto Config
        self.criar_secao(config_frame, "3. Configuração Automática", 
                         "Lê histórico e configura turmas (Recomendado).", 
                         "Executar Auto Config", self.auto_config)

        # Opção 4: Calendário
        self.criar_secao(config_frame, "4. Disciplinas Anuais/Mensais", 
                         "Defina quais disciplinas usam unidades.", 
                         "Configurar Disciplinas", self.configurar_disciplinas)

        # === ABA 2: FERRAMENTAS ===
        self.tab_tools = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_tools, text=" Ferramentas ")

        ttk.Label(self.tab_tools, text="Ferramentas de Apoio", style='Header.TLabel').pack(anchor='w')
        ttk.Label(self.tab_tools, text="Utilitários para gestão e análise.", style='Desc.TLabel').pack(anchor='w', pady=(0, 10))

        tools_frame = ttk.Frame(self.tab_tools)
        tools_frame.pack(fill=tk.BOTH, expand=True)

        self.criar_secao(tools_frame, "Análise de Grade", "Relatório de horas registradas vs necessárias.", "Executar Analisador", lambda: self.app.iniciar_script("analisador_de_grade.py"))
        self.criar_secao(tools_frame, "Estatísticas", "Visualizar contagem de aulas por turma/disciplina.", "Ver Estatísticas", lambda: self.app.iniciar_script("ver_aulas_por_disciplina.py"))
        self.criar_secao(tools_frame, "Conversor PDF", "Converter planos Markdown para PDF.", "Converter MD -> PDF", lambda: self.app.iniciar_script("converter_md_para_pdf.py"))

        frame_files = ttk.LabelFrame(tools_frame, text="Gestão de Arquivos", padding="10")
        frame_files.pack(fill=tk.X, pady=5)
        ttk.Button(frame_files, text="📂 Abrir Pasta de Aulas", command=lambda: self.abrir_pasta("aulas")).pack(fill=tk.X, pady=2)
        ttk.Button(frame_files, text="📂 Abrir Pasta de Logs", command=lambda: self.abrir_pasta("aulas/logs")).pack(fill=tk.X, pady=2)

        # === ABA 3: AJUDA ===
        self.tab_help = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_help, text=" Ajuda ")

        ttk.Label(self.tab_help, text="Documentação", style='Header.TLabel').pack(anchor='w')
        ttk.Label(self.tab_help, text="Acesse os guias do sistema.", style='Desc.TLabel').pack(anchor='w', pady=(0, 10))

        help_frame = ttk.Frame(self.tab_help)
        help_frame.pack(fill=tk.BOTH, expand=True)

        self.criar_secao(help_frame, "Tutorial de Uso", "Guia passo a passo para o professor.", "Ler Tutorial", lambda: self.abrir_documento("tutorial_uso.md"))
        self.criar_secao(help_frame, "Arquitetura Técnica", "Documentação para desenvolvedores.", "Ler Arquitetura", lambda: self.abrir_documento("arquitetura_tecnica.md"))
        self.criar_secao(help_frame, "Leia-me", "Informações gerais do projeto.", "Ler README", lambda: self.abrir_documento("README.md"))

    def criar_secao(self, parent, titulo, descricao, texto_botao, comando):
        frame = ttk.LabelFrame(parent, text=titulo, padding="10")
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text=descricao, wraplength=350).pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(frame, text=texto_botao, command=comando).pack(fill=tk.X)

    def abrir_pasta(self, path_rel):
        raiz = self.app.obter_raiz()
        path = os.path.join(raiz, path_rel)
        os.makedirs(path, exist_ok=True)
        if os.name == 'nt':
            os.startfile(path)
        else:
            try: subprocess.Popen(['xdg-open', path])
            except: pass

    def abrir_documento(self, filename):
        raiz = self.app.obter_raiz()
        path = os.path.join(raiz, 'docs', filename)
        if not os.path.exists(path): path = os.path.join(raiz, filename)
        if os.path.exists(path):
            MarkdownViewer(self.top, f"Ajuda - {filename}", path)
        else:
            messagebox.showerror("Erro", f"Arquivo não encontrado: {filename}")

    def log_gui(self, msg):
        self.app.log(f"[Wizard] {msg}")

    def configurar_login(self):
        cpf = simpledialog.askstring("Login", "Digite seu Usuário (CPF):", parent=self.top)
        if not cpf: return
        senha = simpledialog.askstring("Login", "Digite sua Senha do Portal:", show="*", parent=self.top)
        if not senha: return
        prof = simpledialog.askstring("Configuração", "Nome do Professor (conforme horário):", parent=self.top)
        
        raiz = self.app.obter_raiz()
        data_dir = os.path.join(raiz, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Salvar credentials.json
        with open(os.path.join(data_dir, 'credentials.json'), 'w', encoding='utf-8') as f:
            json.dump({"username": cpf, "password": senha}, f, indent=4)
            
        # Salvar config.json se professor foi informado
        if prof:
            cfg_path = os.path.join(data_dir, 'config.json')
            cfg = {}
            if os.path.exists(cfg_path):
                try: 
                    with open(cfg_path, 'r', encoding='utf-8') as f: cfg = json.load(f)
                except: pass
            cfg['professor'] = prof
            with open(cfg_path, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=4, ensure_ascii=False)
        
        messagebox.showinfo("Sucesso", "Credenciais salvas com sucesso!")
        self.log_gui("Credenciais e Configurações atualizadas.")

    def gerar_modelos(self):
        if messagebox.askyesno("Confirmar", "Isso irá sobrescrever arquivos de configuração em 'data/'. Continuar?"):
            self.wizard.gerar_modelos_ficticios()
            self.log_gui("Modelos gerados com sucesso.")
            messagebox.showinfo("Sucesso", "Arquivos de modelo gerados em data/.")

    def criar_pastas(self):
        self.wizard.gerar_estrutura_inputs()
        self.log_gui("Estrutura de pastas verificada/criada.")
        messagebox.showinfo("Sucesso", "Pastas criadas em aulas/inputs/.")

    def auto_config(self):
        if not messagebox.askyesno("Confirmar", "Isso irá analisar seu histórico e reconfigurar turmas. Continuar?"):
            return
        
        sobrescrever = messagebox.askyesno("Sobrescrever", "Deseja sobrescrever nomes curtos de turmas existentes?\n\nSim: Recria nomes (ex: '1º A')\nNão: Mantém seus nomes personalizados")
        
        def resolver_conflito(turma_completa, sugestao_atual, conflito_com):
            msg = f"Conflito detectado!\n\nO nome curto '{sugestao_atual}' já é usado por:\n'{conflito_com}'\n\nMas a turma atual é:\n'{turma_completa}'\n\nDigite um novo nome curto para a turma atual:"
            novo = simpledialog.askstring("Conflito de Nomes", msg, parent=self.top)
            return novo if novo else sugestao_atual + "_X"

        try:
            self.wizard.gerar_configuracao_via_historico(sobrescrever=sobrescrever, callback_conflito=resolver_conflito)
            self.log_gui("Configuração automática concluída.")
            messagebox.showinfo("Sucesso", "Configuração automática finalizada! Verifique a pasta 'data/'.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def configurar_disciplinas(self):
        disciplinas, calendario, path = self.wizard.obter_dados_disciplinas_calendario()
        if not disciplinas:
            messagebox.showwarning("Aviso", "Nenhuma disciplina encontrada ou arquivos de configuração ausentes.")
            return

        # Janela de diálogo customizada para as disciplinas
        diag = tk.Toplevel(self.top)
        diag.title("Configurar Disciplinas")
        diag.geometry("600x640")

        vars_dict = {}
        anuais_atuais = set(calendario.get('disciplinas_config', {}).get('anuais', []))

        def salvar():
            novas_anuais = [code for code, var in vars_dict.items() if var.get()]
            novas_mensais = [code for code, var in vars_dict.items() if not var.get()]
            
            calendario['disciplinas_config']['anuais'] = sorted(novas_anuais)
            calendario['disciplinas_config']['mensais'] = sorted(novas_mensais)
            
            self.wizard.save_json(path, calendario)
            self.log_gui(f"Disciplinas atualizadas: {len(novas_anuais)} anuais, {len(novas_mensais)} mensais.")
            messagebox.showinfo("Sucesso", "Configuração de disciplinas salva!")
            diag.destroy()

        ttk.Button(diag, text="Salvar Configuração", command=salvar).pack(side="bottom", pady=10)

        canvas = tk.Canvas(diag)
        scrollbar = ttk.Scrollbar(diag, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(scrollable_frame, text="Marque as disciplinas ANUAIS:", font=('bold')).pack(pady=5)

        for disc in sorted(list(disciplinas)):
            codigo = "".join(c for c in disc if c.isalnum()).upper()
            var = tk.BooleanVar(value=(codigo in anuais_atuais))
            chk = ttk.Checkbutton(scrollable_frame, text=f"{disc} ({codigo})", variable=var)
            chk.pack(anchor='w', padx=5)
            vars_dict[codigo] = var

if __name__ == "__main__":
    root = tk.Tk()
    # Tenta definir um ícone se existir (opcional)
    # try: root.iconbitmap("icone.ico")
    # except: pass
    
    app = AppAutomação(root)
    root.mainloop()

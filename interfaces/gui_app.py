import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import os
import sys
import subprocess
import threading
import json

class AppAutomação:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Assistente de Automação de Aulas")
        self.root.geometry("600x640")
        self.root.configure(bg="#f0f0f0")

        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 10), padding=5)
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'), background="#f0f0f0")
        style.configure('Desc.TLabel', font=('Helvetica', 9), background="#f0f0f0", foreground="#555")

        # Cabeçalho
        header_frame = ttk.Frame(root, padding="10")
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Painel de Controle do Professor", style='Header.TLabel').pack()
        ttk.Label(header_frame, text="Selecione a etapa que deseja executar:", style='Desc.TLabel').pack()

        # Botões de Ação
        btn_frame = ttk.Frame(root, padding="10")
        btn_frame.pack(fill=tk.X)

        self.criar_botao(btn_frame, "1. Atualizar Dados (Scraper)", 
                         "Baixa os registros atuais do portal.", 
                         "scraper.py", 0)
        
        self.criar_botao(btn_frame, "2. Planejar Aulas", 
                         "Cria os arquivos vazios para as próximas aulas.", 
                         "preparar_planos.py", 1)
        
        self.criar_botao(btn_frame, "3. Preencher Conteúdos", 
                         "Preenche os planos com base nos seus materiais.", 
                         "preenchedor_planos.py", 2)
        
        self.criar_botao(btn_frame, "4. Registrar no Portal", 
                         "O robô lança as aulas no sistema.", 
                         "registrar_aulas.py", 3)
        
        self.criar_botao(btn_frame, "5. Configuração Inicial", 
                         "Gera modelos de arquivos e pastas de input.", 
                         "WIZARD", 4)

        # Área de Log/Console
        log_frame = ttk.LabelFrame(root, text="Progresso / Logs", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, state='disabled', font=('Consolas', 9))
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # Botão Sair
        ttk.Button(root, text="Sair", command=root.quit).pack(pady=5)

        # Verificação inicial de credenciais
        self.root.after(1000, self.verificar_credenciais)

    def criar_botao(self, parent, texto, descricao, script, row):
        frame = ttk.Frame(parent, padding="5")
        frame.pack(fill=tk.X, pady=2)
        
        if script == "WIZARD":
            btn = ttk.Button(frame, text=texto, command=self.abrir_wizard)
        else:
            btn = ttk.Button(frame, text=texto, command=lambda: self.iniciar_script(script))
        btn.pack(side=tk.LEFT, padx=5)
        
        lbl = ttk.Label(frame, text=descricao, style='Desc.TLabel')
        lbl.pack(side=tk.LEFT, padx=5)

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

class WizardDialog:
    def __init__(self, parent, app_instance):
        self.top = tk.Toplevel(parent)
        self.top.title("🧙 Assistente de Configuração")
        self.top.geometry("600x640")
        self.app = app_instance
        
        # Importa o módulo de wizard dinamicamente
        sys.path.append(self.app.obter_raiz())
        import tools.setup_wizard as wizard_module
        self.wizard = wizard_module

        ttk.Label(self.top, text="Bem-vindo ao Assistente de Configuração", font=('Helvetica', 12, 'bold')).pack(pady=10)
        
        # Opção 0: Credenciais
        frame0 = ttk.LabelFrame(self.top, text="0. Credenciais de Acesso", padding=10)
        frame0.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(frame0, text="Configure seu CPF, Senha e Nome do Professor.").pack(anchor=tk.W)
        ttk.Button(frame0, text="Configurar Login", command=self.configurar_login).pack(pady=5)

        # Opção 1: Reset
        frame1 = ttk.LabelFrame(self.top, text="1. Arquivos Iniciais", padding=10)
        frame1.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(frame1, text="Gera arquivos JSON de exemplo em data/ (Sobrescreve!)").pack(anchor=tk.W)
        ttk.Button(frame1, text="Gerar Modelos", command=self.gerar_modelos).pack(pady=5)

        # Opção 2: Pastas
        frame2 = ttk.LabelFrame(self.top, text="2. Estrutura de Pastas", padding=10)
        frame2.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(frame2, text="Cria pastas em aulas/inputs/ baseadas na configuração atual.").pack(anchor=tk.W)
        ttk.Button(frame2, text="Criar Pastas", command=self.criar_pastas).pack(pady=5)

        # Opção 3: Auto Config
        frame3 = ttk.LabelFrame(self.top, text="3. Configuração Automática (Recomendado)", padding=10)
        frame3.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(frame3, text="Lê 'aulas_coletadas.json' e configura tudo automaticamente.").pack(anchor=tk.W)
        ttk.Button(frame3, text="Executar Auto Config", command=self.auto_config).pack(pady=5)

        # Opção 4: Calendário
        frame4 = ttk.LabelFrame(self.top, text="4. Disciplinas Anuais/Mensais", padding=10)
        frame4.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(frame4, text="Configurar Disciplinas", command=self.configurar_disciplinas).pack(pady=5)

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

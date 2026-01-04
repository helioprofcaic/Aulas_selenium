import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os
import threading

if getattr(sys, 'frozen', False):
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from tools import preenchedor_planos as filler_tool

class PreenchedorViewer(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("📝 Preenchedor de Conteúdos")
        self.geometry("700x600")
        self.configure(bg="#f0f4f8")

        self.aulas_dir = os.path.join(PROJECT_ROOT, 'aulas')
        self.inputs_dir = os.path.join(self.aulas_dir, 'inputs')
        self.data_dir = os.path.join(PROJECT_ROOT, 'data')

        # Carregar dados
        self.grouped_files = filler_tool.find_plan_files(self.aulas_dir)
        self.links_recursos = filler_tool.carregar_links_recursos(self.data_dir)

        # Layout
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(top_frame, text="Selecione as disciplinas para preencher:", font=('Segoe UI', 10, 'bold')).pack(anchor='w')

        # Lista com Checkboxes
        self.check_vars = {}
        
        canvas = tk.Canvas(top_frame, bg="#ffffff", highlightthickness=1, highlightbackground="#ccc")
        scrollbar = ttk.Scrollbar(top_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        if not self.grouped_files:
            ttk.Label(self.scrollable_frame, text="Nenhum plano pendente encontrado.").pack(padx=10, pady=10)
        else:
            for key in sorted(self.grouped_files.keys()):
                turma, disciplina = key
                count = len(self.grouped_files[key])
                var = tk.BooleanVar()
                chk = ttk.Checkbutton(self.scrollable_frame, text=f"{turma} - {disciplina} ({count} arquivos)", variable=var)
                chk.pack(anchor='w', padx=5, pady=2)
                self.check_vars[key] = var

        # Botões
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Preencher Selecionados", command=self.iniciar_preenchimento).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="Selecionar Todos", command=self.selecionar_todos).pack(side=tk.LEFT)

        # Log
        log_frame = ttk.LabelFrame(self, text="Log de Processamento", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, state='disabled', font=('Consolas', 9))
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def selecionar_todos(self):
        for var in self.check_vars.values():
            var.set(True)

    def log(self, msg):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def iniciar_preenchimento(self):
        files_to_process = []
        for key, var in self.check_vars.items():
            if var.get():
                files_to_process.extend(self.grouped_files[key])
        
        if not files_to_process:
            messagebox.showwarning("Aviso", "Nenhuma disciplina selecionada.")
            return

        self.log("-" * 40)
        self.log(f"Iniciando preenchimento de {len(files_to_process)} arquivos...")
        
        # Thread para não travar GUI
        threading.Thread(target=self.processar_arquivos, args=(files_to_process,)).start()

    def processar_arquivos(self, files):
        sucessos = 0
        falhas = 0
        
        for txt_path in files:
            success, msg = filler_tool.preencher_arquivo_plano(txt_path, self.inputs_dir, self.links_recursos)
            if success:
                self.log(f"✅ {os.path.basename(txt_path)}: {msg}")
                sucessos += 1
            else:
                self.log(f"❌ {os.path.basename(txt_path)}: {msg}")
                falhas += 1
        
        self.log("-" * 40)
        self.log(f"Concluído. Sucessos: {sucessos}, Falhas: {falhas}")
        messagebox.showinfo("Concluído", f"Processamento finalizado.\nSucessos: {sucessos}\nFalhas: {falhas}")
        
        # Atualizar lista (recarregar janela seria ideal, mas vamos apenas avisar)
        self.log("Nota: Feche e reabra esta janela para atualizar a lista de pendências.")
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Adiciona a raiz ao path para importar tools
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from tools import ver_aulas_por_disciplina as stats_tool

class StatsViewer(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("📊 Estatísticas de Aulas")
        self.geometry("800x600")
        self.configure(bg="#f0f4f8")

        # Carregar dados
        data_path = os.path.join(PROJECT_ROOT, 'data')
        self.aulas, self.turmas_disciplinas, self.mapa_turmas = stats_tool.carregar_dados(data_path)

        if not self.aulas:
            messagebox.showerror("Erro", "Não foi possível carregar os dados. Execute o Scraper primeiro.")
            self.destroy()
            return

        # Notebook (Abas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.criar_aba_disciplina()
        self.criar_aba_turma()
        self.criar_aba_data()

    def criar_treeview(self, parent, colunas):
        tree = ttk.Treeview(parent, columns=colunas, show='headings')
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    def criar_aba_disciplina(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Por Disciplina")
        
        dados = stats_tool.obter_resumo_disciplina(self.aulas, self.turmas_disciplinas)
        
        cols = ('Código', 'Nome da Disciplina', 'Aulas Registradas')
        tree = self.criar_treeview(frame, cols)
        tree.column('Nome da Disciplina', width=300)
        
        for item in dados:
            tree.insert('', tk.END, values=item)

    def criar_aba_turma(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Por Turma")
        
        dados = stats_tool.obter_resumo_turma_dados(self.aulas, self.mapa_turmas)
        
        cols = ('Nome Curto', 'Nome Completo', 'Aulas Registradas')
        tree = self.criar_treeview(frame, cols)
        tree.column('Nome Completo', width=300)
        
        for item in dados:
            tree.insert('', tk.END, values=item)

    def criar_aba_data(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Por Data")
        
        dados = stats_tool.obter_resumo_data_dados(self.aulas)
        
        cols = ('Data', 'Aulas Registradas')
        tree = self.criar_treeview(frame, cols)
        
        for data_obj, count in dados:
            tree.insert('', tk.END, values=(data_obj.strftime('%d/%m/%Y'), count))
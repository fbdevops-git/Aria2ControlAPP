import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.utils.file_utils import FileUtils

class HistoryWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Histórico de Downloads")
        self.geometry("700x400")
        self.resizable(False, False)

        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        columns = ("filename", "status", "finished_at", "path", "url")

        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        column_titles = {
            "filename": "Filename",
            "status": "Status",
            "finished_at": "Completed At",
            "path": "Path",
            "url": "URL"
        }

        for col in columns:
            self.tree.heading(col, text=column_titles[col])
            self.tree.column(col, anchor="w", width=150 if col != "url" else 300)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.btn_clear = ttk.Button(self, text="Clear History", command=self.clear_history)
        self.btn_clear.pack(pady=5)



    def load_history(self):
        """Carrega e exibe o histórico salvo no arquivo JSON"""
        self.tree.delete(*self.tree.get_children())
        history = FileUtils.load_download_history()
        for entry in history:
            self.tree.insert("", "end", values=(
            entry.get("filename", ""),
            entry.get("status", ""),
            entry.get("finished_at", ""),
            entry.get("path", ""),
            entry.get("url", "")
        ))


    def clear_history(self):
        """Confirma e limpa o histórico de downloads"""
        if messagebox.askyesno("Confirmação", "Deseja realmente limpar todo o histórico?"):
            FileUtils.save_download_history([])  # Salva lista vazia
            self.load_history()

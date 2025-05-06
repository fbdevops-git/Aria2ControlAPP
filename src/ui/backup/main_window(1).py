import tkinter as tk
from tkinter import ttk, scrolledtext

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WebUI-Aria2 - Gerenciador de Downloads")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        # Seção Adicionar Downloads
        frame_add = ttk.LabelFrame(self, text="Adicionar Download")
        frame_add.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_add, text="Link:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_link = tk.Entry(frame_add, width=50)
        self.entry_link.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(frame_add, text="Adicionar Download").grid(row=0, column=2, padx=5, pady=5)

        ttk.Checkbutton(frame_add, text="Pausar após adicionar").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Checkbutton(frame_add, text="Verificar integridade após download").grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Seção Controle de Downloads
        frame_control = ttk.LabelFrame(self, text="Gerenciar Downloads")
        frame_control.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(frame_control, columns=("Nome", "Progresso", "Velocidade", "Tempo", "Ações"), show="headings")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Progresso", text="Progresso")
        self.tree.heading("Velocidade", text="Velocidade")
        self.tree.heading("Tempo", text="Tempo Restante")
        self.tree.heading("Ações", text="Ações")
        self.tree.pack(fill="both", expand=True)

        frame_buttons = tk.Frame(frame_control)
        frame_buttons.pack(pady=5)
        ttk.Button(frame_buttons, text="Iniciar").grid(row=0, column=0, padx=5)
        ttk.Button(frame_buttons, text="Pausar").grid(row=0, column=1, padx=5)
        ttk.Button(frame_buttons, text="Remover").grid(row=0, column=2, padx=5)
        ttk.Button(frame_buttons, text="Forçar Download").grid(row=0, column=3, padx=5)

        # Seção Monitoramento
        frame_monitor = ttk.LabelFrame(self, text="Monitoramento")
        frame_monitor.pack(fill="x", padx=10, pady=5)

        ttk.Progressbar(frame_monitor).pack(fill="x", padx=5, pady=5)
        tk.Label(frame_monitor, text="Velocidade Total: 0 KB/s").pack(side="left", padx=5)
        tk.Label(frame_monitor, text="Upload Total: 0 KB/s").pack(side="left", padx=5)

        # Seção Logs
        frame_logs = ttk.LabelFrame(self, text="Logs")
        frame_logs.pack(fill="both", expand=True, padx=10, pady=5)

        scrolledtext.ScrolledText(frame_logs, height=5).pack(fill="both", expand=True)

        # Status do Aria2
        frame_status = tk.Frame(self)
        frame_status.pack(fill="x", padx=10, pady=5)
        tk.Label(frame_status, text="Status do Aria2: Não verificado").pack()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()

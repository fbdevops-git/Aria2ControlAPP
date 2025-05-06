import tkinter as tk
from tkinter import ttk
from src.ui.utils.file_utils import FileUtils


class NetworkWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("🌐 Configurações de Rede")
        self.geometry("400x180")
        self.create_widgets()
        self.load_saved_settings()


    def create_widgets(self):
        frame_network = ttk.LabelFrame(self, text="Servidor Aria2")
        frame_network.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_network, text="URL do Servidor:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_url_network = tk.Entry(frame_network, width=30)
        entry_url_network.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_network, text="Porta RPC:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        entry_port_rpc = tk.Entry(frame_network, width=10)
        entry_port_rpc.insert(0, "6800")
        entry_port_rpc.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frame_network, text="Senha de acesso:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_password_network = tk.Entry(frame_network, width=20, show="*")
        entry_password_network.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        tk.Label(frame_network, text="(Opcional)").grid(row=2, column=2, padx=5, pady=5, sticky="w")

        btn_apply_network = ttk.Button(self, text="Aplicar")
        btn_apply_network.pack(side="right", padx=10, pady=10)


    def apply_settings(self):
        # Salva as configurações da janela de rede
        url = self.entry_url_network.get().strip()
        port = self.entry_port_rpc.get().strip()
        password = self.entry_password_network.get().strip()

        if not port.isdigit():
            messagebox.showerror("Erro", "A porta RPC deve conter apenas números.")
            return

        config = FileUtils.load_config()
        config["rpc_url"] = url
        config["rpc_port"] = port
        config["rpc_secret"] = password

        FileUtils.save_config(config)
        messagebox.showinfo("Sucesso", "Configurações de rede salvas com sucesso.")

    def load_saved_settings(self):
        # Carrega configurações salvas da rede
        config = FileUtils.load_config()
        if "rpc_url" in config:
            self.entry_url_network.insert(0, config["rpc_url"])
        if "rpc_port" in config:
            self.entry_port_rpc.delete(0, tk.END)
            self.entry_port_rpc.insert(0, config["rpc_port"])
        if "rpc_secret" in config:
            self.entry_password_network.insert(0, config["rpc_secret"])



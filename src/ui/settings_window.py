import tkinter as tk
from tkinter import ttk, filedialog
from src.ui.utils.tooltip import ToolTip
from src.ui.utils.aria2_rpc import Aria2RPC
from src.ui.utils.file_utils import FileUtils



class SettingsWindow(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self.title("⚙️ Configurações de Download")
        self.geometry("424x340")
        self.rpc_client = Aria2RPC()  # Conexão com Aria2
        self.create_widgets()
        self.load_saved_settings()


    def create_widgets(self):
        frame_download = ttk.LabelFrame(self, text="Configurações de Download")
        frame_download.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_download, text="Conexões por servidor:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_server_conn = ttk.Combobox(frame_download, values=["4", "8", "16 (Recomendado)", "32"])
        self.combo_server_conn.set("16 (Recomendado)")
        self.combo_server_conn.grid(row=0, column=1, padx=5, pady=5)
        ToolTip(self.combo_server_conn, "Número máximo de conexões simultâneas por servidor.")

        tk.Label(frame_download, text="Segmentos por download:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.combo_segments = ttk.Combobox(frame_download, values=["8", "16 (Recomendado)", "32", "64"])
        self.combo_segments.set("16 (Recomendado)")
        self.combo_segments.grid(row=1, column=1, padx=5, pady=5)
        ToolTip(self.combo_segments, "Quantidade de partes em que o arquivo será dividido para download.")

        tk.Label(frame_download, text="Limite de upload (KB/s):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.combo_upload_limit = ttk.Combobox(frame_download, values=["0 (Sem limite)", "50 (Recomendado)", "100", "500", "1000"])
        self.combo_upload_limit.set("50 (Recomendado)")
        self.combo_upload_limit.grid(row=2, column=1, padx=5, pady=5)
        ToolTip(self.combo_upload_limit, "Define a velocidade máxima de upload em KB/s.")

        tk.Label(frame_download, text="Diretório de destino:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.entry_dest = tk.Entry(frame_download, width=25)
        self.entry_dest.grid(row=3, column=1, padx=5, pady=5)
        btn_browse = ttk.Button(frame_download, text="Procurar", command=self.browse_directory)
        btn_browse.grid(row=3, column=2, padx=5, pady=5)
        ToolTip(btn_browse, "Escolher diretório para salvar os downloads.")

        frame_buttons = ttk.Frame(self)
        frame_buttons.pack(fill="x", padx=10, pady=10)
        btn_recommended = ttk.Button(frame_buttons, text="✅ Usar Recomendados", command=self.reset_defaults)
        btn_recommended.pack(side="left")
        btn_apply = ttk.Button(frame_buttons, text="🚀 Aplicar", command=self.apply_settings)
        btn_apply.pack(side="right")
        btn_reset = ttk.Button(frame_buttons, text="🔒 Resetar para Padrão", command=self.reset_defaults)
        btn_reset.pack(side="right", padx=5)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.entry_dest.delete(0, tk.END)
            self.entry_dest.insert(0, directory)

    def reset_defaults(self):
        self.combo_server_conn.set("16 (Recomendado)")
        self.combo_segments.set("16 (Recomendado)")
        self.combo_upload_limit.set("50 (Recomendado)")
        self.entry_dest.delete(0, tk.END)

    def apply_settings(self):
        options = {}

        # Pegando e validando conexões
        conn_value = self.combo_conn.get().split()[0]
        if conn_value.isdigit():
            options["max-connection-per-server"] = conn_value

        seg_value = self.combo_segments.get().split()[0]
        if seg_value.isdigit():
            options["split"] = seg_value

        upload_value = self.combo_upload.get().split()[0]
        if upload_value.isdigit():
            options["max-upload-limit"] = upload_value + "K" if upload_value != "0" else "0"

        # Validação de diretório
        dest_dir = self.entry_dest.get()
        if dest_dir:
            if not os.path.exists(dest_dir):
                tk.messagebox.showerror("Erro", "O diretório especificado não existe.")
                return
            options["dir"] = dest_dir

        # Salva as configurações no JSON
        FileUtils.save_config(options)

        result = self.rpc.set_options(options)
        if 'error' in result:
            tk.messagebox.showerror("Erro", "Falha ao aplicar configurações.")
        else:
            tk.messagebox.showinfo("Sucesso", "Configurações aplicadas com sucesso.")


    def load_saved_settings(self):
        """Carrega configurações salvas do arquivo JSON"""
        config = FileUtils.load_config()


        if "max-connection-per-server" in config:
            self.combo_conn.set(f'{config["max-connection-per-server"]} (Saved)')
        if "split" in config:
            self.combo_segments.set(f'{config["split"]} (Saved)')
        if "max-upload-limit" in config:
            val = config["max-upload-limit"]
            val_num = val.replace("K", "") if "K" in val else val
            texto = f"{val_num} (Saved)" if val_num != "0" else "0 (No limit)"
            self.combo_upload.set(texto)
        if "dir" in config:
            self.entry_dest.delete(0, tk.END)
            self.entry_dest.insert(0, config["dir"])



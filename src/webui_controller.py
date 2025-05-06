import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="yellow", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

# Janela Principal
root = tk.Tk()
root.title("WebUI-Aria2 - Gerenciador de Downloads")
root.geometry("800x600")

# --- Seção de Adicionar Downloads ---
frame_add = ttk.LabelFrame(root, text="Adicionar Download")
frame_add.pack(fill="x", padx=10, pady=5)

tk.Label(frame_add, text="Link:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_link = tk.Entry(frame_add, width=50)
entry_link.grid(row=0, column=1, padx=5, pady=5)

btn_add = ttk.Button(frame_add, text="Adicionar Download")
btn_add.grid(row=0, column=2, padx=5, pady=5)

chk_pause = ttk.Checkbutton(frame_add, text="Pausar após adicionar")
chk_pause.grid(row=1, column=0, padx=5, pady=5, sticky="w")
chk_check = ttk.Checkbutton(frame_add, text="Verificar integridade após download")
chk_check.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# --- Seção de Controle de Downloads ---
frame_control = ttk.LabelFrame(root, text="Gerenciar Downloads")
frame_control.pack(fill="both", expand=True, padx=10, pady=5)

tree = ttk.Treeview(frame_control, columns=("Nome", "Progresso", "Velocidade", "Tempo", "Ações"), show="headings")
tree.heading("Nome", text="Nome")
tree.heading("Progresso", text="Progresso")
tree.heading("Velocidade", text="Velocidade")
tree.heading("Tempo", text="Tempo Restante")
tree.heading("Ações", text="Ações")
tree.pack(fill="both", expand=True)

frame_buttons = tk.Frame(frame_control)
frame_buttons.pack(pady=5)

btn_start = ttk.Button(frame_buttons, text="Iniciar")
btn_start.grid(row=0, column=0, padx=5)
btn_pause = ttk.Button(frame_buttons, text="Pausar")
btn_pause.grid(row=0, column=1, padx=5)
btn_remove = ttk.Button(frame_buttons, text="Remover")
btn_remove.grid(row=0, column=2, padx=5)
btn_force = ttk.Button(frame_buttons, text="Forçar Download")
btn_force.grid(row=0, column=3, padx=5)

# --- Seção de Monitoramento ---
frame_monitor = ttk.LabelFrame(root, text="Monitoramento")
frame_monitor.pack(fill="x", padx=10, pady=5)

progress_global = ttk.Progressbar(frame_monitor)
progress_global.pack(fill="x", padx=5, pady=5)

label_speed = tk.Label(frame_monitor, text="Velocidade Total: 0 KB/s")
label_speed.pack(side="left", padx=5)
label_upload = tk.Label(frame_monitor, text="Upload Total: 0 KB/s")
label_upload.pack(side="left", padx=5)

# --- Seção de Logs ---
frame_logs = ttk.LabelFrame(root, text="Logs")
frame_logs.pack(fill="both", expand=True, padx=10, pady=5)

text_logs = scrolledtext.ScrolledText(frame_logs, height=5)
text_logs.pack(fill="both", expand=True)

# --- Janela de Configurações ---
def open_settings_window():
    settings_win = tk.Toplevel(root)
    settings_win.title("⚙️ Configurações do Aria2")
    settings_win.geometry("424x300")

    frame_download = ttk.LabelFrame(settings_win, text="Configurações de Download")
    frame_download.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_download, text="Conexões por servidor:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    combo_server_conn = ttk.Combobox(frame_download, values=["4", "8", "16 (Recomendado)", "32"])
    combo_server_conn.set("16 (Recomendado)")
    combo_server_conn.grid(row=0, column=1, padx=5, pady=5)
    ToolTip(combo_server_conn, "Número máximo de conexões simultâneas por servidor.")

    tk.Label(frame_download, text="Segmentos por download:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    combo_segments = ttk.Combobox(frame_download, values=["8", "16 (Recomendado)", "32", "64"])
    combo_segments.set("16 (Recomendado)")
    combo_segments.grid(row=1, column=1, padx=5, pady=5)
    ToolTip(combo_segments, "Quantidade de partes em que o arquivo será dividido para download.")

    tk.Label(frame_download, text="Limite de upload (KB/s):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    combo_upload_limit = ttk.Combobox(frame_download, values=["0 (Sem limite)", "50 (Recomendado)", "100", "500", "1000"])
    combo_upload_limit.set("50 (Recomendado)")
    combo_upload_limit.grid(row=2, column=1, padx=5, pady=5)
    ToolTip(combo_upload_limit, "Define a velocidade máxima de upload em KB/s.")

    tk.Label(frame_download, text="Diretório de destino:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    entry_dest = tk.Entry(frame_download, width=25)
    entry_dest.grid(row=3, column=1, padx=5, pady=5)
    btn_browse = ttk.Button(frame_download, text="Procurar")
    btn_browse.grid(row=3, column=2, padx=5, pady=5)
    ToolTip(btn_browse, "Escolher diretório para salvar os downloads.")

    btn_recommended = ttk.Button(settings_win, text="✅ Usar Recomendados")
    btn_recommended.pack(side="left", padx=10, pady=10)

    btn_reset = ttk.Button(settings_win, text="🔒 Resetar para Padrão")
    btn_reset.pack(side="right", padx=10, pady=10)

def open_network_settings():
    network_win = tk.Toplevel(root)
    network_win.title("🌐 Configurações de Rede")
    network_win.geometry("400x180")

    frame_network = ttk.LabelFrame(network_win, text="Servidor Aria2")
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

    btn_apply_network = ttk.Button(network_win, text="Aplicar")
    btn_apply_network.pack(side="right", padx=10, pady=10)

# Menu para abrir Configurações
menu_bar = tk.Menu(root)
config_menu = tk.Menu(menu_bar, tearoff=0)
config_menu.add_command(label="⚙️ Configurações de Download", command=open_settings_window)
config_menu.add_command(label="🌐 Configurações de Rede", command=open_network_settings)
menu_bar.add_cascade(label="Configurações", menu=config_menu)
root.config(menu=menu_bar)

# --- Seção de Status do Aria2 ---
frame_status = tk.Frame(root)
frame_status.pack(fill="x", padx=10, pady=5)
label_aria2_status = tk.Label(frame_status, text="Status do Aria2: Não verificado")
label_aria2_status.pack()

root.mainloop()

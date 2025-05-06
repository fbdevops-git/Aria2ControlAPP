import tkinter as tk
import threading  

from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from src.ui.utils.aria2_status_checker import Aria2StatusChecker
from src.ui.controllers.download_controller import DownloadController
from src.ui.utils.log_utils import Logger

from src.ui.history_window import HistoryWindow



class MainWindow(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("WebUI-Aria2 - Gerenciador de Downloads")
        self.geometry("800x640")

        self.controller = DownloadController()  #Adicione aqui

        self.create_widgets()
        self.update_aria2_status()
        self.update_periodically()

        Logger.setup_logger(self.append_log_to_ui)
        Logger.log_info("Aplicativo iniciado.")
        self.tree.bind("<Button-1>", self.on_treeview_click)


    def on_treeview_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if column == "#5" and item_id:  # Coluna Ações
            values = self.tree.item(item_id, "values")
            action_text = values[4]
            gid = item_id  # usamos o GID como iid

            if "⏵" in action_text:
                self.controller.resume_download(gid)
                Logger.log_info(f"Download retomado: {gid}")
            elif "⏸" in action_text:
                self.controller.pause_download(gid)
                Logger.log_info(f"Download pausado: {gid}")
            elif "⏹" in action_text:
                confirm = tk.messagebox.askyesno(
                    "Confirmar remoção",
                    "Tem certeza que deseja parar e remover este download da fila?"
                )
                if confirm:
                    self.controller.stop_download(gid)
                    Logger.log_info(f"Download removido: {gid}")


            # Atualiza a tabela após a ação
            self.load_downloads()


    def ensure_aria2_ready(self):
        from src.ui.utils.aria2_status import Aria2StatusChecker
        import subprocess
        import time

        status = Aria2StatusChecker.get_status()

        if "não instalado" in status.lower():
            tk.messagebox.showerror("Erro", "O Aria2 não está instalado.")
            return False

        if "não está rodando" in status.lower():
            Logger.log_info("Aria2 não está rodando. Tentando iniciar...")
            try:
                subprocess.Popen(["aria2c", "--enable-rpc"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(5)  # Aguarda para dar tempo de iniciar
            except Exception as e:
                tk.messagebox.showerror("Erro", f"Falha ao iniciar o Aria2: {e}")
                Logger.log_error(f"Erro ao iniciar o Aria2: {e}")
                return False

            # Verifica novamente se subiu
            time.sleep(1)
            status = Aria2StatusChecker.get_status()
            if "rodando" not in status.lower():
                tk.messagebox.showerror("Erro", "O Aria2 não pôde ser iniciado.")
                return False

        return True


    def load_downloads(self):
        def trabalho():
            downloads = self.controller.listar_downloads()
            self.after(0, lambda: self.update_treeview(downloads))
        threading.Thread(target=trabalho, daemon=True).start()


    def update_periodically(self, intervalo_ms=5000):
        self.load_downloads()  # Agora roda em thread segura
        self.update_aria2_status()
        self.after(intervalo_ms, self.update_periodically, intervalo_ms)


    def update_treeview(self, downloads):
        self.tree.delete(*self.tree.get_children())

        for item in downloads:
            # Verifica se o download está completo
            if item.get("status") == "complete":
                self.on_download_completed(item)

            # Nome do arquivo
            nome = item.get("bittorrent", {}).get("info", {}).get("name") or \
                item.get("files", [{}])[0].get("path", "Desconhecido").split("/")[-1]

            # Cálculo do progresso
            progresso = f"{float(item.get('completedLength', 0)) / max(float(item.get('totalLength', 1)), 1) * 100:.1f}%"
            velocidade = f"{int(item.get('downloadSpeed', 0)) / 1024:.1f} KB/s"
            tempo = "Calculando..."

            # ✅ Simula botões na coluna Ações
            status = item.get("status", "")
            action_text = "[⏸ ⏹]" if status == "active" else "[⏵ ⏹]"

            # Insere na Treeview com GID como identificador
            self.tree.insert("", "end", iid=item["gid"], values=(nome, progresso, velocidade, tempo, action_text))
    


    def add_download(self):
        if not self.ensure_aria2_ready():
            return  # Se Aria2 não estiver pronto, não continua

        url = self.entry_link.get().strip()
        if not url:
            tk.messagebox.showerror("Erro", "O link está vazio.")
            return

        try:
            gid = self.controller.add_download(url)
            print(f"Download adicionado com GID: {gid}")
            self.load_downloads()
        except Exception as e:
            print(f"Erro ao adicionar download: {e}")
            tk.messagebox.showerror("Erro", f"Não foi possível adicionar o download:\n{e}")



    def update_aria2_status(self):
        status_text = Aria2StatusChecker.get_status()

        color = "black"
        if "não instalado" in status_text.lower():
            color = "red"
        elif "não está rodando" in status_text.lower():
            color = "orange"
        elif "rodando" in status_text.lower():
            color = "green"

        self.lbl_aria2_status.config(text=f"Status do Aria2: {status_text}", fg=color)

        # Desativa ou ativa o botão com base no status
        if hasattr(self, 'btn_add_download'):
            estado = "normal" if "rodando" in status_text.lower() else "disabled"
            self.btn_add_download["state"] = estado


    def append_log_to_ui(self, msg: str):
        self.text_logs.insert("end", msg + "\n")
        self.text_logs.yview("end")  # rola automaticamente para o final


    def create_widgets(self):
        # Seção Adicionar Downloads
        frame_add = ttk.LabelFrame(self, text="Adicionar Download")
        frame_add.pack(fill="x", padx=10, pady=5)

        self.lbl_download_url = tk.Label(frame_add, text="Link:")
        self.lbl_download_url.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.entry_link = tk.Entry(frame_add, width=50)
        self.entry_link.grid(row=0, column=1, padx=5, pady=5)

        self.btn_add_download = ttk.Button(frame_add, text="Adicionar Download", command=self.add_download)
        self.btn_add_download.grid(row=0, column=2, padx=5, pady=5)

        self.chk_pause_after_add = ttk.Checkbutton(frame_add, text="Pausar após adicionar")
        self.chk_pause_after_add.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.chk_check_integrity = ttk.Checkbutton(frame_add, text="Verificar integridade após download")
        self.chk_check_integrity.grid(row=1, column=1, padx=5, pady=5, sticky="w")

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

        self.btn_start = ttk.Button(frame_buttons, text="Iniciar")
        self.btn_start.grid(row=0, column=0, padx=5)

        self.btn_pause = ttk.Button(frame_buttons, text="Pausar")
        self.btn_pause.grid(row=0, column=1, padx=5)

        self.btn_remove = ttk.Button(frame_buttons, text="Remover")
        self.btn_remove.grid(row=0, column=2, padx=5)

        self.btn_force_download = ttk.Button(frame_buttons, text="Forçar Download")
        self.btn_force_download.grid(row=0, column=3, padx=5)

        ttk.Button(self, text="Ver Histórico", command=self.open_history_window).pack(pady=5)


        # Seção Monitoramento
        frame_monitor = ttk.LabelFrame(self, text="Monitoramento")
        frame_monitor.pack(fill="x", padx=10, pady=5)

        ttk.Progressbar(frame_monitor).pack(fill="x", padx=5, pady=5)

        self.lbl_total_speed = tk.Label(frame_monitor, text="Velocidade Total: 0 KB/s")
        self.lbl_total_speed.pack(side="left", padx=5)

        self.lbl_total_upload = tk.Label(frame_monitor, text="Upload Total: 0 KB/s")
        self.lbl_total_upload.pack(side="left", padx=5)

        # Seção Logs
        frame_logs = ttk.LabelFrame(self, text="Logs")
        frame_logs.pack(fill="both", expand=True, padx=10, pady=5)

        self.text_logs = ScrolledText(frame_logs, height=5)
        self.text_logs.pack(fill="both", expand=True)


        # Status do Aria2
        frame_status = tk.Frame(self)
        frame_status.pack(fill="x", padx=10, pady=5)
        self.lbl_aria2_status = tk.Label(frame_status, text="Status do Aria2: Não verificado")
        self.lbl_aria2_status.pack()


    def open_history_window(self):
        HistoryWindow(self)


    def on_download_completed(self, download_data):
        from src.ui.utils.file_utils import FileUtils
        from datetime import datetime
        from plyer import notification
        from playsound import playsound
        import os

        try:
            # Extrai caminho do arquivo e outras informações
            file_path = download_data.get("files", [{}])[0].get("path", "")
            file_name = os.path.basename(file_path)

            entry = {
                "filename": file_name,
                "url": download_data.get("files", [{}])[0].get("uris", [{}])[0].get("uri", ""),
                "path": os.path.dirname(file_path),
                "status": "Concluído",
                "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Salva no histórico
            FileUtils.save_download_history(entry)

            # Mostra notificação
            notification.notify(
                title="Download concluído",
                message=f"{file_name} foi baixado com sucesso!",
                timeout=5
            )

            # Toca som de sucesso
            sound_path = os.path.join(os.path.dirname(__file__), "..", "assets", "sounds", "success.wav")
            sound_path = os.path.abspath(sound_path)  # Garante caminho absoluto
            playsound(sound_path)

        except Exception as e:
            from src.ui.utils.log_utils import Logger
            Logger.log_error(f"Erro ao processar download concluído: {e}")







if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()

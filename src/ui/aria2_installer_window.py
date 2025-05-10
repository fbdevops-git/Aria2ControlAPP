import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread

from src.ui.utils.aria2_installer_utils import Aria2Downloader, Aria2Installer
from src.ui.utils.system_info_utils import SystemInfoUtils
from src.ui.utils.aria2_status_checker import Aria2StatusChecker



class Aria2InstallerWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Instalador do Aria2")
        self.geometry("550x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.parent = parent

        self.version = "1.37.0"
        self.download_urls = {
            "32bit": f"https://github.com/aria2/aria2/releases/download/release-{self.version}/aria2-{self.version}-win-32bit-build1.zip",
            "64bit": f"https://github.com/aria2/aria2/releases/download/release-{self.version}/aria2-{self.version}-win-64bit-build1.zip"
        }

        self.download_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "aria2_download")
        self.install_dir = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), "aria2")

        self.aria2_zip_path = os.path.join(self.download_dir, "aria2.zip")
        self.extracted_dir = None

        self.is_admin = SystemInfoUtils.check_admin()

        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Verificando instalação do Aria2...")

        self.init_gui()
        self.check_if_installed()
        if hasattr(self.parent, 'update_aria2_status'):
            self.parent.update_aria2_status()

        # Se foi relançado com privilégios admin para instalação, executa direto
        if "--install-aria2" in sys.argv:
            self.status_var.set("Instalando Aria2 com privilégios de administrador...")
            self.after(300, self.start_download_and_install)

    def init_gui(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        label = ttk.Label(frame, text="Instalador automático do Aria2", font=("Helvetica", 14, "bold"))
        label.pack(pady=10)

        self.install_button = ttk.Button(frame, text="Baixar & Instalar Aria2", command=self.start_download_and_install, width=30)
        self.install_button.pack(pady=5)

        progress = ttk.Progressbar(frame, orient="horizontal", length=500, mode="determinate", variable=self.progress_var)
        progress.pack(pady=5)

        status_label = ttk.Label(frame, textvariable=self.status_var)
        status_label.pack(pady=5)

    def check_if_installed(self):
        if Aria2StatusChecker.is_aria2_installed():
            self.status_var.set("Aria2 já está instalado nesta máquina.")
            self.install_button.config(state=tk.DISABLED)
        else:
            self.status_var.set("Aria2 não instalado. Pronto para baixar e instalar.")
            self.install_button.config(state=tk.NORMAL)

    def update_progress(self, value, status_text=None):
        self.progress_var.set(value)
        if status_text:
            self.status_var.set(status_text)
        self.update_idletasks()

    def start_download_and_install(self):
        self.install_button.config(state=tk.DISABLED)

        thread = Thread(target=self._download_and_install_thread)
        thread.daemon = True
        thread.start()

    def _download_and_install_thread(self):
        try:
            # Verificar se já está baixado
            if not os.path.exists(self.aria2_zip_path):
                downloader = Aria2Downloader()
                result = downloader.download(
                    self.download_urls[SystemInfoUtils.get_recommended_version()],
                    self.download_dir,
                    self.update_progress
                )

                if not result['success']:
                    self._show_error(result['error'])
                    return

                self.extracted_dir = result['extracted_dir']
            else:
                # Tentar localizar pasta extraída
                for item in os.listdir(self.download_dir):
                    item_path = os.path.join(self.download_dir, item)
                    if os.path.isdir(item_path) and "aria2" in item.lower():
                        self.extracted_dir = item_path
                        break

            if not self.extracted_dir or not os.path.exists(self.extracted_dir):
                self._show_error("Falha ao localizar a pasta extraída do Aria2.")
                return

            # Verificar se é admin
            from os.path import abspath

            if not self.is_admin:
                response = messagebox.askyesno("Permissão", "O instalador precisa de permissão de administrador. Deseja continuar?")
                if response:
                    SystemInfoUtils.run_as_admin(sys.executable, "-m src.main --install-aria2")
                    self.destroy()
                    return

                else:
                    self.status_var.set("Instalação cancelada pelo usuário.")
                    return



            installer = Aria2Installer()
            result = installer.install(
                self.extracted_dir,
                self.install_dir,
                create_shortcut=True,
                startup_with_windows=True,
                enable_rpc=True,
                is_admin=self.is_admin,
                progress_callback=self.update_progress
            )

            if result['success']:
                self.status_var.set("Aria2 instalado com sucesso!")
                self.check_if_installed()
                if hasattr(self.parent, 'update_aria2_status'):
                    self.parent.update_aria2_status()


        except Exception as e:
            self._show_error(f"Erro inesperado: {str(e)}")

    def _show_error(self, message):
        messagebox.showerror("Erro", message, parent=self)
        self.status_var.set("Erro: " + message)
        self.install_button.config(state=tk.NORMAL)

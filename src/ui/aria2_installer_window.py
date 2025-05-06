#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from threading import Thread


# Importações dos módulos de utilitários
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importações dos módulos de utilitários
from src.ui.utils.aria2_installer_utils import Aria2Downloader, Aria2Installer
from src.ui.utils.system_info_utils import SystemInfoUtils
from src.ui.utils.file_utils import FileUtils

from src.ui.utils.aria2_installer_utils import check_and_install_dependencies



class Aria2InstallerWindow(tk.Toplevel):
    """
    Janela para instalação do Aria2
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configurações da janela
        self.title("Instalador do Aria2")
        self.geometry("550x540") 
        self.resizable(False, False)
        self.transient(parent)  # Faz esta janela sempre ficar acima da janela principal
        self.grab_set()  # Impede interação com outras janelas enquanto esta estiver aberta
        
        # Referência à janela pai
        self.parent = parent
        
        # Versão mais recente do Aria2
        self.version = "1.37.0"
        
        # URLs dos binários
        self.download_urls = {
            "32bit": f"https://github.com/aria2/aria2/releases/download/release-{self.version}/aria2-{self.version}-win-32bit-build1.zip",
            "64bit": f"https://github.com/aria2/aria2/releases/download/release-{self.version}/aria2-{self.version}-win-64bit-build1.zip"
        }
        
        # Diretório de instalação padrão
        self.default_install_dir = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), "aria2")
        
        # Diretório de download temporário
        self.download_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "aria2_download")
        
        # Verificar se é admin
        self.is_admin = SystemInfoUtils.check_admin()
        
        # Estado do download
        self.download_complete = False
        self.aria2_zip_path = None
        self.extracted_dir = None
        
        # Iniciar interface gráfica
        self.init_gui()
    



    def init_gui(self):
        """
        Inicializa a interface gráfica
        """
        # Configurar estilo
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("TLabel", padding=6)
        style.configure("TProgressbar", thickness=7)
        style.configure("Green.TButton", foreground="green")
        style.configure("Blue.TButton", foreground="blue")
        
        # Frame principal
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Instalador Automático do Aria2", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=10)
        
        # Informações sobre o Aria2
        info_text = (
            "Aria2 é um utilitário de download leve e multiprotocolo que suporta\n"
            "HTTP/HTTPS, FTP, SFTP, BitTorrent e Metalink.\n\n"
            "1. Clique em 'Baixar' para obter o Aria2.\n"
            "2. Após o download, clique em 'Instalar' para concluir a instalação."
        )
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.CENTER)
        info_label.pack(pady=10)


        # -----------------------------------> INICIO BOTÕES <-----------------------------------
        # Botões
        button_container = ttk.Frame(main_frame)
        button_container.pack(fill=tk.X, pady=10)

        # Frame centralizado para os botões
        button_frame = ttk.Frame(button_container)
        button_frame.pack(expand=True)

        # Botão Baixar
        self.download_button = ttk.Button(
            button_frame, 
            text="Baixar", 
            style="Blue.TButton",
            command=self.start_download,
            width=15
        )
        self.download_button.pack(side=tk.LEFT, padx=5)

        # Botão Instalar
        self.install_button = ttk.Button(
            button_frame, 
            text="Instalar", 
            style="Green.TButton",
            command=self.start_install,
            width=15
        )
        self.install_button.pack(side=tk.LEFT, padx=5)

        # Botão Cancelar
        self.cancel_button = ttk.Button(
            button_frame, 
            text="Cancelar", 
            command=self.destroy,
            width=15
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        # -----------------------------------> FIM BOTÕES <-----------------------------------

        
        # Frame para seleção de versão (NOVO)
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill=tk.X, pady=10)
        
        version_label = ttk.Label(version_frame, text="Selecione a versão:")
        version_label.grid(row=0, column=0, sticky=tk.W)
        
        # ComboBox para seleção de versão (NOVO)
        self.version_var = tk.StringVar()
        self.version_combo = ttk.Combobox(
            version_frame, 
            textvariable=self.version_var,
            values=["32bit", "64bit"],
            width=10,
            state="readonly"
        )
        self.version_combo.grid(row=0, column=1, padx=5)
        
        # Detectar e recomendar versão (NOVO)
        recommended_version = SystemInfoUtils.get_recommended_version()
        self.version_var.set(recommended_version)
        
        # Label de recomendação (NOVO)
        recommend_label = ttk.Label(
            version_frame, 
            text=f"Recomendado: {recommended_version} (baseado no seu sistema)",
            font=("Helvetica", 9, "italic")
        )
        recommend_label.grid(row=0, column=2, padx=5)
        
        # Diretório de instalação
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=10)
        
        dir_label = ttk.Label(dir_frame, text="Diretório de instalação:")
        dir_label.grid(row=0, column=0, sticky=tk.W)
        
        self.install_dir_var = tk.StringVar(value=self.default_install_dir)
        dir_entry = ttk.Entry(dir_frame, textvariable=self.install_dir_var, width=40)
        dir_entry.grid(row=0, column=1, padx=5)
        
        dir_button = ttk.Button(dir_frame, text="...", width=3, command=self.browse_dir)
        dir_button.grid(row=0, column=2)
        
        # Opções adicionais
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=10)
        
        # Opção para iniciar com o Windows
        self.startup_var = tk.BooleanVar(value=True)
        startup_check = ttk.Checkbutton(
            options_frame, 
            text="Iniciar o Aria2 com o Windows", 
            variable=self.startup_var
        )
        startup_check.pack(anchor=tk.W)
        
        # Opção para criar atalho na área de trabalho
        self.shortcut_var = tk.BooleanVar(value=True)
        shortcut_check = ttk.Checkbutton(
            options_frame, 
            text="Criar atalho na área de trabalho", 
            variable=self.shortcut_var
        )
        shortcut_check.pack(anchor=tk.W)
        
        # Configuração para ativar o modo RPC do Aria2
        self.rpc_var = tk.BooleanVar(value=True)
        rpc_check = ttk.Checkbutton(
            options_frame, 
            text="Ativar modo RPC para controle remoto", 
            variable=self.rpc_var
        )
        rpc_check.pack(anchor=tk.W)
        
        # Progresso
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress = ttk.Progressbar(
            progress_frame, 
            orient="horizontal", 
            length=500, 
            mode="determinate",
            variable=self.progress_var
        )
        self.progress.pack(fill=tk.X)
        
        # Status
        self.status_var = tk.StringVar(value="Pronto para iniciar")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(pady=5)
        
        # Centralizar janela em relação à janela principal
        self.center_window()
        
        # Protocolo de fechamento
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    




    def center_window(self):
        """
        Centraliza a janela em relação à janela principal
        """
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_close(self):
        """
        Evento de fechamento da janela
        """
        self.destroy()
    
    def browse_dir(self):
        """
        Abre o diálogo para selecionar o diretório de instalação
        """
        directory = filedialog.askdirectory(
            initialdir=self.install_dir_var.get()
        )
        if directory:
            self.install_dir_var.set(directory)
    
    

    def show_admin_warning(self):
        """
        Mostra um aviso sobre privilégios de administrador
        """
        response = messagebox.askyesno(
            "Privilégios de Administrador",
            "Para instalar o Aria2 corretamente, o programa precisa de privilégios de administrador.\n\n"
            "Deseja continuar com privilégios elevados?",
            icon=messagebox.WARNING,
            parent=self
        )

        if response:
            SystemInfoUtils.run_as_admin(sys.executable, " ".join(sys.argv))
            self.destroy()
            return False  # Interromper o fluxo atual
        else:
            messagebox.showinfo(
                "Instalação Limitada",
                "A instalação continuará sem privilégios administrativos.\n"
                "Algumas funcionalidades podem não funcionar corretamente.",
                parent=self
            )
            return True



    
    def update_progress(self, value, status_text=None):
        """
        Atualiza a barra de progresso e o texto de status
        """
        self.progress_var.set(value)
        if status_text:
            self.status_var.set(status_text)
        self.update_idletasks()
    
    
    
    def _download_thread(self, params):
        """
        Thread para realizar o download
        """
        try:
            # Resetar estado
            self.download_complete = False
            self.aria2_zip_path = None
            self.extracted_dir = None
            
            # Criar e executar o downloader
            downloader = Aria2Downloader()
            result = downloader.download(
                params['download_url'],
                params['download_dir'],
                self.update_progress
            )
            
            if result['success']:
                self.aria2_zip_path = result['zip_path']
                self.extracted_dir = result['extracted_dir']
                self.download_complete = True
                
                # Atualizar os botões na thread principal
                self.after(0, lambda: self.install_button.config(state=tk.NORMAL))
                self.after(0, lambda: self.download_button.config(state=tk.NORMAL))
            else:
                # Mostrar erro na thread principal
                self.after(0, lambda: self._show_error(result['error']))
                
        except Exception as e:
            # Mostrar erro na thread principal
            self.after(0, lambda: self._show_error(f"Erro durante o download: {str(e)}"))




    def _show_error(self, message):
        """
        Exibe uma mensagem de erro e reativa os botões
        """
        messagebox.showerror("Erro", message, parent=self)
        self.download_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL)
        if self.download_complete:
            self.install_button.config(state=tk.NORMAL)

    




    def start_download(self):
        """
        Inicia o processo de download em uma thread separada
        """
        # Não precisa de privilégios de admin para download, então não verificamos aqui
        self.download_button.config(state=tk.DISABLED)
        self.install_button.config(state=tk.DISABLED)
        
        # Obter a versão selecionada
        selected_version = self.version_var.get()
        download_url = self.download_urls[selected_version]
        
        # Parâmetros para o downloader
        download_params = {
            'download_url': download_url,
            'download_dir': self.download_dir,
            'version': selected_version
        }
        
        # Iniciar o download em uma thread separada
        thread = Thread(
            target=self._download_thread,
            args=(download_params,)
        )
        thread.daemon = True
        thread.start()


    def start_install(self):
        """
        Inicia o processo de instalação em uma thread separada
        """
        # Verificar privilégios de admin antes de instalar
        if not self.is_admin:
            response = self.show_admin_warning()
            if not response:  # Se o usuário cancelou a elevação de privilégios
                return  # Não continua com a instalação
        
        self.download_button.config(state=tk.DISABLED)
        self.install_button.config(state=tk.DISABLED)
        
        # Parâmetros de instalação
        install_params = {
            'extracted_dir': self.extracted_dir,
            'install_dir': self.install_dir_var.get(),
            'create_shortcut': self.shortcut_var.get(),
            'startup_with_windows': self.startup_var.get(),
            'enable_rpc': self.rpc_var.get(),
            'is_admin': self.is_admin
        }
        
        # Iniciar a instalação em uma thread separada
        thread = Thread(
            target=self._install_thread,
            args=(install_params,)
        )
        thread.daemon = True
        thread.start()

    
    def _install_thread(self, params):
        """
        Thread para realizar a instalação
        """
        try:
            if not self.download_complete:
                self.after(0, lambda: self._show_error("Por favor, baixe o Aria2 antes de instalar."))
                return
            
            if not self.extracted_dir or not os.path.exists(self.extracted_dir):
                self.after(0, lambda: self._show_error("Arquivos do Aria2 não encontrados. Por favor, baixe novamente."))
                return
            
            # Criar e executar o instalador
            installer = Aria2Installer()
            result = installer.install(
                params['extracted_dir'],
                params['install_dir'],
                params['create_shortcut'],
                params['startup_with_windows'],
                params['enable_rpc'],
                params['is_admin'],
                self.update_progress
            )
            
            if result['success']:
                # Exibir mensagem de sucesso na thread principal
                self.after(0, lambda: messagebox.showinfo(
                    "Instalação Concluída",
                    "O Aria2 foi instalado com sucesso!\n\n"
                    "Para usá-lo, abra um prompt de comando e digite: aria2c [URL]",
                    parent=self
                ))
                
                # Reativar botões
                self.after(0, lambda: self.download_button.config(state=tk.NORMAL))
                self.after(0, lambda: self.install_button.config(state=tk.NORMAL))
            else:
                # Mostrar erro na thread principal
                self.after(0, lambda: self._show_error(result['error']))
                
        except Exception as e:
            # Mostrar erro na thread principal
            self.after(0, lambda: self._show_error(f"Erro durante a instalação: {str(e)}"))
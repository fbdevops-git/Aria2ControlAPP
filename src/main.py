import sys
import os
import tkinter as tk
from src.ui.main_window import MainWindow
from src.ui.settings_window import SettingsWindow
from src.ui.network_window import NetworkWindow
from src.ui.aria2_installer_window import Aria2InstallerWindow
from src.ui.utils.log_utils import Logger


def main():
    Logger.setup_logger()
    Logger.log_info("Aplicativo iniciado.")

    app = MainWindow()

    settings_window_instance = None
    network_window_instance = None
    aria2_installer_window_instance = None

    def open_settings_window():
        nonlocal settings_window_instance
        if settings_window_instance is None or not settings_window_instance.winfo_exists():
            settings_window_instance = SettingsWindow(app)
            settings_window_instance.transient(app)
            settings_window_instance.grab_set()
        else:
            settings_window_instance.lift()

    def open_network_window():
        nonlocal network_window_instance
        if network_window_instance is None or not network_window_instance.winfo_exists():
            network_window_instance = NetworkWindow(app)
            network_window_instance.transient(app)
            network_window_instance.grab_set()
        else:
            network_window_instance.lift()

    def open_aria2_installer_window():
        nonlocal aria2_installer_window_instance
        if aria2_installer_window_instance is None or not aria2_installer_window_instance.winfo_exists():
            aria2_installer_window_instance = Aria2InstallerWindow(app)
            aria2_installer_window_instance.transient(app)
            aria2_installer_window_instance.grab_set()
        else:
            aria2_installer_window_instance.lift()

    # Menu
    menu_bar = tk.Menu(app)
    config_menu = tk.Menu(menu_bar, tearoff=0)
    config_menu.add_command(label="⚙️ Configurações de Download", command=open_settings_window)
    config_menu.add_command(label="🌐 Configurações de Rede", command=open_network_window)
    config_menu.add_command(label="⬇️ Instalar Aria2", command=open_aria2_installer_window)
    menu_bar.add_cascade(label="Configurações", menu=config_menu)
    app.config(menu=menu_bar)

    try:
        app.mainloop()
    except Exception as e:
        Logger.log_error(f"Erro crítico durante execução: {str(e)}")
        raise


if __name__ == "__main__":
    main()

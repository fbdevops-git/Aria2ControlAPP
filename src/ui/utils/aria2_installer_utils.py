import os
import sys
import platform
import subprocess
import zipfile
import urllib.request
import urllib.error

from typing import Dict, Any, Callable, Optional
from src.ui.utils.file_utils import FileUtils
from src.ui.utils.log_utils import Logger


class Aria2Downloader:
    def __init__(self):
        pass

    def download(self, download_url: str, download_dir: str,
                 progress_callback: Optional[Callable[[float, str], None]] = None) -> Dict[str, Any]:
        result = {
            'success': False,
            'zip_path': None,
            'extracted_dir': None,
            'error': None
        }

        Logger.log_info("Iniciando download do Aria2.")

        try:
            if progress_callback:
                progress_callback(10, "Preparando para baixar o Aria2...")

            dir_result = FileUtils.create_directory(download_dir)
            if not dir_result['success']:
                result['error'] = dir_result['error']
                return result

            zip_path = os.path.join(download_dir, "aria2.zip")

            def report_progress(count, block_size, total_size):
                if progress_callback and total_size > 0:
                    progress = 20 + (count * block_size * 30 / total_size)
                    progress_callback(min(progress, 50), "Baixando o Aria2...")

            try:
                urllib.request.urlretrieve(download_url, zip_path, reporthook=report_progress)
            except (urllib.error.HTTPError, urllib.error.URLError, PermissionError) as e:
                result['error'] = f"Erro ao baixar o Aria2: {str(e)}"
                return result
            except Exception as e:
                result['error'] = f"Erro inesperado: {str(e)}"
                return result

            if progress_callback:
                progress_callback(50, "Extraindo arquivos...")

            extract_result = FileUtils.extract_zip(zip_path, download_dir)
            if not extract_result['success']:
                result['error'] = extract_result['error']
                return result

            extracted_dir = None
            for item in os.listdir(download_dir):
                item_path = os.path.join(download_dir, item)
                if os.path.isdir(item_path) and "aria2" in item.lower():
                    extracted_dir = item_path
                    break

            if not extracted_dir:
                result['error'] = "Pasta extraída não encontrada."
                return result

            if progress_callback:
                progress_callback(100, "Download concluído com sucesso!")
                Logger.log_info("Download do Aria2 concluído.")

            result['success'] = True
            result['zip_path'] = zip_path
            result['extracted_dir'] = extracted_dir
            return result

        except Exception as e:
            Logger.log_error(f"Erro durante download: {str(e)}")
            result['error'] = f"Erro geral durante o processo: {str(e)}"
            return result


class Aria2Installer:
    def __init__(self):
        pass

    def install(self, extracted_dir: str, install_dir: str,
                create_shortcut: bool = True, startup_with_windows: bool = True,
                enable_rpc: bool = True, is_admin: bool = False,
                progress_callback: Optional[Callable[[float, str], None]] = None) -> Dict[str, Any]:

        result = {
            'success': False,
            'error': None
        }

        try:
            if not os.path.exists(extracted_dir):
                result['error'] = "Diretório de extração não encontrado."
                return result

            Logger.log_info("Iniciando instalação do Aria2.")

            if progress_callback:
                progress_callback(10, "Iniciando instalação...")

            dir_result = FileUtils.create_directory(install_dir)
            if not dir_result['success']:
                result['error'] = dir_result['error']
                return result

            if progress_callback:
                progress_callback(30, "Copiando arquivos...")

            files_to_copy = [
                os.path.join(extracted_dir, f)
                for f in os.listdir(extracted_dir)
                if os.path.isfile(os.path.join(extracted_dir, f))
            ]

            if not any("aria2c.exe" in f for f in files_to_copy):
                result['error'] = "Arquivo aria2c.exe não encontrado."
                return result

            copy_result = FileUtils.copy_files(files_to_copy, install_dir)
            if not copy_result['success']:
                result['error'] = copy_result['error']
                return result

            if progress_callback:
                progress_callback(50, "Configurando variáveis de ambiente...")

            try:
                path_update = f"{os.environ['PATH']};{install_dir}"
                command = ["setx"]
                if is_admin:
                    command.append("/M")
                command.extend(["PATH", path_update])

                subprocess.run(command, check=True, shell=True, capture_output=True)
            except Exception as e:
                Logger.log_warning(f"Falha ao atualizar PATH: {str(e)}")

            if progress_callback:
                progress_callback(70, "Criando arquivos de configuração...")

            conf_result = self.create_config_file(install_dir, enable_rpc)
            if not conf_result['success']:
                result['error'] = conf_result['error']
                return result

            if create_shortcut:
                self._optional_step(progress_callback, 80, "Criando atalho...",
                                    lambda: self.create_windows_shortcut(install_dir))

            if startup_with_windows:
                self._optional_step(progress_callback, 90, "Configurando inicialização...",
                                    lambda: self.setup_windows_startup(install_dir))

            if progress_callback:
                progress_callback(100, "Instalação concluída com sucesso!")

            result['success'] = True
            os.environ["PATH"] += ";" + install_dir  # ← insira isso aqui
            return result

        except Exception as e:
            Logger.log_error(f"Erro na instalação: {str(e)}")
            result['error'] = str(e)
            return result

    def _optional_step(self, callback, percent, message, func):
        if callback:
            callback(percent, message)
        try:
            func()
        except Exception as e:
            Logger.log_warning(f"Etapa opcional falhou: {str(e)}")

    def create_config_file(self, install_dir: str, enable_rpc: bool = True) -> Dict[str, Any]:
        try:
            config_dir = os.path.join(install_dir, "config")
            FileUtils.create_directory(config_dir)

            config_path = os.path.join(config_dir, "aria2.conf")
            config_lines = [
                "continue=true",
                "max-connection-per-server=16",
                "split=16",
                "dir=~/Downloads",
                "enable-dht=true"
            ]
            if enable_rpc:
                config_lines.extend([
                    "enable-rpc=true",
                    "rpc-listen-all=true",
                    "rpc-allow-origin-all=true",
                    "rpc-listen-port=6800"
                ])
            FileUtils.write_text_file(config_path, "\n".join(config_lines))

            batch_path = os.path.join(install_dir, "start_aria2.bat")
            batch_content = f"@echo off\ncd /d \"%~dp0\"\naria2c.exe --conf-path=\"{config_path}\""
            FileUtils.write_text_file(batch_path, batch_content)

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_windows_shortcut(self, install_dir: str):
        import win32com.client
        from win32com.shell import shell, shellcon

        desktop = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, 0, 0)
        shortcut_path = os.path.join(desktop, "Aria2.lnk")
        target = os.path.join(install_dir, "start_aria2.bat")

        shell_obj = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell_obj.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target
        shortcut.WorkingDirectory = install_dir
        shortcut.Description = "Iniciar Aria2"
        shortcut.IconLocation = os.path.join(install_dir, "aria2c.exe")
        shortcut.save()

    def setup_windows_startup(self, install_dir: str):
        import win32com.client
        from win32com.shell import shell, shellcon

        startup = shell.SHGetFolderPath(0, shellcon.CSIDL_STARTUP, 0, 0)
        shortcut_path = os.path.join(startup, "Aria2.lnk")
        target = os.path.join(install_dir, "start_aria2.bat")

        shell_obj = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell_obj.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target
        shortcut.WorkingDirectory = install_dir
        shortcut.Description = "Inicializar Aria2 com o Windows"
        shortcut.IconLocation = os.path.join(install_dir, "aria2c.exe")
        shortcut.save()

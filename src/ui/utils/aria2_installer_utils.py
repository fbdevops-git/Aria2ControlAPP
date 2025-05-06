#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
import subprocess
import tempfile
import shutil
import zipfile
import urllib.request
import urllib.error

from typing import Dict, Any, Callable, Optional
from src.ui.utils.file_utils import FileUtils  # Certifique-se de que está importando corretamente
from src.ui.utils.log_utils import Logger


class Aria2Downloader:
    """
    Classe responsável por realizar o download do Aria2
    """
    
    def __init__(self):
        """
        Inicializa o downloader
        """
        pass
        
    


    def download(self, download_url: str, download_dir: str,
                progress_callback: Optional[Callable[[float, str], None]] = None) -> Dict[str, Any]:
        """
        Realiza o download do Aria2
        """
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

            # Criar diretório
            dir_result = FileUtils.create_directory(download_dir)
            if not dir_result['success']:
                result['error'] = dir_result['error']
                return result

            if progress_callback:
                progress_callback(20, "Baixando o Aria2...")

            zip_path = os.path.join(download_dir, "aria2.zip")

            def report_progress(count, block_size, total_size):
                if progress_callback and total_size > 0:
                    progress = 20 + (count * block_size * 30 / total_size)
                    progress_callback(min(progress, 50), "Baixando o Aria2...")

            try:
                urllib.request.urlretrieve(download_url, zip_path, reporthook=report_progress)
            except urllib.error.HTTPError as e:
                result['error'] = f"Erro HTTP ao baixar o Aria2: Código {e.code} - {e.reason}"
                return result
            except urllib.error.URLError as e:
                result['error'] = f"Falha de conexão ao baixar o Aria2: {e.reason}"
                return result
            except PermissionError:
                result['error'] = "Permissão negada: não foi possível salvar o arquivo. Execute como administrador ou escolha outro diretório."
                return result
            except Exception as e:
                result['error'] = f"Erro inesperado ao baixar o Aria2: {str(e)}"
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
                if os.path.isdir(item_path) and item.startswith("aria2"):
                    extracted_dir = item_path
                    break

            if not extracted_dir:
                result['error'] = "Não foi possível localizar a pasta extraída do Aria2."
                return result

            if progress_callback:
                progress_callback(100, "Download concluído com sucesso!")
                Logger.log_info("Download do Aria2 concluído com sucesso.")

            result['success'] = True
            result['zip_path'] = zip_path
            result['extracted_dir'] = extracted_dir
            return result

        except Exception as e:
            Logger.log_error(f"Erro ao baixar o Aria2: {str(e)}")
            result['error'] = f"Erro geral durante o processo de download: {str(e)}"
            return result





class Aria2Installer:
    """
    Classe responsável por instalar o Aria2
    """
    
    def __init__(self):
        """
        Inicializa o instalador
        """
        pass
        


    def install(self, extracted_dir: str, install_dir: str,
            create_shortcut: bool = True, startup_with_windows: bool = True,
            enable_rpc: bool = True, is_admin: bool = False,
            progress_callback: Optional[Callable[[float, str], None]] = None) -> Dict[str, Any]:
        """
        Instala o Aria2
        """
        result = {
            'success': False,
            'error': None
        }

        try:
            if not os.path.exists(extracted_dir):
                result['error'] = "Arquivos do Aria2 não encontrados. Baixe novamente antes de instalar."
                return result

            Logger.log_info("Iniciando instalação do Aria2.")

            if progress_callback:
                progress_callback(10, "Iniciando instalação...")

            # Criar diretório de instalação
            dir_result = FileUtils.create_directory(install_dir)
            if not dir_result['success']:
                result['error'] = dir_result['error']
                return result

            if progress_callback:
                progress_callback(30, "Copiando arquivos para o diretório de instalação...")

            # Listar arquivos
            try:
                files_to_copy = [
                    os.path.join(extracted_dir, item)
                    for item in os.listdir(extracted_dir)
                    if os.path.isfile(os.path.join(extracted_dir, item))
                ]
            except PermissionError:
                result['error'] = "Permissão negada para acessar arquivos extraídos. Execute como administrador."
                return result
            except FileNotFoundError:
                result['error'] = "Arquivos extraídos não encontrados para copiar."
                return result

            # Copiar usando FileUtils
            copy_result = FileUtils.copy_files(files_to_copy, install_dir)
            if not copy_result['success']:
                result['error'] = copy_result['error']
                return result

            if progress_callback:
                progress_callback(50, "Configurando variáveis de ambiente...")

            # Atualizar PATH
            try:
                path_update = f"{os.environ['PATH']};{install_dir}"
                command = ["setx"]
                if is_admin:
                    command.append("/M")
                command.extend(["PATH", path_update])

                subprocess.run(command, check=True, shell=True, capture_output=True)

            except subprocess.CalledProcessError as e:
                if progress_callback:
                    progress_callback(50, f"Aviso: Não foi possível adicionar o diretório ao PATH: {e.stderr.decode('utf-8')}")
            except PermissionError:
                if progress_callback:
                    progress_callback(50, "Aviso: Permissão negada para alterar PATH. Execute como administrador.")

            if progress_callback:
                progress_callback(70, "Criando arquivo de configuração...")

            config_result = self.create_config_file(install_dir, enable_rpc)
            if not config_result['success']:
                if progress_callback:
                    progress_callback(70, f"Aviso: {config_result['error']}")

            if create_shortcut:
                if progress_callback:
                    progress_callback(80, "Criando atalho na área de trabalho...")

                shortcut_result = self.create_windows_shortcut(install_dir)
                if not shortcut_result['success']:
                    if progress_callback:
                        progress_callback(80, f"Aviso: {shortcut_result['error']}")

            if startup_with_windows:
                if progress_callback:
                    progress_callback(90, "Configurando inicialização automática...")

                startup_result = self.setup_windows_startup(install_dir)
                if not startup_result['success']:
                    if progress_callback:
                        progress_callback(90, f"Aviso: {startup_result['error']}")

            if progress_callback:
                Logger.log_info("Instalação do Aria2 concluída.")
                progress_callback(100, "Instalação concluída com sucesso!")
                

            result['success'] = True
            return result

        except Exception as e:
            Logger.log_error(f"Erro durante a instalação: {str(e)}")
            result['error'] = f"Erro geral durante a instalação: {str(e)}"

            return result



    def create_config_file(self, install_dir: str, enable_rpc: bool = True) -> Dict[str, Any]:
        """
        Cria o arquivo de configuração para o Aria2
        """
        result = {
            'success': False,
            'error': None
        }

        Logger.log_info("Iniciando criação do arquivo de configuração do Aria2.")

        try:
            config_dir = os.path.join(install_dir, "config")

            # Criar diretório de configuração
            dir_result = FileUtils.create_directory(config_dir)
            if not dir_result['success']:
                Logger.log_error(f"Erro ao criar diretório de configuração: {dir_result['error']}")
                result['error'] = f"Falha ao criar diretório de configuração: {dir_result['error']}"
                return result

            # Criar conteúdo do arquivo .conf
            config_content = [
                "# Configuração básica do Aria2",
                "continue=true",
                "max-connection-per-server=16",
                "min-split-size=1M",
                "split=16",
                f"dir={os.path.join(os.path.expanduser('~'), 'Downloads')}",
                "file-allocation=none",
                "check-integrity=true",
                "conditional-get=true",
                "auto-file-renaming=true",
                "allow-overwrite=false",
                "retry-wait=5",
                "max-tries=5",
                "auto-save-interval=60",
                "",
                "# Configurações de BitTorrent",
                "bt-enable-lpd=true",
                "enable-dht=true",
                "enable-peer-exchange=true",
                "bt-max-peers=0",
                "bt-request-peer-speed-limit=50K",
                "bt-save-metadata=true",
                "seed-time=0"
            ]

            if enable_rpc:
                config_content.extend([
                    "",
                    "# Configurações RPC para controle remoto",
                    "enable-rpc=true",
                    "rpc-listen-all=true",
                    "rpc-allow-origin-all=true",
                    "rpc-listen-port=6800",
                    "rpc-secret="
                ])

            config_file = os.path.join(config_dir, "aria2.conf")

            # Salvar o arquivo de configuração
            write_result = FileUtils.write_text_file(config_file, '\n'.join(config_content))
            if not write_result['success']:
                Logger.log_error(f"Erro ao escrever arquivo de configuração: {write_result['error']}")
                result['error'] = f"Falha ao criar o arquivo de configuração: {write_result['error']}"
                return result

            # Criar arquivo batch para iniciar o Aria2
            batch_file = os.path.join(install_dir, "start_aria2.bat")
            batch_content = f'@echo off\r\ncd /d "%~dp0"\r\naria2c.exe --conf-path="{config_file}"'

            batch_result = FileUtils.write_text_file(batch_file, batch_content)
            if not batch_result['success']:
                Logger.log_error(f"Erro ao criar arquivo .bat: {batch_result['error']}")
                result['error'] = f"Falha ao criar o arquivo de inicialização: {batch_result['error']}"
                return result

            Logger.log_info("Arquivo de configuração criado com sucesso.")
            result['success'] = True
            return result

        except PermissionError:
            result['error'] = "Permissão negada: Não foi possível criar arquivos de configuração. Execute como administrador."
            return result
        except Exception as e:
            Logger.log_error(f"Erro inesperado ao criar arquivos de configuração: {str(e)}")
            result['error'] = f"Erro inesperado ao criar arquivos de configuração: {str(e)}"
            return result
    

    

    def create_windows_shortcut(self, install_dir: str) -> Dict[str, Any]:
        """
        Cria um atalho na área de trabalho para o Aria2
        """
        result = {
            'success': False,
            'error': None
        }

        Logger.log_info("Tentando criar atalho na área de trabalho.")

        try:
            # Verificar dependências
            dep_result = check_and_install_dependencies()
            if not dep_result['success']:
                Logger.log_error(f"Erro ao verificar dependências: {dep_result['error']}")
                result['error'] = f"Falha ao verificar dependências: {dep_result['error']}"
                return result

            try:
                import win32com.client
                from win32com.shell import shell, shellcon
            except ImportError:
                Logger.log_error("Módulo win32com não disponível.")
                result['error'] = "Módulo win32com não disponível. Não foi possível criar o atalho."
                return result

            # Caminho do atalho na área de trabalho
            desktop = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, 0, 0)
            shortcut_path = os.path.join(desktop, "Aria2.lnk")

            # Arquivo batch para iniciar o Aria2
            target = os.path.join(install_dir, "start_aria2.bat")

            # Criar o atalho
            try:
                shell_obj = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell_obj.CreateShortCut(shortcut_path)
                shortcut.TargetPath = target
                shortcut.WorkingDirectory = install_dir
                shortcut.Description = "Iniciar Aria2 Download Manager"
                shortcut.IconLocation = os.path.join(install_dir, "aria2c.exe")
                shortcut.save()

                Logger.log_info("Atalho criado com sucesso na área de trabalho.")
                result['success'] = True
                return result

            except PermissionError:
                Logger.log_error("Permissão negada para criar o atalho.")
                result['error'] = "Permissão negada: Não foi possível criar o atalho. Execute como administrador."
                return result
            except Exception as e:
                Logger.log_error(f"Erro inesperado ao criar o atalho: {str(e)}")
                result['error'] = f"Erro inesperado ao criar o atalho: {str(e)}"
                return result

        except Exception as e:
            result['error'] = f"Erro geral durante a criação do atalho: {str(e)}"
            return result


    def setup_windows_startup(self, install_dir: str) -> Dict[str, Any]:
        """
        Configura o Aria2 para iniciar com o Windows
        """
        result = {
            'success': False,
            'error': None
        }

        Logger.log_info("Configurando inicialização automática com o Windows.")

        try:
            # Verificar dependências
            dep_result = check_and_install_dependencies()
            if not dep_result['success']:
                Logger.log_error(f"Erro ao verificar dependências: {dep_result['error']}")
                result['error'] = f"Falha ao verificar dependências: {dep_result['error']}"
                return result

            try:
                import win32com.client
                from win32com.shell import shell, shellcon
            except ImportError:
                Logger.log_error("Módulo win32com não disponível para inicialização.")
                result['error'] = "Módulo win32com não disponível. Não foi possível configurar a inicialização automática."
                return result

            # Caminho do atalho na pasta de inicialização
            startup_folder = shell.SHGetFolderPath(0, shellcon.CSIDL_STARTUP, 0, 0)
            shortcut_path = os.path.join(startup_folder, "Aria2.lnk")

            # Arquivo batch para iniciar o Aria2
            target = os.path.join(install_dir, "start_aria2.bat")

            # Criar o atalho
            try:
                shell_obj = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell_obj.CreateShortCut(shortcut_path)
                shortcut.TargetPath = target
                shortcut.WorkingDirectory = install_dir
                shortcut.Description = "Iniciar Aria2 Download Manager automaticamente"
                shortcut.IconLocation = os.path.join(install_dir, "aria2c.exe")
                shortcut.save()

                Logger.log_info("Inicialização automática configurada com sucesso.")
                result['success'] = True
                return result

            except PermissionError:
                Logger.log_error("Permissão negada ao configurar inicialização.")
                result['error'] = "Permissão negada: Não foi possível criar o atalho de inicialização. Execute como administrador."
                return result
            except Exception as e:
                Logger.log_error(f"Erro inesperado ao criar o atalho de inicialização: {str(e)}")
                result['error'] = f"Erro inesperado ao criar o atalho de inicialização: {str(e)}"
                return result

        except Exception as e:
            Logger.log_error(f"Erro inesperado ao configurar inicialização: {str(e)}")
            result['error'] = f"Erro geral ao configurar inicialização automática: {str(e)}"
            return result
    
    
    


def check_and_install_dependencies() -> Dict[str, Any]:
    """
    Verifica se as dependências necessárias estão instaladas e tenta instalá-las se necessário
        
    Returns:
        Dicionário com o resultado da operação
    """
    result = {
        'success': False,
        'error': None,
        'installed_packages': []
    }
        
    try:
        # Lista de dependências necessárias
        dependencies = ['pywin32']
            
        # Verificar cada dependência
        missing_dependencies = []
            
        for dep in dependencies:
            try:
                if dep == 'pywin32':
                    # Tentar importar módulos win32com
                    import win32com.client
                    from win32com.shell import shell, shellcon
                # Adicione mais verificações para outras dependências aqui
            except ImportError:
                missing_dependencies.append(dep)
            
        # Se não faltarem dependências, retornar sucesso
        if not missing_dependencies:
            result['success'] = True
            return result
            
        # Instalar dependências faltantes
        for dep in missing_dependencies:
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                result['installed_packages'].append(dep)
            except Exception as e:
                result['error'] = f"Não foi possível instalar a dependência '{dep}': {str(e)}"
                return result
            
        # Verificar novamente se todas as dependências estão instaladas
        try:
            if 'pywin32' in missing_dependencies:
                import win32com.client
                from win32com.shell import shell, shellcon
            # Verificar outras dependências aqui se necessário
        except ImportError as e:
            result['error'] = f"Não foi possível importar os módulos após a instalação: {str(e)}"
            return result
            
        # Se chegou até aqui, todas as dependências estão instaladas
        result['success'] = True
        return result
            
    except Exception as e:
        result['error'] = f"Erro ao verificar ou instalar dependências: {str(e)}"
        return result
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
import ctypes

class SystemInfoUtils:
    """
    Classe utilitária para obter informações do sistema
    """
    
    @staticmethod
    def check_admin() -> bool:
        """
        Verifica se o programa está sendo executado com privilégios administrativos
        
        Returns:
            True se estiver executando como administrador, False caso contrário
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    @staticmethod
    def run_as_admin(executable: str, args: str = "") -> None:
        """
        Reinicia o programa com privilégios de administrador
        
        Args:
            executable: Caminho para o executável
            args: Argumentos para o executável
        """
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, args, None, 0)
        except Exception as e:
            raise Exception(f"Não foi possível obter privilégios de administrador: {str(e)}")
    
    @staticmethod
    def get_os_info() -> dict:
        """
        Obtém informações sobre o sistema operacional
        
        Returns:
            Dicionário com informações do sistema
        """
        info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'is_64bit': platform.machine().endswith('64'),
            'python_version': platform.python_version()
        }
        
        return info
    
    @staticmethod
    def get_recommended_version() -> str:
        """
        Recomenda a versão do Aria2 com base na arquitetura do sistema
        
        Returns:
            String com a versão recomendada ("32bit" ou "64bit")
        """
        # Verificar se o sistema é 64 bit
        is_64bit = platform.machine().endswith('64')
        
        # Se for 64 bit, recomendar a versão 64 bit, caso contrário, 32 bit
        if is_64bit:
            return "64bit"
        else:
            return "32bit"
    
    @staticmethod
    def get_temp_dir() -> str:
        """
        Obtém o diretório temporário do sistema
        
        Returns:
            Caminho para o diretório temporário
        """
        import tempfile
        return tempfile.gettempdir()
    
    @staticmethod
    def get_user_home() -> str:
        """
        Obtém o diretório home do usuário
        
        Returns:
            Caminho para o diretório home do usuário
        """
        return os.path.expanduser("~")
    
    @staticmethod
    def get_program_files_dir() -> str:
        """
        Obtém o diretório Program Files do Windows
        
        Returns:
            Caminho para o diretório Program Files
        """
        return os.environ.get('PROGRAMFILES', 'C:\\Program Files')
    
    @staticmethod
    def is_windows() -> bool:
        """
        Verifica se o sistema operacional é Windows
        
        Returns:
            True se for Windows, False caso contrário
        """
        return platform.system().lower() == 'windows'
    
    @staticmethod
    def is_linux() -> bool:
        """
        Verifica se o sistema operacional é Linux
        
        Returns:
            True se for Linux, False caso contrário
        """
        return platform.system().lower() == 'linux'
    
    @staticmethod
    def is_mac() -> bool:
        """
        Verifica se o sistema operacional é MacOS
        
        Returns:
            True se for MacOS, False caso contrário
        """
        return platform.system().lower() == 'darwin'
# src/utils/aria2_status_checker.py

import subprocess
import shutil

class Aria2StatusChecker:
    @staticmethod
    def is_aria2_installed():
        """Verifica se o executável aria2c está disponível no PATH."""
        return shutil.which("aria2c") is not None

    @staticmethod
    def is_aria2_running():
        """Verifica se o processo aria2c está em execução."""
        try:
            result = subprocess.run(["tasklist"], stdout=subprocess.PIPE, text=True)
            return "aria2c.exe" in result.stdout
        except Exception:
            return False

    @staticmethod
    def get_status():
        """Retorna uma descrição textual do status do Aria2."""
        if not Aria2StatusChecker.is_aria2_installed():
            return "Aria2 não instalado"
        if not Aria2StatusChecker.is_aria2_running():
            return "Aria2 instalado, mas não está rodando"
        return "Aria2 rodando"

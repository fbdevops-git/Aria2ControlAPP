import subprocess
from src.ui.utils.aria2_rpc import Aria2RPC

class Aria2StatusChecker:
    def __init__(self, host='http://localhost', port=6800, token=None):
        self.rpc_client = Aria2RPC(host, port, token)

    def is_installed(self):
        """Verifica se o aria2c está instalado no sistema."""
        try:
            result = subprocess.run(["aria2c", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def is_running(self):
        """Verifica se o Aria2 está rodando via RPC."""
        response = self.rpc_client.get_version()
        return 'result' in response

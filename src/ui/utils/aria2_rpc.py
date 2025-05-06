import requests
from src.ui.utils.file_utils import FileUtils

class Aria2RPC:


    def __init__(self):
        # Carrega config salva
        settings = FileUtils.get_rpc_settings()
        self.url = settings["url"]
        self.token = settings["token"]


    def request(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "id": "qwer",
            "method": method,
            "params": []
        }
        if self.token:
            payload['params'].append(f"token:{self.token}")
        if params:
            payload['params'].extend(params)
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def set_options(self, options):
        """Envia opções de configuração para o Aria2."""
        return self.request("aria2.changeGlobalOption", [options])

    def get_global_stat(self):
        """Obtém estatísticas globais (velocidade total, etc)."""
        return self.request("aria2.getGlobalStat")

    def add_uri(self, uris, options=None):
        """Adiciona um novo download via link."""
        params = [uris]
        if options:
            params.append(options)
        return self.request("aria2.addUri", params)

    def get_version(self):
        """Verifica a versão do Aria2."""
        return self.request("aria2.getVersion")

    def tell_active(self):
        """Retorna downloads ativos."""
        return self.request("aria2.tellActive")

    def tell_waiting(self, offset, num):
        """Retorna downloads em espera."""
        return self.request("aria2.tellWaiting", [offset, num])

    def tell_stopped(self, offset, num):
        """Retorna downloads finalizados/parados."""
        return self.request("aria2.tellStopped", [offset, num])


# src/ui/controllers/download_controller.py

from src.ui.utils.aria2_rpc import Aria2RPC

class DownloadController:
    def __init__(self):
        self.rpc = Aria2RPC()

    def adicionar_download(self, url):
        if not url:
            raise ValueError("O link está vazio.")
        return self.rpc.add_uri([url])

    def listar_downloads(self):
        active = self.rpc.tell_active().get("result", [])
        waiting = self.rpc.tell_waiting(0, 1000).get("result", [])
        stopped = self.rpc.tell_stopped(0, 1000).get("result", [])
        return active + waiting + stopped


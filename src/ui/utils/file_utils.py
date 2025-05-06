#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import zipfile
import tempfile
import json

from typing import List, Dict, Any, Optional
from datetime import datetime

class FileUtils:
    """
    Classe utilitária para operações com arquivos
    """

    # Caminho do arquivo de configuração (salvo na pasta do usuário)
    CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".aria2_control_config.json")

    HISTORY_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "download_history.json")

    @staticmethod
    def save_config(data):
        """Salva as configurações do usuário em um arquivo JSON"""
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_config() -> dict[str, Any]:
        """Carrega as configurações salvas anteriormente"""
        if os.path.exists(FileUtils.CONFIG_PATH):
            with open(FileUtils.CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    

    @staticmethod
    def create_directory(directory: str) -> Dict[str, Any]:
        """
        Cria um diretório se ele não existir
        
        Args:
            directory: Caminho do diretório a ser criado
            
        Returns:
            Dicionário com resultado da operação
        """
        result = {
            'success': False,
            'error': None
        }
        
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            result['success'] = True
            return result
        except Exception as e:
            result['error'] = f"Não foi possível criar o diretório: {str(e)}"
            return result
    

    @staticmethod
    def delete_directory(directory: str, ignore_errors: bool = False) -> Dict[str, Any]:
        """
        Remove um diretório e todo seu conteúdo
        
        Args:
            directory: Caminho do diretório a ser removido
            ignore_errors: Se True, ignora erros durante a remoção
            
        Returns:
            Dicionário com resultado da operação
        """
        result = {
            'success': False,
            'error': None
        }
        
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory, ignore_errors=ignore_errors)
            
            result['success'] = True
            return result
        except Exception as e:
            result['error'] = f"Não foi possível remover o diretório: {str(e)}"
            return result
    

    @staticmethod
    def copy_file(source: str, destination: str) -> Dict[str, Any]:
        """
        Copia um arquivo de um local para outro
        
        Args:
            source: Caminho do arquivo de origem
            destination: Caminho de destino
            
        Returns:
            Dicionário com resultado da operação
        """
        result = {
            'success': False,
            'error': None
        }
        
        try:
            shutil.copy2(source, destination)
            
            result['success'] = True
            return result
        except Exception as e:
            result['error'] = f"Não foi possível copiar o arquivo: {str(e)}"
            return result
    

    @staticmethod
    def copy_files(files: List[str], destination_dir: str) -> Dict[str, Any]:
        """
        Copia uma lista de arquivos para um diretório
        
        Args:
            files: Lista de caminhos dos arquivos a serem copiados
            destination_dir: Diretório de destino
            
        Returns:
            Dicionário com resultado da operação
        """
        result = {
            'success': False,
            'error': None,
            'copied_files': [],
            'failed_files': []
        }
        
        # Verificar se o diretório de destino existe
        dir_result = FileUtils.create_directory(destination_dir)
        if not dir_result['success']:
            result['error'] = dir_result['error']
            return result
        
        # Copiar cada arquivo
        for file_path in files:
            if os.path.isfile(file_path):
                try:
                    # Determinar o caminho de destino
                    dest_path = os.path.join(destination_dir, os.path.basename(file_path))
                    
                    # Copiar o arquivo
                    shutil.copy2(file_path, dest_path)
                    
                    # Adicionar à lista de arquivos copiados
                    result['copied_files'].append(file_path)
                except Exception as e:
                    # Adicionar à lista de arquivos que falharam
                    result['failed_files'].append({
                        'file': file_path,
                        'error': str(e)
                    })
        
        # Se todos os arquivos foram copiados com sucesso
        if len(result['failed_files']) == 0:
            result['success'] = True
        else:
            result['error'] = f"Falha ao copiar {len(result['failed_files'])} arquivos."
        
        return result
    

    @staticmethod
    def copy_directory(source_dir: str, destination_dir: str) -> Dict[str, Any]:
        """
        Copia um diretório e todo seu conteúdo para outro local
        
        Args:
            source_dir: Diretório de origem
            destination_dir: Diretório de destino
            
        Returns:
            Dicionário com resultado da operação
        """
        result = {
            'success': False,
            'error': None
        }
        
        try:
            # Copiar diretório e seu conteúdo
            shutil.copytree(source_dir, destination_dir)
            
            result['success'] = True
            return result
        except Exception as e:
            result['error'] = f"Não foi possível copiar o diretório: {str(e)}"
            return result
    

    @staticmethod
    def extract_zip(zip_file: str, extract_dir: str) -> Dict[str, Any]:
        """
        Extrai um arquivo ZIP para um diretório
        
        Args:
            zip_file: Caminho do arquivo ZIP
            extract_dir: Diretório onde os arquivos serão extraídos
            
        Returns:
            Dicionário com resultado da operação
        """
        result = {
            'success': False,
            'error': None,
            'extracted_files': [],
            'extracted_dirs': []
        }
        
        try:
            # Verificar se o diretório de extração existe
            dir_result = FileUtils.create_directory(extract_dir)
            if not dir_result['success']:
                result['error'] = dir_result['error']
                return result
            
            # Extrair o arquivo ZIP
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                
                # Listar arquivos extraídos
                for file_info in zip_ref.infolist():
                    file_path = os.path.join(extract_dir, file_info.filename)
                    if os.path.isfile(file_path):
                        result['extracted_files'].append(file_path)
                    elif os.path.isdir(file_path):
                        result['extracted_dirs'].append(file_path)
            
            result['success'] = True
            return result
        except Exception as e:
            result['error'] = f"Não foi possível extrair o arquivo ZIP: {str(e)}"
            return result
    

    @staticmethod
    def create_zip(files: List[str], output_zip: str) -> Dict[str, Any]:
        """
        Cria um arquivo ZIP contendo os arquivos especificados
        
        Args:
            files: Lista de caminhos dos arquivos a serem adicionados ao ZIP
            output_zip: Caminho do arquivo ZIP a ser criado
            
        Returns:
            Dicionário com resultado da operação
        """
        result = {
            'success': False,
            'error': None,
            'zip_file': None
        }
        
        try:
            # Criar diretório de saída se necessário
            output_dir = os.path.dirname(output_zip)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Criar arquivo ZIP
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in files:
                    if os.path.isfile(file_path):
                        # Adicionar arquivo ao ZIP com o nome do arquivo (sem o caminho)
                        zip_file.write(file_path, arcname=os.path.basename(file_path))
            
            result['success'] = True
            result['zip_file'] = output_zip
            return result
        except Exception as e:
            result['error'] = f"Não foi possível criar o arquivo ZIP: {str(e)}"
            return result
    

    @staticmethod
    def get_temp_directory() -> str:
        """
        Obtém o caminho para um diretório temporário único
        
        Returns:
            Caminho para um diretório temporário
        """
        return tempfile.mkdtemp()
    

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        Obtém o tamanho de um arquivo em bytes
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Tamanho do arquivo em bytes
        """
        if os.path.isfile(file_path):
            return os.path.getsize(file_path)
        return 0
    

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Formata o tamanho de um arquivo para exibição
        
        Args:
            size_bytes: Tamanho em bytes
            
        Returns:
            String formatada com o tamanho
        """
        # Definir unidades
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        
        # Converter para a unidade apropriada
        unit_index = 0
        while size_bytes >= 1024 and unit_index < len(units) - 1:
            size_bytes /= 1024
            unit_index += 1
        
        # Formatar com 2 casas decimais
        return f"{size_bytes:.2f} {units[unit_index]}"
    

    @staticmethod
    def list_directory(directory: str, include_dirs: bool = True, 
                       include_files: bool = True) -> Dict[str, Any]:
        """
        Lista arquivos e diretórios em um diretório
        
        Args:
            directory: Diretório a ser listado
            include_dirs: Se True, inclui diretórios na listagem
            include_files: Se True, inclui arquivos na listagem
            
        Returns:
            Dicionário com resultado da operação
        """
        result = {
            'success': False,
            'error': None,
            'items': []
        }
        
        try:
            if not os.path.exists(directory):
                result['error'] = f"O diretório não existe: {directory}"
                return result
            
            # Obter lista de itens
            items = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                
                if os.path.isdir(item_path) and include_dirs:
                    items.append({
                        'name': item,
                        'path': item_path,
                        'type': 'directory',
                        'size': 0
                    })
                elif os.path.isfile(item_path) and include_files:
                    size = FileUtils.get_file_size(item_path)
                    items.append({
                        'name': item,
                        'path': item_path,
                        'type': 'file',
                        'size': size,
                        'size_formatted': FileUtils.format_file_size(size)
                    })
            
            result['success'] = True
            result['items'] = items
            return result
        except Exception as e:
            result['error'] = f"Não foi possível listar o diretório: {str(e)}"
            return result
    

    @staticmethod
    def write_text_file(file_path: str, content: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Escreve conteúdo em um arquivo de texto
        
        Args:
            file_path: Caminho do arquivo
            content: Conteúdo a ser escrito
            encoding: Codificação do arquivo
            
        Returns:
            Dicionário com resultado da operação
        """
        result = {
            'success': False,
            'error': None
        }
        
        try:
            # Criar diretório se necessário
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Escrever arquivo
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            result['success'] = True
            return result
        except Exception as e:
            result['error'] = f"Não foi possível escrever no arquivo: {str(e)}"
            return result
    

    @staticmethod
    def read_text_file(file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Lê o conteúdo de um arquivo de texto
        
        Args:
            file_path: Caminho do arquivo
            encoding: Codificação do arquivo
            
        Returns:
            Dicionário com resultado da operação
        """
        result = {
            'success': False,
            'error': None,
            'content': None
        }
        
        try:
            if not os.path.isfile(file_path):
                result['error'] = f"O arquivo não existe: {file_path}"
                return result
            
            # Ler arquivo
            with open(file_path, 'r', encoding=encoding) as f:
                result['content'] = f.read()
            
            result['success'] = True
            return result
        except Exception as e:
            result['error'] = f"Não foi possível ler o arquivo: {str(e)}"
            return result
        

    @staticmethod
    def clean_temp_directory(path: str) -> Dict[str, Any]:
        """
        Remove um diretório temporário de forma segura

        Args:
            path: Caminho do diretório a ser removido

        Returns:
            Dicionário com o resultado da operação
        """
        return FileUtils.delete_directory(path, ignore_errors=True)
    

    @staticmethod
    def save_download_history(entry: dict):
        """Salva uma entrada no histórico de downloads"""
        if not os.path.exists(FileUtils.HISTORY_PATH):
            with open(FileUtils.HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

        with open(FileUtils.HISTORY_PATH, "r", encoding="utf-8") as f:
            history = json.load(f)

        history.append(entry)

        with open(FileUtils.HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)


    @staticmethod
    def load_download_history():
        """Carrega o histórico de downloads (lista de dicionários)"""
        if os.path.exists(FileUtils.HISTORY_PATH):
            with open(FileUtils.HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return []


    @staticmethod
    def get_rpc_settings():
        """Retorna host, porta e token salvos, ou valores padrão"""
        config = FileUtils.load_config()

        host = config.get("rpc_url", "http://localhost")
        port = config.get("rpc_port", "6800")
        secret = config.get("rpc_secret", "")

        return {
            "url": f"{host}:{port}/jsonrpc",
            "token": secret
        }



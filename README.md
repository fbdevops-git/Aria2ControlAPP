# Aria2ControlAPP

Interface gráfica para gerenciamento de downloads utilizando o Aria2.

## Visão Geral
O **Aria2ControlAPP** é uma aplicação desenvolvida em Python com interface Tkinter, projetada para facilitar o controle do Aria2, um cliente de download leve e multiprotocolo.

Ele oferece recursos como:
- Instalação automática do Aria2
- Adição e gerenciamento de downloads
- Pausar, continuar e parar downloads individualmente
- Monitoramento em tempo real de velocidade e progresso
- Notificações com som ao concluir downloads
- Histórico persistente de downloads

## Tecnologias Utilizadas
- **Python 3.13**
- **Tkinter**
- **JSON-RPC** (para comunicação com Aria2)
- **Plyer** (notificações)
- **Playsound** (efeito sonoro)

## Estrutura do Projeto
```
Area2ControlAPP/
├── src/
│   ├── assets/sounds/
│   ├── data/                    # Histórico de downloads
│   ├── logs/                   # Log da aplicação
│   ├── ui/
│   │   ├── controllers/        # DownloadController
│   │   ├── utils/              # Funções auxiliares (RPC, instalação, status, logs)
│   │   ├── main_window.py      # Interface principal
│   │   ├── settings_window.py  # Configurações do Aria2
│   │   ├── network_window.py   # Configurações de rede (opcional)
│   │   ├── history_window.py   # Janela de histórico
│   │   …
├── venv/ (ignorado)
├── README.md
├── requirements.txt
├── .gitignore
```

## Instalação
1. Instale o Python 3.13 (64 bits recomendado)
2. Clone o repositório:
```bash
git clone https://github.com/fbdevops-git/Aria2ControlAPP.git
cd Aria2ControlAPP
```
3. Crie e ative o ambiente virtual:
```bash
python -m venv venv
venv\Scripts\activate  # no Windows
```
4. Instale as dependências:
```bash
pip install -r requirements.txt
```
5. Execute o aplicativo:
```bash
python -m src.main
```

## Licença
Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Contribuições
Ainda não está aberto para colaboração externa. Caso queira sugerir melhorias, entre em contato com o autor via GitHub.

---
**Desenvolvido por [fbdevops-git](https://github.com/fbdevops-git)**

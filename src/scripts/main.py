import os
import sys
# Caminho para encontrar a pasta 'src'
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)
import logging
import socket
from datetime import datetime
from data.conexaoGupy import conexaoGupy
from data.conexaoSenior import DatabaseSenior
from ponteSeniorGupy import ponteSeniorGupy
from utils.config import dict_extract

class main:
    def __init__(self):
        self.bancoSenior = DatabaseSenior()
        self.bancoSenior.conexaoBancoSenior()
        self.apiGupy = conexaoGupy()
        self.ponteSenioGupy = ponteSeniorGupy()
        self.colaboradores = []
    @staticmethod
    
    def logs():
        nome_host = socket.gethostname()
        ip_local = socket.gethostbyname(nome_host)
        diretorioLocal = os.getcwd()
        log_directory = f"{diretorioLocal}/Logs" 
        
        if not os.path.exists(log_directory):
            os.makedirs(log_directory) #caso a pasta nao exista ele vai criar

        current_datetime = datetime.now()
        log_filename = os.path.join(log_directory, current_datetime.strftime("%Y-%m-%d") + "_log_.log") #declara o nome do arquivo log
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            encoding='utf-8',
            datefmt="%Y-%m-%d %H:%M:%S",
            filename=log_filename, 
            force=True
        )
        logging.info(f"-------------->>>Informações do executor--------------")
        logging.info(f"IPV4: {ip_local}")
        logging.info(f"HOST: {nome_host}") 

    logs()
    
if __name__ == "__main__":
    conexao = DatabaseSenior(**dict_extract["Senior"]).conexaoBancoSenior()
    # print(conexao) # Recebendo
    colaboradores = DatabaseSenior.buscaColaboradorSenior(conexao)
    # print(colaboradores) # Recebendo
    ponte = ponteSeniorGupy()
    ligacao = ponte.verificaColaboradores(colaboradores)
    
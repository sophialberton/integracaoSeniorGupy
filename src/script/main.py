import os
import sys
# Caminho para encontrar a pasta 'src'
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)
import logging
import socket

from datetime import datetime
from ponteSeniorGupy import ponteSeniorGupy
from data.conexaoGupy import conexaoGupy
from data.conexaoGraph import conexaoGraph
from data.conexaoSenior import conexaoSenior
banco = conexaoSenior(
    host_senior=os.getenv("host_senior"),
    port_senior=os.getenv("port_senior"),
    service_name_senior=os.getenv("service_name_senior"),
    user_senior=os.getenv("user_senior"),
    password_senior=os.getenv("password_senior")
)
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())  # Isso garante que o .env será encontrado corretamente

from utils.config import dict_extract
from utils.config import email_log, dict_extract

def configurar_logs():
    """Configura o sistema de logging para registrar as operações em um arquivo e no console."""
    log_directory = os.path.join(os.getcwd(), "Logs")
    os.makedirs(log_directory, exist_ok=True)
    log_filename = os.path.join(log_directory, datetime.now().strftime("%Y-%m-%d") + "_log.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding='utf-8',
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(log_filename), logging.StreamHandler(sys.stdout)],
        force=True
    )
    logging.info(f"Executando em: HOST={socket.gethostname()}, IP={socket.gethostbyname(socket.gethostname())}")  

class main:
    
    def __init__(self):
        load_dotenv(find_dotenv())
        self.conexao_senior = conexaoSenior(**dict_extract["Senior"])
        self.apiGupy = conexaoGupy()
        self.ponteSenioGupy = ponteSeniorGupy()
        self.utilitarios = conexaoGraph()
        self.colaboradores = []

    def enviar_log_diario(self):
        """Envia o log do dia atual como anexo via Graph API."""
        log_directory = r"C:\github\integracaoSeniorGupy\Logs"
        log_filename = os.path.join(log_directory, datetime.now().strftime("%Y-%m-%d") + "_log.log")

        if not os.path.exists(log_filename):
            logging.warning(f"Log do dia não encontrado: {log_filename}")
            return

        assunto = "Log Diário - Integração Gupy"
        corpo = "Segue em anexo o log diário referente a automação de cadastros e atualizações de colaboradores na plataforma gupy."

        self.utilitarios.enviar_email_log(email_log, log_filename, assunto, corpo)

    def executar(self):
            """Ponto de entrada principal que executa todo o processo."""
            logging.info(">>> Iniciando processo de envio de e-mails.")
            # Garante a conexão com o banco de dados antes de prosseguir
            if not self.conexao_senior.conexaoBancoSenior():
                logging.error("Falha ao conectar no banco de dados. Encerrando execução.")
                return

            try:
                # 1. Busca os dados brutos dos colaboradores
                colaboradores_df = self.conexao_senior.consultaDadosSenior()
                if colaboradores_df.empty:
                    logging.warning("Nenhum colaborador encontrado. Encerrando execução.")
                    return
                # Codigo
                ponte = ponteSeniorGupy()
                ligacao = ponte.processar_colaboradores(colaboradores_df)

            finally:
                # Garante que a conexão com o banco de dados seja sempre fechada
                self.conexao_senior.desconectar()
                logging.info(">>> Processo finalizado.")
                self.enviar_log_diario()

if __name__ == "__main__":
    configurar_logs()
    main_app = main()
    main_app.executar()
    
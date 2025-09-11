import os
import sys
import logging
import socket
from datetime import datetime
from dotenv import load_dotenv

# Adiciona o caminho do projeto ao sys.path
project_path = os.path.abspath(os.path.dirname(__file__))
if project_path not in sys.path:
    sys.path.append(project_path)

from connectors.senior_connector import SeniorConnector
from connectors.gupy_connector import GupyConnector
from connectors.graph_connector import GraphConnector
from services.collaborator_service import CollaboratorService
from config.settings import (
    SENIOR_CONFIG, GUPY_CONFIG, GRAPH_CONFIG, EMAIL_LOG,
    IGNORED_CPFS_PATH, LOG_DIRECTORY
)

def setup_logging():
    """Configura o sistema de logging."""
    os.makedirs(LOG_DIRECTORY, exist_ok=True)
    log_filename = os.path.join(LOG_DIRECTORY, f"{datetime.now().strftime('%Y-%m-%d')}_log.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding='utf-8',
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(log_filename), logging.StreamHandler(sys.stdout)],
        force=True
    )
    logging.info(f"Executando em: HOST={socket.gethostname()}, IP={socket.gethostbyname(socket.gethostname())}")

class Main:
    """Classe principal que orquestra a integração."""
    def __init__(self):
        load_dotenv()
        self.senior_connector = SeniorConnector(**SENIOR_CONFIG)
        self.gupy_connector = GupyConnector(**GUPY_CONFIG)
        self.graph_connector = GraphConnector(**GRAPH_CONFIG)
        self.collaborator_service = CollaboratorService(self.gupy_connector, IGNORED_CPFS_PATH)

    def run(self):
        """Executa o processo de integração."""
        logging.info(">>> Iniciando processo de integração Senior-Gupy.")
        if not self.senior_connector.connect():
            logging.error("Falha ao conectar no banco de dados Senior. Encerrando execução.")
            return

        try:
            collaborators_df = self.senior_connector.get_collaborators_data()
            if collaborators_df.empty:
                logging.warning("Nenhum colaborador encontrado. Encerrando execução.")
                return

            self.collaborator_service.process_collaborators(collaborators_df)

        finally:
            self.senior_connector.disconnect()
            logging.info(">>> Processo finalizado.")
            self.send_daily_log()

    def send_daily_log(self):
        """Envia o log diário por e-mail."""
        log_filename = os.path.join(LOG_DIRECTORY, f"{datetime.now().strftime('%Y-%m-%d')}_log.log")
        if not os.path.exists(log_filename):
            logging.warning(f"Log do dia não encontrado: {log_filename}")
            return

        subject = "Log Diário - Integração Gupy"
        body = "Segue em anexo o log diário referente à automação de cadastros e atualizações de colaboradores na plataforma Gupy."
        self.graph_connector.send_email_with_attachment(EMAIL_LOG, subject, body, log_filename)

if __name__ == "__main__":
    setup_logging()
    main_app = Main()
    main_app.run()
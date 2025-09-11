import logging
import os
import socket
from datetime import datetime

from servicos.conexao_senior import ServicoSenior
from servicos.conexao_gupy import ServicoGupy
from servicos.servico_email import ServicoEmail
from utils.colaboradores import processar_colaboradores
from config import (
    DB_CONFIG,
    EMAIL_CONFIG,
    GUPY_TOKEN
)

def configurar_logs():
    """Configura o sistema de logging."""
    log_directory = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_directory, exist_ok=True)
    log_filename = os.path.join(log_directory, f"{datetime.now().strftime('%Y-%m-%d')}_log.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding='utf-8',
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
        force=True
    )
    logging.info(f"Executando em: HOST={socket.gethostname()}, IP={socket.gethostbyname(socket.gethostname())}")

def main():
    """Função principal que orquestra a integração."""
    configurar_logs()
    logging.info(">>> Iniciando processo de integração Senior-Gupy.")

    servico_senior = ServicoSenior(**DB_CONFIG)
    servico_gupy = ServicoGupy(GUPY_TOKEN)
    
    try:
        if not servico_senior.conectar():
            logging.error("Não foi possível conectar ao banco de dados Senior. Encerrando.")
            return

        colaboradores_df = servico_senior.consultar_dados_senior()

        if colaboradores_df.empty:
            logging.warning("Nenhum colaborador encontrado na consulta. Encerrando.")
            return
        
        processar_colaboradores(servico_gupy, colaboradores_df)

    except Exception as e:
        logging.critical(f"Ocorreu um erro inesperado no processo principal: {e}", exc_info=True)
    finally:
        servico_senior.desconectar()
        logging.info(">>> Processo finalizado.")
        
        # Envio de log por e-mail
        servico_email = ServicoEmail(**EMAIL_CONFIG)
        log_directory = os.path.join(os.getcwd(), "logs")
        log_filename = os.path.join(log_directory, f"{datetime.now().strftime('%Y-%m-%d')}_log.log")
        
        if os.path.exists(log_filename):
            assunto = "Log Diário - Integração Gupy"
            corpo = "Segue em anexo o log da execução de hoje."
            servico_email.enviar_email_com_anexo(EMAIL_CONFIG['destinatario'], assunto, corpo, log_filename)
        else:
            logging.warning(f"Arquivo de log não encontrado: {log_filename}")

if __name__ == "__main__":
    main()
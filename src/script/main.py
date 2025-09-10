import os
import sys
import logging
import socket
from datetime import datetime

# Caminho para encontrar a pasta 'src'
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from data.conexaoGupy import conexaoGupy
from data.conexaoGraph import conexaoGraph
from data.conexaoSenior import conexaoSenior
from utils.colaboradores import (
    carregar_cpfs_ignorados,
    classificar_usuarios_df,
    agrupar_por_cpf_df,
    processar_cpf_df,
)
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from utils.config import dict_extract, email_log

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

class Main:
    def __init__(self):
        self.conexao_senior = conexaoSenior(**dict_extract["Senior"])
        self.apiGupy = conexaoGupy()
        self.utilitarios = conexaoGraph()

    def enviar_log_diario(self):
        """Envia o log do dia atual como anexo via Graph API."""
        log_directory = os.path.join(os.getcwd(), "Logs")
        log_filename = os.path.join(log_directory, datetime.now().strftime("%Y-%m-%d") + "_log.log")

        if not os.path.exists(log_filename):
            logging.warning(f"Log do dia não encontrado: {log_filename}")
            return

        assunto = "Log Diário - Integração Gupy"
        corpo = "Segue em anexo o log diário referente a automação de cadastros e atualizações de colaboradores na plataforma gupy."
        self.utilitarios.enviar_email_log(email_log, log_filename, assunto, corpo)

    def executar(self):
        """Ponto de entrada principal que executa todo o processo."""
        logging.info(">>> Iniciando processo de integração Senior-Gupy.")
        if not self.conexao_senior.conexaoBancoSenior():
            logging.error("Falha ao conectar no banco de dados. Encerrando execução.")
            return

        try:
            colaboradores_df = self.conexao_senior.consultaDadosSenior()
            if colaboradores_df.empty:
                logging.warning("Nenhum colaborador encontrado. Encerrando execução.")
                return

            logging.info("> Iniciando verificação de colaboradores")
            cpfs_ignorados = carregar_cpfs_ignorados('src/data/ignoradosRH.csv')
            print(f"> CPFs ignorados carregados: {len(cpfs_ignorados)}")

            df_validos, df_invalidos, df_ignorados = classificar_usuarios_df(colaboradores_df, cpfs_ignorados)
            df_nao_ignorados = pd.concat([df_validos, df_invalidos], ignore_index=True)
            usuarios_ativos_sem_email = df_invalidos[df_invalidos['Situacao'] != 7]

            print(f"> Total de registros: {len(df_nao_ignorados)}")
            print(f"> Total de registros ignorados (RH e Diretorias): {len(df_ignorados)}")
            print(f"> Total de registros validos (Com email valido para criar usuario Gupy): {len(df_validos)}")
            print(f"> Total de registros invalidos (Sem email valido para criar usuario Gupy): {len(df_invalidos)}")
            print(f"> Total de registros ATIVOS SEM EMAIL (Deve criar usuario mas nao eh possivel por ausensia de email valido): {len(usuarios_ativos_sem_email)}")
            logging.info(f"> Total de registros: {len(df_nao_ignorados)}")
            logging.info(f"> Total de registros ignorados (RH e Diretorias): {len(df_ignorados)}")
            logging.info(f"> Total de registros validos (Com email valido para criar usuario Gupy): {len(df_validos)}")
            logging.info(f"> Total de registros invalidos (Sem email valido para criar usuario Gupy): {len(df_invalidos)}")
            logging.info(f"> Total de registros ATIVOS SEM EMAIL (Deve criar usuario mas nao eh possivel por ausensia de email valido): {len(usuarios_ativos_sem_email)}")

            logging.info("> Agrupando colaboradores por CPF")
            usuarios_por_cpf = agrupar_por_cpf_df(df_nao_ignorados)
            print(f"> Total de CPFs agrupados: {len(usuarios_por_cpf)}")
            logging.info("> Iniciando processamento por CPF")

            for cpf, registros_df in usuarios_por_cpf.items():
                logging.warning(f"> Processando CPF: {cpf}")
                processar_cpf_df(self.apiGupy, cpf, registros_df)

        finally:
            self.conexao_senior.desconectar()
            logging.info(">>> Processo finalizado.")
            self.enviar_log_diario()

if __name__ == "__main__":
    configurar_logs()
    main_app = Main()
    main_app.executar()
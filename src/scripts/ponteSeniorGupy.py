import sys
import os
import logging
import pandas as pd
from dotenv import load_dotenv,find_dotenv
from collections import defaultdict
from data.conexaoGupy import conexaoGupy
from data.conexaoSenior import DatabaseSenior

from utils.colaboradores  import (
    carregar_cpfs_ignorados,
    classificar_usuarios_df,
    agrupar_por_cpf_df,
    processar_cpf_df
)
# Caminho para encontrar a pasta 'src'
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)
    
class ponteSeniorGupy():
    def __init__(self,):
        load_dotenv(find_dotenv())
        self.data = []   
        self.conexaoSenior = DatabaseSenior()
        self.connection = None  # Declara conexão como None
        self.cursor = None # Declara cursor como None

    def dadosSenior(self, colaboradores_df):
        try:
            df = colaboradores_df[['Nome','Branch_gupy','Role_gupy,','Departamento_gupy','Filial_cod','Matricula','Cpf', 'Situacao', 'Email']].copy()
            return df
        except Exception as e:
            logging.error(f"Erro ao preparar dados do Senior: {e}")
            return pd.DataFrame(columns=['Nome','Branch_gupy','Role_gupy,','Departamento_gupy','Filial_cod','Matricula','Cpf', 'Situacao', 'Email'])

    def verificaColaboradores(self, colaboradores):
        logging.info("> Iniciando verificação de colaboradores")
        api = conexaoGupy()
        df_usuarios = self.dadosSenior(colaboradores)
        
        # Carregar CPFs ignorados
        cpfs_ignorados = carregar_cpfs_ignorados('src/data/ignoradosRH.csv')
        # Classificar os usuários
        df_validos, df_invalidos, df_ignorados = classificar_usuarios_df(df_usuarios, cpfs_ignorados)
        # Juntar todos os não ignorados (válidos + inválidos)
        df_nao_ignorados = pd.concat([df_validos, df_invalidos], ignore_index=True)
        # Filtrar usuários ativos sem e-mail válido
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

        # Agrupar por CPF
        logging.info("> Agrupando colaboradores por CPF")
        usuarios_por_cpf = agrupar_por_cpf_df(df_nao_ignorados)
        print(f"> Total de CPFs agrupados: {len(usuarios_por_cpf)}")
        logging.info("> Iniciando processamento por CPF")
        for cpf, registros_df in usuarios_por_cpf.items():
            processar_cpf_df(api, cpf, registros_df)
        logging.info("> Verificação de colaboradores concluída")

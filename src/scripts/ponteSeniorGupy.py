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
    processar_cpf_df,
)
from utils.camposCadastros import processar_campos
from utils.helpers import textoPadrao

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
            # Normaliza apenas as colunas desejadas
            for col in ['Branch_gupy', 'Role_gupy,', 'Departamento_gupy']:
                df[col] = df[col].apply(textoPadrao)
            return df
        except Exception as e:
            logging.error(f"Erro ao preparar dados do Senior: {e}")
            return pd.DataFrame(columns=['Nome','Branch_gupy','Role_gupy,','Departamento_gupy','Filial_cod','Matricula','Cpf', 'Situacao', 'Email'])

    def processar_colaboradores(self, colaboradores):
        logging.info("> Iniciando verificação de colaboradores")
        
        api = conexaoGupy()
        df_usuarios = self.dadosSenior(colaboradores)
        # para ver se a formatação chegou certinho
        pd.set_option('display.max_columns', None) # Para mostrar todas colunas
        # logging.info(df_usuarios) # Recebendo!
        # print(df_usuarios)
        # Carregar CPFs ignorados
        
        cpfs_ignorados = carregar_cpfs_ignorados('src/data/ignoradosRH.csv')
        print(f"> CPFs ignorados carregados: {len(cpfs_ignorados)}")
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
            logging.info(f"> Processando CPF: {cpf}")
            resultado = processar_cpf_df(api, cpf, registros_df)

            if not resultado or not resultado.get("usuario"):
                logging.warning(f"> Nenhum resultado válido para CPF {cpf}")
                continue

            usuario = resultado["usuario"]
            campos = resultado["campos"]

            # Garante que todas as chaves existam
            department_id = campos.get("departmentId", 0)
            role_id = campos.get("roleId", 0)
            branch_ids = campos.get("branchIds", [0])
            branch_id = branch_ids[0] if branch_ids != [0] else None

            campos_faltam = (
                department_id == 0 or
                role_id == 0 or
                branch_id is None
            )

            if campos_faltam:
                nome_base = registros_df.iloc[0]['Nome']
                email_base = registros_df.iloc[0]['Email']
                nomeFilialBranch = registros_df.iloc[0].get('Branch_gupy', 'Filial Padrão')

                campos_corrigidos = processar_campos(
                    api,
                    nome_base,
                    email_base,
                    usuario["userGupyId"],
                    usuario["emailUserGupy"],
                    department_id if department_id != 0 else None,
                    role_id if role_id != 0 else None,
                    branch_id,
                    nomeFilialBranch,
                    registros_df
                )

                logging.info(f"> Usuário com email {usuario['emailUserGupy']} teve campos atualizados: {campos_corrigidos}")
            else:
                logging.info(f"> Usuário com email {usuario['emailUserGupy']} já possui todos os campos. Nenhuma ação necessária.")

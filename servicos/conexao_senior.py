# servicos/conexao_senior.py

import oracledb
import pandas as pd
import logging
import time
from utils.helpers import padronizar_texto

class ServicoSenior:
    """Classe para gerenciar a conexão e consulta ao banco de dados Senior."""
    
    def __init__(self, user_senior, password_senior, host_senior, port_senior, service_name_senior):
        self.user = user_senior
        self.password = password_senior
        self.host = host_senior
        self.port = port_senior
        self.service_name = service_name_senior
        self.connection = None
        
    def conectar(self, tentativas=3, atraso=5):
        """Tenta estabelecer a conexão com o banco de dados Oracle."""
        if not all([self.user, self.password, self.host, self.port, self.service_name]):
            logging.error("Parâmetros de conexão com o Senior estão ausentes ou incompletos.")
            return False

        dsn = oracledb.makedsn(self.host, self.port, service_name=self.service_name)
        
        for tentativa in range(tentativas):
            try:
                self.connection = oracledb.connect(user=self.user, password=self.password, dsn=dsn)
                logging.info("Conexão com o banco de dados Senior estabelecida com sucesso.")
                return True
            except oracledb.DatabaseError as e:
                logging.error(f"Erro ao conectar ao Senior (tentativa {tentativa + 1}/{tentativas}): {e}")
                if tentativa < tentativas - 1:
                    time.sleep(atraso)
        return False

    def desconectar(self):
        """Fecha a conexão com o banco de dados de forma segura."""
        if self.connection:
            self.connection.close()
            logging.info("Conexão com o banco de dados Senior fechada.")

    def consultar_dados_senior(self):
        """Executa a consulta SQL para buscar colaboradores e retorna um DataFrame tratado."""
        if not self.connection:
            logging.error("Conexão com o Senior não estabelecida. Consulta cancelada.")
            return pd.DataFrame()

        # A query não foi alterada, conforme solicitado.
        query = """
        SELECT
            FUN.NOMFUN AS Nome,
            CASE
                WHEN E.NOMCCU LIKE '%VENDAS%' THEN F.NOMFIL || ' - ' || E.NOMCCU
                ELSE F.NOMFIL
            END AS "Branch_gupy",
            CAR.TITCAR || ' - ' || R.DESSIS AS "Role_gupy" ,
            CASE
                WHEN UPPER(G.NOMLOC) LIKE '%VENDAS%'
                OR UPPER(G.NOMLOC) LIKE '%REGIÃO%' THEN E.NOMCCU
                ELSE E.NOMCCU || ' - ' || G.NOMLOC
            END AS "Departamento_gupy",
            FUN.NUMEMP AS "Filial_cod",
            FUN.NUMCAD AS Matricula,
            FUN.NUMCPF AS Cpf,
            FUN.SITAFA AS Situacao,
            EM.EMACOM AS Email
        FROM
            SENIOR.R034FUN FUN
            INNER JOIN SENIOR.R024CAR CAR ON FUN.CODCAR = CAR.CODCAR AND FUN.ESTCAR = CAR.ESTCAR
            JOIN SENIOR.R018CCU E ON E.NUMEMP = FUN.NUMEMP AND E.CODCCU = FUN.CODCCU
            JOIN SENIOR.R030FIL F ON FUN.NUMEMP = F.NUMEMP AND FUN.CODFIL = F.CODFIL
            JOIN SENIOR.R016ORN G ON G.TABORG = FUN.TABORG AND G.NUMLOC = FUN.NUMLOC
            LEFT JOIN SENIOR.R024SIS R ON CAR.SISCAR = R.SISCAR
            LEFT JOIN SENIOR.R034CPL EM ON FUN.NUMEMP = EM.NUMEMP AND FUN.NUMCAD = EM.NUMCAD AND FUN.TIPCOL = EM.TIPCOL
        WHERE
            FUN.NUMEMP IN (219, 220, 221, 620)
            AND FUN.TIPCOL = 1
            --AND FUN.SITAFA <> 7
            AND FUN.CODCAR NOT IN (110355)
        ORDER BY
            FUN.NUMEMP, FUN.CODFIL, FUN.NUMCAD
        """
        try:
            df = pd.read_sql_query(query, self.connection)
            df.columns = ['Nome', 'Branch_gupy', 'Role_gupy', 'Departamento_gupy', 'Filial_cod', 'Matricula', 'Cpf', 'Situacao', 'Email']
            
            # Padronização dos dados acontece aqui, centralizando a responsabilidade.
            for col in ['Branch_gupy', 'Role_gupy', 'Departamento_gupy', 'Nome']:
                df[col] = df[col].apply(padronizar_texto)
            
            logging.info(f"Consulta ao Senior retornou {len(df)} registros.")
            return df
        except (oracledb.DatabaseError, pd.io.sql.DatabaseError) as e:
            logging.error(f"Erro ao executar a consulta no Senior: {e}")
            return pd.DataFrame()
import oracledb
import logging
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import time
from utils.helpers import textoPadrao

load_dotenv(find_dotenv())

class conexaoSenior:
    def __init__(self, **kwargs):
        self.connection = None
        self.cursor = None
        self.user_senior = kwargs.get("user_senior")
        self.password_senior = kwargs.get("password_senior")
        self.host_senior = kwargs.get("host_senior")
        self.port_senior = kwargs.get("port_senior")
        self.service_name_senior = kwargs.get("service_name_senior")

    def conexaoBancoSenior(self, tentativas=3, atraso=5):
        if not all([self.host_senior, self.port_senior, self.service_name_senior]):
            logging.error("Parâmetros de conexão ausentes: host, porta ou service_name estão nulos.")
            return False

        dsn_str = oracledb.makedsn(self.host_senior, self.port_senior, service_name=self.service_name_senior)

        for tentativa in range(tentativas):
            try:
                self.connection = oracledb.connect(user=self.user_senior, password=self.password_senior, dsn=dsn_str)
                self.cursor = self.connection.cursor()
                logging.info("-------------->>>Informacoes da Database--------------")
                logging.info(">Conexao com o banco de dados estabelecida com sucesso")
                return True
            except oracledb.DatabaseError as e:
                logging.error(f">Erro ao estabelecer conexão (tentativa {tentativa + 1}/{tentativas}): {e}")
                if tentativa < tentativas - 1:
                    logging.info(f"Tentando novamente em {atraso} segundos...")
                    time.sleep(atraso)
                else:
                    logging.error("Não foi possível conectar ao banco de dados após várias tentativas.")
                    return False
        return False

    def desconectar(self):
        if self.cursor:
            try:
                self.cursor.close()
                logging.info(">Cursor fechado.")
            except oracledb.DatabaseError as e:
                logging.error(f">Erro ao fechar o cursor: {e}")
            finally:
                self.cursor = None
        if self.connection:
            try:
                self.connection.close()
                logging.info(">Conexão com o banco de dados fechada.")
            except oracledb.DatabaseError as e:
                logging.error(f">Erro ao fechar a conexão: {e}")
            finally:
                self.connection = None

    def consultaDadosSenior(self):
        if not self.connection:
            logging.error("> Conexao com o banco de dados não foi estabelecida.")
            return pd.DataFrame()

        query = """
                SELECT
                    FUN.NOMFUN AS Nome,
                    CASE WHEN E.NOMCCU LIKE '%VENDAS%' THEN F.NOMFIL || ' - ' || E.NOMCCU ELSE F.NOMFIL END AS "Branch_gupy",
                    CAR.TITCAR || ' - ' || R.DESSIS AS "Role_gupy" ,
                    CASE WHEN UPPER(G.NOMLOC) LIKE '%VENDAS%' OR UPPER(G.NOMLOC) LIKE '%REGIÃO%' THEN E.NOMCCU ELSE E.NOMCCU || ' - ' || G.NOMLOC END AS "Departamento_gupy",
                    FUN.NUMEMP AS "Filial_cod",
                    FUN.NUMCAD AS Matricula,
                    FUN.NUMCPF AS Cpf,
                    FUN.SITAFA AS Situacao,
                    EM.EMACOM AS Email,
                    S.INIETB,
                    S.FIMETB
                FROM SENIOR.R034FUN FUN
                INNER JOIN SENIOR.R024CAR CAR ON FUN.CODCAR = CAR.CODCAR AND FUN.ESTCAR = CAR.ESTCAR
                JOIN SENIOR.R018CCU E ON E.NUMEMP = FUN.NUMEMP AND E.CODCCU = FUN.CODCCU
                JOIN SENIOR.R030FIL F ON FUN.NUMEMP = F.NUMEMP AND FUN.CODFIL = F.CODFIL
                JOIN SENIOR.R016ORN G ON G.TABORG = FUN.TABORG AND G.NUMLOC = FUN.NUMLOC
                LEFT JOIN SENIOR.R024SIS R ON CAR.SISCAR = R.SISCAR
                LEFT JOIN SENIOR.R034CPL EM ON FUN.NUMEMP = EM.NUMEMP AND FUN.NUMCAD = EM.NUMCAD AND FUN.TIPCOL = EM.TIPCOL
                LEFT JOIN SENIOR.R038HEB S ON FUN.NUMEMP = S.NUMEMP AND FUN.TIPCOL = S.TIPCOL AND FUN.NUMCAD = S.NUMCAD AND FUN.DATETB = S.INIETB
                WHERE FUN.NUMEMP IN (219, 220, 221, 620) AND FUN.TIPCOL = 1 AND FUN.SITAFA <> 7 AND FUN.CODCAR NOT IN (110355)
                ORDER BY FUN.NUMEMP, FUN.CODFIL, FUN.NUMCAD
                """
        try:
            logging.info("-------------->>>Query---------------------------------")
            df = pd.read_sql_query(query, self.connection)
            df.columns = ['Nome','Branch_gupy','Role_gupy','Departamento_gupy','Filial_cod','Matricula','Cpf', 'Situacao', 'Email','INIETB','FIMETB']
            for col in ['Branch_gupy', 'Role_gupy', 'Departamento_gupy']:
                df[col] = df[col].apply(textoPadrao)
            logging.info(f">Consulta executada com sucesso. {len(df)} registros encontrados.")
            return df
        except (oracledb.DatabaseError, pd.io.sql.DatabaseError) as e:
            logging.error(f">Erro ao executar query: {e}")
            return pd.DataFrame()
        finally:
            logging.info("-------------->>>Script Rodando------------------------")
import oracledb
import logging
import pandas as pd
import time

class SeniorConnector:
    """Classe para gerenciar a conexão com o banco de dados Senior."""

    _QUERY = """
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
    
    def __init__(self, user, password, host, port, service_name):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.service_name = service_name
        self.connection = None
        self.cursor = None

    def connect(self, retries=3, delay=5):
        """Estabelece conexão com o banco de dados."""
        if not all([self.host, self.port, self.service_name]):
            logging.error("Parâmetros de conexão ausentes.")
            return False

        dsn = oracledb.makedsn(self.host, self.port, service_name=self.service_name)

        for attempt in range(retries):
            try:
                self.connection = oracledb.connect(user=self.user, password=self.password, dsn=dsn)
                self.cursor = self.connection.cursor()
                logging.info("Conexão com o banco de dados Senior estabelecida com sucesso.")
                return True
            except oracledb.DatabaseError as e:
                logging.error(f"Erro ao conectar (tentativa {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    logging.error("Não foi possível conectar ao banco de dados após várias tentativas.")
                    return False
        return False

    def disconnect(self):
        """Fecha a conexão com o banco de dados."""
        if self.cursor:
            self.cursor.close()
            logging.info("Cursor do banco de dados Senior fechado.")
        if self.connection:
            self.connection.close()
            logging.info("Conexão com o banco de dados Senior fechada.")

    def get_collaborators_data(self):
        """Busca os dados dos colaboradores no banco de dados."""
        if not self.connection:
            logging.error("Conexão com o banco de dados não estabelecida.")
            return pd.DataFrame()
        try:
            df = pd.read_sql_query(self._QUERY, self.connection)
            df.columns = ['Nome','Branch_gupy','Role_gupy','Departamento_gupy','Filial_cod','Matricula','Cpf', 'Situacao', 'Email','INIETB','FIMETB']
            logging.info(f"Consulta executada com sucesso. {len(df)} registros encontrados.")
            return df
        except (oracledb.DatabaseError, pd.io.sql.DatabaseError) as e:
            logging.error(f"Erro ao executar a consulta no banco de dados Senior: {e}")
            return pd.DataFrame()
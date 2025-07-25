import oracledb
import logging
from collections import namedtuple
from utils.config import host_data, port_data, service_name_data, user_data, password_data

class Database:
    def __init__(self):
        self.connection = None  # Declara conexão como None
        self.cursor = None      # Declara cursor como None

    def connectData(self):
        dsn = {
            'host': host_data,
            'port': port_data,
            'service_name': service_name_data,
            'user': user_data,
            'password': password_data
        }
        # Verifica se as variaveis de ambiente foram carregadas 
        if None in dsn.values():
            logging.error("Missing one or more environment variables.")
            return
        try:
            self.connection = oracledb.connect(
                user=dsn['user'],
                password=dsn['password'],
                dsn=oracledb.makedsn(dsn['host'], dsn['port'], service_name=dsn['service_name'])
            )
            logging.info(f"-------------->>>Informações da Database--------------")
            logging.info(">Conexão com o banco de dados estabelecida com sucesso")
            # logging.info(f"------------------------------------------------------------------------------------")           
        except oracledb.DatabaseError as e:
            logging.error("Erro ao estabelecer conexão: %s", e)
    
    def query_TenureMail(self):
        if self.connection is None:
            logging.error("No database connection established.")
            return []
        row_data_list = []
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(
                """
                SELECT
                *
                FROM
                (
                SELECT
                    FUN.SITAFA AS SITAFA,
                    FUN.NUMCPF AS NUMCPF,
                    FUN.NUMCAD AS NUMCAD,
                    FUN.DATADM AS DATADM,
                    FUN.DATAFA AS DATAFA,
                    FUN.NOMFUN AS NOMFUN,
                    EM.EMAPAR AS EMAPAR,
                    EM.EMACOM AS EMACOM,
                    CAR.TITCAR AS TITCAR,
                    ORN.NOMLOC AS NOMLOCAL,
                    FUN.ESTPOS AS ESTPOS,  -- Adicionando a coluna ESTPOS
                    FUN.POSTRA AS POSTRA,  -- Adicionando a coluna POSTRA
                    ROW_NUMBER() OVER (PARTITION BY FUN.NUMCAD ORDER BY FUN.SITAFA) AS RN
                FROM
                    senior.R034FUN FUN
                    INNER JOIN senior.R030EMP EMP ON FUN.NUMEMP = EMP.NUMEMP
                    INNER JOIN senior.R024CAR CAR ON FUN.CODCAR = CAR.CODCAR AND FUN.ESTCAR = CAR.ESTCAR 
                    INNER JOIN senior.R034CPL EM ON FUN.NUMCAD = EM.NUMCAD AND FUN.NUMEMP = EM.NUMEMP
                    INNER JOIN senior.R016ORN ORN ON ORN.NUMLOC = FUN.NUMLOC
                    INNER JOIN senior.R030FIL FIL ON FUN.CODFIL = FIL.CODFIL AND FUN.NUMEMP = FIL.NUMEMP
                    LEFT JOIN senior.R034USU FUS ON FUN.NUMEMP = FUS.NUMEMP AND FUN.NUMCAD = FUS.NUMCAD AND FUN.TIPCOL = FUS.TIPCOL
                    LEFT JOIN senior.R999USU USU ON USU.CODUSU = FUS.CODUSU
                    LEFT JOIN senior.R034FOT PHO ON FUN.NUMCAD = PHO.NUMCAD AND FUN.TIPCOL = PHO.TIPCOL AND FUN.NUMEMP = PHO.NUMEMP
                WHERE
                    FUN.TIPCOL = '1'
                    AND CAR.TITCAR <> 'PENSIONISTA'
                    AND FUN.NUMEMP <> 100
                )
                WHERE
                RN = 1
                """)
            RowData = namedtuple('RowData', [desc[0] for desc in self.cursor.description])
            rows = self.cursor.fetchall()
            for row in rows:
                row_data_object = RowData(*row)
                row_data_list.append(row_data_object)
            logging.info("-------------->>>Query---------------------------------")
            logging.info(">Consulta executada com sucesso.")
            # logging.info("------------------------------------------------------------------------------------")            
        except oracledb.DatabaseError as e:
            logging.error("Error executing query: %s", e)
        finally:
            if self.cursor:
                self.cursor.close()
            logging.info(">Cursor fechado")
            logging.info("-------------->>>Script Rodandno------------------------")
        return row_data_list        
    
    def query_nomesup(self, ESTPOS, POSTRA):
        if self.connection is None:
            logging.error("No database connection established.")
            return None
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute("""
                SELECT K.NOMFUN
                FROM senior.R034FUN K
                WHERE ROWNUM = 1
                AND K.SITAFA <> 7
                AND K.ESTPOS = :estpos
                AND K.POSTRA = (
                    SELECT Z.POSTRA
                    FROM senior.R017HIE Z
                    WHERE Z.ESTPOS = :estpos
                    AND ROWNUM <= 1
                    AND Z.POSPOS = (
                        SELECT SUBSTR(POSPOS, 0, LENGTH(POSPOS)-2)
                        FROM senior.R017HIE HIE
                        WHERE HIE.ESTPOS = :estpos
                        AND HIE.POSTRA = :postra
                        AND ROWNUM <= 1
                    )
                )
            """, estpos=ESTPOS, postra=POSTRA)
            row = self.cursor.fetchone()
            return row[0] if row else None
        except oracledb.DatabaseError as e:
            logging.error("Error executing query: %s", e)
        finally:
            if self.cursor:
                self.cursor.close()
       
    def query_mailsup(self, ESTPOS, POSTRA):
        if self.connection is None:
            logging.error("No database connection established.")
            return None
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute("""
                SELECT
                    E.EMACOM
                FROM
                    senior.R034FUN K
                    INNER JOIN senior.R034CPL E ON K.NUMCAD = E.NUMCAD AND K.NUMEMP = E.NUMEMP
                WHERE
                    ROWNUM = 1
                    AND K.SITAFA <> 7
                    AND K.ESTPOS = :estpos
                    AND K.POSTRA = (
                        SELECT
                            Z.POSTRA
                        FROM
                            senior.R017HIE Z
                        WHERE                    
                            Z.ESTPOS = :estpos
                            AND ROWNUM <= 1
                            AND Z.POSPOS = (
                                SELECT
                                SUBSTR(POSPOS, 0, LENGTH(POSPOS)-2)
                                FROM
                                senior.R017HIE HIE
                                WHERE HIE.ESTPOS = :estpos
                                AND HIE.POSTRA = :postra
                                AND ROWNUM <= 1
                            )
                        )
            """, estpos=ESTPOS, postra=POSTRA)
            row = self.cursor.fetchone()
            return row[0] if row else None
        except oracledb.DatabaseError as e:
            logging.error("Error executing query: %s", e)
        finally:
            if self.cursor:
                self.cursor.close()
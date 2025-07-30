import oracledb
import logging
from collections import namedtuple
# from dotenv import load_dotenv,find_dotenv

class Database:
    def __init__(self):
        self.connection = None  # Declara conexão como None
        self.cursor = None      # Declara cursor como None
    def connectData(self,host,port,service,user,password):
        dsn = {
            'host': host,
            'port': port,
            'service_name': service,
            'user': user,
            'password': password
        }
        # Verifica se as variaveis de ambiente foram carregadas 
        if None in dsn.values():
            logging.error("Faltando uma ou mais variáveis de ambiente.")
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
    
    def querySenior(self):
        if self.connection is None:
            logging.error("Nenhuma conexão de banco de dados estabelecida.")
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
                            FUN.SITAFA AS "Situacao",
                            FUN.NUMCAD AS "Matricula",
                            FUN.NOMFUN AS "Nome",
                            EM.EMACOM AS "Email",
                            CAR.TITCAR AS "Cargo",
                            ORN.NOMLOC AS "LocalTrabalho",
                                        ROW_NUMBER() OVER (PARTITION BY FUN.NUMCAD
                        ORDER BY
                            FUN.SITAFA) AS RN
                        FROM
                            senior.R034FUN FUN
                        INNER JOIN senior.R030EMP EMP ON
                            FUN.NUMEMP = EMP.NUMEMP
                        INNER JOIN senior.R024CAR CAR ON
                            FUN.CODCAR = CAR.CODCAR
                            AND FUN.ESTCAR = CAR.ESTCAR
                        INNER JOIN senior.R034CPL EM ON
                            FUN.NUMCAD = EM.NUMCAD
                            AND FUN.NUMEMP = EM.NUMEMP
                        INNER JOIN senior.R016ORN ORN ON
                            ORN.NUMLOC = FUN.NUMLOC
                        INNER JOIN senior.R030FIL FIL ON
                            FUN.CODFIL = FIL.CODFIL
                            AND FUN.NUMEMP = FIL.NUMEMP
                        LEFT JOIN senior.R034USU FUS ON
                            FUN.NUMEMP = FUS.NUMEMP
                            AND FUN.NUMCAD = FUS.NUMCAD
                            AND FUN.TIPCOL = FUS.TIPCOL
                        LEFT JOIN senior.R999USU USU ON
                            USU.CODUSU = FUS.CODUSU
                        LEFT JOIN senior.R034FOT PHO ON
                            FUN.NUMCAD = PHO.NUMCAD
                            AND FUN.TIPCOL = PHO.TIPCOL
                            AND FUN.NUMEMP = PHO.NUMEMP
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
    
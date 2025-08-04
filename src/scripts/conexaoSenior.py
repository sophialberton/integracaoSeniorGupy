import os
import sys
import oracledb
import logging
from collections import namedtuple
from dotenv import load_dotenv,find_dotenv
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

class DatabaseSenior():
    def __init__(self,**kwargs):
        load_dotenv(find_dotenv())
        self.connection = None  # Declara conexão como None
        self.cursor = None # Declara cursor como None
        self.user_senior = kwargs.get("user_senior")
        self.password_senior = kwargs.get("password_senior")
        self.host_senior = kwargs.get("host_senior")
        self.port_senior = kwargs.get("port_senior")
        self.service_name_senior = kwargs.get("service_name_senior")
    
    def conexaoBancoSenior(self):
        dsn = {
            'host_senior': self.host_senior,
            'port_senior': self.port_senior,
            'service_name_senior': self.service_name_senior,
            'user_senior': self.user_senior,
            'password_senior': self.password_senior
        }
        # Verifica se as variaveis de ambiente foram carregadas 
        if None in dsn.values():
            logging.error("Faltando uma ou mais variáveis de ambiente.")
            return False
        try:
            self.connection = oracledb.connect( 
                user=dsn['user_senior'],
                password=dsn['password_senior'],
                dsn=oracledb.makedsn(dsn['host_senior'],dsn['port_senior'],service_name=dsn['service_name_senior'])
            )
            self.cursor = self.connection.cursor()
            logging.info(f"-------------->>>Informações da Database--------------")
            logging.info(">Conexão com o banco de dados estabelecida com sucesso")
            return self.cursor
            # logging.info(f"------------------------------------------------------------------------------------")           
        except oracledb.DatabaseError as e:
            logging.error("Erro ao estabelecer conexão: %s", e)
            return False
                        
    def buscaColaboradorSenior(self):
        row_data_list = []
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(
                # IMPORTANTE: Achar tabela "areaSenior" do Senior para atualizar a área do usuário da Gupy (departmentId)
                """
                SELECT
                        *
                    FROM 
                        (
                        SELECT
                            FUN.SITAFA AS "Situacao", -- 0
                            FUN.NUMCAD AS "Matricula", -- 1 
                            FUN.NUMCPF AS "Cpf", -- 2
                            FUN.NOMFUN AS "Nome", -- 3
                            EM.EMACOM AS "Email", -- 4
                            CAR.TITCAR AS "Cargo", -- 5
                            ORN.NOMLOC AS "Filial", -- 6
                            FUN.NUMEMP AS "Empresa", -- //
                            FUN.TIPCOL AS "TipoColaborador", --//
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
                # print(row)
            logging.info("-------------->>>Query---------------------------------")
            logging.info(">Consulta executada com sucesso.")
            # logging.info("------------------------------------------------------------------------------------")            
        except oracledb.DatabaseError as e:
            logging.error("Erro ao executar query: %s", e)

        finally:
            if self.cursor:
                self.cursor.close()
            logging.info(">Cursor fechado")
            logging.info("-------------->>>Script Rodandno------------------------")
            # print(self.row_data_list)
        return row_data_list    
                
    # connectData()

# Database(**dict_extract["Senior"])
        
        
        
        
        
        
        
        
        
        
        
        
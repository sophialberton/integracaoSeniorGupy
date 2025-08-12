import os
import sys
import oracledb
import logging
import pandas as pd
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
        except oracledb.DatabaseError as e:
            logging.error(">Erro ao estabelecer conexão: %s", e)
            return False
                        
    def buscaColaboradorSenior(self):
        row_data_list = []
        df = pd.DataFrame()
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(# IMPORTANTE: Achar tabela "areaSenior" do Senior para atualizar a área do usuário da Gupy (departmentId)
                    """
                    SELECT
                        FUN.NOMFUN AS Nome,
                        CASE
                            WHEN E.NOMCCU LIKE '%VENDAS%' THEN F.NOMFIL || ' - ' || E.NOMCCU
                            ELSE F.NOMFIL
                        END AS Branch_gupy,
                        CAR.TITCAR || ' - ' || R.DESSIS AS Role_gupy,
                        CASE
                            WHEN UPPER(G.NOMLOC) LIKE '%VENDAS%'
                            OR UPPER(G.NOMLOC) LIKE '%REGIÃO%' THEN E.NOMCCU
                            ELSE E.NOMCCU || ' - ' || G.NOMLOC
                        END AS Departamento_gupy,
                        FUN.NUMCAD AS Matricula,
                        FUN.NUMCPF AS Cpf,
                        FUN.SITAFA AS Situacao,
                        EM.EMACOM AS Email,
                        S.INIETB,
                        S.FIMETB
                    FROM
                        SENIOR.R034FUN FUN
                    INNER JOIN SENIOR.R024CAR CAR ON
                        FUN.CODCAR = CAR.CODCAR
                        AND FUN.ESTCAR = CAR.ESTCAR
                    JOIN SENIOR.R018CCU E ON
                        E.NUMEMP = FUN.NUMEMP
                        AND E.CODCCU = FUN.CODCCU
                    JOIN SENIOR.R030FIL F ON
                        FUN.NUMEMP = F.NUMEMP
                        AND FUN.CODFIL = F.CODFIL
                    JOIN SENIOR.R016ORN G ON
                        G.TABORG = FUN.TABORG
                        AND G.NUMLOC = FUN.NUMLOC
                    LEFT JOIN SENIOR.R024SIS R ON
                        CAR.SISCAR = R.SISCAR
                    LEFT JOIN SENIOR.R034CPL EM ON
                        FUN.NUMEMP = EM.NUMEMP
                        AND FUN.NUMCAD = EM.NUMCAD
                        AND FUN.TIPCOL = EM.TIPCOL
                    LEFT JOIN SENIOR.R038HEB S ON
                        FUN.NUMEMP = S.NUMEMP
                        AND FUN.TIPCOL = S.TIPCOL
                        AND FUN.NUMCAD = S.NUMCAD
                        AND FUN.DATETB = S.INIETB
                    WHERE
                        FUN.NUMEMP IN (219, 220, 221, 620)
                        AND FUN.TIPCOL = 1
                        AND FUN.SITAFA <> 7
                        AND FUN.CODCAR NOT IN (110355)
                    ORDER BY
                        FUN.NUMEMP,
                        FUN.CODFIL,
                        FUN.NUMCAD
               """ )
            RowData = namedtuple('RowData', [desc[0] for desc in self.cursor.description])
            
            colunas = ['Nome','Branch_gupy','Role_gupy,','Departamento_gupy','Matricula','Cpf', 'Situacao', 'Email','INIETB','FIMETB']
            # Definindo os nomes das colunas
            # colunas = ['Empresa', 'Nome', 'TipoColaborador', 'Matricula', 'Cpf', 'Situacao', 'Email']

            # Criando o DataFrame
            df = pd.DataFrame(self.cursor.fetchall(), columns=colunas)
                
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
        return df    
                  
        
        
        
        
        
        
        
        
        
        
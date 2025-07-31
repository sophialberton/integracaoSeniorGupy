import os
import sys
import oracledb
import logging
from collections import namedtuple
from dotenv import load_dotenv,find_dotenv
from utils.config import dict_extract
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

class Database():
    def __init__(self,**kwargs):
        load_dotenv(find_dotenv())
        self.connection = None  # Declara conexão como None
        self.cursor = None # Declara cursor como None
        self.user_senior = kwargs.get("user_senior")
        self.password_senior = kwargs.get("password_senior")
        self.host_senior = kwargs.get("host_senior")
        self.port_senior = kwargs.get("port_senior")
        self.service_name_senior = kwargs.get("service_name_senior")
    
    def connectData(self):
        dsn = {
            'host_senior': self.host_senior,
            'port_senior': self.port_senior,
            'service_name_senior': self.service_name_senior,
            'user_senior': self.user_senior,
            'password_senior': self.password_senior
        }
        # Verifica se as variaveis de ambiente foram carregadas 
        print(dsn)
        if None in dsn.values():
            logging.error("Faltando uma ou mais variáveis de ambiente.")
            return False
        try:
            self.connection = oracledb.connect( 
                user=dsn['user_senior'],
                password=dsn['password_senior'],
                dsn=oracledb.makedsn(dsn['host_senior'],dsn['port_senior'],service_name=dsn['service_name_senior'])
            )
            
            logging.info(f"-------------->>>Informações da Database--------------")
            logging.info(">Conexão com o banco de dados estabelecida com sucesso")
            return True
            # logging.info(f"------------------------------------------------------------------------------------")           
        except oracledb.DatabaseError as e:
            logging.error("Erro ao estabelecer conexão: %s", e)
            return False
        
    # connectData()

# Database(**dict_extract["Senior"])
        
        
        
        
        
        
        
        
        
        
        
        
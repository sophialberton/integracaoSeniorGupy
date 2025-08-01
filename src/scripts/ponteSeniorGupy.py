import sys
import os
import requests
import logging
from dotenv import load_dotenv,find_dotenv
from utils.config import dict_extract
from data.querySenior import ConsultaSenior
from scripts.conexaoDB import Database
# Caminho para encontrar a pasta 'src'
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)
    
class ponteSeniorGupy():
    def __init__(self,**kwargs):
        load_dotenv(find_dotenv())
        self.token = kwargs.get("token")       
        self.data = []   
        self.db_connection = Database()    
      
    def connectionDB(self):
        logging.info("ConnectionDB")
        # Conexão com database    
        db_results = ConsultaSenior.querySenior()
        for data in db_results:
            self.process_user(data)  
    
    def process_user(self,data):      
        lista = []          
        situacaoSenior      = data.Situacao
        matriculaSenior     = data.Matricula
        nomeSenior          = data.Nome
        emailSenior         = data.Email
        cargoSenior         = data.Cargo
        localtrabalhoSenior = data.LocalTrabalho
        lista.append([situacaoSenior,matriculaSenior,nomeSenior,emailSenior,cargoSenior,localtrabalhoSenior])
        return lista
         
    def verificaColaboradores(self,data):
        logging.info("Verificando Colaboradores")
        data = self.process_user(self)
        
        for situacaoSenior,matriculaSenior,nomeSenior,emailSenior,cargoSenior,localtrabalhoSenior in data:
            if situacaoSenior == 7:
                # Requisição API gupy
                url = f"https://api.gupy.io/api/v1/users?email={emailSenior}&perPage=10&page=1"
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {self.token}"
                } 
                response = requests.get(url,  headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    ids = []
                    print(data['totalResults'])
                    if data['results']:  
                        for item in data['results']:
                            try:
                                id = item['id']
                            except:
                                pass
                            ids.append([id])  
                else:
                    continue
                return ids
            else:
                self.listaColaboradores(nomeSenior,emailSenior,localtrabalhoSenior)
        logging.info("Colaboradores Verificados")
 
    def listaColaboradores(self):
        logging.info("listaColaboradores")
        # DEPOIS DE FILTRAR SE É SITUACAO != 7 ELE VAI VIR PARA CÁ, AQUI VAI SER VERIFICADO SE O USUARIO JÁ TEM CADASTRO NA GUPY, 
        # SE NAO TIVER ELE VAI PARA O CADASTRO
        pass
   
    def criaColaboradoresGupy(self):
        logging.info("criaColaboradores")
        dados = self.querySenior()
        url = "https://api.gupy.io/api/v1/users"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer f21dcc63-73bc-4b69-85f0-b9ac179d457f"
        }
        response = requests.post(url, headers=headers)
        print(response.text)
        
    def updateColaboradores(self):
        logging.info("updateColaboradores")
        dados = self.listaColaboradores()
        for id,nome,email in dados:
            try:        
                url = f"https://api.gupy.io/api/v1/users/{id}"

                payload = {
                    "name": f"{nome}",
                    "email": f"{email}"
                }
                headers = {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "authorization": f"Bearer {self.token}"
                }

                response = requests.put(url, json=payload, headers=headers)

                print(response.text)   
            except:
                pass 
  
    def deleteColaboradores(self):
        logging.info("deleteColaboradores")
        dados = self.verificaColaboradores()
        for ids in dados:
            try:
                url = f"https://api.gupy.io/api/v1/users/{ids}"
                headers = {
                    "accept": "application/json",
                    "authorization": "Bearer f21dcc63-73bc-4b69-85f0-b9ac179d457f"
                }
                response = requests.delete(url, headers=headers)

                print(response.text)
            except Exception as e:
                print(e)
  
    def run(self):
        self.updateColaboradores()

ponteSeniorGupy(**dict_extract["Gupy"]).listaColaboradores()
    
import sys
import os
import requests
import logging
from dotenv import load_dotenv,find_dotenv
from utils.config import dict_extract
from conexaoGupy import conexaoGupy
# from data.querySenior import ConsultaSenior
from conexaoSenior import DatabaseSenior
# Caminho para encontrar a pasta 'src'
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)
    
class ponteSeniorGupy():
    def __init__(self,**kwargs):
        load_dotenv(find_dotenv())
        self.token = kwargs.get("token")       
        self.data = []   
        self.conexaoSenior = DatabaseSenior()
        # self.emailSenior = DatabaseSenior.buscaColaboradorSenior(self="Email")
      
    def connectionDB(self):
        logging.info("ConnectionDB")
        # Conexão com DatabaseSenior    
        dadosSenior = DatabaseSenior.buscaColaboradorSenior()
        for data in dadosSenior:
            self.process_user(data)  
    
    def process_user(self,data):    
        listaSenior = []
        # Verifica se 'data' é um dicionário
        if isinstance(data, dict):
            situacaoSenior  = data.get("Situacao")
            matriculaSenior = data.get("Matricula")
            cpfSenior       = data.get("Cpf")
            nomeSenior      = data.get("Nome")
            emailSenior     = data.get("Email")
            cargoSenior     = data.get("Cargo")
            filialSenior    = data.get("Filial")
        else:
            # Se for um objeto com atributos
            situacaoSenior  = getattr(data, "Situacao", None)
            matriculaSenior = getattr(data, "Matricula", None)
            cpfSenior       = getattr(data, "Cpf", None)
            nomeSenior      = getattr(data, "Nome", None)
            emailSenior     = getattr(data, "Email", None)
            cargoSenior     = getattr(data, "Cargo", None)
            filialSenior    = getattr(data, "Filial", None)

        listaSenior.append([situacaoSenior, matriculaSenior, cpfSenior, nomeSenior, emailSenior, cargoSenior, filialSenior])
        return listaSenior
 
        """ 
        lista = []          
        situacaoSenior      = data.Situacao
        matriculaSenior     = data.Matricula
        nomeSenior          = data.Nome
        emailSenior         = data.Email
        cargoSenior         = data.Cargo
        filialSenior        = data.Filial
        lista.append([situacaoSenior,matriculaSenior,nomeSenior,emailSenior,cargoSenior,filialSenior])
        return lista
         """
    def verificaColaboradores(self,usuarios):
        logging.info(">Verificando Colaboradores")
        usuarios = self.process_user(self)
        
        for situacaoSenior, matriculaSenior, cpfSenior, nomeSenior, emailSenior, cargoSenior, filialSenior in usuarios:
            if situacaoSenior == 7: # Se demitido
                
                # conexaoGupy.deletaUsuarioGupy(id) 
                # Requisição API gupy
                url = f"https://api.gupy.io/api/v1/users?email={emailSenior}&perPage=10&page=1"
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {self.token}"
                } 
                response = requests.get(url,  headers=headers)

                if response.status_code == 200:
                    usuarios = response.json()
                    ids = []
                    print(usuarios['totalResults'])
                    if usuarios['results']:  
                        for item in usuarios['results']:
                            try:
                                id = item['id']
                            except:
                                pass
                            ids.append([id])  
                else:
                    continue
                return ids
            else:
                logging.info(">>Lista Colaboradores")
                # conexaoGupy.listaUsuariosGupy(emailSenior)
                # self.listaColaboradores(nomeSenior,emailSenior,filialSenior)
        logging.info("Colaboradores Verificados")
 
    def listaColaboradores(self):
        logging.info(">ListaColaboradores")
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

# ponteSeniorGupy(**dict_extract["Gupy"]).listaColaboradores()
    
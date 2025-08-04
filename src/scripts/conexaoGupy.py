import sys
import os
import requests
import logging
from dotenv import load_dotenv,find_dotenv
from utils.config import dict_extract
# from data.querySenior import ConsultaSenior
from conexaoSenior import DatabaseSenior
# Caminho para encontrar a pasta 'src'
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

class conexaoGupy():
    def __init__(self):
        load_dotenv(find_dotenv())
        # self.token = kwargs.get("token")  
        self.token = os.getenv("token")   
        self.data = []   
        self.db_connection = DatabaseSenior()    
        print(f"token carregado: {self.token}")
    
    def listaUsuariosGupy(self,emailSenior):
        # Requisição API gupy
        url = f"https://api.gupy.io/api/v1/users?email={emailSenior}&perPage=10&page=1"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}"
        } 
        response = requests.get(url,  headers=headers)
        print(response.text)
   
    def criaUsuarioGupy(self,nomeSenior,emailSenior):
        url = "https://api.gupy.io/api/v1/users"
        payload = {
            f"name": str(nomeSenior),
            f"email": str(emailSenior)
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.token}"
            }
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        
    def atualizaUsuarioGupy(self,idGupy,nomeSenior,emailSenior,cargoSenior,areaSenior,filialSenior):
        url = f"https://api.gupy.io/api/v1/users/{idGupy}"
        payload = {
            f"name": str(nomeSenior),
            f"email": str(emailSenior),
            f"roleId": str(cargoSenior), # Cargo
            f"departmentId": str(areaSenior), # Departamento é a área
            f"branchIds": str([filialSenior]) # Branch é a Filial
        }        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        "authorization": f"Bearer {self.token}"
        }
        response = requests.put(url, json=payload, headers=headers)
        print(response.text)
    
    def deletaUsuarioGupy(self,idGupy):
        url = f"https://api.gupy.io/api/v1/users/{idGupy}"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}"
        }
        response = requests.delete(url, headers=headers)
        print(response.text)
        
        
        dados = self.listaUsuariosGupy()
        for ids in dados:
            try:
                url = f"https://api.gupy.io/api/v1/users/{ids}"
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {self.token}"
                }
                response = requests.delete(url, headers=headers)

                print(response.text)
            except Exception as e:
                print(e)
  
# conexaoGupy(**dict_extract["Gupy"]).listaUsuariosGupy(emailSenior)
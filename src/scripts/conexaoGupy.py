import sys
import os
import requests
import logging
from conexaoSenior import DatabaseSenior
# Caminho para encontrar a pasta 'src'
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

class conexaoGupy():
    def __init__(self):
        self.token = os.getenv("token")     
    
    def listaUsuariosGupy(self,emailSenior):
        # Requisição API gupy
        url = f"https://api.gupy.io/api/v1/users?email={emailSenior}&perPage=10&page=1"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}"
        } 
        response = requests.get(url,  headers=headers)
        # print(response.text)
        data = response.json()
        detalhe = data.get("detail", "Erro desconhecido")
        if response.status_code == 201:
            logging.info(f">Listando usuario na gupy: {emailSenior} (verificaColaboradores.api.criaUsuarioGupy)")
        if response.status_code == 400:
            logging.error(f">{detalhe} >> Usuário: {emailSenior}, (verificaColaboradores.api.criaUsuarioGupy)")

   
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
        
        data = response.json()
        detalhe = data.get("detail", "Erro desconhecido")
        # print("Detalhe do erro:", data.get("detail"))        
        if response.status_code == 201:
            logging.info(f">Criando usuario na gupy: {nomeSenior, emailSenior} (verificaColaboradores.api.criaUsuarioGupy)")
        if response.status_code == 400:
            logging.error(f">{detalhe} >> Usuário: {nomeSenior, emailSenior}, (verificaColaboradores.api.criaUsuarioGupy)")
                          
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
        data = response.json()
        detalhe = data.get("detail", "Erro desconhecido")
        print("Detalhe do erro:", data.get("detail"))        
        if response.status_code == 201:
            logging.info(f">Atualizando usuario na gupy: {idGupy, nomeSenior} (verificaColaboradores.api.atualizaUsuarioGupy)")
        if response.status_code == 400:
            logging.error(f">{detalhe} >> Usuário: {idGupy, nomeSenior}, (verificaColaboradores.api.atualizaUsuarioGupy)")
    
    def deletaUsuarioGupy(self,idGupy, nomeSenior):
        url = f"https://api.gupy.io/api/v1/users/{idGupy}"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}"
        }
        response = requests.delete(url, headers=headers)
        data = response.json()
        detalhe = data.get("detail", "Erro desconhecido")
        # print("Detalhe do erro:", data.get("detail"))        
        if response.status_code == 201:
            logging.info(f">Deletando usuário desligado: {idGupy, nomeSenior} (verificaColaboradores.api.deletaUsuarioGupy)")
        if response.status_code == 400:
            logging.error(f">{detalhe} >> Usuário: {idGupy, nomeSenior}, (verificaColaboradores.api.deletaUsuarioGupy)")
  
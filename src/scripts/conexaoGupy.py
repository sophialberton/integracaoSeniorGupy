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
        url = f"https://api.gupy.io/api/v1/users?email={emailSenior}&perPage=10&page=1"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}"
        } 
        response = requests.get(url,  headers=headers)
        data = response.json()
        detalhe = data.get("detail", "Erro desconhecido")
        if response.status_code == 201:
            logging.info(f">Listando usuario na gupy: {emailSenior} (verificaColaboradores.api.criaUsuarioGupy)")
        if response.status_code == 400:
            logging.error(f"> '{detalhe}' >> Usuario: {emailSenior}, (verificaColaboradores.api.criaUsuarioGupy)")

   
    def criaUsuarioGupy(self,nomeSenior,emailSenior,cpfSenior):
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
        if response.status_code == 201:
            print(f">Criou usuario {nomeSenior} com email {emailSenior}")
            logging.info(f">Criou usuario na gupy: {nomeSenior, emailSenior} (verificaColaboradores.api.criaUsuarioGupy)")
        if response.status_code == 400:
            print(f">WARNING: '{detalhe}'>> Usuario > Cpf: {cpfSenior}; Nome: {nomeSenior}; Email: {emailSenior}")
            logging.warning(f"> '{detalhe}' >> Usuario: {nomeSenior, emailSenior}, (verificaColaboradores.api.criaUsuarioGupy)")
                          
    
    def deletaUsuarioGupy(self,idGupy, nomeSenior):
        url = f"https://api.gupy.io/api/v1/users/{idGupy}"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}"
        }
        response = requests.delete(url, headers=headers)
        data = response.json()
        detalhe = data.get("detail", "Erro desconhecido")
        if response.status_code == 201:
            print(f">Deletou usuario desligado: {idGupy, nomeSenior}")
            logging.info(f">Deletou usuario desligado: {idGupy, nomeSenior} (verificaColaboradores.api.deletaUsuarioGupy)")
        if response.status_code == 400:
            print(f">WARNING: '{detalhe}' >> Usuario: {idGupy, nomeSenior}")
            logging.warning(f"> '{detalhe}' >> Usuario: {idGupy, nomeSenior}, (verificaColaboradores.api.deletaUsuarioGupy)")
  
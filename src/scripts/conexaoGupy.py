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

    def listaUsuariosGupy(self, nomeSenior, emailSenior):
        if not emailSenior:
            logging.warning(f"> Email nulo para {nomeSenior}, não será possível listar na GUPY.")
            return None
        email = emailSenior.strip()
        if "@fgmdentalgroup.com" in email or "@fgm.ind.br" in email:
            url = f"https://api.gupy.io/api/v1/users?email={email}&perPage=10&page=1"
            headers = {
                "accept": "application/json",
                "authorization": f"Bearer {self.token}"
            }
            response = requests.get(url, headers=headers)
            data = response.json()
            detalhe = data.get("detail", "Erro desconhecido")

            if response.status_code == 200:
                usuarios = data.get("results", [])
                if usuarios:
                    user_id = usuarios[0].get("id")
                    print(f"> Listou usuario {nomeSenior} com email {emailSenior} na GUPY")
                    logging.warning(f"> Listou usuario {nomeSenior} com email {emailSenior} na GUPY (verificaColaboradores.api.listaUsuariosGupy)")
                    return user_id
                else:
                    print(f"> Nenhum usuario encontrado para {emailSenior}")
                    logging.warning(f"> Nenhum usuario encontrado para {emailSenior} (verificaColaboradores.api.listaUsuariosGupy)")
                    return None
            elif response.status_code == 400:
                print(f"> WARNING: '{detalhe}' >> Usuario > Nome: {nomeSenior}; Email: {emailSenior}")
                logging.error(f"> '{detalhe}' >> Usuario: {nomeSenior, emailSenior}, (verificaColaboradores.api.criaUsuarioGupy)")
            else:
                logging.error(f"> Erro ao listar usuario: {detalhe}")
                return None

    def criaUsuarioGupy(self,nomeSenior,emailSenior,cpfSenior):
        # url = "https://api.gupy.io/api/v1/users"
        # payload = {
        #     f"name": str(nomeSenior),
        #     f"email": str(emailSenior)
        # }
        # headers = {
        #     "accept": "application/json",
        #     "content-type": "application/json",
        #     "authorization": f"Bearer {self.token}"
        #     }
        # response = requests.post(url, json=payload, headers=headers)
        # data = response.json()
        # detalhe = data.get("detail", "Erro desconhecido")
        # if response.status_code == 201:
            print(f"> Criou usuario {nomeSenior} com email {emailSenior}")
            logging.info(f"> Criou usuario na gupy: {nomeSenior, emailSenior} (verificaColaboradores.api.criaUsuarioGupy)")
        # if response.status_code == 400:
        #     print(f">WARNING: '{detalhe}'>> Usuario > Cpf: {cpfSenior}; Nome: {nomeSenior}; Email: {emailSenior}")
        #     logging.warning(f"> '{detalhe}' >> Usuario: {nomeSenior, emailSenior}, (verificaColaboradores.api.criaUsuarioGupy)")
    
    def deletaUsuarioGupy(self, idGupy, nomeSenior):
        # url = f"https://api.gupy.io/api/v1/users/{idGupy}"
        # headers = {
        #     "accept": "application/json",
        #     "authorization": f"Bearer {self.token}"
        # }
        # response = requests.delete(url, headers=headers)
        # data = response.json()
        # detalhe = data.get("detail", "Erro desconhecido")
        # if response.status_code == 201:
        #     print(f">Deletou usuario desligado: {nomeSenior, idGupy}")
        #     logging.info(f">Deletou usuario desligado: {nomeSenior, idGupy} (verificaColaboradores.api.deletaUsuarioGupy)")
        # if response.status_code == 400:
        #     print(f">WARNING: '{detalhe}' >> Usuario: {nomeSenior, idGupy}")
        #     logging.warning(f"> '{detalhe}' >> Usuario: {nomeSenior, idGupy}, (verificaColaboradores.api.deletaUsuarioGupy)")
        print(f"> Chamou o delete para usuario desligado: {nomeSenior, idGupy}")
        logging.critical(f"> Chamou o DELETE para usuario desligado: {nomeSenior, idGupy}")
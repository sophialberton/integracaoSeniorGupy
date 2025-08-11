import sys
import os
import requests
import logging
# Caminho para encontrar a pasta 'src'
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)
# from data.conexaoSenior import DatabaseSenior

class conexaoGupy():
    def __init__(self):
        self.token = os.getenv("token")     

    # Cria usuario na Gupy com dados da Senior
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
            print(f"> Criou usuario {nomeSenior} com email {emailSenior}")
            logging.info(f"> Criou usuario na gupy: {nomeSenior, emailSenior} (verificaColaboradores.api.criaUsuarioGupy)")
        if response.status_code == 400:
            print(f">WARNING: '{detalhe}'>> Usuario > Cpf: {cpfSenior}; Nome: {nomeSenior}; Email: {emailSenior}")
            logging.warning(f"> '{detalhe}' >> Usuario: {nomeSenior, emailSenior}, (verificaColaboradores.api.criaUsuarioGupy)")
    
    # Procura cadastro Gupy e retornar o ID da gupy
    def listaIdUsuariosGupy(self, nomeSenior, emailSenior):
        if not emailSenior:
            logging.warning(f"> Email nulo para {nomeSenior}, não será possível listar na GUPY.")
            return None
        emailSenior = emailSenior.strip()
        # Define o segundo email alternativo com base no domínio original
        if "@fgmdentalgroup.com" in emailSenior:
            emailAlternativo = emailSenior.replace("@fgmdentalgroup.com", "@fgm.ind.br")
        elif "@fgm.ind.br" in emailSenior:
            emailAlternativo = emailSenior.replace("@fgm.ind.br", "@fgmdentalgroup.com")
        else:
            logging.warning(f"> Email {emailSenior} não possui domínio reconhecido.")
            return None
        # Tenta buscar com os dois emails
        for email in [emailSenior, emailAlternativo]:
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
                    print(f"> Listou usuario {nomeSenior} com email {email} na GUPY")
                    logging.warning(f"> Listou usuario {nomeSenior} com email {email} na GUPY (verificaColaboradores.api.listaUsuariosGupy)")
                    return user_id
                else:
                    print(f"> Nenhum usuario encontrado para {email}")
                    logging.warning(f"> Nenhum usuario encontrado para {email} (verificaColaboradores.api.listaUsuariosGupy)")
            elif response.status_code == 400:
                print(f"> WARNING: '{detalhe}' >> Usuario > Nome: {nomeSenior}; Email: {email}")
                logging.error(f"> '{detalhe}' >> Usuario: {nomeSenior, email}, (verificaColaboradores.api.criaUsuarioGupy)")
            else:
                logging.error(f"> Erro ao listar usuario: {detalhe}")
        return None

    # Com o ID da Gupy retornar o email que esta cadastrado na Gupy
    def listaEmailUsuarioGupy(self, idGupy, nomeSenior):
        url = f"https://api.gupy.io/api/v1/users?id={idGupy}perPage=10&page=1"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        data = response.json()
        detalhe = data.get("detail", "Erro desconhecido")
        if response.status_code == 200:
            usuarios = data.get("results", [])
            if usuarios:
                emailGupy = usuarios[0].get("email")
                print(f"> Listou usuario {nomeSenior} com email {emailGupy} na GUPY")
                logging.warning(f"> Listou usuario {nomeSenior} com email {emailGupy} na GUPY (verificaColaboradores.api.listaUsuariosGupy)")
                return emailGupy
            else:
                print(f"> Nenhum usuario encontrado para {emailGupy}")
                logging.warning(f"> Nenhum usuario encontrado para {emailGupy} (verificaColaboradores.api.listaUsuariosGupy)")
        elif response.status_code == 400:
            print(f"> WARNING: '{detalhe}' >> Usuario > Nome: {nomeSenior}; Email: {emailGupy}")
            logging.error(f"> '{detalhe}' >> Usuario: {nomeSenior, emailGupy}, (verificaColaboradores.api.criaUsuarioGupy)")
        else:
            logging.error(f"> Erro ao listar usuario: {detalhe}")
        return None    
        
    # Deleta usuario da Gupy
    def deletaUsuarioGupy(self, idGupy, nomeSenior):
        url = f"https://api.gupy.io/api/v1/users/{idGupy}"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}"
        }
        response = requests.delete(url, headers=headers)

        try:
            data = response.json()
            detalhe = data.get("detail", "Erro desconhecido")
        except ValueError:
            detalhe = "Resposta não está em formato JSON ou está vazia."
            data = None

        if response.status_code == 201:
            print(f"> Deletou usuario desligado: {nomeSenior, idGupy}")
            logging.info(f"> Deletou usuario desligado: {nomeSenior, idGupy} (verificaColaboradores.api.deletaUsuarioGupy)")
        elif response.status_code == 400:
            print(f"> WARNING: '{detalhe}' >> Usuario: {nomeSenior, idGupy}")
            logging.warning(f"> '{detalhe}' >> Usuario: {nomeSenior, idGupy}, (verificaColaboradores.api.deletaUsuarioGupy)")
        else:
            print(f"> DELETE retornou status {response.status_code} para usuario: {nomeSenior, idGupy}")
            logging.warning(f"> DELETE retornou status {response.status_code} para usuario: {nomeSenior, idGupy}")

        print(f"> Chamou o delete para usuario desligado: {nomeSenior, idGupy}")
        logging.critical(f"> Chamou o DELETE para usuario desligado: {nomeSenior, idGupy}")

    # Lista acessos do cadastro de usuario da Gupy
    def listaAcessoUsuarioGupy(self, idGupy):
        url = f"https://api.gupy.io/api/v1/user-access-profiles?id={idGupy}perPage=10&page=1"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        print(response.text)

    def atualizaUsuarioGupy(self, idGupy, nomeSenior, emailGupy):
        url = f"https://api.gupy.io/api/v1/users/{idGupy}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        response = requests.put(url, headers=headers)
        print(response.text)
    


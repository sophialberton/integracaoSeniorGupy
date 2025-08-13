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
                    print(f"> Listou id da gupy do usuario {nomeSenior} com email {email} e id sendo {user_id} na GUPY")
                    logging.warning(f"> Listou id da gupy do usuario {nomeSenior} com email {email} e id sendo {user_id} na GUPY")
                    return user_id
                else:
                    print(f"> Nenhum usuario encontrado para {email}")
                    logging.warning(f"> Nenhum usuario encontrado para {email}")
            elif response.status_code == 400:
                print(f"> WARNING: '{detalhe}' >> Usuario > Nome: {nomeSenior}; Email: {email}")
                logging.error(f"> '{detalhe}' >> Usuario: {nomeSenior, email}, (verificaColaboradores.api.criaUsuarioGupy)")
            else:
                logging.error(f"> Erro ao listar id Gupy de usuario: {detalhe}")
        return None

    # Com o ID da Gupy retornar o email que esta cadastrado na Gupy
    def listaEmailUsuarioGupy(self, idGupy, nomeSenior):
        url = f"https://api.gupy.io/api/v1/users?id={idGupy}perPage=10&page=1"
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
                emailGupy = usuarios[0].get("email")
                print(f"> Listou email de usuario {nomeSenior} com email {emailGupy} na GUPY")
                logging.warning(f"> Listou email de usuario {nomeSenior} com email {emailGupy} na GUPY")
                return emailGupy
            else:
                print(f"> Nenhum usuario encontrado para {emailGupy}")
                logging.warning(f"> Nenhum usuario encontrado para {emailGupy}")
        elif response.status_code == 400:
            print(f"> WARNING: '{detalhe}' >> Usuario > Nome: {nomeSenior}; Email: {emailGupy}")
            logging.error(f"> '{detalhe}' >> Usuario: {nomeSenior, emailGupy}, (verificaColaboradores.api.criaUsuarioGupy)")
        else:
            logging.error(f"> Erro ao listar email de usuario: {detalhe}")
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

# ================================ V2. Atualizando Cadastros ========================================

    # Lista campos do cadastro de usuario da Gupy
    def listaCamposUsuarioGupy(self, idGupy, nomeSenior, emailGupy):
        url = f"https://api.gupy.io/api/v1/users?email={emailGupy}&perPage=10&page=1"
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
                departamentId = usuarios[0].get("departmentId", None)
                roleId = usuarios[0].get("roleId", None)
                branchIds = usuarios[0].get("branchIds", None)
                logging.warning(f"> Listou campos de cadastro do usuário {nomeSenior} com email {emailGupy} e id {idGupy}")
                return departamentId, roleId, branchIds
            else:
                logging.warning(f"> Nenhum usuário encontrado para {emailGupy}")
                return None, None, None
        elif response.status_code == 400:
            logging.warning(f"> '{detalhe}' >> Usuário >> Id: {idGupy}; Nome: {nomeSenior}; Email: {emailGupy}")
            return None, None, None
        else:
            logging.error(f"> Erro ao listar campos de usuário: {detalhe}")
            return None, None, None  # <- Certifique-se de que este retorno está correto



    def atualizaUsuarioGupy(self, idGupy, nomeSenior, emailGupy, roleIdGupy, departamentIdGupy, branchIdGupy):
        url = f"https://api.gupy.io/api/v1/users/{idGupy}"
        payload = {
        f"roleId": {roleIdGupy},
        f"departmentId": {departamentIdGupy},
        f"branchIds": [{branchIdGupy}]
        }
        headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {self.token}"
        }
        response = requests.put(url, json=payload, headers=headers)
        data = response.json()
        detalhe = data.get("detail", "Erro desconhecido")
        if response.status_code == 201:
            print(f"> Atualizou usuario {nomeSenior} com email {emailGupy} e id {idGupy}")
            logging.info(f"> Atualizou usuario {nomeSenior} com email {emailGupy} e id {idGupy}")
        if response.status_code == 400:
            print(f">WARNING: '{detalhe}'>> Usuario > Id: {idGupy}; Nome: {nomeSenior}; Email: {emailGupy}")
            logging.warning(f"> '{detalhe}' >> Usuario > Id: {idGupy}; Nome: {nomeSenior}; Email: {emailGupy}")
    
    def listaAreaDepartamento(self, idDepartamento, nomeDepartamento):
        url = "https://api.gupy.io/api/v1/departments?id=asd&perPage=10&page=1"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        print(response.text)
        pass
    
    def criaAreaDepartamento(self, nomeAreaDepartamento):
        url = "https://api.gupy.io/api/v1/departments"
        payload = { 
            "similarTo": "financial_management",
            f"name": str(nomeAreaDepartamento),
            }
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        pass
    
    def listaCargoRole():
        pass
    
    def criaCargoRole():
        pass
    
    def listaFilialBranch():
        pass
    
    def criaFilialBranch():
        pass
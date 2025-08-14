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
        url = "https://api.gupy.io/api/v1/roles"
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
    
    # Procura cadastro Gupy e retornar o Nome, ID e email da gupy
    def listaUsuarioGupy(self, nomeSenior, emailSenior):
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
                    user_name = usuarios[0].get("name")
                    user_email = usuarios[0].get("email")
                    print(f"> Listou id da gupy do usuario {user_name} com email {user_email} e id sendo {user_id} na GUPY")
                    logging.warning(f"> Listou id da gupy do usuario {user_name} com email {user_email} e id sendo {user_id} na GUPY")
                    return user_id, user_name, user_email
                else:
                    print(f"> Nenhum id cadastrado encontrado para {email}")
                    logging.warning(f"> Nenhum id cadastrado encontrado para {email}")
            elif response.status_code == 400:
                print(f"> WARNING: '{detalhe}' >> Usuario > Nome: {nomeSenior}; Email: {email}")
                logging.error(f"> '{detalhe}' >> Usuario: {nomeSenior, email}, (verificaColaboradores.api.criaUsuarioGupy)")
            else:
                logging.error(f"> Erro ao listar id Gupy de usuario {nomeSenior}: > {detalhe}")
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
        logging.warning(f"> Listando campos do usuário {nomeSenior} - {emailGupy} - {idGupy}")
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
                usuario = usuarios[0] 
                departamentId = usuario.get("departmentId", None)
                roleId = usuario.get("roleId", None)
                branchIds = usuario.get("branchIds", None)  
                logging.warning(f"> Listou campos de cadastro do usuario {nomeSenior} - {emailGupy} - {idGupy}")
                return departamentId, roleId, branchIds
            else:
                logging.warning(f"> Nenhum campo cadastrado encontrado para {nomeSenior} - {emailGupy}")
                return None, None, None
        elif response.status_code == 400:
            logging.warning(f"> '{detalhe}' >> Usuário Gupy: {nomeSenior} >> Email Gupy: {emailGupy} >> Id Gupy: {idGupy}")
            return None, None, None
        else:
            logging.error(f"> Erro ao listar campos de usuário: {nomeSenior} >> {detalhe}")
            return None, None, None 

    def atualizaUsuarioGupy(self, idGupy, nomeSenior, emailGupy, roleIdGupy, departamentIdGupy, branchIdGupy):
        logging.warning(f"> Atualizando campos de cadastro do usuario {nomeSenior} - {emailGupy}")
        print(f"> Atualizando campos de cadastro do usuario {nomeSenior} - {emailGupy}")
        # url = f"https://api.gupy.io/api/v1/users/{idGupy}"
        # payload = {
        # f"roleId": {roleIdGupy},
        # f"departmentId": {departamentIdGupy},
        # f"branchIds": [{branchIdGupy}]
        # }
        # headers = {
        # "accept": "application/json",
        # "content-type": "application/json",
        # "authorization": f"Bearer {self.token}"
        # }
        # response = requests.put(url, json=payload, headers=headers)
        # data = response.json()
        # detalhe = data.get("detail", "Erro desconhecido")
        # if response.status_code == 201:
        # print(f"> Atualizou usuario {nomeSenior} com email {emailGupy} e id {idGupy}")
        # logging.info(f"> Atualizou usuario {nomeSenior} com email {emailGupy} e id {idGupy}")
        # if response.status_code == 400:
        #     print(f">WARNING: '{detalhe}'>> Usuario > Id: {idGupy}; Nome: {nomeSenior}; Email: {emailGupy}")
        #     logging.warning(f"> '{detalhe}' >> Usuario > Id: {idGupy}; Nome: {nomeSenior}; Email: {emailGupy}")
    
# ============================= Processando Campos para Atualizar =============================================
    # Lista Area/departamento da Gupy
    def listaAreaDepartamento(self, nomeDepartamento):
        logging.warning(f"> Listando Departamento/Area: {nomeDepartamento}")
        url = "https://api.gupy.io/api/v1/departments?id=asd&perPage=10&page=1"
        headers = {"accept": "application/json",
                   "authorization": f"Bearer {self.token}"
                   }
        response = requests.get(url, headers=headers)
        data = response.json()
        detalhe = data.get("detail", "Erro desconhecido")
        if response.status_code == 200:
            cargos = data.get("results", [])
            if cargos:
                departament_id = cargos[0].get("id")
                dapartament_name = cargos[0].get("name")
                departament_similarTo = cargos[0].get("similarTo")
                print(f"> Listou id da gupy da area departamento {dapartament_name} com similarTo {departament_similarTo} e id sendo {departament_id} na GUPY")
                logging.warning(f"> Listou id da gupy da area departamento {dapartament_name} com similarTo {departament_similarTo} e id sendo {departament_id} na GUPY")
                return departament_id, dapartament_name, departament_similarTo
            else:
                print(f"> Nenhum id cadastrado encontrado para {dapartament_name}")
                logging.warning(f"> Nenhum id cadastrado encontrado para {dapartament_name}")
        elif response.status_code == 400:
            print(f"> WARNING: '{detalhe}' >> Cargo > Nome: {nomeDepartamento}")
            logging.error(f"> '{detalhe}' >> Cargo > {nomeDepartamento}")
        else:
            logging.error(f"> Erro ao listar Departamento area Gupy {nomeDepartamento}: > {detalhe}")
            return None
    
    # Lista Cargo/Role da Gupy   
    def listaCargoRole(self, nomeCargoRole):
        logging.warning(f"> Listando Cargo Role: {nomeCargoRole}")
        url = "https://api.gupy.io/api/v1/departments?id=asd&perPage=10&page=1"
        headers = {"accept": "application/json",
                   "authorization": f"Bearer {self.token}"
                   }
        response = requests.get(url, headers=headers)
        data = response.json()
        detalhe = data.get("detail", "Erro desconhecido")
        if response.status_code == 200:
            cargos = data.get("results", [])
            if cargos:
                role_id = cargos[0].get("id")
                role_name = cargos[0].get("name")
                role_similarTo = cargos[0].get("similarTo")
                print(f"> Listou Id da Gupy do Cargo {role_name} com similarTo {role_similarTo} e id sendo {role_id} na GUPY")
                logging.warning(f"> Listou id da gupy do cargo {role_name} com similarTo {role_similarTo} e id sendo {role_id} na GUPY")
                return role_id, role_name, role_similarTo
            else:
                print(f"> Nenhum id cadastrado encontrado para {role_name}")
                logging.warning(f"> Nenhum id cadastrado encontrado para {role_name}")
        elif response.status_code == 400:
            print(f"> WARNING: '{detalhe}' >> Cargo > Nome: {nomeCargoRole}")
            logging.error(f"> '{detalhe}' >> Cargo > {nomeCargoRole}")
        else:
            logging.error(f"> Erro ao listar Cargo role Gupy de {nomeCargoRole}: {detalhe}")
            return None
    
    # Lista FilialBranch da Gupy
    def listaFilialBranch(self, nomeFilialBranch, codFilialBranch):
        logging.warning(f"> Listando Filial Branch: {nomeFilialBranch} com codigo {codFilialBranch}")
        url = f"https://api.gupy.io/api/v1/branches?name={nomeFilialBranch}&perPage=10&page=1"
        headers = {
                "accept": "application/json",
                "authorization": f"Bearer {self.token}"
            }
        response = requests.get(url, headers=headers)
        data = response.json()
        detalhe = data.get("detail", "Erro desconhecido")
        if response.status_code == 200:
            branchs = data.get("results", [])
            if branchs:
                    branch_id = branchs[0].get("id")
                    branch_name = branchs[0].get("name")
                    branch_path = branchs[0].get("path")
                    print(f"> Listou id da gupy da filial {branch_name} com path {branch_path} e id sendo {branch_id} na GUPY")
                    logging.warning(f"> Listou id da gupy da filial {branch_name} com path {branch_path} e id sendo {branch_id} na GUPY")
                    return branch_id, branch_name, branch_path
            else:
                print(f"> Nenhum id cadastrado encontrado para {nomeFilialBranch}")
                logging.warning(f"> Nenhum id cadastrado encontrado para {nomeFilialBranch}")
        elif response.status_code == 400:
            print(f"> WARNING: '{detalhe}' >> Branch > Cod: {codFilialBranch}; Nome: {nomeFilialBranch}")
            logging.error(f"> '{detalhe}' >> Branch: {codFilialBranch, nomeFilialBranch}")
        else:
           logging.error(f"> Erro ao listar Filial branch {nomeFilialBranch}: {detalhe}")
        return None
    
    # Cria area departamento
    def criaAreaDepartamento(self, nomeAreaDepartamento, similarTo):
        logging.critical(f"> criando Area Departamento com {nomeAreaDepartamento} e similar {similarTo}")
        # url = "https://api.gupy.io/api/v1/departments"
        # payload = { 
        #     f"similarTo": str(similarTo),
        #     f"name": str(nomeAreaDepartamento),
        #     }
        # headers = {
        #     "accept": "application/json",
        #     "content-type": "application/json",
        #     "authorization": f"Bearer {self.token}"
        # }
        # response = requests.post(url, json=payload, headers=headers)
        # data = response.json()
        # detalhe = data.get("detail", "Erro desconhecido")
        # if response.status_code == 201:
            # print(f"> Criou area Departamento {nomeAreaDepartamento}")
            # logging.info(f"> Criou area Departamento {nomeAreaDepartamento}")
        # if response.status_code == 400:
        #     print(f">WARNING: '{detalhe}'>> Area/Departamento > {nomeAreaDepartamento};")
        #     logging.warning(f"> '{detalhe}' >> Area/Departamento > {nomeAreaDepartamento}")
      
    # Cria cargo role
    def criaCargoRole(self, nomeCargoRole, similarTo ):
        logging.critical(f"> Criando Cargo Role com {nomeCargoRole} e similar {similarTo}")
        # url = "https://api.gupy.io/api/v1/roles"
        # payload = { 
        #     f"similarTo": str(similarTo),
        #     f"name": str(nomeCargoRole),
        #     }
        # headers = {
        #     "accept": "application/json",
        #     "content-type": "application/json",
        #     "authorization": f"Bearer {self.token}"
        # }
        # response = requests.post(url, json=payload, headers=headers)
        # data = response.json()
        # detalhe = data.get("detail", "Erro desconhecido")
        # if response.status_code == 201:
        #     print(f"> Criou area Departamento {nomeCargoRole}")
        #     logging.info(f"> Criou area Departamento {nomeCargoRole}")
        # if response.status_code == 400:
        #     print(f">WARNING: '{detalhe}'>> Area/Departamento > {nomeCargoRole};")
        #     logging.warning(f"> '{detalhe}' >> Area/Departamento > {nomeCargoRole}")
    
    # Cria filial Branch
    def criaFilialBranch(self, cod_filialBranch, nomeFilialBranch):
        logging.critical(f"> Criando Filial Branch com {cod_filialBranch} e nome {nomeFilialBranch}")
        # url = "https://api.gupy.io/api/v1/departments"
        # payload = { 
        #     f"similarTo": str(cod_filialBranch),
        #     f"name": str(nomeFilialBranch),
        #     "path": ["Path FGM"]
        #     }
        # headers = {
        #     "accept": "application/json",
        #     "content-type": "application/json",
        #     "authorization": f"Bearer {self.token}"
        # }
        # response = requests.post(url, json=payload, headers=headers)
        # data = response.json()
        # detalhe = data.get("detail", "Erro desconhecido")
        # if response.status_code == 201:
            # print(f"> Criou filial com cod {cod_filialBranch} e {nomeFilialBranch}")
            # logging.info(f"> Criou area Departamento {nomeFilialBranch}")
        # # if response.status_code == 400:
        #     print(f">WARNING: '{detalhe}'>> Area/Departamento > {nomeFilialBranch};")
        #     logging.warning(f"> '{detalhe}' >> Area/Departamento > {nomeFilialBranch}")
        
    def obter_dados_usuario_gupy_por_id(self, user_id):
        logging.warning(f"> Buscando dados do usuário com ID {user_id}")
        url = f"https://api.gupy.io/api/v1/users?id={user_id}&perPage=10&page=1"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                "departmentId": data.get("department", {}).get("id"),
                "roleId": data.get("role", {}).get("id"),
                "branchId": data.get("branch", {}).get("id")
            }
        else:
            logging.warning(f"> Falha ao buscar dados do usuário {user_id}: {response.status_code}")
            return {}

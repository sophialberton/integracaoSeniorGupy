# Crie ou substitua o conteúdo do arquivo: servicos/conexao_gupy.py

import requests
import logging

class ServicoGupy:
    """Classe para interagir com a API da Gupy."""
    
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.gupy.io/api/v1"
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

    def _realizar_requisicao(self, method, endpoint, **kwargs):
        """Função auxiliar para realizar requisições HTTP."""
        url = f"{self.base_url}/{endpoint}"
        logging.info("Realizou a requisicao geral")
        # try:
        #     response = requests.request(method, url, headers=self.headers, timeout=20, **kwargs)
        #     response.raise_for_status()
        #     # Retorna None para status 204 (No Content) que é comum em DELETE
        #     if response.status_code == 204:
        #         return None
        #     return response.json()
        # except requests.exceptions.HTTPError as e:
        #     logging.error(f"Erro HTTP na API Gupy para {url}: {e.response.status_code} - {e.response.text}")
        # except requests.exceptions.RequestException as e:
        #     logging.error(f"Erro de conexão com a API Gupy para {url}: {e}")
        return None
    
    def _realizar_requisicao_lista(self, method, endpoint, **kwargs):
        """Função auxiliar para realizar requisições HTTP."""
        url = f"{self.base_url}/{endpoint}"
        logging.info("Realizou a requisicao para lista")
        try:
            response = requests.request(method, url, headers=self.headers, timeout=20, **kwargs)
            response.raise_for_status()
            # Retorna None para status 204 (No Content) que é comum em DELETE
            if response.status_code == 204:
                return None
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"Erro HTTP na API Gupy para {url}: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro de conexão com a API Gupy para {url}: {e}")
        return None

    def listar_usuario_por_email(self, nome, email):
        if not email:
            logging.warning(f"> Email nulo para {nome}, não será possível listar na GUPY.")
            return None, None, None

        email = email.strip()

        # Define o segundo email alternativo com base no domínio original
        if "@fgmdentalgroup.com" in email:
            email_alternativo = email.replace("@fgmdentalgroup.com", "@fgm.ind.br")
        elif "@fgm.ind.br" in email:
            email_alternativo = email.replace("@fgm.ind.br", "@fgmdentalgroup.com")
        else:
            logging.warning(f"> Email {email} não possui domínio reconhecido.")
            return None, None, None
        # Tenta buscar com os dois emails
        for email_consulta in [email, email_alternativo]:
            endpoint = f"users?email={email_consulta}&perPage=10&page=1"
            data = self._realizar_requisicao_lista("GET", endpoint)

            if data is None:
                logging.warning(f"> Nenhuma resposta da API para o email {email_consulta}")
                continue

            detalhe = data.get("detail", "Erro desconhecido")

            if "results" in data:
                usuarios = data["results"]
                if usuarios:
                    user_id = usuarios[0].get("id")
                    user_name = usuarios[0].get("name")
                    user_email = usuarios[0].get("email")
                    logging.info(f"> Listou id da Gupy do usuário {user_name} com email {user_email} e id {user_id}")
                    return user_id, user_name, user_email
                else:
                    logging.warning(f"> Nenhum id cadastrado encontrado para {email_consulta}")
            else:
                logging.error(f"> Erro ao listar id Gupy de usuário {nome}: {detalhe}")

        return None, None, None

    
    def criar_usuario(self, nome, email, cpf):
        usuario_existente = self.listar_usuario_por_email(nome, email)
        
        if usuario_existente:
            logging.warning(f"> Usuário já existe: {usuario_existente}")
            return usuario_existente
        
        logging.info(f"> Criando usuário: {nome} ({email})")
        endpoint = "users"
        payload = {"name": nome, "email": email}
        data = self._realizar_requisicao("post", endpoint, json=payload)
        
        if data:
            return data
        logging.warning(f"> Falha ao criar usuário: {nome} ({email})")
        return None

    def deletar_usuario(self, user_id, nome):
        """Deleta um usuário da Gupy."""
        endpoint = f"users/{user_id}"
        self._realizar_requisicao("delete", endpoint)
        logging.info(f"Comando de deleção enviado para o usuário: {nome} (ID: {user_id})")

    def atualizar_usuario(self, user_id, dados_atualizacao):
        """Atualiza os dados de um usuário na Gupy."""
        endpoint = f"users/{user_id}"
        
        data = self._realizar_requisicao("put", endpoint, json=dados_atualizacao)
        if data:
            logging.info(f"Usuário atualizado (ID: {user_id}) com os dados: {dados_atualizacao}")
            return data
        return None
    
    def listar_campos_por_id(self, id_gupy, nome, email):
        logging.warning(f"> Listando campos do usuário {nome} - {email} - {id_gupy}")
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
                usuario = usuarios[0] 
                departamentId = usuario.get("departmentId", None)
                roleId = usuario.get("roleId", None)
                branchIds = usuario.get("branchIds", None)  
                logging.warning(f"> Listou campos do usuario {nome} - {email} - {id_gupy}")
                return departamentId, roleId, branchIds
            else:
                logging.warning(f"> Nenhum campo cadastrado encontrado para {nome} - {email}")
                return None, None, None
        elif response.status_code == 400:
            logging.warning(f"> '{detalhe}' >> Usuário Gupy: {nome} >> Email Gupy: {email} >> Id Gupy: {id_gupy}")
            return None, None, None
        else:
            logging.error(f"> Erro ao listar campos de usuário: {nome} >> {detalhe}")
            return None, None, None 

    def listar_departamento(self, nome_departamento):
        logging.warning(f"> Listando Departamento: '{nome_departamento}'")
        endpoint = f"departments?name={nome_departamento}&perPage=10&page=1"
        data = self._realizar_requisicao_lista("get", endpoint)
        
        if data and data.get("results"):
            departamento = data["results"][0]
            return departamento.get("id"), departamento.get("name"), departamento.get("similarTo")
        
        logging.warning(f"> Nenhum departamento encontrado para '{nome_departamento}'")
        return None, None, None

    def criar_departamento(self, nome_departamento, similarTo):
        id_departamento, nome_existente, similar_existente = self.listar_departamento(nome_departamento)
        
        if id_departamento:
            logging.critical(f"> Departamento '{nome_existente}' com similar '{similar_existente}' já existe (ID: {id_departamento})")
            return id_departamento
        
        logging.critical(f"> Criando Departamento '{nome_departamento}' com similar '{similarTo}'")
        endpoint = "departments"
        payload = {"name": nome_departamento, "similarTo": similarTo}
        data = self._realizar_requisicao("post", endpoint, json=payload)
        
        if data:
            return data.get("id")
        
        logging.error(f"> Falha ao criar departamento '{nome_departamento}'")
        return None

    def criar_cargo(self, nome_cargo, similarTo):
        def listar_cargo(self, nome_cargo):
            logging.warning(f"> Listando > Cargo/Role: >> '{nome_cargo}'")
            url = f"https://api.gupy.io/api/v1/departments?name={nome_cargo}&perPage=10&page=1"
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
                    print(f"> Listou >> Cargo/Role: {role_name} >> similarTo: {role_similarTo} >> id: {role_id}")
                    logging.warning(f"> Listou >> Cargo/Role: {role_name} >> similarTo: {role_similarTo} >> id: {role_id}")
                    return role_id, role_name, role_similarTo
                else:
                    print(f"> Nenhum id cadastrado encontrado para cargo >> {nome_cargo}")
                    logging.warning(f"> Nenhum id cadastrado encontrado para caargo >> {nome_cargo}")
                    return None, None, None
            elif response.status_code == 400:
                print(f"> WARNING: '{detalhe}' >> Cargo/Role > Nome: {nome_cargo}")
                logging.error(f"> '{detalhe}' >> Cargo/Role > {nome_cargo}")
            else:
                logging.error(f"> Erro ao listar Cargo role Gupy de {nome_cargo}: {detalhe}")
                return None, None, None
        
        # Mesma lógica

    def criar_filial(self, nome_filial, cod_filial):
        def listar_filial(self, nome_filial, cod_filial):
            logging.warning(f"> Listando Filial Branch: '{nome_filial}' com codigo '{cod_filial}'")
            url = f"https://api.gupy.io/api/v1/branches?code={cod_filial}&perPage=10&page=1"
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
                    print(f"> Nenhum id cadastrado encontrado para {nome_filial}")
                    logging.warning(f"> Nenhum id cadastrado encontrado para {nome_filial}")
            elif response.status_code == 400:
                print(f"> WARNING: '{detalhe}' >> Branch > Cod: {cod_filial}; Nome: {nome_filial}")
                logging.error(f"> '{detalhe}' >> Branch: {cod_filial, nome_filial}")
            else:
                logging.error(f"> Erro ao listar Filial branch {nome_filial}: {detalhe}")
            return None, None, None
    
    # Antes de criar qualquer campo ele deve listar para ver se já nao tem algum equivalente
    # def criar_departamento(self, nome_departamento, similarTo):
    #     # Adpatar Funções para ficar refatoradinha como as outras
    #     def listar_departamento(self, nome_departamento):
    #         logging.warning(f"> Listando > Area/Departament: >> '{nome_departamento}'")
    #         url = f"https://api.gupy.io/api/v1/departments?name={nome_departamento}&perPage=10&page=1"
    #         headers = {"accept": "application/json",
    #                 "authorization": f"Bearer {self.token}"
    #                 }
    #         response = requests.get(url, headers=headers)
    #         data = response.json()
    #         detalhe = data.get("detail", "Erro desconhecido")
    #         if response.status_code == 200:
    #             cargos = data.get("results", [])
    #             if cargos:
    #                 departament_id = cargos[0].get("id")
    #                 dapartament_name = cargos[0].get("name")
    #                 departament_similarTo = cargos[0].get("similarTo")
    #                 print(f"> Listou >> Area/Departament: {dapartament_name} >> similarTo: {departament_similarTo} >> id: {departament_id}")
    #                 logging.warning(f"> Listou >> Area/Departament: {dapartament_name} >> similarTo: {departament_similarTo} >> id: {departament_id}")
    #                 return departament_id, dapartament_name, departament_similarTo
    #             else:
    #                 print(f"> Nenhum id cadastrado encontrado para {nome_departamento}")
    #                 logging.warning(f"> Nenhum id cadastrado encontrado para {nome_departamento}")
    #                 return None, None, None
    #         elif response.status_code == 400:
    #             print(f"> WARNING: '{detalhe}' >> Area/Departament > {nome_departamento}")
    #             logging.error(f"> '{detalhe}' >> Area/Departament > {nome_departamento}")
    #         else:
    #             logging.error(f"> Erro ao listar Departamento area Gupy {nome_departamento}: > {detalhe}")
    #             return None, None, None

    #     id_departamento, nome_departamento, similarTo = listar_departamento(nome_departamento, similarTo)
    #     # Se lsitar_departamento retornou id, nome e similarTo
    #         # retorna que ja existe: 
    #         # logging.critical(f"> Departamento com '{nome_departamento}' e similar '{similarTo}' já existe com o id '{id_departamento}")
    #     # Se listar_departamento retornou none
    #         # Cria
    #         # logging.critical(f"> Criando Departamento com '{nome_departamento}' e similar '{similarTo}'")

    # A mesma lógica se aplica para os outros, sempre eantes de CRIAR qualquer coisa deve-se lista para PROCURAR se já nao tem.
    
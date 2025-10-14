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
        # """Função auxiliar para realizar requisições HTTP."""
        url = f"{self.base_url}/{endpoint}"
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
    
    def _realizar_requisicao_lista(self, method, endpoint, **kwargs):
        """Função auxiliar para realizar requisições HTTP."""
        url = f"{self.base_url}/{endpoint}"
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
            return None

        email = email.strip()

        # Lista de domínios válidos
        dominios_validos = [
            "@fgmdentalgroup.com",
            "@fgm.ind.br",
            "@biocircle.ind.br"
        ]

        # Verifica se o domínio é válido
        dominio_atual = next((d for d in dominios_validos if d in email), None)
        if not dominio_atual:
            logging.warning(f"> Email {email} não possui domínio reconhecido.")
            return None

        # Gera variações com os outros domínios válidos
        email_variacoes = [email]
        usuario_parte = email.split("@")[0]
        for dominio in dominios_validos:
            novo_email = f"{usuario_parte}{dominio}"
            if novo_email not in email_variacoes:
                email_variacoes.append(novo_email)

        # Consulta a API com cada variação
        for email_consulta in email_variacoes:
            endpoint = f"users?email={email_consulta}&perPage=10&page=1"
            data = self._realizar_requisicao_lista("GET", endpoint)

            if data is None:
                logging.warning(f"> Nenhuma resposta da API para o email {email_consulta}")
                continue

            detalhe = data.get("detail", "Erro desconhecido")

            if "results" in data:
                usuarios = data["results"]
                if usuarios:
                    usuario = usuarios[0]
                    return {
                        "id": usuario.get("id"),
                        "name": usuario.get("name"),
                        "email": usuario.get("email"),
                        "roleId": usuario.get("roleId"),
                        "departmentId": usuario.get("departmentId"),
                        "branchIds": usuario.get("branchIds"),
                        "profileTestEnabled": usuario.get("profileTestEnabled", True),
                        "accessProfileId": usuario.get("accessProfileId")
                    }

            else:
                logging.error(f"> Erro ao listar id Gupy de usuário {nome}: {detalhe}")

    def criar_usuario(self, nome, email, cpf):
        usuario = self.listar_usuario_por_email(nome, email)

        if usuario is not None:
            return usuario  # Retorna o objeto completo, não só o ID

        logging.critical(f"> Criando usuário: {nome} ({email})")
        endpoint = "users"
        payload = {"name": nome, "email": email}
        data = self._realizar_requisicao("post", endpoint, json=payload)

        if data:
            return data  # Aqui também retorna o objeto completo

        return None

    def deletar_usuario(self, user_id, nome):
        """Deleta um usuário da Gupy."""
        endpoint = f"users/{user_id}"
        self._realizar_requisicao("delete", endpoint)
        logging.critical(f"> Comando de deleção enviado para o usuário: {nome} (ID: {user_id})")

    def atualizar_usuario(self, user_id, dados_atualizacao):
        """Atualiza os dados de um usuário na Gupy usando PUT, apenas se houver diferenças reais."""

        endpoint = f"users/{user_id}"
        nome = dados_atualizacao.get("name")
        email = dados_atualizacao.get("email")

        usuario_atual = self.listar_usuario_por_email(nome, email)
        if not usuario_atual:
            logging.error(f"Não foi possível obter dados atuais do usuário {user_id} ({email})")
            return None

        # Preserva profileTestEnabled se estiver presente
        profile_test_enabled = usuario_atual.get("profileTestEnabled", True)

        # Monta o payload com os dados recebidos
        payload = {
            "name": dados_atualizacao.get("name"),
            "email": dados_atualizacao.get("email"),
            "roleId": dados_atualizacao.get("roleId"),
            "departmentId": dados_atualizacao.get("departmentId"),
            "branchIds": dados_atualizacao.get("branchIds"),
            "accessProfileId": dados_atualizacao.get("accessProfileId"),
            "profileTestEnabled": profile_test_enabled
        }

        # Remove campos com valor None
        payload = {k: v for k, v in payload.items() if v is not None}

        def normalizar(valor):
            if isinstance(valor, list):
                return sorted([str(v).strip().lower() for v in valor])
            if isinstance(valor, str):
                return valor.strip().lower()
            return valor

        dados_diferentes = {}
        for k, v_novo in payload.items():
            v_atual = usuario_atual.get(k)
            if normalizar(v_novo) != normalizar(v_atual):
                logging.debug(f"Dado diferente detectado: {k} | Atual: {v_atual} | Novo: {v_novo}")
                dados_diferentes[k] = v_novo

        if not dados_diferentes:
            # logging.info(f"Usuário {user_id} já está atualizado. Nenhuma alteração necessária.")
            return None

        data = self._realizar_requisicao("put", endpoint, json=payload)
        if data:
            logging.critical(f"Usuário atualizado (ID: {user_id}) com os dados: {payload}")
            return data
        return None
    
    def listar_campos_por_id(self, id_gupy, nome, email):
        # logging.info(f"> Buscando campos do usuário {nome} - {email} - {id_gupy}")
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
                logging.warning(f">    Buscou campos do usuario {nome} - {email} - {id_gupy}")
                return departamentId, roleId, branchIds
            else:
                logging.warning(f">    Nenhum campo cadastrado encontrado para {nome} - {email}")
                return None, None, None
        elif response.status_code == 400:
            logging.warning(f"> '{detalhe}' >> Usuário Gupy: {nome} >> Email Gupy: {email} >> Id Gupy: {id_gupy}")
            return None, None, None
        else:
            logging.error(f"> Erro ao listar campos de usuário: {nome} >> {detalhe}")
            return None, None, None 

    # Funções auxiliar para listar/buscar pelo nome departamento/cargo/filial
    def listar_departamento(self, nome_departamento):
        # logging.info(f">    Buscando Departamento: '{nome_departamento}'")
        endpoint = f"departments?name={nome_departamento}&perPage=10&page=1"
        data = self._realizar_requisicao_lista("get", endpoint)
        
        if data and data.get("results"):
            departamento = data["results"][0]
            return departamento.get("id"), departamento.get("name"), departamento.get("similarTo")
        
        logging.warning(f">        Nenhum departamento encontrado para '{nome_departamento}'")
        return None, None, None

    def listar_cargo(self, nome_cargo):
        # logging.info(f">    Buscando Cargo/Role: '{nome_cargo}'")
        endpoint = f"roles?name={nome_cargo}&perPage=10&page=1"
        data = self._realizar_requisicao_lista("get", endpoint)

        if data and data.get("results"):
            cargo = data["results"][0]
            return cargo.get("id"), cargo.get("name"), cargo.get("similarTo")

        logging.warning(f">        Nenhum cargo encontrado para '{nome_cargo}'")
        return None, None, None

    def listar_filial(self, nome_filial, cod_filial):
        # logging.info(f">    Bucando Filial: '{nome_filial}' com código '{cod_filial}'")
        endpoint = f"branches?code={cod_filial}&perPage=10&page=1"
        data = self._realizar_requisicao_lista("get", endpoint)

        if data and data.get("results"):
            filial = data["results"][0]
            return filial.get("id"), filial.get("name"), filial.get("path")

        logging.warning(f">        Filial não encontrada para '{nome_filial}' com código '{cod_filial}'")
        return None, None, None

    # Busca e/ou Cria departamento/cargo/filial 
    def obtem_departamento(self, nome_departamento, similarTo):
        id_departamento, nome_existente, similar_existente = self.listar_departamento(nome_departamento)
        
        if id_departamento:
            # logging.info(f">       Departamento Existente: '{nome_existente}' (ID: {id_departamento}/similar{similar_existente})")
            return id_departamento
        
        logging.critical(f">       Criando Departamento '{nome_departamento}' com similar '{similarTo}'")
        endpoint = "departments"
        payload = {"name": nome_departamento, "similarTo": similarTo}
        data = self._realizar_requisicao("post", endpoint, json=payload)
        
        if data:
            return data.get("id")
        
        logging.error(f"> Falha ao criar departamento '{nome_departamento}'")
        return None

    def obtem_cargo(self, nome_cargo, similarTo):
        role_id, nome_existente, similar_existente = self.listar_cargo(nome_cargo)

        if role_id:
            # logging.info(f">       Cargo Existente '{nome_existente}' (ID: {role_id}/similar{similar_existente})")
            return role_id

        logging.critical(f">       Criando Cargo '{nome_cargo}' com similar '{similarTo}'")
        endpoint = "roles"
        payload = {"name": nome_cargo, "similarTo": similarTo}
        data = self._realizar_requisicao("post", endpoint, json=payload)

        if data:
            return data.get("id")

        logging.error(f"> Falha ao criar cargo '{nome_cargo}'")
        return None

    def obtem_filial(self, nome_filial, cod_filial):
        def gerar_path(nome_filial):
            return nome_filial.lower().replace(" ", "-")
        branch_id, nome_existente, path_existente = self.listar_filial(nome_filial, cod_filial)

        if branch_id:
            # logging.info(f">       Filial Existente '{nome_existente}' (ID: {branch_id}/Path: '{path_existente}')")
            return branch_id

        logging.critical(f">       Criando Filial '{nome_filial}' com código '{cod_filial}'")
        endpoint = "branches"
        payload = {
            "name": nome_filial,
            "code": str(cod_filial),
            "path": [gerar_path(nome_filial)]  # array de string
        }

        data = self._realizar_requisicao("post", endpoint, json=payload)

        if data:
            return data.get("id")

        logging.error(f"> Falha ao criar filial '{nome_filial}'")
        return None

# ====================================================================== Employee

    def lista_employee(self, id_gupy_employee):
        endpoint = f"company-employees?id={id_gupy_employee}"
        data = self._realizar_requisicao("post", endpoint)
        payload = {"id": id_gupy_employee, } 
        if data:
            return data.get("id")

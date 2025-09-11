# Crie ou substitua o conteúdo do arquivo: servicos/conexao_gupy.py

import requests
import logging

class ServicoGupy:
    """Classe para interagir com a API da Gupy."""
    
    def __init__(self, token):
        self.base_url = "https://api.gupy.io/api/v1"
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

    def _realizar_requisicao(self, method, endpoint, **kwargs):
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

    def listar_usuario_por_email(self, email):
        """Busca um usuário na Gupy pelo e-mail."""
        if not email:
            return None
        
        endpoint = f"users?email={email.strip()}"
        data = self._realizar_requisicao("get", endpoint)
        
        if data and data.get("results"):
            return data["results"][0]
        return None

    def criar_usuario(self, nome, email, cpf):
        """Cria um novo usuário na Gupy."""
        endpoint = "users"
        payload = {"name": str(nome), "email": str(email)}
        
        data = self._realizar_requisicao("post", endpoint, json=payload)
        
        if data:
            logging.info(f"Usuário criado na Gupy: {nome} ({email})")
            return data
        logging.warning(f"Falha ao criar usuário na Gupy: {nome} ({email})")
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
# servicos/servico_email.py

import requests
import json
import logging
import os
import base64

class ServicoEmail:
    """Classe para gerenciar o envio de e-mails via API Microsoft Graph."""

    def __init__(self, tenant_id, client_id, client_secret, scope, email_remetente, **kwargs):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.email_remetente = email_remetente
        self.token = self._obter_token_acesso()

    def _obter_token_acesso(self):
        """Obtém um token de acesso da plataforma de identidade da Microsoft."""
        url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': self.scope
        }
        response = requests.post(url, data=data)
        try:
            response.raise_for_status()
            token_data = response.json()
            logging.info("Token de acesso para o MS Graph obtido com sucesso.")
            return token_data.get('access_token')
        except requests.exceptions.HTTPError as e:
            logging.error(f"Falha ao obter token do MS Graph: {e.response.text}")
            return None

    def enviar_email_com_anexo(self, destinatario, assunto, corpo, caminho_anexo):
        """Envia um e-mail com anexo usando a API Graph."""
        if not self.token:
            logging.error("Não foi possível enviar e-mail por falta de token de acesso.")
            return

        try:
            with open(caminho_anexo, "rb") as f:
                conteudo_anexo = f.read()
                anexo_base64 = base64.b64encode(conteudo_anexo).decode("utf-8")
        except FileNotFoundError:
            logging.error(f"Arquivo de anexo não encontrado: {caminho_anexo}")
            return

        url_envio = f'https://graph.microsoft.com/v1.0/users/{self.email_remetente}/sendMail'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        mensagem = {
            'message': {
                'subject': assunto,
                'body': {'contentType': 'HTML', 'content': corpo},
                'toRecipients': [{'emailAddress': {'address': destinatario}}],
                'attachments': [{
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": os.path.basename(caminho_anexo),
                    "contentBytes": anexo_base64
                }]
            }
        }
        
        response = requests.post(url_envio, headers=headers, data=json.dumps(mensagem))

        if response.status_code == 202:
            logging.info(f"E-mail de log enviado com sucesso para {destinatario}.")
        else:
            logging.error(f'Falha ao enviar e-mail de log: {response.status_code} - {response.text}')
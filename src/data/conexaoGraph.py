import requests
import json
import logging
import os
import base64
from utils.config import client_secret, client_id, tenant_id, scope, email_log

class conexaoGraph:
    def enviar_email_log(self, email_destino, log_path, assunto, corpo):
        # Obter token de acesso
        url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': scope
        }
        response = requests.post(url, data=data)
        token = response.json().get('access_token')

        # Preparar destinatário
        destinatarios = [{'emailAddress': {'address': email_destino}}]

        # Preparar anexo
        with open(log_path, "rb") as f:
            conteudo = f.read()
            attachment = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": os.path.basename(log_path),
                "contentBytes": base64.b64encode(conteudo).decode("utf-8")
            }

        # Enviar email
        url = f'https://graph.microsoft.com/v1.0/users/{email_log}/sendMail'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        mensagem = {
            'message': {
                'subject': assunto,
                'body': {
                    'contentType': 'HTML',
                    'content': corpo
                },
                'toRecipients': destinatarios,
                'attachments': [attachment]
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(mensagem))

        if response.status_code == 202:
            logging.info(f"E-mail de log enviado para {email_destino}")
        else:
            logging.error(f'Falha ao enviar email: {response.status_code}: {response.text}')

import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# --- Configurações do Banco de Dados Senior ---
DB_CONFIG = {
    "user_senior": os.getenv("user_senior"),
    "password_senior": os.getenv("password_senior"),
    "host_senior": os.getenv("host_senior"),
    "port_senior": os.getenv("port_senior"),
    "service_name_senior": os.getenv("service_name_senior"),
}

# --- Configurações da API da Gupy ---
GUPY_TOKEN = os.getenv("TOKEN")

# --- Configurações para Envio de E-mail (API Graph) ---
EMAIL_CONFIG = {
    "tenant_id": os.getenv("TENANT_ID"),
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "scope": os.getenv("SCOPE", "https://graph.microsoft.com/.default"),
    "email_remetente": os.getenv("EMAIL_LOG"),
    "destinatario": os.getenv("EMAIL_LOG")
}
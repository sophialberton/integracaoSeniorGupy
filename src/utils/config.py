import os 
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'venv', '.env')
load_dotenv(dotenv_path)

#Database
host_data = os.getenv('host')
port_data = os.getenv('port')
service_name_data=os.getenv('service_name')
user_data=os.getenv('user')
password_data=os.getenv('password')
pictureBirth = os.getenv('PICTUREBIRTH')
pictureNew = os.getenv('PICTURENEW')
linkRedirect= os.getenv('LINKREDIRECT')

#API
scope = os.getenv("SCOPE")
tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
email_from = os.getenv("USER_MAIL")
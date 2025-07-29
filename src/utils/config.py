import os 
from dotenv import load_dotenv


load_dotenv("venv/.env")

#Database
host_data = os.getenv('host')
port_data = os.getenv('port')
service_name_data=os.getenv('service_name')
user_data=os.getenv('user')
password_data=os.getenv('password')
token = os.getenv("TOKEN") 

dict_extract = {
    "Gupy":{
        "token":    token,
        "host":     host_data,
        "port":     port_data,
        "service":  service_name_data,
        "user":     user_data,
        "password": password_data
    }
}
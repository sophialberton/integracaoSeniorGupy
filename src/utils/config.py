import os 
from dotenv import load_dotenv

load_dotenv("venv/.env")

#Database
host_senior           = os.getenv('host_senior')
port_senior           = os.getenv('port_senior')
service_name_senior   =os.getenv('service_name_senior')
user_senior           =os.getenv('user_senior')
password_senior       =os.getenv('password_senior')
token               = os.getenv("TOKEN") 

dict_extract = {
    "Gupy":{
        "token":    token,
        "host_senior":     host_senior,
        "port_senior":     port_senior,
        "service_senior":  service_name_senior,
        "user_senior":     user_senior,
        "password_senior": password_senior
    }
}
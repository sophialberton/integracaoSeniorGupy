import sys
import os
import requests
import logging
from dotenv import load_dotenv,find_dotenv
# from utils.config import dict_extract
from collections import defaultdict
from conexaoGupy import conexaoGupy
# from data.querySenior import ConsultaSenior
from conexaoSenior import DatabaseSenior
# Caminho para encontrar a pasta 'src'
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)
    
class ponteSeniorGupy():
    def __init__(self,**kwargs):
        load_dotenv(find_dotenv())
        self.token = kwargs.get("token")       
        self.data = []   
        self.conexaoSenior = DatabaseSenior()
        # self.emailSenior = DatabaseSenior.buscaColaboradorSenior(self="Email")
        self.connection = None  # Declara conexão como None
        self.cursor = None # Declara cursor como None
    
    def process_user(self, data):            
        listaSenior = []
        try:
            situacaoSenior  = getattr(data, "Situacao", None)
            matriculaSenior = getattr(data, "Matricula", None)
            cpfSenior       = getattr(data, "Cpf", None)
            nomeSenior      = getattr(data, "Nome", None)
            emailSenior     = getattr(data, "Email", None)
            cargoSenior     = getattr(data, "Cargo", None)
            filialSenior    = getattr(data, "Filial", None)

            listaSenior.append([
                situacaoSenior, matriculaSenior, cpfSenior,
                nomeSenior, emailSenior, cargoSenior, filialSenior
            ])
        except Exception as e:
            logging.error(f"Erro ao processar colaborador: {e}")
        
        return listaSenior

        """ 
        # listaSenior = []
        # # Verifica se 'data' é um dicionário
        # if isinstance(self.data, dict):
        #     situacaoSenior  = self.data.get("Situacao")
        #     matriculaSenior = self.data.get("Matricula")
        #     cpfSenior       = self.data.get("Cpf")
        #     nomeSenior      = self.data.get("Nome")
        #     emailSenior     = self.data.get("Email")
        #     cargoSenior     = self.data.get("Cargo")
        #     filialSenior    = self.data.get("Filial")
        # else:
        #     # Se for um objeto com atributos
        #     situacaoSenior  = getattr(self.data, "Situacao", None)
        #     matriculaSenior = getattr(self.data, "Matricula", None)
        #     cpfSenior       = getattr(self.data, "Cpf", None)
        #     nomeSenior      = getattr(self.data, "Nome", None)
        #     emailSenior     = getattr(self.data, "Email", None)
        #     cargoSenior     = getattr(self.data, "Cargo", None)
        #     filialSenior    = getattr(self.data, "Filial", None)

        # listaSenior.append([situacaoSenior, matriculaSenior, cpfSenior, nomeSenior, emailSenior, cargoSenior, filialSenior])
        # return listaSenior
        lista = []          
        situacaoSenior      = data.Situacao
        matriculaSenior     = data.Matricula
        nomeSenior          = data.Nome
        emailSenior         = data.Email
        cargoSenior         = data.Cargo
        filialSenior        = data.Filial
        lista.append([situacaoSenior,matriculaSenior,nomeSenior,emailSenior,cargoSenior,filialSenior])
        return lista
         """
    
    def dataSenior(self, colaboradores):
        # print(colaboradores)
        logging.info(">Processando dados colaboradores Senior (dataSenior)")
        # usuarios = self.process_user(colaboradores)        
        usuarios = []
        for colaborador in colaboradores:
                usuario = self.process_user(colaborador)
                usuarios.extend(usuario)  # pois process_user retorna uma lista com um item
        # print(usuarios) 
        logging.info(">Dados colaboradores Senior processados (dataSenior)")
        return usuarios
    
    def verificaColaboradores(self, colaboradores):
        conexao = conexaoGupy()
        usuarios = ponteSeniorGupy.dataSenior(self, colaboradores)
        logging.info(">Verificando Colaboradores (verificaColaboradores)")
        # print(colaboradores)
        # usuarios = self.process_user(self)
        # print(usuarios) # Esta funcionando
        
        for item in usuarios:
            if isinstance(item, (list, tuple)) and len(item) >= 3:
                cpfSenior = item[2]
                matriculaSenior = item[1]
                # processar aqui
            else:
                print(f"Formato inesperado: {item}")

        
        # Agrupando por CPF
        cpf_dict = defaultdict(list)
        for item in usuarios:
            cpf_dict[cpfSenior].append(matriculaSenior)
        logging.info(">Agrupando por CPFs (verificaColaboradores)")
        
        # Verifica se um CPF se repete:
        for cpfSenior, contagem in cpf_dict.items():
            # Se cpfSenior repete:
            if len(contagem) > 1:
                # le matriculas vinculadas ao cpf (loop) e conta a quantidade de matricula
                for cpfSenior, matriculaSenior,nomeSenior,emailSenior, situacaoSenior, cargoSenior,filialSenior in usuarios:
                    contador_matricula = 0
                    qtd_matriculas = len(contagem)
                    # se situação da matricula for diferente de demitido (ou seja, esta admitido)
                    if situacaoSenior != '7':
                        # se tem nao cadastro na gupy
                        if not conexao.listaUsuariosGupy(emailSenior):
                            # cria cadastro
                            conexao.criaUsuarioGupy(nomeSenior,emailSenior)
                    # se situação da matricula for igual a demitido
                    else:
                        # se contador matricula for igual a quantidade de matriculas
                        if contador_matricula == qtd_matriculas:
                            # se tem cadastro na gupy
                            if conexao.listaUsuariosGupy(emailSenior):
                                # Deleta
                                conexao.deletaUsuarioGupy(cpfSenior)
                contador_matricula += 1
            # se cpf nao se repete
            else:
                print(f"CPF {cpfSenior} aparece apenas uma vez.")                
                # Le matricula vinculada ao CPF -> Não sei como fazer a leitura da matricula do Cpf
                matricula = matriculaSenior[0]
                situacaoSenior = matricula["situacaoSenior"]
                # tem_cadastro_gupy = matricula["tem_cadastro_gupy"]
                
                #se situação da matricula for diferente de demitido (ou seja, esta admitido)
                if situacaoSenior != '7':
                    # se tem nao cadastro na gupy
                    if not conexao.listaUsuariosGupy(emailSenior):
                        # Cria cadastro
                        conexao.criaUsuarioGupy(nomeSenior,emailSenior)
                # Se situação da matricula for igual a demitido
                else:
                    # Se tem cadastro na Gupy
                    if conexao.listaUsuariosGupy(emailSenior):
                        # Deleta cadastro
                        conexao.deletaUsuarioGupy(cpfSenior)
        logging.info(">Colaboradores Verificados")
 
    def listaColaboradores(self):
        logging.info(">ListaColaboradores")
        # DEPOIS DE FILTRAR SE É SITUACAO != 7 ELE VAI VIR PARA CÁ, AQUI VAI SER VERIFICADO SE O USUARIO JÁ TEM CADASTRO NA GUPY, 
        # SE NAO TIVER ELE VAI PARA O CADASTRO
        pass
   
    def criaColaboradoresGupy(self):
        logging.info("criaColaboradores")
        dados = self.querySenior()
        url = "https://api.gupy.io/api/v1/users"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer f21dcc63-73bc-4b69-85f0-b9ac179d457f"
        }
        response = requests.post(url, headers=headers)
        print(response.text)
        
    def updateColaboradores(self):
        logging.info("updateColaboradores")
        dados = self.listaColaboradores()
        for id,nome,email in dados:
            try:        
                url = f"https://api.gupy.io/api/v1/users/{id}"

                payload = {
                    "name": f"{nome}",
                    "email": f"{email}"
                }
                headers = {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "authorization": f"Bearer {self.token}"
                }

                response = requests.put(url, json=payload, headers=headers)

                print(response.text)   
            except:
                pass 
  
    def deleteColaboradores(self):
        logging.info("deleteColaboradores")
        dados = self.verificaColaboradores()
        for ids in dados:
            try:
                url = f"https://api.gupy.io/api/v1/users/{ids}"
                headers = {
                    "accept": "application/json",
                    "authorization": "Bearer f21dcc63-73bc-4b69-85f0-b9ac179d457f"
                }
                response = requests.delete(url, headers=headers)

                print(response.text)
            except Exception as e:
                print(e)
  
    def run(self):
        self.updateColaboradores()

# ponteSeniorGupy(**dict_extract["Gupy"]).listaColaboradores()
    
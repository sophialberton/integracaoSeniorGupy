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
    def __init__(self,):
        load_dotenv(find_dotenv())
        self.data = []   
        self.conexaoSenior = DatabaseSenior()
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
        # print(usuarios) # Esta funcionando
        
        usuarios_validos = []
        usuarios_invalidos = []

        for item in usuarios:
            if isinstance(item, (list, tuple)) and len(item) >= 5:
                email = item[4]  # Supondo que o email esteja na posição 3
                if email and email.strip() != "":
                    usuarios_validos.append(item)
                else:
                    usuarios_invalidos.append(item)
            else:
                print(f"Formato inesperado: {item}")

        # print(f"usuarios válidos: {usuarios_validos}") # recebendo [situação, matrícula, cpf, nome, email, cargo, filial] nesta ordem
        
        for item in usuarios_validos:
            if isinstance(item, (list, tuple)) and len(item) >= 3:
                cpfSenior = item[2]
                matriculaSenior = item[1]
            else:
                print(f"Formato inesperado: {item}")

        

        # Agrupando por CPF
        cpf_dict = defaultdict(list)
        for item in usuarios_validos:
            if isinstance(item, (list, tuple)) and len(item) >= 7:
                cpf = item[2]
                matricula = item[1]
                cpf_dict[cpf].append(matricula)
            else:
                print(f"Formato inesperado: {item}")
        logging.info(">Agrupando por CPFs (verificaColaboradores)")

        
        logging.info(">Verficando CPFs, se repete ou não (verificaColaboradores)")
        # Verifica se um CPF se repete:
        for cpfSenior, matriculas in cpf_dict.items():
            # Se cpfSenior repete:
            if len(matriculas) > 1:
                # le matriculas vinculadas ao cpf (loop) e conta a quantidade de matricula
                contador_matricula = 0
                qtd_matriculas = len(matriculas)
                for item in usuarios_validos:
                    if item[2] == cpfSenior:
                        situacaoSenior = item[0]
                        matriculaSenior = item[1]
                        nomeSenior = item[3]
                        emailSenior = item[4]
                        cargoSenior = item[5]
                        filialSenior = item[6]
                        # se situação da matricula for diferente de demitido (ou seja, esta admitido)
                        if situacaoSenior != 7:
                            # se tem nao cadastro na gupy
                            if not conexao.listaUsuariosGupy(emailSenior):
                                # cria cadastro
                                conexao.criaUsuarioGupy(nomeSenior, emailSenior)
                        else:
                            # se tem cadastro na gupy
                            if conexao.listaUsuariosGupy(emailSenior):
                                # Deleta
                                logging.info(f">Deletando usuario demitido na gupy: {nomeSenior, emailSenior} (verificaColaboradores.conexao.deletaUsuarioGupy)")
                                conexao.deletaUsuarioGupy(cpfSenior)

                        contador_matricula += 1

            # se cpf nao se repete
            else:
                print(f">>>CPF {cpfSenior} aparece apenas uma vez.")
                # Le matricula vinculada ao CPF
                for item in usuarios_validos:
                    if item[2] == cpfSenior:
                        situacaoSenior = item[0]
                        nomeSenior = item[3]
                        emailSenior = item[4]

                        # se situação da matricula for diferente de demitido (ou seja, esta admitido)
                        if situacaoSenior != 7:
                            # se tem nao cadastro na gupy
                            if not conexao.listaUsuariosGupy(emailSenior):
                                # Cria cadastro
                                conexao.criaUsuarioGupy(nomeSenior, emailSenior)
                        else:
                            # Se tem cadastro na Gupy
                            if conexao.listaUsuariosGupy(emailSenior):
                                # Deleta cadastro
                                logging.info(f">Deletando usuario demitido na gupy: {nomeSenior, emailSenior} (verificaColaboradores.conexao.deletaUsuarioGupy)")
                                conexao.deletaUsuarioGupy(cpfSenior)

        logging.info(">Colaboradores Verificados")

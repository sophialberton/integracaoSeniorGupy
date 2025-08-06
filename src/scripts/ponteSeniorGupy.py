import sys
import os
import csv
import logging
from dotenv import load_dotenv,find_dotenv
from collections import defaultdict
from conexaoGupy import conexaoGupy
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
        # print(colaboradores) # Recebendo
        logging.info(">Processando dados colaboradores Senior (dataSenior)")
        usuarios = []
        for colaborador in colaboradores:
                usuario = self.process_user(colaborador)
                usuarios.extend(usuario)  # Process_user retorna uma lista com um item
        # print(usuarios) # Recebendo OK
        logging.info(">Dados colaboradores Senior processados (dataSenior)")
        return usuarios
      
    def verificaColaboradores(self, colaboradores):
        logging.info(">Verificando Colaboradores (verificaColaboradores)")
        # print(colaboradores) # Recebendo
        api = conexaoGupy()
        usuarios = ponteSeniorGupy.dataSenior(self, colaboradores)
        # print(usuarios) # Dados de Colaboradores tratados.
        usuarios_validos = []
        usuarios_invalidos = []
        usuarios_ignorados = []
        
        logging.info(">Carregando CPF ignorados do arquivo ignoradosRH.csv") # nome completo;cpf
        cpfs_ignorados_csv = set()
        with open('src/scripts/ignoradosRH.csv', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if len(row) >= 2:
                    cpf = row[1].strip()
                    if cpf:
                        cpfs_ignorados_csv.add(cpf)
                        
        cpfs_ignorados = list(cpfs_ignorados_csv)
        cpfs_ignorados_str =  ",".join(cpfs_ignorados)
 
        logging.info(">Valida apenas colaboradores com email @fgmdental.group.com;(verificaColaboradores)")        
        logging.info(">Ignora RH e Direção(verificaColaboradores)")        
        for item in usuarios:
            if isinstance(item, (list, tuple)) and len(item) >= 5:            
                # Filtro comparação cpfs Senior com cpfs de ignoradosRh.csv    
                cpfSenior = item[2]
                if cpfSenior and cpfs_ignorados_str.strip():
                    cpfSenior = str(item[2]).strip()
                    if cpfSenior in cpfs_ignorados_csv:
                        usuarios_ignorados.append(item)

                # Filtro emails validos ou invalidos
                emailSenior = item[4]
                if emailSenior and emailSenior.strip() != "":
                    # Separar os e-mails, assumindo que estão separados por vírgula ou espaço
                    emails = [e.strip() for e in emailSenior.replace(',', ' ').split() if e.strip()]
                    # Filtra apenas os e-mails do domínio @fgmdentalgroup.com
                    emails_fgmdental = [e for e in emails if "@fgmdentalgroup.com" in e]
                    if emails_fgmdental:
                        # Substituir o campo de e-mail com apenas os válidos do domínio
                        item[4] = ', '.join(emails_fgmdental[:1])  # incluir apenas um
                        usuarios_validos.append(item)
                    else:
                        # Se não houver e-mail do domínio desejado, considerar inválido
                        usuarios_invalidos.append(item)
                else:
                    # E-mail vazio
                    usuarios_invalidos.append(item)
            else:
                print(f"Formato inesperado: {item}")
        
        # listas: [situação, matrícula, cpf, nome, email, cargo, filial] nesta ordem
        # print(f"usuarios ignorados: {usuarios_ignorados}") # recebendo corretamente
        # print(f"usuarios válidos: {usuarios_validos}") # recebendo corretamente
        # print(f"usuarios invalidos: {usuarios_invalidos}") # recebendo corretamente
        
        for item in usuarios_ignorados:
            if isinstance(item, (list, tuple)) and len(item) > 3:
                nome = item[3]
                logging.info(f"Usuário ignorado: {nome}")
            else:
                logging.warning(f"Formato inesperado: {item}")
       
        logging.info(">Agrupando por CPFs (verificaColaboradores)")
        cpf_dict = defaultdict(list)
        for item in usuarios_validos:
            if isinstance(item, (list, tuple)) and len(item) >= 7:
                cpf = item[2]
                matricula = item[1]
                cpf_dict[cpf].append(matricula)
            else:
                logging.error(f"Formato inesperado: {item}")
        
        # verifica se um CPF se repete:
        cpfs_repetidos = []
        cpfs_unitarios = []
        
        logging.info(">Verficando CPFs repetidos(verificaColaboradores)")
        for cpfSenior, matriculas in cpf_dict.items():
            # se cpfSenior repete:
            if len(matriculas) > 1:
                cpfs_repetidos.append(cpfSenior)
                print(f">>>CPF {cpfSenior} com duas matriculas")
                # le matriculas vinculadas ao cpf (loop) e conta a quantidade de matricula
                contador_matricula = 0
                for item in usuarios_validos:
                    if item[2] == cpfSenior:
                        situacaoSenior = item[0]
                        nomeSenior = item[3]
                        emailSenior = item[4]
                        # se situação da matricula for diferente de demitido (ou seja, esta admitido)
                        if situacaoSenior != 7:
                            # se tem nao cadastro na gupy
                            if not api.listaUsuariosGupy(emailSenior):
                                # cria cadastro
                                api.criaUsuarioGupy(nomeSenior, emailSenior, cpfSenior)
                        else:
                            # se tem cadastro na gupy
                            if api.listaUsuariosGupy(emailSenior):
                                # Deleta
                                api.deletaUsuarioGupy(cpfSenior)
                    contador_matricula += 1
            # se cpf nao se repete
            else:
                cpfs_unitarios.append(cpfSenior)
                print(f">>>CPF {cpfSenior} com uma matrícula.")
                # le matricula vinculada ao CPF
                for item in usuarios_validos:
                    if item[2] == cpfSenior:
                        situacaoSenior = item[0]
                        nomeSenior = item[3]
                        emailSenior = item[4]
                        # se situação da matricula for diferente de demitido (ou seja, esta admitido)
                        if situacaoSenior != 7:
                            # se tem nao cadastro na gupy
                            if not api.listaUsuariosGupy(emailSenior):
                                # Cria cadastro
                                api.criaUsuarioGupy(nomeSenior, emailSenior, cpfSenior)
                        else:
                            # Se tem cadastro na Gupy
                            if api.listaUsuariosGupy(emailSenior):
                                # Deleta cadastro
                                api.deletaUsuarioGupy(cpfSenior)
        # print(cpfs_repetidos)
        logging.info(">Colaboradores Verificados")

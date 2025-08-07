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
            # cargoSenior     = getattr(data, "Cargo", None)
            # filialSenior    = getattr(data, "Filial", None)
            listaSenior.append([
                situacaoSenior, matriculaSenior, cpfSenior,
                nomeSenior, emailSenior])
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
                        
 
        logging.info(">Valida apenas colaboradores com email @fgmdental.group.com;(verificaColaboradores)")        
        logging.info(">Ignora RH e Direção(verificaColaboradores)")        
 
        for item in usuarios:
            if isinstance(item, (list, tuple)) and len(item) >= 5:            
                # Filtro comparação cpfs Senior com cpfs de ignoradosRh.csv    
                cpfSenior = str(item[2]).strip()
                if cpfSenior in cpfs_ignorados_csv:
                    usuarios_ignorados.append(item)
                    continue
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
        
        cpf_dict = defaultdict(list)
        for item in usuarios_validos:
            if isinstance(item, (list, tuple)) and len(item) >= 5:
                cpf = str(item[2]).strip()
                # matricula = item[1]
                cpf_dict[cpf].append(item)
            else:
                logging.warning(f"Formato inesperado ao agrupar CPFs: {item}")
        
        # listas: [situação, matrícula, cpf, nome, email, cargo, filial] nesta ordem
        # print(f"usuarios ignorados: {usuarios_ignorados}") # recebendo corretamente
        # print(f"usuarios validos: {usuarios_validos}") # recebendo corretamente
        # print(f"usuarios invalidos: {usuarios_invalidos}") # recebendo corretamente
        
        """
        for item in usuarios_ignorados:
            if isinstance(item, (list, tuple)) and len(item) > 3:
                nome = item[3]
                logging.info(f">Usuario ignorado: {nome}")
            else:
                logging.warning(f"Formato inesperado: {item}")
                """
       
        logging.info(">Agrupando por CPFs (verificaColaboradores)")
        
        # verifica se um CPF se repete:
        cpfs_repetidos = []
        cpfs_unitarios = []
        
        logging.info(">Verficando CPFs repetidos(verificaColaboradores)")
        
        for cpfSenior, matriculas_do_cpf in cpf_dict.items():
            # se cpfSenior repete:
            if len(matriculas_do_cpf) > 1:
                cpfs_repetidos.append(cpfSenior)
                # Filtra todas as matrículas válidas desse CPF

                cpfs_repetidos.append(cpfSenior)
                print(f"> CPF {cpfSenior} com mais de uma matricula")
                nomeSenior = matriculas_do_cpf[0][3]
                print(f">  Matriculas encontradas para {nomeSenior}:")
                todas_demitidas = True
                # Assume que todas estão demitidas até encontrar uma que não esteja
                        
                # Filtra todas as matrículas válidas desse CPF
                for i, item in enumerate(matriculas_do_cpf, start=1):
                    situacao = int(item[0])
                    nome = item[3]
                    email = item[4]                    
                    print(f">    Matricula {i} - {item[1]}:")
                    print(f">      Situacao: {situacao} (tipo: {type(item[0])})")
                    print(f">      Nome: {nome}")
                    print(f">      Email: {email}")
                    if situacao != 7:
                        todas_demitidas = False
                print(f">  Todas as matriculas estao demitidas? {'Sim' if todas_demitidas else 'Nao'}")
                nomeSenior = matriculas_do_cpf[0][3]
                emailSenior = matriculas_do_cpf[0][4]
                
                if todas_demitidas:
                    # Só deleta se TODAS estiverem demitidas
                    idGupy = api.listaUsuariosGupy(nomeSenior, emailSenior)
                    if idGupy:
                        api.deletaUsuarioGupy(idGupy, nomeSenior)
                else:
                    # Se tem pelo menos uma ativa, garante que o cadastro exista
                    situacao = int(matriculas_do_cpf[0][0])
                    if int(item[0]) != 7:
                        # nomeSenior = item[3]
                        # emailSenior = item[4]
                        idGupy = api.listaUsuariosGupy(nomeSenior, emailSenior)
                        if not idGupy:
                            print(f">Criou usuario {nomeSenior} com email {emailSenior}")
                            logging.info(f">Criou usuario na gupy: {nomeSenior, emailSenior} (verificaColaboradores.api.criaUsuarioGupy)")
                            # api.criaUsuarioGupy(nomeSenior, emailSenior, cpfSenior)

            # se cpf NÂO se repete
            else:  
                todas_demitidas = True
                # Filtra todas as matrículas válidas desse CPF
                for i, item in enumerate(matriculas_do_cpf, start=1):
                    situacao = int(item[0])
                    nome = item[3]
                    email = item[4]                    
                    print(f">    Matricula {i} - {item[1]}:")
                    print(f">      Situacao: {situacao} (tipo: {type(item[0])})")
                    print(f">      Nome: {nome}")
                    print(f">      Email: {email}")
                    if situacao != 7:
                        todas_demitidas = False
                print(f">  Todas as matriculas estao demitidas? {'Sim' if todas_demitidas else 'Nao'}")
                nomeSenior = matriculas_do_cpf[0][3]
                emailSenior = matriculas_do_cpf[0][4]
                
                if todas_demitidas:
                    # Só deleta se TODAS estiverem demitidas
                    idGupy = api.listaUsuariosGupy(nomeSenior, emailSenior)
                    if idGupy:
                        api.deletaUsuarioGupy(idGupy, nomeSenior)
                    if not idGupy:
                        api.criaUsuarioGupy(nomeSenior, emailSenior, cpfSenior)
                
                cpfs_unitarios.append(cpfSenior)
                
        # print(cpfs_repetidos)
        # print(cpfs_unitarios)
        logging.info(">Colaboradores Verificados")

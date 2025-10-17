# utils/colaboradores.py

import logging
import csv
import pandas as pd
from .helpers import extrair_email_valido, encontrar_similar_to
from .mapeamento import MAPA_CARGOS, MAPA_DEPARTAMENTOS
from servicos.conexao_gupy import ServicoGupy

def carregar_cpfs_ignorados(caminho_arquivo="dados/ignoradosRH.csv"):
    """Carrega os CPFs a serem ignorados de um arquivo CSV."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            # Garante que a linha tem pelo menos 2 colunas e que a segunda não está vazia
            return {row[1].strip() for row in reader if len(row) > 1 and row[1]}
    except FileNotFoundError:
        logging.warning(f"Arquivo de CPFs ignorados não encontrado em: {caminho_arquivo}. Nenhum CPF será ignorado.")
        return set()
    except Exception as e:
        logging.error(f"Erro ao ler o arquivo de CPFs ignorados: {e}")
        return set()

def classificar_usuarios(df, cpfs_ignorados):
    """Classifica o DataFrame de colaboradores em válidos, inválidos, ignorados e desligados."""
    df['Cpf'] = df['Cpf'].astype(str).str.strip().str.zfill(11)
    
    df_ignorados = df[df['Cpf'].isin(cpfs_ignorados)]
    df_processar = df[~df['Cpf'].isin(cpfs_ignorados)].copy()
    
    # Aplica a extração de e-mail válido
    df_processar['EmailValido'] = df_processar['Email'].apply(extrair_email_valido)
    
    # Agrupa por CPF para verificar se todos os registros estão desligados
    desligados_cpfs = []
    for cpf, grupo in df_processar.groupby('Cpf'):
        if (grupo['Situacao'] == 7).all():
            desligados_cpfs.append(cpf)
    
    df_desligados = df_processar[df_processar['Cpf'].isin(desligados_cpfs)]
    df_processar = df_processar[~df_processar['Cpf'].isin(desligados_cpfs)]
    
    df_validos = df_processar[df_processar['EmailValido'].notna()].copy()
    df_invalidos = df_processar[df_processar['EmailValido'].isna()].copy()
    
    df_invalidos.drop(columns=['EmailValido'], inplace=True)
    
    return df_validos, df_invalidos, df_ignorados, df_desligados


def cria_e_obtem_campos(servico_gupy, registro, email_gupy=None):
    """
    Função auxiliar para obter ou criar IDs de cargo, departamento e filial na Gupy.
    Isso centraliza a lógica que antes estava em `camposCadastros.py`.
    """
    dados_atualizacao = {}

    nome = registro.get("Nome")
    if nome:
        dados_atualizacao["name"] = nome

    email = email_gupy or registro.get("EmailValido") or registro.get("Email")
    if email:
        dados_atualizacao["email"] = email

    # 1. Processar Cargo (Role)
    nome_cargo = registro.get("Role_gupy")
    if nome_cargo:
        similar_to_cargo = encontrar_similar_to(nome_cargo, MAPA_CARGOS)
        cargo_id = servico_gupy.obtem_cargo(nome_cargo, similar_to_cargo)
        if cargo_id:
            dados_atualizacao['roleId'] = cargo_id
            dados_atualizacao['roleName'] = nome_cargo


            # Para os comuns deve ser o 231953
            # Verifica se o cargo exige accessProfileId especial
            palavras_chave = ["gerente", "líder", "lider", "especialista", "supervisor", "coordenador", "diretor"]
            if any(palavra in nome_cargo.lower() for palavra in palavras_chave):
                dados_atualizacao['accessProfileId'] = 127509
            else:
                dados_atualizacao['accessProfileId'] = 231953
                logging.info(f'Atualiazando perfil de acesso para Comunicação & Endo')

    # 2. Processar Departamento (Department)
    nome_departamento = registro.get("Departamento_gupy")
    if nome_departamento:
        similar_to_dep = encontrar_similar_to(nome_departamento, MAPA_DEPARTAMENTOS)
        dep_id = servico_gupy.obtem_departamento(nome_departamento, similar_to_dep)
        if dep_id:
            dados_atualizacao['departmentId'] = dep_id
    
    # 3. Processar Filial (Branch)
    nome_filial = registro.get("Branch_gupy")
    cod_filial = registro.get("Filial_cod")
    if nome_filial and cod_filial:
        branch_id = servico_gupy.obtem_filial(nome_filial, cod_filial)
        if branch_id:
            dados_atualizacao['branchIds'] = [branch_id]

    return dados_atualizacao

def processar_colaboradores(servico_gupy: ServicoGupy, df_total: pd.DataFrame):
    """
    Função principal que orquestra todo o processamento dos colaboradores,
    centralizando a lógica de negócio.
    """
    cpfs_ignorados = carregar_cpfs_ignorados()
    df_validos, df_invalidos, df_ignorados, df_desligados = classificar_usuarios(df_total, cpfs_ignorados)
    df_invalidos_ativos = df_invalidos[df_invalidos['Situacao'] != 7]
    nomes_sem_email_valido = df_invalidos_ativos['Nome'].unique().tolist()
    nomes_formatados = "\n".join(nomes_sem_email_valido)

    # Logging dos totais para conferência
    logging.info(f"Total de registros recebidos do Senior: {len(df_total)}")
    logging.info(f"Registros com e-mail válido para processar: {len(df_validos)}")
    logging.info(f"Registros sem e-mail válido nos domínios: {len(df_invalidos)}")
    logging.info(f"Registros ignorados por CPF: {len(df_ignorados)}")
    logging.info(f"Registros totalmente desligados: {len(df_desligados)}")
    logging.info(f"Registros ATIVOS sem e-mail válido nos domínios: {len(nomes_sem_email_valido)}")

    logging.info("Nomes de colaboradores ativos sem e-mail válido nos domínios:\n" + nomes_formatados)


    # === 1. Processa os desligados com e-mail válido ===
    # usuarios_desligados = {cpf: grupo for cpf, grupo in df_desligados.groupby('Cpf')}
    # for cpf, registros_df in usuarios_desligados.items():
    #     # Verifica se há pelo menos um registro com e-mail válido
    #     registros_com_email = registros_df[registros_df['EmailValido'].notna()]
    #     if registros_com_email.empty:
    #         # logging.info(f"> [DESLIGADO] CPF {cpf} ignorado por não ter e-mail válido.")
    #         continue

    #     registro_principal = registros_com_email.iloc[0]
    #     nome = registro_principal['Nome']
    #     email = registro_principal['EmailValido']
    #     logging.info(f">===================================================================================")
    #     logging.info(f">    [DESLIGADO] Processando CPF: {cpf} - Nome: {nome}")

    #     usuario = servico_gupy.listar_usuario_por_email(nome, email)
    #     if usuario:
    #         logging.critical(f"> Colaborador desligado com cadastro na Gupy. Deletando usuário da Gupy: {usuario['name']} (email: {usuario['email']}/ID: {usuario['id']})")
    #         servico_gupy.deletar_usuario(usuario["id"], nome)
        
    #     employee = servico_gupy.lista_employee(cpf)
    #     if employee:
    #         logging.critical(f"> Colaborador desligado com nome na lista de colaboradores na Gupy. Deletando cadastro da lista Gupy: {usuario['name']} (cpf: {usuario['cpf']})")
    #         servico_gupy.deleta_employee(employee['id'], nome)


    # === 2. Processa os colaboradores ativos ===
    usuarios_ativos = {cpf: grupo for cpf, grupo in df_validos.groupby('Cpf')}
    for cpf, registros_df in usuarios_ativos.items():
        registros_ativos = registros_df[registros_df['Situacao'] != 7]
        if registros_ativos.empty:
            continue  # Nenhum registro ativo, ignora
        registro_principal = registros_ativos.iloc[0]  # Pega o primeiro ativo
        nome = registro_principal['Nome']
        email = registro_principal['EmailValido']
        logging.info(f">===================================================================================")
        logging.info(f">    [ATIVO] Processando CPF: {cpf} - Nome: {nome}")

        employee = servico_gupy.obtem_employee(nome, cpf)
        if not employee:
            logging.warning(f"> Employee com CPF {cpf} não pôde ser criado ou obtido.")
            continue  # pula para o próximo

        usuario = servico_gupy.criar_usuario(nome, email, cpf)
        if usuario:
            usuario_id = usuario["id"]
            dados_para_atualizar = cria_e_obtem_campos(servico_gupy, registro_principal, usuario["email"])
            if dados_para_atualizar:
                servico_gupy.atualizar_usuario(usuario_id, dados_para_atualizar)
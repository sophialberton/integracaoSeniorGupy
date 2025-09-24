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
    """Classifica o DataFrame de colaboradores em válidos, inválidos e ignorados."""
    df['Cpf'] = df['Cpf'].astype(str).str.strip().str.zfill(11)
    
    df_ignorados = df[df['Cpf'].isin(cpfs_ignorados)]
    df_processar = df[~df['Cpf'].isin(cpfs_ignorados)].copy()
    
    # Aplica a extração de e-mail válido para separar os colaboradores processáveis
    df_processar['EmailValido'] = df_processar['Email'].apply(extrair_email_valido)
    
    df_validos = df_processar[df_processar['EmailValido'].notna()].copy()
    df_invalidos = df_processar[df_processar['EmailValido'].isna()].copy()
    
    # A coluna 'EmailValido' agora contém o e-mail limpo e será usada no processamento
    df_invalidos.drop(columns=['EmailValido'], inplace=True)
    
    return df_validos, df_invalidos, df_ignorados

def cria_e_obtem_campos(servico_gupy, registro):
    """
    Função auxiliar para obter ou criar IDs de cargo, departamento e filial na Gupy.
    Isso centraliza a lógica que antes estava em `camposCadastros.py`.
    """
    dados_atualizacao = {}
    
    nome = registro.get("Nome")
    if nome:
        dados_atualizacao["name"] = nome
    
    email = registro.get("EmailValido") or registro.get("Email")
    if email:
        dados_atualizacao["email"] = email

    # 1. Processar Cargo (Role)
    nome_cargo = registro.get("Role_gupy")
    if nome_cargo:
        similar_to_cargo = encontrar_similar_to(nome_cargo, MAPA_CARGOS)
        # Supondo que ServicoGupy terá um método `obter_ou_criar_cargo`
        cargo_id = servico_gupy.obtem_cargo(nome_cargo, similar_to_cargo)
        if cargo_id:
            dados_atualizacao['roleId'] = cargo_id

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
    df_validos, df_invalidos, df_ignorados = classificar_usuarios(df_total, cpfs_ignorados)

    # Logging dos totais para conferência
    logging.info(f"Total de registros recebidos do Senior: {len(df_total)}")
    logging.info(f"Registros com e-mail válido para processar: {len(df_validos)}")
    logging.info(f"Registros sem e-mail válido nos domínios: {len(df_invalidos)}")
    logging.info(f"Registros ignorados por CPF: {len(df_ignorados)}")

    # Agrupa por CPF para tratar múltiplas matrículas
    usuarios_agrupados = {cpf: grupo for cpf, grupo in df_validos.groupby('Cpf')}

    for cpf, registros_df in usuarios_agrupados.items():
        # A lógica considera o registro mais recente ou o primeiro como principal
        registro_principal = registros_df.iloc[0]
        nome = registro_principal['Nome']
        email = registro_principal['EmailValido']  # Usa o e-mail já validado
        logging.info(f">===================================================================================")
        logging.info(f">    Processando CPF: {cpf} - Nome: {nome}")

        # Verifica a situação de todas as matrículas do CPF. Se TODAS forem 7, ele está desligado.
        todas_desligadas = (registros_df['Situacao'] == 7).all()

        if todas_desligadas:
            usuario = servico_gupy.listar_usuario_por_email(nome, email)
            if usuario:
                logging.info(f"> Colaborador desligado. Deletando usuário da Gupy: {usuario['name']} (email: {usuario['email']}/ID: {usuario['id']})")
                servico_gupy.deletar_usuario(usuario["id"], nome)
            else:
                logging.info(f"> Colaborador desligado ({nome}) não foi encontrado na Gupy. Nenhuma ação necessária.")
        else:  # Colaborador está ATIVO
            usuario_id = servico_gupy.criar_usuario(nome, email, cpf)
            if usuario_id:
                # Após criar, busca os dados de cargo/depto/filial para atualizar
                dados_para_atualizar = cria_e_obtem_campos(servico_gupy, registro_principal)
                logging.info(f"> CHEGOU AQUI : {dados_para_atualizar}")
                if dados_para_atualizar:
                    logging.info(f"> Atualizando dados do usuário: {nome}")
                    servico_gupy.atualizar_usuario(usuario_id, dados_para_atualizar)
          
def montar_payload_somente_campos_vazios(servico_gupy, registro, dados_atuais):
    payload = {}

    # Nome
    nome_novo = registro.get("Nome")
    nome_atual = dados_atuais.get("name")
    if nome_novo and not nome_atual:
        payload["name"] = nome_novo

    # Email
    email_novo = registro.get("Email_gupy")
    email_atual = dados_atuais.get("email")
    if email_novo and not email_atual:
        payload["email"] = email_novo
    # Cargo
    nome_cargo = registro.get("Role_gupy")
    if nome_cargo and not dados_atuais.get("roleId"):
        similar_to_cargo = encontrar_similar_to(nome_cargo, MAPA_CARGOS)
        cargo_id = servico_gupy.obtem_cargo(nome_cargo, similar_to_cargo)
        if cargo_id:
            payload["roleId"] = cargo_id

    # Departamento
    nome_departamento = registro.get("Departamento_gupy")
    if nome_departamento and not dados_atuais.get("departmentId"):
        similar_to_dep = encontrar_similar_to(nome_departamento, MAPA_DEPARTAMENTOS)
        dep_id = servico_gupy.obtem_departamento(nome_departamento, similar_to_dep)
        if dep_id:
            payload["departmentId"] = dep_id

    # Filial
    nome_filial = registro.get("Branch_gupy")
    cod_filial = registro.get("Filial_cod")
    if nome_filial and cod_filial and not dados_atuais.get("branchIds"):
        branch_id = servico_gupy.obtem_filial(nome_filial, cod_filial)
        if branch_id:
            payload["branchIds"] = [branch_id]

    return payload


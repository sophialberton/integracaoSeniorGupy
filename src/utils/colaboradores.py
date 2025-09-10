import logging
import re
import csv
from .helpers import obter_dados_usuario_gupy
from .camposCadastros import processar_campos

def carregar_cpfs_ignorados(caminho_arquivo):
    logging.info("> Carregando CPFs ignorados")
    cpfs = set()
    with open(caminho_arquivo, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if len(row) >= 2:
                cpf = row[1].strip()
                if cpf:
                    cpfs.add(cpf)
    return cpfs

def extrair_email_valido(e):
    if not isinstance(e, str):
        return None
    emails = e.replace(',', ' ').split()
    for email in emails:
        email = email.strip()
        if "@fgmdentalgroup.com" in email or "@fgm.ind.br" in email:
            return email
    return None

def classificar_usuarios_df(usuarios, cpfs_ignorados):
    usuarios['Cpf'] = usuarios['Cpf'].astype(str).str.strip().str.zfill(11)
    usuarios_ignorados = usuarios[usuarios['Cpf'].isin(cpfs_ignorados)]
    usuarios_restante = usuarios[~usuarios['Cpf'].isin(cpfs_ignorados)].copy()
    usuarios_restante['EmailValido'] = usuarios_restante['Email'].apply(extrair_email_valido)
    usuarios_validos = usuarios_restante[usuarios_restante['EmailValido'].notnull()].copy()
    usuarios_validos['Email'] = usuarios_validos['EmailValido']
    usuarios_invalidos = usuarios_restante[usuarios_restante['EmailValido'].isnull()].copy()
    usuarios_validos.drop(columns=['EmailValido'], inplace=True)
    usuarios_invalidos.drop(columns=['EmailValido'], inplace=True)
    return usuarios_validos, usuarios_invalidos, usuarios_ignorados

def agrupar_por_cpf_df(df):
    df['Cpf'] = df['Cpf'].astype(str).str.strip().str.zfill(11)
    return {cpf: grupo for cpf, grupo in df.groupby('Cpf')}

def processar_cpf_df(api, cpf, registros_df):
    registros_df['Situacao'] = registros_df['Situacao'].astype(int)
    todas_demitidas = (registros_df['Situacao'] == 7).all()
    nome_base, email_base = None, None
    userGupyId, emailUserGupy, departamentGupyId, roleGupyId, branchGupyId = None, None, None, None, None

    for _, row in registros_df.iterrows():
        nome = row['Nome']
        email = extrair_email_valido(row['Email'])
        if email:
            nome_base, email_base = nome, email
            userGupyId, emailUserGupy, departamentGupyId, roleGupyId, branchGupyId = obter_dados_usuario_gupy(api, nome, email)
            if userGupyId:
                break
    
    if not email_base:
        logging.warning(f"> CPF {cpf} sem email válido. Nenhuma ação será tomada.")
        return

    if todas_demitidas:
        if userGupyId:
            api.deletaUsuarioGupy(userGupyId, nome_base)
    else:
        if not userGupyId:
            api.criaUsuarioGupy(nome_base, email_base, cpf)
        else:
            processar_campos(api, nome_base, email_base, userGupyId, emailUserGupy, departamentGupyId, roleGupyId, branchGupyId, registros_df.iloc[0].get('Branch_gupy', 'Filial Padrão'), registros_df)
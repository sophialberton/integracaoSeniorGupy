import logging
import csv
from collections import defaultdict
import re
import pandas as df

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

def classificar_usuarios_df(usuarios, cpfs_ignorados):
    usuarios['Cpf'] = usuarios['Cpf'].astype(str).str.strip().str.zfill(11)
    # Classificar como ignorado
    usuarios_ignorados = usuarios[usuarios['Cpf'].isin(cpfs_ignorados)]
    # Filtrar os que não são ignorados
    usuarios_restante = usuarios[~usuarios['Cpf'].isin(cpfs_ignorados)].copy()
    # Validar e limpar e-mails
    usuarios_restante['EmailValido'] = usuarios_restante['Email'].apply(
        lambda e: next(
            (email.strip() for email in (e or '').replace(',', ' ').split() if "@fgmdentalgroup.com" in email), None)
    )
    # Separar válidos e inválidos
    usuarios_validos = usuarios_restante[usuarios_restante['EmailValido'].notnull()].copy()
    usuarios_validos['Email'] = usuarios_validos['EmailValido']
    usuarios_invalidos = usuarios_restante[usuarios_restante['EmailValido'].isnull()].copy()
    # Remover coluna auxiliar
    usuarios_validos.drop(columns=['EmailValido'], inplace=True)
    usuarios_invalidos.drop(columns=['EmailValido'], inplace=True)

    return usuarios_validos, usuarios_invalidos, usuarios_ignorados



def agrupar_por_cpf_df(df_validos):
    df_validos['Cpf'] = df_validos['Cpf'].astype(str).str.strip().str.zfill(11)
    agrupados = {
        cpf: grupo for cpf, grupo in df_validos.groupby('Cpf')
    }
    return agrupados

def processar_cpf_df(api, cpf, registros_df):
    logging.info("> chegou aqyui")
    nome_base = registros_df.iloc[0]['Nome']
    email_base = registros_df.iloc[0]['Email']

    todas_demitidas = (registros_df['Situacao'].astype(int) == 7).all()

    if not re.fullmatch(r'\d{11}', cpf):
        logging.warning(f"CPF suspeito: {cpf}")

    if len(registros_df) > 1:
        print(f"> CPF {cpf} com múltiplas matrículas")
    else:
        print(f"> CPF {cpf} com uma matrícula")

    for i, row in registros_df.iterrows():
        print(f"  Matrícula - {row['Matricula']} | Situação: {row['Situacao']} | Nome: {row['Nome']} | Email: {row['Email']}")

    print(f"  Todas as matrículas estão demitidas? {'Sim' if todas_demitidas else 'Não'}")

    id_gupy = api.listaUsuariosGupy(nome_base, email_base)

    if todas_demitidas:
        if id_gupy:
            api.deletaUsuarioGupy(id_gupy, nome_base)
    else:
        if not id_gupy:
            api.criaUsuarioGupy(nome_base, email_base, cpf)

import logging
import csv
from collections import defaultdict
import re

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

def classificar_usuarios(usuarios, cpfs_ignorados):
    validos, invalidos, ignorados = [], [], []

    for usuario in usuarios:
        if not (isinstance(usuario, (list, tuple)) and len(usuario) >= 5):
            logging.warning(f"Formato inesperado: {usuario}")
            continue

        cpf = str(usuario[2]).strip()
        cpf = cpf.zfill(11)
        email = usuario[4]

        if cpf in cpfs_ignorados:
            ignorados.append(usuario)
            continue

        emails_validos = [e.strip() for e in email.replace(',', ' ').split() if "@fgmdentalgroup.com" in e]
        if emails_validos:
            usuario[4] = emails_validos[0]
            validos.append(usuario)
        else:
            invalidos.append(usuario)

    return validos, invalidos, ignorados

def agrupar_por_cpf(usuarios):
    agrupados = defaultdict(list)
    for usuario in usuarios:
        cpf = str(usuario[2]).strip()
        cpf = cpf.zfill(11)
        agrupados[cpf].append(usuario)
    return agrupados

def processar_cpf(api, cpf, registros):
    nome = registros[0][3]
    email = registros[0][4]
    todas_demitidas = all(int(r[0]) == 7 for r in registros)
    
    if not re.fullmatch(r'\d{11}', cpf):
        logging.warning(f"CPF suspeito: {cpf}")

    if len(registros) > 1:
        print(f"> CPF {cpf} com multiplas matriculas")
    else:
        print(f"> CPF {cpf} com uma matricula")

    for i, r in enumerate(registros, start=1):
        print(f"  Matricula {i} - {r[1]} | Situacao: {r[0]} | Nome: {r[3]} | Email: {r[4]}")

    print(f"  Todas as matriculas estao demitidas? {'Sim' if todas_demitidas else 'Nao'}")

    id_gupy = api.listaUsuariosGupy(nome, email)

    if todas_demitidas:
        if id_gupy:
            api.deletaUsuarioGupy(id_gupy, nome)
    else:
        if not id_gupy:
            api.criaUsuarioGupy(nome, email, cpf)

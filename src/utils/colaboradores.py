import logging
import re
import csv
from utils.helpers import mapear_campos_usuario, obter_dados_usuario_gupy, find_similar_to
from utils.comum import role_mapping, departament_mapping


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
    email_fgm_dental = None
    email_fgm_ind = None

    for email in emails:
        email = email.strip()
        if "@fgmdentalgroup.com" in email:
            email_fgm_dental = email
        elif "@fgm.ind.br" in email:
            email_fgm_ind = email

    if email_fgm_dental:
        return email_fgm_dental
    elif email_fgm_ind:
        return email_fgm_ind # .replace("@fgm.ind.br", "@fgmdentalgroup.com") # Troca o domínio para @fgmdentalgroup.com
    else:
        return None

def classificar_usuarios_df(usuarios, cpfs_ignorados):
    usuarios['Cpf'] = usuarios['Cpf'].astype(str).str.strip().str.zfill(11)
    # Classificar como ignorado
    usuarios_ignorados = usuarios[usuarios['Cpf'].isin(cpfs_ignorados)]
    # Filtrar os que não são ignorados
    usuarios_restante = usuarios[~usuarios['Cpf'].isin(cpfs_ignorados)].copy()
    # Validar e limpar e-mails
    usuarios_restante['EmailValido'] = usuarios_restante['Email'].apply(extrair_email_valido)
    # Separar válidos e inválidos
    usuarios_validos = usuarios_restante[usuarios_restante['EmailValido'].notnull()].copy()
    usuarios_validos['Email'] = usuarios_validos['EmailValido']
    usuarios_invalidos = usuarios_restante[usuarios_restante['EmailValido'].isnull()].copy()
    # Remover coluna auxiliar
    usuarios_validos.drop(columns=['EmailValido'], inplace=True)
    usuarios_invalidos.drop(columns=['EmailValido'], inplace=True)

    return usuarios_validos, usuarios_invalidos, usuarios_ignorados

def verificar_cpfs_repetidos(df):
    cpfs = df['Cpf'].astype(str).str.strip().str.zfill(11)
    cpfs_repetidos = cpfs[cpfs.duplicated()].unique().tolist()
    print(f"> Total de CPFs repetidos encontrados: {len(cpfs_repetidos)}")
    # for cpf in cpfs_repetidos:
    #     print(f"  - {cpf}")
    # return cpfs_repetidos

def agrupar_por_cpf_df(df_validos):
    df_validos['Cpf'] = df_validos['Cpf'].astype(str).str.strip().str.zfill(11)
    verificar_cpfs_repetidos(df_validos)  # Adiciona verificação explícita
    agrupados = {
        cpf: grupo for cpf, grupo in df_validos.groupby('Cpf')
    }
    return agrupados

def processar_cpf_df(api, cpf, registros_df):
    registros_df['Situacao'] = registros_df['Situacao'].astype(int)
    todas_demitidas = (registros_df['Situacao'] == 7).all()

    nomeFilialBranch = registros_df.iloc[0].get('Branch_gupy', 'Filial Padrão')

    # Tenta encontrar um nome/email válido e consistente
    userGupyId = None
    emailUserGupy = None
    departamentGupyId = None
    roleGupyId = None
    branchGupyId = None
    nome_base = None
    email_base = None
    

    for _, row in registros_df.iterrows():
        nome = row['Nome']
        email = extrair_email_valido(row['Email'])
        if not email:
            continue
        nome_base = nome
        email_base = email
        userGupyId, emailUserGupy, departamentGupyId, roleGupyId, branchGupyId = obter_dados_usuario_gupy(api, nome, email)
        if userGupyId and emailUserGupy:
        # Verifica se o email retornado já está associado a outro nome
            if emailUserGupy != email_base:
                logging.warning(f"> Email retornado '{emailUserGupy}' não corresponde ao email base '{email_base}' para nome '{nome}'")
                continue
            break
    if not email_base:
        logging.warning(f"> CPF {cpf} sem email válido. Nenhuma ação será tomada.")
        return None

    campos = {
        "departmentId": departamentGupyId or 0,
        "roleId": roleGupyId or 0,
        "branchIds": [branchGupyId] if branchGupyId else [0],
        "branchName": nomeFilialBranch or "Filial Padrão"
    }
    branch_ids = campos.get("branchIds", [0])
    branch_id = branch_ids[0] if branch_ids != [0] else None
    if None in (departamentGupyId, roleGupyId, branchGupyId):
        campos = mapear_campos_usuario({
            "departament_gupy": registros_df.iloc[0].get('Departamento_gupy', ''),
            "cargo": registros_df.iloc[0].get('Role_gupy', ''),
            "branchIds": [0]
        })
        campos["branchName"] = nomeFilialBranch
        
        if departamentGupyId is None:
            departamento_nome = registros_df.iloc[0].get('Departamento_gupy', '')
            departamento_mapeado = find_similar_to(departamento_nome, departament_mapping)
            if departamento_mapeado:
                api.criaAreaDepartamento(departamento_nome, departamento_mapeado)
        if roleGupyId is None:
            cargoRole_nome = registros_df.iloc[0].get('Role_gupy', '')
            cargoRole_mapeado = find_similar_to(cargoRole_nome, role_mapping)
            if cargoRole_mapeado:
                api.criaCargoRole(cargoRole_nome, cargoRole_mapeado)
        """if campos['roleId'] != 0 and roleGupyId is None:
            api.criaCargoRole(campos['roleId'])"""
        if campos['branchIds'] != [0] and branchGupyId is None:
            filial_cod = registros_df.iloc[0].get('Filial_cod', 'default_branch')
            api.criaFilialBranch(filial_cod, campos['branchName'])

    if not re.fullmatch(r'\d{11}', cpf):
        logging.warning(f"CPF suspeito: {cpf}")
        print(f"> CPF {cpf} com {'múltiplas' if len(registros_df) > 1 else 'uma'} matrícula(s)")
        for _, row in registros_df.iterrows():
            print(f">  Matrícula - {row['Matricula']} | Situação: {row['Situacao']} | Nome: {row['Nome']} | Email: {row['Email']}")
        print(f">  Todas as matrículas estão demitidas? {'Sim' if todas_demitidas else 'Não'}")

        if todas_demitidas:
            if userGupyId:
                api.deletaUsuarioGupy(userGupyId, nome_base)
        else:
            if userGupyId:
                api.atualizaUsuarioGupy(userGupyId, nome_base, emailUserGupy, roleGupyId, departamentGupyId, branchGupyId)
            else:
                api.criaUsuarioGupy(nome_base, email_base, cpf)

    return {
        "usuario": {
            "userGupyId": userGupyId,
            "emailUserGupy": emailUserGupy
        },
        "campos": {
            "departmentId": campos["departmentId"],
            "roleId": campos["roleId"],
            "branchId": campos["branchIds"][0],
            "branchName": campos["branchName"]
        }
    }
    
import logging
import re
import csv

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
    nome_base = registros_df.iloc[0]['Nome']
    email_base = extrair_email_valido(registros_df.iloc[0]['Email'])

    # DEBUG
    if not re.fullmatch(r'\d{11}', cpf):
        logging.warning(f"CPF suspeito: {cpf}")

    print(f"> CPF {cpf} com {'multiplas' if len(registros_df) > 1 else 'uma'} matricula(s)")
    for _, row in registros_df.iterrows():
        print(f">  Matricula - {row['Matricula']} | Situacao: {row['Situacao']} | Nome: {row['Nome']} | Email: {row['Email']}")

    print(f">  Todas as matriculas estao demitidas? {'Sim' if todas_demitidas else 'Nao'}")

    id_gupy = api.listaUsuariosGupy(nome_base, email_base)

    if todas_demitidas:
        if id_gupy:
            api.deletaUsuarioGupy(id_gupy, nome_base)
    else:
        if email_base:
            if id_gupy:
                print(">> Implementar atualizacao de usuario na versao 2.0")
                # api.atualizaUsuarioGupy(id_gupy, nome_base, email_base, cpf)
            else:
                api.criaUsuarioGupy(nome_base, email_base, cpf)
        else:
            print(f">  Email inválido para CPF {cpf}, nao sera criado/atualizado.")

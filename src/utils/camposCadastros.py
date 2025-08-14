import logging
from utils.helpers import mapear_campos_usuario, find_similar_to
from utils.comum import role_mapping, departament_mapping

def processar_campos(api, nome_base, email_base, userGupyId, emailUserGupy, departamentGupyId, roleGupyId, branchGupyId, nomeFilialBranch, registros_df):
    logging.warning(f"> Processando campos do usuário {nome_base} dono do email {email_base}")
    campos_faltantes = []

    if roleGupyId is None:
        role_nome = registros_df.iloc[0].get("Role_gupy", "")
        roleGupyId, _, _ = obter_ou_criar_cargo(api, role_nome)
        campos_faltantes.append("cargo")

    if departamentGupyId is None:
        departamento_nome = registros_df.iloc[0].get("Departamento_gupy", "")
        departamentGupyId, _, _ = obter_ou_criar_departamento(api, departamento_nome)
        campos_faltantes.append("departamento")

    if branchGupyId is None:
        filial_nome = registros_df.iloc[0].get("Branch_gupy", "Filial Padrão")
        filial_cod = registros_df.iloc[0].get("Filial_cod", "default_branch")
        branchGupyId = obter_ou_criar_filial(api, filial_nome, filial_cod)
        campos_faltantes.append("filial")

    campos = {
        "departmentId": departamentGupyId,
        "roleId": roleGupyId,
        "branchIds": [branchGupyId],
        "branchName": nomeFilialBranch or "Filial Padrão"
    }
    # ==================================
    dados_atuais = {
    "departmentId": departamentGupyId,
    "roleId": roleGupyId,
    "branchId": branchGupyId
    }

    dados_usuario = api.obter_dados_usuario_gupy_por_id(userGupyId)

    if dados_atuais != dados_usuario:
        logging.warning(f"> Atualizando cadastro do usuário {nome_base} com campos corrigidos: {campos_faltantes}")
        api.atualizaUsuarioGupy(userGupyId, nome_base, emailUserGupy, roleGupyId, departamentGupyId, branchGupyId)
    else:
        logging.warning(f"> Nenhuma atualização necessária para o usuário {nome_base}")

    if campos_faltantes:
        logging.warning(f"> Atualizando cadastro do usuário {nome_base} com campos corrigidos: {campos_faltantes}")
        api.atualizaUsuarioGupy(userGupyId, nome_base, emailUserGupy, roleGupyId, departamentGupyId, branchGupyId)

    return campos

def obter_ou_criar_departamento(api, nome_departamento):
    mapeado = find_similar_to(nome_departamento, departament_mapping)
    if mapeado:
        departamento_id, departamento_nome, departamento_similarTo = api.listaAreaDepartamento(nome_departamento)
        if not departamento_id:
            departamento_id = api.criaAreaDepartamento(nome_departamento, mapeado)
        return departamento_id, departamento_nome, departamento_similarTo
    return 0, "", ""

def obter_ou_criar_cargo(api, nome_cargo):
    mapeado = find_similar_to(nome_cargo, role_mapping)
    if mapeado:
        cargo_id, cargo_nome, cargo_similarTo = api.listaCargoRole(nome_cargo)
        if not cargo_id:
            cargo_id = api.criaCargoRole(nome_cargo, mapeado)
        return cargo_id, cargo_nome, cargo_similarTo
    return 0, "", ""

def obter_ou_criar_filial(api, nome_filial, cod_filial):
    branch_id = api.listaFilialBranch(nome_filial, cod_filial)
    if not branch_id:
        branch_id = api.criaFilialBranch(cod_filial, nome_filial)
    return branch_id
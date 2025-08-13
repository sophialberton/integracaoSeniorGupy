import logging
from utils.helpers import mapear_campos_usuario, find_similar_to
from utils.comum import role_mapping, departament_mapping

def processar_campos(api, nome_base, email_base, userGupyId, emailUserGupy, departamentGupyId, roleGupyId, branchGupyId, nomeFilialBranch, registros_df):
    logging.info(f"> Processando campos do usuário dono do email {email_base}")
    campos = {
        "departmentId": departamentGupyId or 0,
        "roleId": roleGupyId or 0,
        "branchIds": [branchGupyId] if branchGupyId else [0],
        "branchName": nomeFilialBranch or "Filial Padrão"
    }
    campos_faltantes = []
    # 1. Cargo
    if roleGupyId is None:
        role_nome = registros_df.iloc[0].get("Role_gupy", "")
        cargo_mapeado = find_similar_to(role_nome, role_mapping)
        if cargo_mapeado:
            role_id = api.listaCargoRole(cargo_mapeado)
            if not role_id:
                role_id = api.criaCargoRole(cargo_mapeado)
            campos["roleId"] = role_id
            campos_faltantes.append("cargo")
    # 2. Departamento
    if departamentGupyId is None:
        departamento_nome = registros_df.iloc[0].get("Departamento_gupy", "")
        departamento_mapeado = find_similar_to(departamento_nome, departament_mapping)
        if departamento_mapeado:
            departamento_id = api.listaAreaDepartamento(departamento_mapeado)
            if not departamento_id:
                departamento_id = api.criaAreaDepartamento(departamento_mapeado)
            campos["departmentId"] = departamento_id
            campos_faltantes.append("departamento")
    # 3. Filial
    if branchGupyId is None:
        filial_nome = registros_df.iloc[0].get("Branch_gupy", "Filial Padrão")
        filial_cod = registros_df.iloc[0].get("Filial_cod", "default_branch")
        branch_id = api.listaFilialBranch(filial_cod)
        if not branch_id:
            branch_id = api.criaFilialBranch(filial_cod, filial_nome)
        campos["branchIds"] = [branch_id]
        campos["branchName"] = filial_nome
        campos_faltantes.append("filial")
    # Atualiza o cadastro do usuário se necessário
    if campos_faltantes:
        logging.info(f"> Atualizando cadastro do usuário {nome_base} com campos corrigidos: {campos_faltantes}")
        api.atualizaUsuarioGupy(
            userGupyId,
            nome_base,
            emailUserGupy,
            campos["roleId"],
            campos["departmentId"],
            campos["branchIds"][0]
        )
    return campos


def atualizaCamposCadastro():
    pass
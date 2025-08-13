import re
import logging
from utils.helpers import mapear_campos_usuario


def processar_campos(api, nome_base, email_base, userGupyId, emailUserGupy, departamentGupyId, roleGupyId, branchGupyId, nomeFilialBranch):
    logging.info(f"> Processando campos do usuário dono do email {email_base}")

    departamentGupyId, roleGupyId, branchGupyId = api.listaCamposUsuarioGupy(userGupyId, nome_base, emailUserGupy)
    campos = {
        "departmentId": departamentGupyId or 0,
        "roleId": roleGupyId or 0,
        "branchIds": [branchGupyId] if branchGupyId else [0],
        "branchName": nomeFilialBranch or "Filial Padrão"  # exemplo
    }
    if None in (departamentGupyId, roleGupyId, branchGupyId):
        logging.warning(f"> Campos incompletos para usuário {nome_base}")
        campos = mapear_campos_usuario(campos)

        # Aqui você pode chamar funções para criar os dados faltantes
        if campos['departmentId'] != 0 and departamentGupyId is None:
            api.criaAreaDepartamento(campos['departmentId'])

        if campos['roleId'] != 0 and roleGupyId is None:
            api.criaCargoRole(campos['roleId'])

        if campos['branchIds'] != [0] and branchGupyId is None:
            api.criaFilialBranch(campos['branchIds'][0], campos['branchName'])
    return campos


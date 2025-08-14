import logging
import re
from utils.comum  import (
    departament_mapping,
    role_mapping
)

def obter_dados_usuario_gupy(api, nome_base, email_base):
    userGupyId, nomeUserGupy, emailUserGupy = api.listaUsuarioGupy(nome_base, email_base)
    if nomeUserGupy and nomeUserGupy.strip().lower() != nome_base.strip().lower():
        logging.warning(f"> Nome inconsistente: esperado '{nome_base}', recebido '{nomeUserGupy}' para email '{email_base}'")
        return None, None, None, None, None
    departamentGupyId, roleGupyId, branchGupyId = api.listaCamposUsuarioGupy(userGupyId, nome_base, emailUserGupy)
    return userGupyId, emailUserGupy, departamentGupyId, roleGupyId, branchGupyId


# Função principal de atualização de cadastro
def mapear_campos_usuario(usuario):
    logging.info("> Mapeando campos do usuário")
    # Garante estrutura mínima
    campos = {
        "departmentId": usuario.get("departmentId", 0),
        "roleId": usuario.get("roleId", 0),
        "branchIds": usuario.get("branchIds", [0])
    }
    # Mapeia departamento
    if campos["departmentId"] == 0:
        departamento = find_similar_to(usuario.get("departament_gupy", ""), departament_mapping)
        if departamento:
            campos["departmentId"] = departamento
    # Mapeia cargo
    if campos["roleId"] == 0:
        cargo = find_similar_to(usuario.get("cargo", ""), role_mapping)
        if cargo:
            campos["roleId"] = cargo
    # Mapeia filial
    if campos["branchIds"] == [0]:
        campos["branchIds"] = ["default_branch"]
    return campos


# Função para padronizar texto
def textoPadrao(texto):
    texto = str(texto)
    # Lista de siglas que devem ser preservadas
    siglas_preservadas = ['III', 'II', 'I']

    palavras = texto.split()
    palavras_formatadas = []

    for palavra in palavras:
        if palavra.upper() in siglas_preservadas:
            palavras_formatadas.append(palavra.upper())
        else:
            palavras_formatadas.append(palavra.capitalize())
    return ' '.join(palavras_formatadas)

# Função para identificar similarTo equivalente
def find_similar_to(role_gupy, mapping):
    role_gupy = role_gupy.lower()
    for keywords, equivalent in mapping.items():
        for keyword in keywords.lower().split('/'):
            if re.search(rf'\b{re.escape(keyword)}\b', role_gupy):
                return equivalent
    return None

import logging
import re
from utils.comum  import (
    departament_mapping,
    role_mapping
)

def obter_dados_usuario_gupy(api, nome_base, email_base):
    userGupyId = api.listaIdUsuariosGupy(nome_base, email_base)
    emailUserGupy = api.listaEmailUsuarioGupy(userGupyId, nome_base)
    departamentGupyId, roleGupyId, branchGupyId = api.listaCamposUsuarioGupy(userGupyId, nome_base, emailUserGupy)

    return userGupyId, emailUserGupy, departamentGupyId, roleGupyId, branchGupyId

# Função principal de atualização de cadastro
def mapear_campos_usuario(usuario):
    logging.info("> Mapeando campos do usuário")
    if usuario.get('departmentId', 0) == 0:
        departamento = find_similar_to(usuario.get('departament_gupy', ''), departament_mapping)
        if departamento:
            usuario['departmentId'] = departamento
    if usuario.get('roleId', 0) == 0:
        cargo = find_similar_to(usuario.get('cargo', ''), role_mapping)
        if cargo:
            usuario['roleId'] = cargo
    if usuario.get('branchIds', [0]) == [0]:
        usuario['branchIds'] = ['default_branch']
    return usuario

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

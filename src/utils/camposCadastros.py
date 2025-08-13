import re

# Mapeamentos de palavras-chave para departamentos
departament_mapping = {
    "Tecnologia": "technology",
    "Segurança": "security",
    "Vendas/exportação/loja": "sales",
    "Suprimentos/suplly": "purchases",
    "Processos": "project_or_processes",
    "Produção/Banco de Talentos": "operations",
    "almoxarifado/logistica/PPCPM": "logistics",
    "Laboratorio/Relacionamento/Consultoria Cientifica/Pesquisa e Desenvolvimento": "innovation_or_product",
    "Gestao Pessoas": "human_resources",
    "Financeiro Contas pagar e receber / Adminsitração Diretoria": "financial_management",
    "Manutenção": "engineering_or_maintenance_or_technical_services",
    "Marketing": "communication_or_design_or_marketing",
    "Qualidade": "audit_or_quality",
    "Central de Relacionamento": "attendance",
    "Financeiro": "accounting_or_controlling"
}

# Mapeamentos de palavras-chave para cargos (roles)
role_mapping = {
    "Analista/Atendente/Consultor/Desinger/Preparador/Programador": "analyst",
    "Assistente/Recepcionista": "auxiliary",
    "Consultor": "consultant",
    "Coordenador": "coordinator",
    "Estagiario": "intern",
    "Inspetor/Metrologista/Técnico": "technician",
    "Supervisor": "supervisor",
    "Científico/Especialista/Pesquisador": "specialist",
    "Operador/Almoxarife/Torneiro": "operator",
    "Gerente": "manager"
}

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
def find_similar_to(cargo, mapping):
    for keywords, equivalent in mapping.items():
        for keyword in keywords.split('/'):
            if re.search(rf'\\b{keyword}\\b', cargo, re.IGNORECASE):
                return equivalent
    return None

# Função principal de atualização de cadastro
def atualizar_cadastro(usuario):
    usuario['cargo'] = textoPadrao(usuario['cargo'])

    if usuario.get('departmentId', 0) == 0:
        departamento = find_similar_to(usuario['cargo'], departament_mapping)
        if departamento:
            usuario['departmentId'] = departamento

    if usuario.get('roleId', 0) == 0:
        role = find_similar_to(usuario['cargo'], role_mapping)
        if role:
            usuario['roleId'] = role

    if usuario.get('branchIds', [0]) == [0]:
        usuario['branchIds'] = ['default_branch']

    return usuario

# Exemplo de uso
usuario_exemplo = {
    "id": 123,
    "email": "usuario@example.com",
    "cargo": "Consultor de vendas",
    "departmentId": 0,
    "roleId": 0,
    "branchIds": [0]
}

usuario_atualizado = atualizar_cadastro(usuario_exemplo)
print(usuario_atualizado)

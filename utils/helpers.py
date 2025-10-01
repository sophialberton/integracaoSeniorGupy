# utils/helpers.py

import re
from unidecode import unidecode

def padronizar_texto(texto):
    """
    Capitaliza o texto de forma inteligente, preservando siglas comuns,
    e remove acentos.
    """
    if not isinstance(texto, str):
        return texto
    
    # Remove acentos e converte para minúsculas
    texto_normalizado = unidecode(texto.lower())
    
    # Siglas ou palavras que devem ser mantidas em maiúsculo
    siglas = ['iii', 'ii', 'i', 'ti', 'rh', 'pcp', 'ppcpm', 'dho']
    
    palavras_formatadas = []
    for palavra in texto_normalizado.split():
        if palavra in siglas:
            palavras_formatadas.append(palavra.upper())
        else:
            palavras_formatadas.append(palavra.capitalize())
            
    return ' '.join(palavras_formatadas)


import re

def extrair_email_valido(email_texto):
    """
    Extrai o primeiro e-mail corporativo válido de uma string, com prioridade:
    1. @fgmdentalgroup.com
    2. @fgm.ind.br
    3. @biocircle.ind.br
    Se não houver nenhum desses, retorna o primeiro e-mail corporativo encontrado.
    E-mails pessoais (como gmail.com, hotmail.com etc.) são ignorados.
    """
    if not isinstance(email_texto, str):
        return None

    # Domínios corporativos válidos
    dominios_prioritarios = [
        r'@fgmdentalgroup\.com',
        r'@fgm\.ind\.br',
        r'@biocircle\.ind\.br'
    ]

    # Lista de domínios pessoais comuns para exclusão
    dominios_pessoais = [
        r'@gmail\.com',
        r'@hotmail\.com',
        r'@outlook\.com',
        r'@yahoo\.com',
        r'@live\.com',
        r'@icloud\.com'
    ]

    # Extrai todos os e-mails da string
    todos_emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', email_texto, re.IGNORECASE)

    # Filtra apenas e-mails corporativos (exclui pessoais)
    emails_corporativos = [
        email for email in todos_emails
        if not any(re.search(dom, email, re.IGNORECASE) for dom in dominios_pessoais)
    ]

    # Prioriza os domínios definidos
    for dominio in dominios_prioritarios:
        for email in emails_corporativos:
            if re.search(dominio, email, re.IGNORECASE):
                return email

    # Se não houver e-mail dos domínios prioritários, retorna o primeiro corporativo
    return emails_corporativos[0] if emails_corporativos else None


def encontrar_similar_to(texto_entrada, mapa):
    """
    Busca no texto de entrada por palavras-chave definidas no mapa
    e retorna o valor 'similarTo' correspondente.
    """
    if not isinstance(texto_entrada, str):
        return None

    texto_normalizado = unidecode(texto_entrada.lower())
    
    for palavra_chave, similar_to in mapa.items():
        if palavra_chave in texto_normalizado:
            return similar_to
            
    return None
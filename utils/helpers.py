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


def extrair_email_valido(email_texto):
    """
    Extrai o primeiro e-mail com domínio válido (@fgm.ind.br ou @fgmdentalgroup.com)
    de uma string, que pode conter múltiplos e-mails.
    """
    if not isinstance(email_texto, str):
        return None
    
    # CORREÇÃO: Usamos (?:...) para criar um "grupo de não-captura",
    # garantindo que a expressão regular retorne o e-mail completo.
    emails_encontrados = re.findall(
        r'[\w\.-]+@(?:fgm\.ind\.br|fgmdentalgroup\.com)', 
        email_texto, 
        re.IGNORECASE
    )
    
    return emails_encontrados[0] if emails_encontrados else None


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
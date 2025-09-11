import re

def format_text(text):
    """Formata o texto para o padrão Title Case, preservando siglas."""
    text = str(text)
    preserved_acronyms = ['III', 'II', 'I']
    words = text.split()
    formatted_words = [word.upper() if word.upper() in preserved_acronyms else word.capitalize() for word in words]
    return ' '.join(formatted_words)

def find_similar_to(text, mapping):
    """Encontra um valor correspondente em um dicionário de mapeamento."""
    text_lower = text.lower()
    for keywords, equivalent in mapping.items():
        for keyword in keywords.lower().split('/'):
            if re.search(rf'\b{re.escape(keyword)}\b', text_lower):
                return equivalent
    return None

def extract_valid_email(email_string):
    """Extrai um e-mail válido de uma string."""
    if not isinstance(email_string, str):
        return None
    
    valid_domains = ["@fgmdentalgroup.com", "@fgm.ind.br"]
    emails = email_string.replace(',', ' ').split()
    
    for email in emails:
        email = email.strip()
        for domain in valid_domains:
            if domain in email:
                return email
    return None
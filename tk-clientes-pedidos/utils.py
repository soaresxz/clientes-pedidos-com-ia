import re
from datetime import datetime
import logging

# Padrão de regex simples para e-mail (Prompt 2)
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Padrão para telefone, 8 a 15 dígitos (Prompt 2)
PHONE_REGEX = r'^\d{8,15}$'

def validate_email(email):
    """Valida um formato de e-mail simples."""
    if not email:
        return True # Permite e-mail vazio
    return re.match(EMAIL_REGEX, email) is not None

def validate_phone(phone):
    """Valida um telefone com 8 a 15 dígitos."""
    if not phone:
        return True # Permite telefone vazio
    return re.match(PHONE_REGEX, phone) is not None

def format_date_to_iso(date_str_ddmmyyyy):
    """Converte data DD/MM/AAAA para AAAA-MM-DD (ISO)."""
    try:
        # Converte a string para objeto datetime
        dt = datetime.strptime(date_str_ddmmyyyy, '%d/%m/%Y')
        # Formata de volta para string no formato ISO
        return dt.strftime('%Y-%m-%d')
    except ValueError as e:
        logging.warning(f"Tentativa de formatar data inválida: {date_str_ddmmyyyy} - {e}")
        raise ValueError("Formato de data inválido.")

def validate_float(value_str):
    """Tenta converter string para float, tratando vírgula."""
    if not value_str:
        raise ValueError("Valor não pode ser vazio.")
    try:
        # Substitui vírgula por ponto para aceitar R$ 1,50
        return float(value_str.replace(',', '.'))
    except ValueError:
        raise ValueError("Valor não é um número válido.")

def validate_int(value_str):
    """Tenta converter string para int."""
    if not value_str:
        raise ValueError("Valor não pode ser vazio.")
    try:
        return int(value_str)
    except ValueError:
        raise ValueError("Valor não é um número inteiro válido.")


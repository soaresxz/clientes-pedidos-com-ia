import re
from datetime import datetime


def is_valid_email(email):
    """
    Valida formato simples de e-mail (Prompt 2).
    """
    if not email:
        return False
    # Regex simples: algo@algo.algo
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def is_valid_phone(phone):
    """
    Valida telefone com 8 a 15 dígitos (Prompt 2).
    Permite apenas dígitos.
    """
    if not phone:
        return True  # Telefone é opcional

    # Remove caracteres não numéricos (ex: +, -, ( ), ' ') para contar
    digits_only = re.sub(r'\D', '', phone)

    return 8 <= len(digits_only) <= 15


def get_today_date_str():
    """Retorna a data de hoje formatada como YYYY-MM-DD."""
    return datetime.now().strftime('%Y-%m-%d')

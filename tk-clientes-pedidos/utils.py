import re
from datetime import datetime
import logging
import json
import requests
import os
from dotenv import load_dotenv

# Padrão de regex simples para e-mail (Prompt 2)
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Padrão para telefone, 8 a 15 dígitos (Prompt 2)
PHONE_REGEX = r'^\d{8,15}$'

load_dotenv()
# Configuração da API Google Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")  
GEMINI_MODEL = "gemini-2.5-flash"  

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


def analisar_pedidos(conn):
    """
    Analisa os últimos 5 pedidos do banco usando Google Gemini.
    
    Args:
        conn: Conexão com o banco de dados SQLite
    
    Returns:
        dict: {'success': bool, 'insights': str, 'error': str (opcional)}
    """
    try:
        # 1. Buscar os últimos 5 pedidos com detalhes
        cursor = conn.cursor()
        
        query = """
        SELECT 
            p.id as pedido_id,
            p.data,
            p.total,
            c.nome as cliente_nome,
            GROUP_CONCAT(
                ip.produto || ' (Qtd: ' || ip.quantidade || 
                ', R$ ' || PRINTF('%.2f', ip.preco_unit) || ')'
            , '; ') as itens
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        LEFT JOIN itens_pedido ip ON p.id = ip.pedido_id
        GROUP BY p.id
        ORDER BY p.data DESC
        LIMIT 5
        """
        
        cursor.execute(query)
        pedidos = cursor.fetchall()
        
        if not pedidos:
            return {
                'success': False,
                'error': 'Nenhum pedido encontrado no banco de dados.'
            }
        
        # 2. Montar o resumo textual dos pedidos
        resumo_pedidos = "Últimos 5 pedidos:\n\n"
        for idx, pedido in enumerate(pedidos, 1):
            resumo_pedidos += f"Pedido #{pedido['pedido_id']} - {pedido['data']}\n"
            resumo_pedidos += f"Cliente: {pedido['cliente_nome']}\n"
            resumo_pedidos += f"Total: R$ {pedido['total']:.2f}\n"
            resumo_pedidos += f"Itens: {pedido['itens'] or 'Nenhum item'}\n"
            resumo_pedidos += "-" * 60 + "\n"
        
        # 3. Criar o prompt para a IA
        prompt = f"""Você é um analista de vendas especializado em e-commerce brasileiro. Analise os seguintes pedidos e forneça insights valiosos:

{resumo_pedidos}

Por favor, forneça uma análise detalhada com:
1. Produtos mais vendidos (com quantidades totais somadas)
2. Valor médio dos pedidos
3. Padrões de compra identificados
4. Recomendações estratégicas práticas para aumentar vendas

Seja específico, objetivo e use dados numéricos quando possível."""
        
        # 4. Chamar a API do Gemini
        insights = _chamar_gemini(prompt)
        
        logging.info("Análise de pedidos concluída com sucesso.")
        return {
            'success': True,
            'insights': insights,
            'resumo': resumo_pedidos
        }
        
    except Exception as e:
        logging.error(f"Erro ao analisar pedidos: {e}")
        return {
            'success': False,
            'error': f'Erro ao analisar pedidos: {str(e)}'
        }


def _chamar_gemini(prompt):
    """Chama a API do Google Gemini."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
        }
    }
    
    try:
        logging.info(f"Enviando requisição para Google Gemini (modelo: {GEMINI_MODEL})...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Extrair o texto da resposta do Gemini
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                insights = candidate['content']['parts'][0]['text']
                logging.info("Resposta recebida do Gemini com sucesso.")
                return insights
        
        raise Exception("Formato de resposta inesperado do Gemini")
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"Erro HTTP {response.status_code}"
        try:
            error_detail = response.json()
            if 'error' in error_detail:
                error_msg += f": {error_detail['error'].get('message', 'Erro desconhecido')}"
        except:
            pass
        logging.error(f"Erro ao chamar Gemini API: {error_msg}")
        
        # Mensagens específicas para erros comuns
        if response.status_code == 400:
            raise Exception(f"Requisição inválida para o Gemini. Verifique o formato dos dados.\n{error_msg}")
        elif response.status_code == 403:
            raise Exception("API Key do Gemini inválida ou sem permissões. Verifique sua chave em https://makersuite.google.com/app/apikey")
        elif response.status_code == 429:
            raise Exception("Limite de requisições do Gemini excedido. Aguarde alguns minutos e tente novamente.")
        else:
            raise Exception(error_msg)
        
    except requests.exceptions.Timeout:
        logging.error("Timeout ao chamar Gemini API")
        raise Exception("A requisição para o Gemini demorou muito tempo. Tente novamente.")
        
    except requests.exceptions.ConnectionError:
        logging.error("Erro de conexão com Gemini API")
        raise Exception("Não foi possível conectar à API do Gemini. Verifique sua conexão com a internet.")
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao chamar Gemini API: {e}")
        raise Exception(f"Erro na API do Gemini: {str(e)}")
from db import execute_query, execute_transaction
import logging


# --- Funções de Clientes (Prompts 2, 3) ---

def add_client(nome, email, telefone):
    """Adiciona um novo cliente."""
    query = "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)"
    try:
        execute_query(query, (nome, email, telefone), commit=True)
        return True
    except ValueError as e:  # Captura o erro de e-mail duplicado de db.py
        logging.warning(f"Falha ao adicionar cliente: {e}")
        raise e  # Re-levanta para o formulário exibir a mensagem
    except Exception as e:
        logging.error(f"Erro inesperado ao adicionar cliente: {e}")
        raise Exception(f"Erro inesperado: {e}")


def update_client(client_id, nome, email, telefone):
    """Atualiza um cliente existente."""
    query = "UPDATE clientes SET nome = ?, email = ?, telefone = ? WHERE id = ?"
    try:
        execute_query(query, (nome, email, telefone, client_id), commit=True)
        return True
    except ValueError as e:
        logging.warning(f"Falha ao atualizar cliente: {e}")
        raise e
    except Exception as e:
        logging.error(f"Erro inesperado ao atualizar cliente: {e}")
        raise Exception(f"Erro inesperado: {e}")


def delete_client(client_id):
    """Exclui um cliente (e seus pedidos/itens em cascata)."""
    query = "DELETE FROM clientes WHERE id = ?"
    try:
        execute_query(query, (client_id,), commit=True)
        return True
    except Exception as e:
        logging.error(f"Erro ao excluir cliente {client_id}: {e}")
        return False


def get_all_clients(search_term=None):
    """Busca todos os clientes, com filtro opcional (Prompt 3)."""
    query = "SELECT * FROM clientes"
    params = ()

    if search_term:
        query += " WHERE nome LIKE ? OR email LIKE ?"
        params = (f"%{search_term}%", f"%{search_term}%")

    query += " ORDER BY nome"  # Ordena por nome

    try:
        return execute_query(query, params, fetch_all=True)
    except Exception as e:
        logging.error(f"Erro ao buscar clientes: {e}")
        return []


def get_client_by_id(client_id):
    """Busca um cliente pelo ID."""
    query = "SELECT * FROM clientes WHERE id = ?"
    try:
        return execute_query(query, (client_id,), fetch_one=True)
    except Exception as e:
        logging.error(f"Erro ao buscar cliente {client_id}: {e}")
        return None


# --- Funções de Pedidos (Prompt 4) ---

def add_order_transaction(cliente_id, data, total, itens):
    """
    Salva um pedido e seus itens de forma transacional (Prompt 4).
    """

    # 1. Operação para inserir o pedido
    order_query = "INSERT INTO pedidos (cliente_id, data, total) VALUES (?, ?, ?)"
    order_params = (cliente_id, data, total)

    operations = [(order_query, order_params)]

    # 2. Operações para inserir os itens
    item_query = "INSERT INTO itens_pedido (pedido_id, produto, quantidade, preco_unit) VALUES (?, ?, ?, ?)"

    for item in itens:
        # O 'None' no pedido_id será substituído pelo ID do pedido pelo 'execute_transaction'
        item_params = (None, item['produto'], item['quantidade'], item['preco_unit'])
        operations.append((item_query, item_params))

    try:
        return execute_transaction(operations)
    except Exception as e:
        logging.error(f"Erro ao criar transação de pedido: {e}")
        return False


# --- NOVAS Funções de Produtos ---
# (Estas funções corrigem o ImportError)

def add_product(nome, preco_sugerido):
    """Adiciona um novo produto."""
    query = "INSERT INTO produtos (nome, preco_sugerido) VALUES (?, ?)"
    try:
        execute_query(query, (nome, preco_sugerido), commit=True)
        return True
    except ValueError as e:
        logging.warning(f"Falha ao adicionar produto: {e}")
        raise e
    except Exception as e:
        logging.error(f"Erro inesperado ao adicionar produto: {e}")
        raise Exception(f"Erro inesperado: {e}")


def update_product(product_id, nome, preco_sugerido):
    """Atualiza um produto existente."""
    query = "UPDATE produtos SET nome = ?, preco_sugerido = ? WHERE id = ?"
    try:
        execute_query(query, (nome, preco_sugerido, product_id), commit=True)
        return True
    except ValueError as e:
        logging.warning(f"Falha ao atualizar produto: {e}")
        raise e
    except Exception as e:
        logging.error(f"Erro inesperado ao atualizar produto: {e}")
        raise Exception(f"Erro inesperado: {e}")


def delete_product(product_id):
    """Exclui um produto."""
    query = "DELETE FROM produtos WHERE id = ?"
    try:
        execute_query(query, (product_id,), commit=True)
        return True
    except Exception as e:
        logging.error(f"Erro ao excluir produto {product_id}: {e}")
        return False


def get_all_products(search_term=None):
    """Busca todos os produtos, com filtro opcional."""
    query = "SELECT * FROM produtos"
    params = ()

    if search_term:
        query += " WHERE nome LIKE ?"
        params = (f"%{search_term}%",)

    query += " ORDER BY nome"

    try:
        return execute_query(query, params, fetch_all=True)
    except Exception as e:
        logging.error(f"Erro ao buscar produtos: {e}")
        return []


def get_product_by_id(product_id):
    """Busca um produto pelo ID."""
    query = "SELECT * FROM produtos WHERE id = ?"
    try:
        return execute_query(query, (product_id,), fetch_one=True)
    except Exception as e:
        logging.error(f"Erro ao buscar produto {product_id}: {e}")
        return None


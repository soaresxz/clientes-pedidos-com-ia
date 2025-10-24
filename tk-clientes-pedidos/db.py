import sqlite3
import logging

# Configuração de log simples (para Prompt 5)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE = 'clientes_pedidos.db'


def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        conn.execute("PRAGMA foreign_keys = ON;")  # Garante integridade referencial
    except sqlite3.Error as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
    return conn


def init_db():
    """Inicializa o esquema do banco de dados (tabelas)."""

    # Esquema SQL (Prompt 1)
    schema = """
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE,
        telefone TEXT
    );

    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        data TEXT NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER NOT NULL,
        produto TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        preco_unit REAL NOT NULL,
        FOREIGN KEY (pedido_id) REFERENCES pedidos (id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        preco_sugerido REAL NOT NULL DEFAULT 0.0
    );
    """

    conn = get_db_connection()
    if conn:
        try:
            with conn:
                conn.executescript(schema)
            logging.info("Banco de dados inicializado com sucesso.")
        except sqlite3.Error as e:
            logging.error(f"Erro ao inicializar o banco de dados: {e}")
        finally:
            conn.close()


def execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    """
    Executa uma consulta parametrizada no banco de dados. (Prompt 1)

    :param query: A string da consulta SQL.
    :param params: Uma tupla de parâmetros para a consulta.
    :param fetch_one: True se deve retornar um único resultado.
    :param fetch_all: True se deve retornar todos os resultados.
    :param commit: True se a transação deve ser comitada (para INSERT, UPDATE, DELETE).
    :return: O resultado da consulta (se fetch_one/fetch_all) ou o ID da linha (se commit) ou None.
    """
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn:  # Inicia uma transação
            cursor = conn.cursor()
            cursor.execute(query, params)

            if commit:
                conn.commit()
                return cursor.lastrowid  # Retorna o ID do item inserido

            if fetch_one:
                return cursor.fetchone()

            if fetch_all:
                return cursor.fetchall()

    except sqlite3.Error as e:
        # Tratamento de erro (Prompt 1 e 5)
        logging.error(f"Erro ao executar consulta: {e}\nQuery: {query}\nParams: {params}")
        # Tratamento específico para violação de constraint (ex: e-mail duplicado)
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Erro: O e-mail fornecido já existe.")
        raise  # Re-levanta a exceção para ser tratada pela camada superior (modelo/view)

    finally:
        if conn:
            conn.close()


def execute_transaction(operations):
    """
    Executa uma lista de operações (consultas e parâmetros) de forma transacional.
    Usado para salvar Pedido e Itens do Pedido (Prompt 4).

    :param operations: Lista de tuplas, onde cada tupla é (query, params).
    :return: True se sucesso, False se falha.
    """
    conn = get_db_connection()
    if not conn:
        return False

    try:
        with conn:  # 'with conn' gerencia a transação (commit/rollback)
            cursor = conn.cursor()
            last_id = None

            for i, (query, params) in enumerate(operations):
                # Lógica para pegar o ID do pedido e usar nos itens
                if i > 0 and '?' in query and last_id is not None:
                    # Substitui o primeiro '?' (que deve ser o pedido_id) pelo last_id
                    params = (last_id,) + params[1:]

                cursor.execute(query, params)

                if i == 0:  # Assume que a primeira operação é inserir o Pedido
                    last_id = cursor.lastrowid
                    if last_id is None:
                        raise sqlite3.Error("Falha ao obter o ID do pedido principal.")

        logging.info("Transação concluída com sucesso.")
        return True

    except sqlite3.Error as e:
        logging.error(f"Erro na transação. Rollback automático: {e}")
        return False

    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    # Permite inicializar o DB executando 'python db.py'
    print("Inicializando o banco de dados...")
    init_db()

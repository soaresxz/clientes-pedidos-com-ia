import tkinter as tk
from tkinter import ttk
from db import init_db
from views.client_list import ClientListFrame
from views.product_list import ProductListFrame  # Importa a nova lista de produtos
import logging


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Clientes e Pedidos")
        self.geometry("800x600")

        # Configura o estilo ttk
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            logging.warning("Tema 'clam' do ttk não encontrado, usando padrão.")

        # --- MODIFICAÇÃO: Usa Abas (Notebook) ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Aba de Clientes (Código original)
        client_frame = ClientListFrame(self.notebook)
        self.notebook.add(client_frame, text='Clientes')

        # Nova Aba de Produtos
        product_frame = ProductListFrame(self.notebook)
        self.notebook.add(product_frame, text='Produtos')


if __name__ == "__main__":
    # Configuração de log (Prompt 5)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("app.log"),
                            logging.StreamHandler()
                        ])

    logging.info("Iniciando a aplicação...")

    try:
        # Inicializa o banco de dados
        init_db()

        # Inicia a aplicação
        app = MainApplication()
        app.mainloop()

    except Exception as e:
        logging.critical(f"Erro fatal ao iniciar a aplicação: {e}")
        print(f"Erro fatal: {e}")


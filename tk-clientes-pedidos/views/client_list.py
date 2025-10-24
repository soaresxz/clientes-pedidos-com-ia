import tkinter as tk
from tkinter import ttk, messagebox
from models import get_all_clients, delete_client
from views.client_form import ClientForm
from views.order_form import OrderForm
import logging


class ClientListFrame(ttk.Frame):
    """
    Frame principal para listar Clientes (Prompt 3).
    """

    def __init__(self, parent):
        super().__init__(parent, padding="10")
        self.parent = parent

        self.create_widgets()
        self.load_clients()

    def create_widgets(self):
        # --- Frame de Ações (Busca e Botões) ---
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, pady=5)

        # Busca (Prompt 3)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search)  # Busca dinâmica

        ttk.Label(action_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        search_entry = ttk.Entry(action_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Botões (Prompt 3)
        self.delete_btn = ttk.Button(action_frame, text="Excluir", command=self.on_delete)
        self.delete_btn.pack(side=tk.RIGHT, padx=5)

        self.edit_btn = ttk.Button(action_frame, text="Editar", command=self.on_edit)
        self.edit_btn.pack(side=tk.RIGHT, padx=5)

        self.new_btn = ttk.Button(action_frame, text="Novo Cliente", command=self.on_new)
        self.new_btn.pack(side=tk.RIGHT, padx=5)

        self.new_order_btn = ttk.Button(action_frame, text="Novo Pedido", command=self.on_new_order)
        self.new_order_btn.pack(side=tk.RIGHT, padx=5)

        # --- Treeview (Prompt 3) ---
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        cols = ('id', 'nome', 'email', 'telefone')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings')

        # Cabeçalhos
        self.tree.heading('id', text='ID')
        self.tree.heading('nome', text='Nome')
        self.tree.heading('email', text='E-mail')
        self.tree.heading('telefone', text='Telefone')

        # Largura das colunas
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('nome', width=250)
        self.tree.column('email', width=250)
        self.tree.column('telefone', width=150)

        # Scrollbars
        ysb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        xsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)

        ysb.pack(side=tk.RIGHT, fill=tk.Y)
        xsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind duplo clique para editar
        self.tree.bind("<Double-1>", self.on_edit)

        # Desabilita botões que dependem de seleção
        self.update_button_states()
        self.tree.bind("<<TreeviewSelect>>", self.update_button_states)

    def load_clients(self, search_term=None):
        """Carrega/Recarrega os clientes no Treeview (Prompt 3)."""
        try:
            # Limpa a árvore
            for i in self.tree.get_children():
                self.tree.delete(i)

            # Busca clientes
            clients = get_all_clients(search_term)

            # Preenche a árvore
            for client in clients:
                self.tree.insert('', tk.END, iid=client['id'], values=(
                    client['id'],
                    client['nome'],
                    client['email'] or '',
                    client['telefone'] or ''
                ))
        except Exception as e:
            logging.error(f"Erro ao carregar clientes: {e}")
            messagebox.showerror("Erro", f"Não foi possível carregar os clientes:\n{e}", parent=self)

        self.update_button_states()

    def get_selected_client_id(self):
        """Retorna o ID do cliente selecionado no Treeview."""
        try:
            selected_item = self.tree.selection()[0]  # Pega o primeiro (e único) item selecionado
            return selected_item  # O iid é o ID do cliente
        except IndexError:
            return None  # Nada selecionado

    def update_button_states(self, event=None):
        """Ativa/Desativa botões baseados na seleção."""
        if self.get_selected_client_id():
            self.edit_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
            self.new_order_btn.config(state=tk.NORMAL)
        else:
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
            self.new_order_btn.config(state=tk.DISABLED)

    def on_search(self, *args):
        """Callback para a barra de busca."""
        search_term = self.search_var.get().strip()
        self.load_clients(search_term)

    def on_new(self):
        """Abre o formulário para um novo cliente (Prompt 3)."""
        ClientForm(self, on_close_callback=self.load_clients)

    def on_edit(self, event=None):
        """Abre o formulário para editar o cliente selecionado (Prompt 3)."""
        client_id = self.get_selected_client_id()
        if not client_id:
            messagebox.showwarning("Seleção", "Por favor, selecione um cliente para editar.", parent=self)
            return

        ClientForm(self, client_id=client_id, on_close_callback=self.load_clients)

    def on_delete(self):
        """Exclui o cliente selecionado (Prompt 3)."""
        client_id = self.get_selected_client_id()
        if not client_id:
            messagebox.showwarning("Seleção", "Por favor, selecione um cliente para excluir.", parent=self)
            return

        # Pede confirmação (Prompt 3 e 5)
        client = self.tree.item(client_id, 'values')
        client_name = client[1] if client else "este cliente"

        if not messagebox.askyesno("Confirmar Exclusão",
                                   f"Tem certeza que deseja excluir '{client_name}'?\n"
                                   "TODOS os pedidos associados a ele também serão excluídos.",
                                   parent=self):
            return

        try:
            if delete_client(client_id):
                messagebox.showinfo("Sucesso", f"Cliente '{client_name}' excluído com sucesso.", parent=self)
                self.load_clients()  # Recarrega a lista (Prompt 3)
            else:
                messagebox.showerror("Erro", "Falha ao excluir o cliente.", parent=self)
        except Exception as e:
            logging.error(f"Erro ao excluir: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado:\n{e}", parent=self)

    def on_new_order(self):
        """Abre o formulário de novo pedido para o cliente selecionado (Prompt 4)."""
        client_id = self.get_selected_client_id()
        if not client_id:
            messagebox.showwarning("Seleção", "Por favor, selecione um cliente para criar um pedido.", parent=self)
            return

        # Passa todos os clientes (para o combobox) e o ID selecionado
        all_clients = get_all_clients()
        OrderForm(self, all_clients=all_clients, selected_client_id=client_id)

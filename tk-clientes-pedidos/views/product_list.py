import tkinter as tk
from tkinter import ttk, messagebox
from models import get_all_products, delete_product
from views.product_form import ProductForm
import logging


class ProductListFrame(ttk.Frame):
    """
    Frame para listar Produtos.
    """

    def __init__(self, parent):
        super().__init__(parent, padding="10")
        self.parent = parent

        self.create_widgets()
        self.load_products()

    def create_widgets(self):
        # Frame de Ações (Busca e Botões)
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search)

        ttk.Label(action_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        search_entry = ttk.Entry(action_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.delete_btn = ttk.Button(action_frame, text="Excluir", command=self.on_delete)
        self.delete_btn.pack(side=tk.RIGHT, padx=5)

        self.edit_btn = ttk.Button(action_frame, text="Editar", command=self.on_edit)
        self.edit_btn.pack(side=tk.RIGHT, padx=5)

        self.new_btn = ttk.Button(action_frame, text="Novo Produto", command=self.on_new)
        self.new_btn.pack(side=tk.RIGHT, padx=5)

        # --- Treeview ---
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        cols = ('id', 'nome', 'preco_sugerido')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings')

        self.tree.heading('id', text='ID')
        self.tree.heading('nome', text='Nome')
        self.tree.heading('preco_sugerido', text='Preço Sugerido')

        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('nome', width=400)
        self.tree.column('preco_sugerido', width=150, anchor=tk.E)

        ysb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        xsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)

        ysb.pack(side=tk.RIGHT, fill=tk.Y)
        xsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.on_edit)

        self.update_button_states()
        self.tree.bind("<<TreeviewSelect>>", self.update_button_states)

    def load_products(self, search_term=None):
        """Carrega/Recarrega os produtos no Treeview."""
        try:
            for i in self.tree.get_children():
                self.tree.delete(i)

            products = get_all_products(search_term)

            for product in products:
                self.tree.insert('', tk.END, iid=product['id'], values=(
                    product['id'],
                    product['nome'],
                    f"R$ {product['preco_sugerido']:.2f}"
                ))
        except Exception as e:
            logging.error(f"Erro ao carregar produtos: {e}")
            messagebox.showerror("Erro", f"Não foi possível carregar os produtos:\n{e}", parent=self)

        self.update_button_states()

    def get_selected_product_id(self):
        try:
            selected_item = self.tree.selection()[0]
            return selected_item
        except IndexError:
            return None

    def update_button_states(self, event=None):
        if self.get_selected_product_id():
            self.edit_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
        else:
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)

    def on_search(self, *args):
        search_term = self.search_var.get().strip()
        self.load_products(search_term)

    def on_new(self):
        ProductForm(self, on_close_callback=self.load_products)

    def on_edit(self, event=None):
        product_id = self.get_selected_product_id()
        if not product_id:
            messagebox.showwarning("Seleção", "Por favor, selecione um produto para editar.", parent=self)
            return

        ProductForm(self, product_id=product_id, on_close_callback=self.load_products)

    def on_delete(self):
        product_id = self.get_selected_product_id()
        if not product_id:
            messagebox.showwarning("Seleção", "Por favor, selecione um produto para excluir.", parent=self)
            return

        product = self.tree.item(product_id, 'values')
        product_name = product[1] if product else "este produto"

        if not messagebox.askyesno("Confirmar Exclusão",
                                   f"Tem certeza que deseja excluir '{product_name}'?",
                                   parent=self):
            return

        try:
            if delete_product(product_id):
                messagebox.showinfo("Sucesso", f"Produto '{product_name}' excluído com sucesso.", parent=self)
                self.load_products()
            else:
                messagebox.showerror("Erro", "Falha ao excluir o produto.", parent=self)
        except Exception as e:
            logging.error(f"Erro ao excluir produto: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado:\n{e}", parent=self)

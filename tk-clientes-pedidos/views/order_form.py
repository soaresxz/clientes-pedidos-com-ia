import tkinter as tk
from tkinter import ttk, messagebox
from models import get_all_products, add_order_transaction
from utils import format_date_to_iso, validate_float, validate_int
import logging
from datetime import datetime


class OrderForm(tk.Toplevel):
    """
    Janela Toplevel para criar um novo Pedido (Prompt 4 e 5).
    """

    def __init__(self, parent, all_clients, selected_client_id=None):
        super().__init__(parent)
        self.parent = parent
        self.all_clients = all_clients
        self.selected_client_id = selected_client_id

        # Lista de produtos (para o combobox de itens)
        self.products_list = []
        # Mapa de nomes de produtos para IDs/preços
        self.products_map = {}

        # Lista local de itens adicionados ao pedido
        self.order_items = []

        # Configuração da janela
        self.title("Novo Pedido")
        self.geometry("800x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        # Protocolo para fechar (Prompt 5)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Carrega os dados necessários
        self.load_products_data()

        # Cria os widgets
        self.create_widgets()

        # Pré-seleciona o cliente, se foi passado
        if self.selected_client_id:
            try:
                client_id_int = int(self.selected_client_id)
                client_name = self.clients_map.get(client_id_int)
                if client_name:
                    self.client_combo.set(client_name)
            except (ValueError, TypeError):
                logging.warning(f"ID de cliente selecionado inválido: {self.selected_client_id}")

    def load_products_data(self):
        """Carrega os produtos do banco para o combobox de itens."""
        try:
            products_db = get_all_products(None)
            
            # Limpa listas anteriores
            self.products_list = []
            self.products_map = {}

            for prod in products_db:
                # Formato: "Nome (R$ Preço)"
                display_name = f"{prod['nome']} (R$ {prod['preco_sugerido']:.2f})"
                self.products_list.append(display_name)
                self.products_map[display_name] = {
                    'id': prod['id'],
                    'nome': prod['nome'],
                    'preco_sugerido': prod['preco_sugerido']
                }

        except Exception as e:
            logging.error(f"Erro ao carregar lista de produtos: {e}")
            messagebox.showerror("Erro de Produtos", "Não foi possível carregar o catálogo de produtos.", parent=self)
            self.destroy()

    def create_widgets(self):
        # Frame principal com padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.rowconfigure(2, weight=1)  # Faz a área de itens crescer
        main_frame.columnconfigure(0, weight=1)

        # --- 1. Informações do Pedido (Cliente e Data) ---
        info_frame = ttk.LabelFrame(main_frame, text="Informações do Pedido", padding="10")
        info_frame.grid(row=0, column=0, sticky=tk.EW, pady=5)
        info_frame.columnconfigure(1, weight=1)  # CORRIGIDO: columnconfigure
        info_frame.columnconfigure(3, weight=1)

        # Cliente
        ttk.Label(info_frame, text="Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        # Mapa de Clientes (ID -> Nome) para o combobox
        self.client_names = [client['nome'] for client in self.all_clients]
        self.clients_map = {client['id']: client['nome'] for client in self.all_clients}
        self.clients_name_map = {client['nome']: client['id'] for client in self.all_clients}

        self.client_combo = ttk.Combobox(info_frame, values=self.client_names, state="readonly")
        self.client_combo.grid(row=0, column=1, padx=5, sticky=tk.EW)

        # Data
        ttk.Label(info_frame, text="Data:").grid(row=0, column=2, padx=(20, 5), sticky=tk.W)
        self.data_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        ttk.Entry(info_frame, textvariable=self.data_var, width=15).grid(row=0, column=3, padx=5, sticky=tk.W)

        # --- 2. Adicionar Itens ---
        add_item_frame = ttk.LabelFrame(main_frame, text="Adicionar Item", padding="10")
        add_item_frame.grid(row=1, column=0, sticky=tk.EW, pady=10)
        add_item_frame.columnconfigure(1, weight=3)  # CORRIGIDO: columnconfigure
        add_item_frame.columnconfigure(3, weight=1)
        add_item_frame.columnconfigure(5, weight=1)

        # Produto (Combobox)
        ttk.Label(add_item_frame, text="Produto:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.item_produto_combo = ttk.Combobox(add_item_frame, values=self.products_list)
        self.item_produto_combo.grid(row=0, column=1, padx=5, sticky=tk.EW)
        self.item_produto_combo.bind("<<ComboboxSelected>>", self.on_product_select)

        # Quantidade
        ttk.Label(add_item_frame, text="Qtd:").grid(row=0, column=2, padx=(10, 5), sticky=tk.W)
        self.item_qtd_var = tk.StringVar(value="1")
        ttk.Entry(add_item_frame, textvariable=self.item_qtd_var, width=10).grid(row=0, column=3, padx=5, sticky=tk.EW)

        # Preço Unitário
        ttk.Label(add_item_frame, text="Preço Unit:").grid(row=0, column=4, padx=(10, 5), sticky=tk.W)
        self.item_preco_var = tk.StringVar()
        ttk.Entry(add_item_frame, textvariable=self.item_preco_var, width=10).grid(row=0, column=5, padx=5, sticky=tk.EW)

        # Botão Adicionar
        add_btn = ttk.Button(add_item_frame, text="Adicionar Item", command=self.add_item_to_tree)
        add_btn.grid(row=0, column=6, padx=(10, 0))

        # --- 3. Itens do Pedido (Treeview) ---
        items_frame = ttk.Frame(main_frame)
        items_frame.grid(row=2, column=0, sticky=tk.NSEW, pady=5)

        cols = ('produto', 'qtd', 'preco_unit', 'subtotal')
        self.tree = ttk.Treeview(items_frame, columns=cols, show='headings')
        self.tree.heading('produto', text='Produto')
        self.tree.heading('qtd', text='Quantidade')
        self.tree.heading('preco_unit', text='Preço Unit.')
        self.tree.heading('subtotal', text='Subtotal')
        self.tree.column('produto', width=300)
        self.tree.column('qtd', width=80, anchor=tk.E)
        self.tree.column('preco_unit', width=100, anchor=tk.E)
        self.tree.column('subtotal', width=100, anchor=tk.E)

        ysb = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.tree.yview)
        xsb = ttk.Scrollbar(items_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)

        ysb.pack(side=tk.RIGHT, fill=tk.Y)
        xsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Botão Remover Item
        self.remove_item_btn = ttk.Button(main_frame, text="Remover Item Selecionado",
                                          command=self.remove_item_from_tree)
        self.remove_item_btn.grid(row=3, column=0, sticky=tk.E, pady=5)
        self.remove_item_btn.config(state=tk.DISABLED)
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.remove_item_btn.config(state=tk.NORMAL))

        # --- 4. Total e Botões de Ação ---
        total_frame = ttk.Frame(main_frame)
        total_frame.grid(row=4, column=0, sticky=tk.EW, pady=10)
        total_frame.columnconfigure(0, weight=1)  # CORRIGIDO: columnconfigure

        # Label Total - CORRIGIDO: Criar ANTES de usar
        self.total_var = tk.StringVar(value="Total: R$ 0.00")
        total_label = ttk.Label(total_frame, textvariable=self.total_var, font=("-weight bold", 12))
        total_label.grid(row=0, column=0, sticky=tk.E, padx=5)

        # Botões Salvar/Cancelar
        self.cancel_btn = ttk.Button(total_frame, text="Cancelar", command=self.on_close)
        self.cancel_btn.grid(row=0, column=1, padx=5)

        self.save_btn = ttk.Button(total_frame, text="Salvar Pedido", command=self.on_save)
        self.save_btn.grid(row=0, column=2, padx=5)

    def on_product_select(self, event=None):
        """Callback para quando um produto é selecionado no combobox."""
        selected_display_name = self.item_produto_combo.get()
        product_data = self.products_map.get(selected_display_name)

        if product_data:
            self.item_preco_var.set(f"{product_data['preco_sugerido']:.2f}")
            self.item_qtd_var.set("1")

    def add_item_to_tree(self):
        """Valida e adiciona um item ao Treeview de itens."""

        # 1. Validar Produto
        selected_display_name = self.item_produto_combo.get()
        product_data = self.products_map.get(selected_display_name)

        if not product_data:
            found = False
            for display_name, data in self.products_map.items():
                if data['nome'].lower() == selected_display_name.lower():
                    product_data = data
                    selected_display_name = display_name
                    self.item_produto_combo.set(display_name)
                    found = True
                    break
            if not found:
                messagebox.showerror("Erro", "Produto inválido ou não selecionado.", parent=self)
                return

        produto_nome = product_data['nome']

        # 2. Validar Quantidade
        try:
            quantidade = validate_int(self.item_qtd_var.get())
            if quantidade <= 0:
                raise ValueError("Quantidade deve ser positiva.")
        except ValueError as e:
            messagebox.showerror("Erro", f"Quantidade inválida: {e}", parent=self)
            return

        # 3. Validar Preço
        try:
            preco_unit = validate_float(self.item_preco_var.get())
            if preco_unit < 0:
                raise ValueError("Preço não pode ser negativo.")
        except ValueError as e:
            messagebox.showerror("Erro", f"Preço unitário inválido: {e}", parent=self)
            return

        # 4. Calcular Subtotal
        subtotal = quantidade * preco_unit

        # 5. Adicionar ao Treeview
        values = (produto_nome, f"{quantidade}", f"{preco_unit:.2f}", f"{subtotal:.2f}")
        item_id = self.tree.insert('', tk.END, values=values)

        # 6. Adicionar à lista interna
        self.order_items.append({
            'item_id_tree': item_id,
            'produto': produto_nome,
            'quantidade': quantidade,
            'preco_unit': preco_unit
        })

        # 7. Limpar campos e atualizar total
        self.update_total()
        self.item_produto_combo.set("")
        self.item_qtd_var.set("1")
        self.item_preco_var.set("")
        self.item_produto_combo.focus()

    def remove_item_from_tree(self):
        """Remove o item selecionado do Treeview e da lista interna."""
        try:
            selected_item_id = self.tree.selection()[0]
        except IndexError:
            messagebox.showwarning("Seleção", "Nenhum item selecionado para remover.", parent=self)
            return

        # Remove da lista interna
        self.order_items = [item for item in self.order_items if item['item_id_tree'] != selected_item_id]

        # Remove do Treeview
        self.tree.delete(selected_item_id)

        # Atualiza o total e desabilita o botão
        self.update_total()
        self.remove_item_btn.config(state=tk.DISABLED)

    def update_total(self):
        """Calcula e exibe o total do pedido."""
        total = 0.0
        for item in self.order_items:
            total += item['quantidade'] * item['preco_unit']

        self.total_var.set(f"Total: R$ {total:.2f}")
        return total

    def on_save(self):
        """Valida e salva o pedido completo (transacional)."""

        # 1. Validar Cliente
        client_name = self.client_combo.get()
        cliente_id = self.clients_name_map.get(client_name)
        if not cliente_id:
            messagebox.showerror("Erro", "Cliente inválido ou não selecionado.", parent=self)
            return

        # 2. Validar Data
        try:
            data_iso = format_date_to_iso(self.data_var.get())
        except ValueError as e:
            messagebox.showerror("Erro", f"Data inválida: {e}\nUse o formato DD/MM/AAAA.", parent=self)
            return

        # 3. Validar Itens
        if not self.order_items:
            messagebox.showerror("Erro", "O pedido deve ter pelo menos um item.", parent=self)
            return

        # 4. Pegar o total
        total = self.update_total()

        # Confirmação
        if not messagebox.askyesno("Confirmar Pedido",
                                   f"Salvar pedido para '{client_name}'?\n"
                                   f"Total: R$ {total:.2f}\n"
                                   f"Itens: {len(self.order_items)}",
                                   parent=self):
            return

        # 5. Salvar no DB (Transacional)
        try:
            if add_order_transaction(cliente_id, data_iso, total, self.order_items):
                messagebox.showinfo("Sucesso", "Pedido salvo com sucesso!", parent=self)
                self.destroy()
            else:
                messagebox.showerror("Erro de Banco de Dados", "Não foi possível salvar o pedido. Verifique os logs.",
                                     parent=self)
        except Exception as e:
            logging.error(f"Erro ao salvar pedido (on_save): {e}")
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}", parent=self)

    def on_close(self):
        """Verifica se há dados não salvos antes de fechar."""
        if self.order_items:
            if messagebox.askyesno("Pedido não Salvo",
                                   "Você tem itens no pedido que não foram salvos.\nDeseja fechar mesmo assim?",
                                   parent=self):
                self.destroy()
        else:
            self.destroy()
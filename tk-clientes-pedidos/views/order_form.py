import tkinter as tk
from tkinter import ttk, messagebox
from models import add_order_transaction
from utils import get_today_date_str
import logging


class OrderForm(tk.Toplevel):
    """
    Janela Toplevel para Criar Pedidos (Prompt 4).
    """

    def __init__(self, parent, all_clients, selected_client_id=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.title("Novo Pedido")
        self.geometry("700x550")

        self.all_clients = all_clients
        self.selected_client_id = selected_client_id
        self.itens_pedido = []  # Armazena os itens (dict)

        # --- Frame Superior (Cliente e Data) ---
        top_frame = ttk.Frame(self, padding="10")
        top_frame.pack(fill=tk.X)

        # Seleção de Cliente (Combobox - Prompt 4)
        ttk.Label(top_frame, text="Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Prepara dados para o Combobox (Nome, ID)
        self.client_map = {client['nome']: client['id'] for client in self.all_clients}
        client_names = sorted(self.client_map.keys())

        self.client_var = tk.StringVar()
        self_client_combo = ttk.Combobox(top_frame, textvariable=self.client_var,
                                         values=client_names, state='readonly', width=40)
        self_client_combo.grid(row=0, column=1, padx=5, pady=5)

        # Tenta pré-selecionar o cliente (se vindo da lista)
        if self.selected_client_id:
            for name, cid in self.client_map.items():
                if cid == int(self.selected_client_id):
                    self.client_var.set(name)
                    break

        # Data (Padrão hoje - Prompt 4)
        ttk.Label(top_frame, text="Data:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.data_var = tk.StringVar(value=get_today_date_str())
        self.data_entry = ttk.Entry(top_frame, textvariable=self.data_var, width=12)
        self.data_entry.grid(row=0, column=3, padx=5, pady=5)
        # (Nota: Para um app real, um DatePicker (ttk.Calendar) seria melhor)

        # --- Frame de Itens (Adicionar) ---
        item_entry_frame = ttk.Frame(self, padding="5")
        item_entry_frame.pack(fill=tk.X)
        item_entry_frame.column_configure(1, weight=3)  # Produto
        item_entry_frame.column_configure(3, weight=1)  # Qtd
        item_entry_frame.column_configure(5, weight=1)  # Preço

        ttk.Label(item_entry_frame, text="Produto:").grid(row=0, column=0, padx=5, pady=5)
        self.produto_var = tk.StringVar()
        self.produto_entry = ttk.Entry(item_entry_frame, textvariable=self.produto_var)
        self.produto_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(item_entry_frame, text="Qtd:").grid(row=0, column=2, padx=5, pady=5)
        self.qtd_var = tk.StringVar(value="1")
        self.qtd_entry = ttk.Entry(item_entry_frame, textvariable=self.qtd_var, width=5)
        self.qtd_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(item_entry_frame, text="Preço Unit:").grid(row=0, column=4, padx=5, pady=5)
        self.preco_var = tk.StringVar(value="0.00")
        self.preco_entry = ttk.Entry(item_entry_frame, textvariable=self.preco_var, width=10)
        self.preco_entry.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        self.add_item_btn = ttk.Button(item_entry_frame, text="Adicionar Item", command=self.add_item)
        self.add_item_btn.grid(row=0, column=6, padx=10, pady=5)

        # Bind <Return> para adicionar item (UX - Prompt 5)
        self.preco_entry.bind("<Return>", self.add_item)

        # --- Frame da Tabela de Itens (Prompt 4) ---
        item_list_frame = ttk.Frame(self, padding="10")
        item_list_frame.pack(fill=tk.BOTH, expand=True)

        cols = ('produto', 'qtd', 'preco_unit', 'subtotal')
        self.tree = ttk.Treeview(item_list_frame, columns=cols, show='headings')

        self.tree.heading('produto', text='Produto')
        self.tree.heading('qtd', text='Qtd')
        self.tree.heading('preco_unit', text='Preço Unit.')
        self.tree.heading('subtotal', text='Subtotal')

        self.tree.column('produto', width=300)
        self.tree.column('qtd', width=80, anchor=tk.CENTER)
        self.tree.column('preco_unit', width=120, anchor=tk.E)
        self.tree.column('subtotal', width=120, anchor=tk.E)

        ysb = ttk.Scrollbar(item_list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=ysb.set)
        ysb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # --- Frame Inferior (Total e Ações) ---
        bottom_frame = ttk.Frame(self, padding="10")
        bottom_frame.pack(fill=tk.X)

        self.remove_item_btn = ttk.Button(bottom_frame, text="Remover Item Selecionado", command=self.remove_item)
        self.remove_item_btn.pack(side=tk.LEFT)

        self.total_label_var = tk.StringVar(value="Total Pedido: R$ 0.00")
        ttk.Label(bottom_frame, textvariable=self.total_label_var, font=("Helvetica", 14, "bold")).pack(side=tk.LEFT,
                                                                                                        padx=20)

        self.cancel_btn = ttk.Button(bottom_frame, text="Cancelar", command=self.on_cancel)
        self.cancel_btn.pack(side=tk.RIGHT, padx=10)

        self.save_btn = ttk.Button(bottom_frame, text="Salvar Pedido", command=self.on_save)
        self.save_btn.pack(side=tk.RIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        # Foco inicial
        self.produto_entry.focus_set()

    def validate_item(self):
        """Valida os campos de entrada do item."""
        produto = self.produto_var.get().strip()
        if not produto:
            messagebox.showwarning("Item Inválido", "O nome do produto não pode estar vazio.", parent=self)
            self.produto_entry.focus_set()
            return None

        try:
            qtd = int(self.qtd_var.get())
            if qtd <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Item Inválido", "A quantidade deve ser um número inteiro positivo.", parent=self)
            self.qtd_entry.focus_set()
            return None

        try:
            preco = float(self.preco_var.get().replace(",", "."))
            if preco < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Item Inválido", "O preço deve ser um número positivo.", parent=self)
            self.preco_entry.focus_set()
            return None

        return {'produto': produto, 'quantidade': qtd, 'preco_unit': preco}

    def add_item(self, event=None):
        """Adiciona o item na lista e no Treeview (Prompt 4)."""
        item = self.validate_item()
        if not item:
            return

        # Adiciona na lista interna
        self.itens_pedido.append(item)

        # Adiciona no Treeview
        subtotal = item['quantidade'] * item['preco_unit']
        self.tree.insert('', tk.END, values=(
            item['produto'],
            item['quantidade'],
            f"R$ {item['preco_unit']:.2f}",
            f"R$ {subtotal:.2f}"
        ))

        self.update_total()

        # Limpa campos e foca no produto (UX - Prompt 5)
        self.produto_var.set("")
        self.qtd_var.set("1")
        self.preco_var.set("0.00")
        self.produto_entry.focus_set()

    def remove_item(self):
        """Remove o item selecionado (Prompt 4)."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Seleção", "Selecione um item para remover.", parent=self)
            return

        if not messagebox.askyesno("Confirmar", "Remover o item selecionado?", parent=self):
            return

        for selected_item in selected_items:
            # Encontra o índice no treeview
            index = self.tree.index(selected_item)

            # Remove da lista interna (pelo índice)
            if 0 <= index < len(self.itens_pedido):
                del self.itens_pedido[index]
            else:
                logging.warning(f"Índice {index} fora do range para a lista de itens.")

            # Remove do treeview
            self.tree.delete(selected_item)

        self.update_total()

    def update_total(self):
        """Calcula e exibe o total (Prompt 4)."""
        total = 0.0
        for item in self.itens_pedido:
            total += item['quantidade'] * item['preco_unit']

        self.total_label_var.set(f"Total Pedido: R$ {total:.2f}")
        return total

    def validate_order(self):
        """Valida os dados gerais do pedido."""
        cliente_nome = self.client_var.get()
        if not cliente_nome:
            messagebox.showwarning("Pedido Inválido", "Selecione um cliente.", parent=self)
            return None

        data = self.data_var.get().strip()
        # (Validação de formato de data seria ideal aqui)
        if len(data) != 10:  # YYYY-MM-DD
            messagebox.showwarning("Pedido Inválido", "Formato de data inválido (use AAAA-MM-DD).", parent=self)
            return None

        if not self.itens_pedido:
            messagebox.showwarning("Pedido Inválido", "O pedido deve ter pelo menos um item.", parent=self)
            return None

        cliente_id = self.client_map[cliente_nome]
        total = self.update_total()  # Pega o total calculado

        return cliente_id, data, total

    def on_save(self):
        """Salva o pedido e os itens (Prompt 4 - Transacional)."""

        validation_data = self.validate_order()
        if not validation_data:
            return

        cliente_id, data, total = validation_data

        if not messagebox.askyesno("Confirmar Pedido",
                                   f"Salvar pedido no valor de {self.total_label_var.get()} para o cliente '{self.client_var.get()}'?",
                                   parent=self):
            return

        try:
            # Chama o modelo transacional (Prompt 4)
            success = add_order_transaction(cliente_id, data, total, self.itens_pedido)

            if success:
                messagebox.showinfo("Sucesso", "Pedido salvo com sucesso!", parent=self)
                self.destroy()  # Fecha a janela
            else:
                # Erro vindo de db.py (Prompt 5)
                messagebox.showerror("Erro", "Falha ao salvar o pedido. Verifique os logs.", parent=self)

        except Exception as e:
            logging.error(f"Erro ao salvar pedido: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado:\n{e}", parent=self)

    def on_cancel(self):
        """Fecha a janela (Prompt 5 - Verificação)."""
        if self.itens_pedido:
            if not messagebox.askyesno("Confirmar Saída",
                                       "O pedido atual não foi salvo e será perdido. Deseja sair?",
                                       parent=self):
                return
        self.destroy()

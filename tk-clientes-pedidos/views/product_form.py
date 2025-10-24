import tkinter as tk
from tkinter import ttk, messagebox
from models import add_product, update_product, get_product_by_id
import logging


class ProductForm(tk.Toplevel):
    """
    Formulário Toplevel para Criar/Editar Produtos.
    """

    def __init__(self, parent, product_id=None, on_close_callback=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.product_id = product_id
        self.on_close_callback = on_close_callback
        self.data_changed = False

        self.title("Novo Produto" if product_id is None else "Editar Produto")
        self.geometry("400x200")
        self.resizable(False, False)

        # Variáveis
        self.nome_var = tk.StringVar()
        self.preco_var = tk.StringVar(value="0.00")

        self.nome_var.trace_add("write", self.mark_as_changed)
        self.preco_var.trace_add("write", self.mark_as_changed)

        # Layout
        frame = ttk.Frame(self, padding="10")
        frame.pack(expand=True, fill=tk.BOTH)

        # Campos
        ttk.Label(frame, text="Nome: *").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nome_entry = ttk.Entry(frame, textvariable=self.nome_var, width=40)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Preço Sugerido:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.preco_entry = ttk.Entry(frame, textvariable=self.preco_var, width=20)
        self.preco_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame, text="* Campo obrigatório").grid(row=2, column=1, padx=5, pady=2, sticky="e")

        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        self.save_btn = ttk.Button(btn_frame, text="Salvar", command=self.on_save)
        self.save_btn.pack(side=tk.LEFT, padx=10)

        self.cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=self.on_cancel)
        self.cancel_btn.pack(side=tk.LEFT, padx=10)

        if self.product_id:
            self.load_product_data()

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.nome_entry.focus_set()

    def mark_as_changed(self, *args):
        self.data_changed = True

    def load_product_data(self):
        """Carrega dados do produto (para edição)."""
        product = get_product_by_id(self.product_id)
        if product:
            self.nome_var.set(product['nome'])
            self.preco_var.set(f"{product['preco_sugerido']:.2f}")
            self.data_changed = False

    def validate_form(self):
        """Valida os campos do formulário."""
        nome = self.nome_var.get().strip()
        preco_str = self.preco_var.get().strip().replace(",", ".")

        if not nome:
            messagebox.showwarning("Validação Falhou", "O campo 'Nome' é obrigatório.", parent=self)
            self.nome_entry.focus_set()
            return None, None

        try:
            preco = float(preco_str)
            if preco < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validação Falhou", "O preço deve ser um número positivo.", parent=self)
            self.preco_entry.focus_set()
            return None, None

        return nome, preco

    def on_save(self):
        """Callback do botão Salvar."""
        nome, preco = self.validate_form()
        if nome is None:
            return

        try:
            if self.product_id:
                success = update_product(self.product_id, nome, preco)
                msg = "Produto atualizado com sucesso!"
            else:
                success = add_product(nome, preco)
                msg = "Produto adicionado com sucesso!"

            if success:
                messagebox.showinfo("Sucesso", msg, parent=self)
                if self.on_close_callback:
                    self.on_close_callback()
                self.destroy()

        except ValueError as e:
            messagebox.showerror("Erro", str(e), parent=self)
        except Exception as e:
            logging.error(f"Erro ao salvar produto: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado:\n{e}", parent=self)

    def on_cancel(self):
        """Callback do botão Cancelar."""
        if self.data_changed:
            if not messagebox.askyesno("Confirmar Saída",
                                       "Você tem alterações não salvas. Deseja realmente sair?",
                                       parent=self):
                return

        self.destroy()

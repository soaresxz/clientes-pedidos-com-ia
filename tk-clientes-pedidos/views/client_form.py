import tkinter as tk
from tkinter import ttk, messagebox
from models import add_client, update_client
from utils import is_valid_email, is_valid_phone
import logging


class ClientForm(tk.Toplevel):
    """
    Formulário Toplevel para Criar/Editar Clientes (Prompt 2).
    """

    def __init__(self, parent, client_id=None, on_close_callback=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()  # Modal

        self.client_id = client_id
        self.on_close_callback = on_close_callback  # Callback para recarregar lista (Prompt 3)
        self.data_changed = False  # Flag para Prompt 5

        self.title("Novo Cliente" if client_id is None else "Editar Cliente")
        self.geometry("400x250")
        self.resizable(False, False)

        # Variáveis
        self.nome_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.telefone_var = tk.StringVar()

        # Rastreia mudanças (Prompt 5)
        self.nome_var.trace_add("write", self.mark_as_changed)
        self.email_var.trace_add("write", self.mark_as_changed)
        self.telefone_var.trace_add("write", self.mark_as_changed)

        # Layout
        frame = ttk.Frame(self, padding="10")
        frame.pack(expand=True, fill=tk.BOTH)

        # Campos do formulário
        ttk.Label(frame, text="Nome: *").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nome_entry = ttk.Entry(frame, textvariable=self.nome_var, width=40)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="E-mail:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.email_entry = ttk.Entry(frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Telefone:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.telefone_entry = ttk.Entry(frame, textvariable=self.telefone_var, width=40)
        self.telefone_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="* Campo obrigatório").grid(row=3, column=1, padx=5, pady=2, sticky="e")

        # Botões (Prompt 2)
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)

        self.save_btn = ttk.Button(btn_frame, text="Salvar", command=self.on_save)
        self.save_btn.pack(side=tk.LEFT, padx=10)

        self.cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=self.on_cancel)
        self.cancel_btn.pack(side=tk.LEFT, padx=10)

        # Carrega dados se for edição
        if self.client_id:
            self.load_client_data()

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)  # Prompt 5

        # Foco inicial
        self.nome_entry.focus_set()

    def mark_as_changed(self, *args):
        self.data_changed = True

    def load_client_data(self):
        """Carrega dados do cliente (para edição)."""
        from models import get_client_by_id  # Importação tardia
        client = get_client_by_id(self.client_id)
        if client:
            self.nome_var.set(client['nome'])
            self.email_var.set(client['email'] or "")
            self.telefone_var.set(client['telefone'] or "")
            self.data_changed = False  # Reseta flag após carregar

    def validate_form(self):
        """Valida os campos do formulário (Prompt 2 e 5)."""
        nome = self.nome_var.get().strip()
        email = self.email_var.get().strip()
        telefone = self.telefone_var.get().strip()

        # Nome obrigatório
        if not nome:
            messagebox.showwarning("Validação Falhou", "O campo 'Nome' é obrigatório.", parent=self)
            self.nome_entry.focus_set()
            return False

        # Validação de e-mail (se preenchido)
        if email and not is_valid_email(email):
            messagebox.showwarning("Validação Falhou", "O formato do e-mail é inválido.", parent=self)
            self.email_entry.focus_set()
            return False

        # Validação de telefone
        if not is_valid_phone(telefone):
            messagebox.showwarning("Validação Falhou",
                                   "O telefone deve conter apenas números e ter entre 8 e 15 dígitos.",
                                   parent=self)
            self.telefone_entry.focus_set()
            return False

        return True

    def on_save(self):
        """Callback do botão Salvar (Prompt 2)."""
        if not self.validate_form():
            return

        nome = self.nome_var.get().strip()
        email = self.email_var.get().strip()
        telefone = self.telefone_var.get().strip()

        try:
            if self.client_id:
                # Atualizar
                success = update_client(self.client_id, nome, email, telefone)
                msg = "Cliente atualizado com sucesso!"
            else:
                # Adicionar
                success = add_client(nome, email, telefone)
                msg = "Cliente adicionado com sucesso!"

            if success:
                messagebox.showinfo("Sucesso", msg, parent=self)
                if self.on_close_callback:
                    self.on_close_callback()  # Recarrega a lista (Prompt 3)
                self.destroy()

        except ValueError as e:  # Captura e-mail duplicado (Prompt 5)
            messagebox.showerror("Erro", str(e), parent=self)
        except Exception as e:
            logging.error(f"Erro ao salvar cliente: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado:\n{e}", parent=self)

    def on_cancel(self):
        """Callback do botão Cancelar (Prompt 2 e 5)."""
        if self.data_changed:
            if not messagebox.askyesno("Confirmar Saída",
                                       "Você tem alterações não salvas. Deseja realmente sair?",
                                       parent=self):
                return

        self.destroy()

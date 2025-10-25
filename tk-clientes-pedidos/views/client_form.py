import tkinter as tk
from tkinter import ttk, messagebox
import logging
# Importa os nomes de função corretos do utils.py
from utils import validate_email, validate_phone
from models import add_client, get_client_by_id, update_client

class ClientForm(tk.Toplevel):
    """
    Janela Toplevel para Adicionar/Editar Clientes (Prompt 2 e 5).
    """
    def __init__(self, parent, client_id=None, on_close_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.client_id = client_id
        self.on_close_callback = on_close_callback

        self.data_changed = False # Flag para (Prompt 5)

        # Configuração da Janela
        self.title("Novo Cliente" if client_id is None else "Editar Cliente")
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Janela modal: impede interação com a janela principal
        self.transient(parent)
        self.grab_set()

        # Protocolo para fechar (Prompt 5)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Variáveis dos campos
        self.nome_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.telefone_var = tk.StringVar()
        
        # Rastreia mudanças (Prompt 5)
        self.nome_var.trace_add("write", self.mark_as_changed)
        self.email_var.trace_add("write", self.mark_as_changed)
        self.telefone_var.trace_add("write", self.mark_as_changed)

        self.create_widgets()

        if self.client_id:
            self.load_client_data()
            self.data_changed = False # Reseta flag após carregar

    def create_widgets(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        frame.columnconfigure(1, weight=1)

        # Nome
        ttk.Label(frame, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.nome_entry = ttk.Entry(frame, textvariable=self.nome_var, width=40)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        # Email
        ttk.Label(frame, text="E-mail:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.email_entry = ttk.Entry(frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        # Telefone
        ttk.Label(frame, text="Telefone:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.telefone_entry = ttk.Entry(frame, textvariable=self.telefone_var, width=40)
        self.telefone_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.E)

        self.cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=self.on_close)
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)

        self.save_btn = ttk.Button(btn_frame, text="Salvar", command=self.on_save)
        self.save_btn.pack(side=tk.RIGHT)

        # Feedback de validação (Prompt 5)
        self.validation_label = ttk.Label(frame, text="", foreground="red")
        self.validation_label.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        
        self.nome_entry.focus()

    def mark_as_changed(self, *args):
        """Marca que os dados foram alterados (Prompt 5)."""
        self.data_changed = True

    def load_client_data(self):
        """Carrega os dados do cliente (se for edição)."""
        try:
            client = get_client_by_id(self.client_id)
            if client:
                self.nome_var.set(client.get('nome', ''))
                self.email_var.set(client.get('email', ''))
                self.telefone_var.set(client.get('telefone', ''))
            else:
                messagebox.showerror("Erro", "Cliente não encontrado.", parent=self)
                self.destroy()
        except Exception as e:
            logging.error(f"Erro ao carregar cliente (ID: {self.client_id}): {e}")
            messagebox.showerror("Erro", f"Não foi possível carregar o cliente:\n{e}", parent=self)
            self.destroy()

    def validate(self):
        """Valida os campos do formulário (Prompt 2 e 5)."""
        self.validation_label.config(text="") # Limpa feedback anterior
        nome = self.nome_var.get().strip()
        email = self.email_var.get().strip()
        telefone = self.telefone_var.get().strip()

        # 1. Nome (Obrigatório)
        if not nome:
            self.validation_label.config(text="Erro: O campo 'Nome' é obrigatório.")
            self.nome_entry.focus()
            return False

        # 2. E-mail (Formato)
        # CORREÇÃO: Usa o nome de função correto
        if not validate_email(email):
            self.validation_label.config(text="Erro: 'E-mail' inválido (ex: nome@dominio.com).")
            self.email_entry.focus()
            return False

        # 3. Telefone (Dígitos)
        # CORREÇÃO: Usa o nome de função correto
        if not validate_phone(telefone):
            self.validation_label.config(text="Erro: 'Telefone' deve ter de 8 a 15 dígitos.")
            self.telefone_entry.focus()
            return False

        return True

    def on_save(self):
        """Callback do botão Salvar."""
        if not self.validate():
            return

        nome = self.nome_var.get().strip()
        email = self.email_var.get().strip()
        telefone = self.telefone_var.get().strip()

        try:
            if self.client_id:
                # --- Atualizar Cliente ---
                if update_client(self.client_id, nome, email, telefone):
                    logging.info(f"Cliente (ID: {self.client_id}) atualizado.")
                    messagebox.showinfo("Sucesso", f"Cliente '{nome}' atualizado com sucesso.", parent=self)
                else:
                    messagebox.showerror("Erro", "Falha ao atualizar o cliente.", parent=self)
                    return # Não fecha se falhar
            else:
                # --- Adicionar Novo Cliente ---
                new_id = add_client(nome, email, telefone)
                if new_id:
                    logging.info(f"Cliente '{nome}' (ID: {new_id}) adicionado.")
                    messagebox.showinfo("Sucesso", f"Cliente '{nome}' cadastrado com sucesso.", parent=self)
                else:
                    messagebox.showerror("Erro", "Falha ao cadastrar o cliente.", parent=self)
                    return # Não fecha se falhar

            self.data_changed = False # Marca como salvo
            
            # Chama o callback (para recarregar a lista)
            if self.on_close_callback:
                self.on_close_callback()
                
            self.destroy() # Fecha a janela

        except Exception as e:
            logging.error(f"Erro ao salvar cliente: {e}")
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao salvar:\n{e}", parent=self)

    def on_close(self):
        """
        Verifica se há dados não salvos antes de fechar (Prompt 5).
        """
        if self.data_changed:
            if not messagebox.askyesno("Dados Não Salvos",
                                       "Você modificou os dados, mas não salvou.\nDeseja fechar mesmo assim?",
                                       parent=self):
                return # Não fecha
        
        self.destroy()


import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import logging
from datetime import datetime


class HistoryFrame(ttk.Frame):
    """
    Frame para exibir o histórico de ações do sistema.
    Lê o arquivo app.log e exibe os eventos.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        self.log_file_path = "app.log"

        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        # Frame superior com título e botões
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=tk.X)

        # Título
        ttk.Label(
            top_frame,
            text="📜 Histórico de Ações do Sistema",
            font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)

        # Botões
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT)

        self.refresh_btn = ttk.Button(
            button_frame,
            text="🔄 Atualizar",
            command=self.load_history,
            width=15
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Limpar Histórico",
            command=self.clear_history,
            width=18
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Frame de filtros
        filter_frame = ttk.LabelFrame(self, text="Filtros", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(filter_frame, text="Tipo:").pack(side=tk.LEFT, padx=(0, 5))

        self.filter_var = tk.StringVar(value="TODOS")
        filter_options = ["TODOS", "CLIENTE", "PEDIDO", "PRODUTO", "ERRO"]

        for option in filter_options:
            ttk.Radiobutton(
                filter_frame,
                text=option,
                variable=self.filter_var,
                value=option,
                command=self.apply_filter
            ).pack(side=tk.LEFT, padx=5)

        # Frame principal com o texto do log
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Text widget com scrollbar
        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Courier", 9),
            bg="#f5f5f5",
            fg="#333333",
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Configurar tags para colorir diferentes tipos de log
        self.log_text.tag_config("INFO", foreground="#0066cc")
        self.log_text.tag_config("ERROR", foreground="#cc0000", font=("Courier", 9, "bold"))
        self.log_text.tag_config("WARNING", foreground="#ff8800")
        self.log_text.tag_config("CLIENTE", foreground="#008800")
        self.log_text.tag_config("PEDIDO", foreground="#0066ff")
        self.log_text.tag_config("PRODUTO", foreground="#9900cc")
        self.log_text.tag_config("timestamp", foreground="#666666")

        # Label de status
        self.status_label = ttk.Label(
            self,
            text="",
            font=("Arial", 9),
            foreground="gray"
        )
        self.status_label.pack(pady=(5, 10))

    def load_history(self):
        """Carrega e exibe o histórico do arquivo de log"""
        try:
            if not os.path.exists(self.log_file_path):
                self.display_message("⚠️ Arquivo de log não encontrado.\n\nNenhuma ação foi registrada ainda.")
                self.status_label.config(text="Arquivo app.log não existe")
                return

            with open(self.log_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            if not lines:
                self.display_message("📭 O histórico está vazio.\n\nNenhuma ação foi registrada ainda.")
                self.status_label.config(text="Histórico vazio")
                return

            # Armazena todas as linhas para filtragem
            self.all_lines = lines

            # Aplica o filtro atual
            self.apply_filter()

            # Atualiza status
            now = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
            self.status_label.config(text=f"Última atualização: {now} | Total de eventos: {len(lines)}")

            logging.info("Histórico de ações carregado com sucesso.")

        except Exception as e:
            logging.error(f"Erro ao carregar histórico: {e}")
            self.display_message(f"❌ Erro ao carregar histórico:\n\n{str(e)}")
            self.status_label.config(text="Erro ao carregar histórico")

    def apply_filter(self):
        """Aplica o filtro selecionado no histórico"""
        if not hasattr(self, 'all_lines'):
            return

        filter_type = self.filter_var.get()

        # Filtra as linhas
        if filter_type == "TODOS":
            filtered_lines = self.all_lines
        else:
            filtered_lines = [line for line in self.all_lines if f"[{filter_type}]" in line]

        # Exibe as linhas filtradas
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)

        if not filtered_lines:
            self.log_text.insert(tk.END, f"📭 Nenhum evento do tipo '{filter_type}' encontrado.")
        else:
            for line in filtered_lines:
                self.insert_colored_line(line)

        self.log_text.config(state=tk.DISABLED)

        # Rola para o final
        self.log_text.see(tk.END)

        # Atualiza status
        self.status_label.config(
            text=f"Exibindo: {len(filtered_lines)} de {len(self.all_lines)} eventos | Filtro: {filter_type}"
        )

    def insert_colored_line(self, line):
        """Insere uma linha com cores baseadas no tipo de log"""
        # Identifica o tipo de log
        if " - ERROR - " in line:
            tag = "ERROR"
        elif " - WARNING - " in line:
            tag = "WARNING"
        elif "[CLIENTE]" in line:
            tag = "CLIENTE"
        elif "[PEDIDO]" in line:
            tag = "PEDIDO"
        elif "[PRODUTO]" in line:
            tag = "PRODUTO"
        else:
            tag = "INFO"

        # Insere a linha com a tag apropriada
        self.log_text.insert(tk.END, line, tag)

    def display_message(self, message):
        """Exibe uma mensagem no widget de texto"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(1.0, message)
        self.log_text.config(state=tk.DISABLED)

    def clear_history(self):
        """Limpa o histórico com confirmação"""
        # Verifica se o arquivo existe
        if not os.path.exists(self.log_file_path):
            messagebox.showinfo(
                "Histórico Vazio",
                "Não há histórico para limpar.",
                parent=self
            )
            return

        # Confirmação dupla
        resposta1 = messagebox.askyesno(
            "Confirmar Limpeza",
            "⚠️ Tem certeza que deseja limpar todo o histórico?\n\n"
            "Esta ação NÃO pode ser desfeita!",
            icon='warning',
            parent=self
        )

        if not resposta1:
            return

        resposta2 = messagebox.askyesno(
            "Confirmação Final",
            "🗑️ Esta é sua última chance!\n\n"
            "Deseja REALMENTE apagar todo o histórico de ações?",
            icon='warning',
            parent=self
        )

        if not resposta2:
            return

        try:
            # Limpa o arquivo (mantém o arquivo, mas vazio)
            with open(self.log_file_path, 'w', encoding='utf-8') as file:
                file.write("")

            logging.info("Histórico de ações foi limpo pelo usuário.")

            messagebox.showinfo(
                "Histórico Limpo",
                "✅ O histórico foi limpo com sucesso!",
                parent=self
            )

            # Recarrega a visualização
            self.load_history()

        except Exception as e:
            logging.error(f"Erro ao limpar histórico: {e}")
            messagebox.showerror(
                "Erro",
                f"❌ Erro ao limpar o histórico:\n\n{str(e)}",
                parent=self
            )

    def export_history(self):
        """Exporta o histórico para um arquivo (funcionalidade extra)"""
        from tkinter import filedialog

        if not os.path.exists(self.log_file_path):
            messagebox.showinfo(
                "Histórico Vazio",
                "Não há histórico para exportar.",
                parent=self
            )
            return

        # Pede ao usuário onde salvar
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Arquivo de Texto", "*.txt"),
                ("Todos os Arquivos", "*.*")
            ],
            initialfile=f"historico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            parent=self
        )

        if not file_path:
            return

        try:
            # Copia o arquivo
            with open(self.log_file_path, 'r', encoding='utf-8') as src:
                content = src.read()

            with open(file_path, 'w', encoding='utf-8') as dst:
                dst.write(content)

            messagebox.showinfo(
                "Exportação Concluída",
                f"✅ Histórico exportado com sucesso!\n\n{file_path}",
                parent=self
            )

        except Exception as e:
            logging.error(f"Erro ao exportar histórico: {e}")
            messagebox.showerror(
                "Erro",
                f"❌ Erro ao exportar o histórico:\n\n{str(e)}",
                parent=self
            )
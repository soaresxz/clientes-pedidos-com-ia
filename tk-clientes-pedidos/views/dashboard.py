import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from db import get_db_connection
from utils import analisar_pedidos
import logging
from datetime import datetime


class DashboardFrame(ttk.Frame):
    """
    Dashboard que exibe estatísticas do sistema:
    - Total de clientes
    - Total de pedidos no mês atual
    - Ticket médio dos pedidos
    - Análise de pedidos com IA
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        # Título do Dashboard
        title_label = ttk.Label(
            self,
            text="📊 Dashboard - Visão Geral",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)

        # Frame principal para os cards de estatísticas
        self.stats_frame = ttk.Frame(self)
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Configura o grid do stats_frame para 3 colunas
        self.stats_frame.columnconfigure(0, weight=1)
        self.stats_frame.columnconfigure(1, weight=1)
        self.stats_frame.columnconfigure(2, weight=1)

        # Cria os cards de estatísticas
        self.create_stat_card("Total de Clientes", "0", 0)
        self.create_stat_card("Pedidos este Mês", "0", 1)
        self.create_stat_card("Ticket Médio", "R$ 0,00", 2)

        # Frame para informações adicionais
        self.info_frame = ttk.LabelFrame(self, text="Informações Detalhadas", padding=15)
        self.info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.info_text = tk.Text(
            self.info_frame,
            height=8,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED,
            bg="#f5f5f5"
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Frame para os botões
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)

        self.refresh_button = ttk.Button(
            button_frame,
            text="🔄 Atualizar Dados",
            command=self.load_statistics,
            width=20
        )
        self.refresh_button.grid(row=0, column=0, padx=5)

        self.analyze_button = ttk.Button(
            button_frame,
            text="✨ Analisar Pedidos (Gemini AI)",
            command=self.run_analysis,
            width=30
        )
        self.analyze_button.grid(row=0, column=1, padx=5)

        # Label para última atualização
        self.last_update_label = ttk.Label(
            self,
            text="Última atualização: Nunca",
            font=("Arial", 9),
            foreground="gray"
        )
        self.last_update_label.pack(pady=(0, 20))

        # Carrega os dados inicialmente
        self.load_statistics()

    def create_stat_card(self, title, initial_value, column):
        """Cria um card de estatística"""
        card_frame = ttk.LabelFrame(self.stats_frame, text=title, padding=20)
        card_frame.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")

        value_label = ttk.Label(
            card_frame,
            text=initial_value,
            font=("Arial", 24, "bold"),
            foreground="#2c3e50"
        )
        value_label.pack()

        # Guarda referência ao label para atualizar depois
        if column == 0:
            self.clients_label = value_label
        elif column == 1:
            self.orders_label = value_label
        elif column == 2:
            self.ticket_label = value_label

    def load_statistics(self):
        """Carrega todas as estatísticas do banco de dados"""
        try:
            # Obtém o mês e ano atual
            now = datetime.now()
            current_month = now.strftime("%Y-%m")

            conn = get_db_connection()
            if not conn:
                messagebox.showerror(
                    "Erro de Conexão",
                    "Não foi possível conectar ao banco de dados."
                )
                return

            cursor = conn.cursor()

            # 1. Total de Clientes
            cursor.execute("SELECT COUNT(*) as total FROM clientes")
            total_clients = cursor.fetchone()['total']
            self.clients_label.config(text=str(total_clients))

            # 2. Total de Pedidos no Mês Atual
            cursor.execute(
                """
                SELECT COUNT(*) as total 
                FROM pedidos 
                WHERE strftime('%Y-%m', data) = ?
                """,
                (current_month,)
            )
            total_orders_month = cursor.fetchone()['total']
            self.orders_label.config(text=str(total_orders_month))

            # 3. Ticket Médio (de todos os pedidos)
            cursor.execute(
                """
                SELECT AVG(total) as ticket_medio 
                FROM pedidos
                """
            )
            result = cursor.fetchone()
            ticket_medio = result['ticket_medio'] if result['ticket_medio'] else 0
            self.ticket_label.config(text=f"R$ {ticket_medio:,.2f}")

            # 4. Informações Detalhadas
            self.load_detailed_info(cursor, current_month)

            conn.close()

            # Atualiza o label de última atualização
            self.last_update_label.config(
                text=f"Última atualização: {now.strftime('%d/%m/%Y às %H:%M:%S')}"
            )

            logging.info("Estatísticas do dashboard atualizadas com sucesso.")
            messagebox.showinfo(
                "Atualização Concluída",
                f"✅ Dashboard atualizado com sucesso!\n\n"
                f"• {total_clients} clientes cadastrados\n"
                f"• {total_orders_month} pedidos em {now.strftime('%B/%Y')}\n"
                f"• Ticket médio: R$ {ticket_medio:,.2f}"
            )

        except Exception as e:
            logging.error(f"Erro ao carregar estatísticas do dashboard: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao carregar estatísticas:\n{str(e)}"
            )

    def load_detailed_info(self, cursor, current_month):
        """Carrega informações detalhadas para o painel de texto"""
        info_lines = []

        try:
            # Total de pedidos (todos)
            cursor.execute("SELECT COUNT(*) as total FROM pedidos")
            total_all_orders = cursor.fetchone()['total']
            info_lines.append(f"📦 Total de Pedidos (Histórico): {total_all_orders}")

            # Valor total de vendas (todos os pedidos)
            cursor.execute("SELECT SUM(total) as total_vendas FROM pedidos")
            result = cursor.fetchone()
            total_vendas = result['total_vendas'] if result['total_vendas'] else 0
            info_lines.append(f"💰 Valor Total de Vendas: R$ {total_vendas:,.2f}")

            # Valor total de vendas no mês atual
            cursor.execute(
                """
                SELECT SUM(total) as total_mes 
                FROM pedidos 
                WHERE strftime('%Y-%m', data) = ?
                """,
                (current_month,)
            )
            result = cursor.fetchone()
            total_mes = result['total_mes'] if result['total_mes'] else 0
            info_lines.append(f"💵 Vendas este Mês: R$ {total_mes:,.2f}")

            # Cliente com mais pedidos
            cursor.execute(
                """
                SELECT c.nome, COUNT(p.id) as num_pedidos
                FROM clientes c
                LEFT JOIN pedidos p ON c.id = p.cliente_id
                GROUP BY c.id
                ORDER BY num_pedidos DESC
                LIMIT 1
                """
            )
            result = cursor.fetchone()
            if result:
                info_lines.append(
                    f"\n⭐ Cliente Destaque: {result['nome']} "
                    f"({result['num_pedidos']} pedidos)"
                )

            # Produto mais vendido
            cursor.execute(
                """
                SELECT produto, SUM(quantidade) as total_vendido
                FROM itens_pedido
                GROUP BY produto
                ORDER BY total_vendido DESC
                LIMIT 1
                """
            )
            result = cursor.fetchone()
            if result:
                info_lines.append(
                    f"🏆 Produto Mais Vendido: {result['produto']} "
                    f"({result['total_vendido']} unidades)"
                )

            # Atualiza o campo de texto
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, "\n".join(info_lines))
            self.info_text.config(state=tk.DISABLED)

        except Exception as e:
            logging.error(f"Erro ao carregar informações detalhadas: {e}")
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, "Erro ao carregar informações detalhadas.")
            self.info_text.config(state=tk.DISABLED)

    def run_analysis(self):
        """Executa a análise de pedidos com Gemini AI e mostra o resultado"""
        try:
            # Confirmar com o usuário
            resposta = messagebox.askyesno(
                "Análise com IA",
                "✨ Deseja analisar os últimos 5 pedidos usando Gemini AI (Google)?\n\n"
                "Esta operação pode levar alguns segundos e é totalmente gratuita!",
                icon='question'
            )
            
            if not resposta:
                return

            # Mostrar mensagem de processamento
            progress_window = tk.Toplevel(self)
            progress_window.title("Processando...")
            progress_window.geometry("350x120")
            progress_window.resizable(False, False)
            progress_window.transient(self)
            progress_window.grab_set()

            # Frame com padding
            progress_frame = ttk.Frame(progress_window, padding=20)
            progress_frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(
                progress_frame,
                text="✨ Analisando pedidos com Gemini AI...",
                font=("Arial", 11, "bold"),
                justify=tk.CENTER
            ).pack(pady=(0, 10))

            ttk.Label(
                progress_frame,
                text="Aguarde, isso pode levar alguns segundos...",
                font=("Arial", 9),
                justify=tk.CENTER,
                foreground="gray"
            ).pack()

            # Centralizar janela
            progress_window.update_idletasks()
            x = (progress_window.winfo_screenwidth() // 2) - (progress_window.winfo_width() // 2)
            y = (progress_window.winfo_screenheight() // 2) - (progress_window.winfo_height() // 2)
            progress_window.geometry(f"+{x}+{y}")

            progress_window.update()

            # Conectar ao banco e executar análise
            conn = get_db_connection()
            if not conn:
                progress_window.destroy()
                messagebox.showerror(
                    "Erro de Conexão",
                    "Não foi possível conectar ao banco de dados."
                )
                return

            # Executar análise
            result = analisar_pedidos(conn)
            conn.close()

            # Fechar janela de progresso
            progress_window.destroy()

            if result['success']:
                # Mostrar resultado em uma nova janela
                self.show_insights_window(result)
            else:
                messagebox.showerror(
                    "Erro na Análise",
                    f"❌ Erro ao analisar pedidos:\n\n{result.get('error', 'Erro desconhecido')}"
                )

        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            logging.error(f"Erro ao executar análise: {e}")
            messagebox.showerror(
                "Erro",
                f"❌ Erro ao executar análise:\n\n{str(e)}"
            )

    def show_insights_window(self, result):
        """Mostra os insights da análise em uma janela com rolagem"""
        # Criar janela de resultado
        insights_window = tk.Toplevel(self)
        insights_window.title("📊 Insights de Vendas - Gemini AI")
        insights_window.geometry("750x550")
        insights_window.transient(self)

        # Frame principal
        main_frame = ttk.Frame(insights_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            title_frame,
            text="✨ Análise Inteligente dos Últimos 5 Pedidos",
            font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT)

        ttk.Label(
            title_frame,
            text="Powered by Google Gemini",
            font=("Arial", 8),
            foreground="gray"
        ).pack(side=tk.RIGHT, padx=10)

        # Criar notebook (abas)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Aba 1: Insights
        insights_frame = ttk.Frame(notebook, padding=10)
        notebook.add(insights_frame, text="💡 Insights")

        insights_text = scrolledtext.ScrolledText(
            insights_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#f9f9f9",
            padx=10,
            pady=10
        )
        insights_text.pack(fill=tk.BOTH, expand=True)
        insights_text.insert(1.0, result['insights'])
        insights_text.config(state=tk.DISABLED)

        # Aba 2: Dados Brutos
        data_frame = ttk.Frame(notebook, padding=10)
        notebook.add(data_frame, text="📋 Dados dos Pedidos")

        data_text = scrolledtext.ScrolledText(
            data_frame,
            wrap=tk.WORD,
            font=("Courier", 9),
            bg="#f9f9f9",
            padx=10,
            pady=10
        )
        data_text.pack(fill=tk.BOTH, expand=True)
        data_text.insert(1.0, result.get('resumo', 'Sem dados disponíveis'))
        data_text.config(state=tk.DISABLED)

        # Frame inferior com botões
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))

        # Informação sobre o modelo
        ttk.Label(
            bottom_frame,
            text="Modelo: Gemini 1.5 Flash (Gratuito)",
            font=("Arial", 8),
            foreground="gray"
        ).pack(side=tk.LEFT)

        # Botão copiar
        def copiar_insights():
            insights_window.clipboard_clear()
            insights_window.clipboard_append(result['insights'])
            messagebox.showinfo("Copiado", "✅ Insights copiados para a área de transferência!")

        ttk.Button(
            bottom_frame,
            text="📋 Copiar Insights",
            command=copiar_insights,
            width=18
        ).pack(side=tk.RIGHT, padx=5)

        # Botão fechar
        ttk.Button(
            bottom_frame,
            text="✅ Fechar",
            command=insights_window.destroy,
            width=15
        ).pack(side=tk.RIGHT)

        # Centralizar janela
        insights_window.update_idletasks()
        x = (insights_window.winfo_screenwidth() // 2) - (insights_window.winfo_width() // 2)
        y = (insights_window.winfo_screenheight() // 2) - (insights_window.winfo_height() // 2)
        insights_window.geometry(f"+{x}+{y}")
import tkinter as tk
from tkinter import ttk, messagebox
from db import init_db
from views.dashboard import DashboardFrame
from views.client_list import ClientListFrame
from views.product_list import ProductListFrame
from views.reports import ReportsFrame
from views.history import HistoryFrame  
import logging


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Clientes e Pedidos")
        self.geometry("900x650")
        
        # Controle de alterações não salvas
        self.has_unsaved_changes = False
        
        # Tema atual (claro ou escuro)
        self.current_theme = "claro"
        
        # Configura o estilo ttk
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except tk.TclError:
            logging.warning("Tema 'clam' do ttk não encontrado, usando padrão.")
        
        # Protocolo para fechar a janela
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # NOVO: Cria o Menu Bar
        self.create_menu_bar()
        
        # NOVO: Frame para barra de status
        self.create_status_bar()
        
        # --- Notebook com Abas (MANTIDO EXATAMENTE COMO ESTAVA) ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Bind para detectar mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Aba de Dashboard
        self.dashboard_frame = DashboardFrame(self.notebook)
        self.notebook.add(self.dashboard_frame, text='📊 Dashboard')
        
        # Aba de Clientes
        self.client_frame = ClientListFrame(self.notebook)
        self.notebook.add(self.client_frame, text='👥 Clientes')
        
        # Aba de Produtos
        self.product_frame = ProductListFrame(self.notebook)
        self.notebook.add(self.product_frame, text='📦 Produtos')
        
        # Aba de Relatórios (MANTIDA INTACTA - NÃO MEXEMOS AQUI)
        self.reports_frame = ReportsFrame(self.notebook)
        self.notebook.add(self.reports_frame, text='📈 Relatórios')
        
        # Aba de Histórico (DESCOMENTE SE EXISTIR O ARQUIVO)
        self.history_frame = HistoryFrame(self.notebook)
        self.notebook.add(self.history_frame, text='📜 Histórico')
        
        # Atualiza status inicial
        self.update_status("Sistema iniciado com sucesso")
        
        logging.info("Interface gráfica inicializada com sucesso.")

    def create_menu_bar(self):
        """Cria a barra de menu principal."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo Cliente", command=self.menu_new_client)
        file_menu.add_command(label="Novo Pedido", command=self.menu_new_order)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.on_closing)
        
        # Menu Clientes
        client_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Clientes", menu=client_menu)
        client_menu.add_command(label="Ir para Clientes", command=lambda: self.go_to_tab(1))
        client_menu.add_command(label="Novo Cliente", command=self.menu_new_client)
        
        # Menu Pedidos
        order_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Pedidos", menu=order_menu)
        order_menu.add_command(label="Novo Pedido", command=self.menu_new_order)
        
        # Menu Dashboard
        dashboard_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dashboard", menu=dashboard_menu)
        dashboard_menu.add_command(label="Ir para Dashboard", command=lambda: self.go_to_tab(0))
        dashboard_menu.add_command(label="Atualizar Dashboard", command=self.refresh_dashboard)
        
        # Menu Relatórios
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Relatórios", menu=reports_menu)
        reports_menu.add_command(label="Ir para Relatórios", command=lambda: self.go_to_tab(3))
        reports_menu.add_command(label="Gerar Relatório", command=self.menu_generate_report)
        
        # Menu IA / Análises
        ia_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="IA / Análises", menu=ia_menu)
        ia_menu.add_command(label="Previsão de Vendas", command=self.menu_ia_previsao)
        ia_menu.add_command(label="Análise de Clientes", command=self.menu_ia_clientes)
        ia_menu.add_command(label="Produtos Recomendados", command=self.menu_ia_recomendacoes)
        ia_menu.add_separator()
        ia_menu.add_command(label="Sobre IA", command=self.menu_ia_sobre)
        
        # Menu Visualizar
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizar", menu=view_menu)
        view_menu.add_command(label="Tema Claro", command=self.apply_light_theme)
        view_menu.add_command(label="Tema Escuro", command=self.apply_dark_theme)
        view_menu.add_separator()
        self.status_bar_visible = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(
            label="Barra de Status",
            variable=self.status_bar_visible,
            command=self.toggle_status_bar
        )
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Manual do Usuário", command=self.menu_help_manual)
        help_menu.add_command(label="Atalhos de Teclado", command=self.menu_help_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="Sobre", command=self.menu_help_about)
        
        # Bind de atalhos de teclado
        self.bind_shortcuts()

    def create_status_bar(self):
        """Cria a barra de status na parte inferior."""
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        # Label de status
        self.status_label = ttk.Label(
            self.status_frame,
            text="Pronto",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Label de tema
        self.theme_label = ttk.Label(
            self.status_frame,
            text="Tema: Claro",
            relief=tk.SUNKEN,
            width=15
        )
        self.theme_label.pack(side=tk.RIGHT)

    def bind_shortcuts(self):
        """Vincula atalhos de teclado."""
        # Atalhos de navegação (Ctrl+1 a Ctrl+4)
        self.bind('<Control-Key-1>', lambda e: self.go_to_tab(0))
        self.bind('<Control-Key-2>', lambda e: self.go_to_tab(1))
        self.bind('<Control-Key-3>', lambda e: self.go_to_tab(2))
        self.bind('<Control-Key-4>', lambda e: self.go_to_tab(3))
        
        # Atalhos de ações
        self.bind('<Control-n>', lambda e: self.menu_new_client())
        self.bind('<Control-N>', lambda e: self.menu_new_client())
        self.bind('<Control-p>', lambda e: self.menu_new_order())
        self.bind('<Control-P>', lambda e: self.menu_new_order())
        
        # Alternância rápida de tema
        self.bind('<Control-t>', lambda e: self.toggle_theme())
        self.bind('<Control-T>', lambda e: self.toggle_theme())

    def go_to_tab(self, index):
        """Navega para uma aba específica."""
        try:
            self.notebook.select(index)
            tab_names = ['Dashboard', 'Clientes', 'Produtos', 'Relatórios']
            if index < len(tab_names):
                self.update_status(f"Navegado para: {tab_names[index]}")
        except tk.TclError:
            pass

    def on_tab_changed(self, event):
        """Callback quando a aba é alterada."""
        try:
            current_tab = self.notebook.index(self.notebook.select())
            tab_names = ['Dashboard', 'Clientes', 'Produtos', 'Relatórios']
            if current_tab < len(tab_names):
                self.update_status(f"Visualizando: {tab_names[current_tab]}")
        except:
            pass

    def update_status(self, message):
        """Atualiza a mensagem da barra de status."""
        self.status_label.config(text=f"  {message}")

    def toggle_status_bar(self):
        """Alterna a visibilidade da barra de status."""
        if self.status_bar_visible.get():
            self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        else:
            self.status_frame.pack_forget()

    def apply_light_theme(self):
        """Aplica o tema claro."""
        try:
            self.style.theme_use('clam')
            
            # Cores do tema claro
            self.style.configure('TFrame', background='#f0f0f0')
            self.style.configure('TLabel', background='#f0f0f0', foreground='#000000')
            self.style.configure('TButton', background='#e0e0e0', foreground='#000000')
            self.style.configure('TLabelframe', background='#f0f0f0', foreground='#000000')
            self.style.configure('TLabelframe.Label', background='#f0f0f0', foreground='#000000')
            self.style.configure('Treeview', background='#ffffff', foreground='#000000', fieldbackground='#ffffff')
            self.style.configure('TNotebook', background='#f0f0f0')
            self.style.configure('TNotebook.Tab', background='#e0e0e0', foreground='#000000')
            self.style.map('TNotebook.Tab', background=[('selected', '#ffffff')])
            
            self.configure(bg='#f0f0f0')
            self.current_theme = "claro"
            self.theme_label.config(text="Tema: Claro")
            
            self.update_status("Tema claro aplicado")
            logging.info("Tema claro aplicado.")
            
        except Exception as e:
            logging.error(f"Erro ao aplicar tema claro: {e}")

    def apply_dark_theme(self):
        """Aplica o tema escuro."""
        try:
            self.style.theme_use('clam')
            
            # Cores do tema escuro
            bg_dark = '#2b2b2b'
            fg_light = '#ffffff'
            bg_widget = '#3c3c3c'
            
            self.style.configure('TFrame', background=bg_dark)
            self.style.configure('TLabel', background=bg_dark, foreground=fg_light)
            self.style.configure('TButton', background=bg_widget, foreground=fg_light)
            self.style.configure('TLabelframe', background=bg_dark, foreground=fg_light)
            self.style.configure('TLabelframe.Label', background=bg_dark, foreground=fg_light)
            self.style.configure('Treeview', background=bg_widget, foreground=fg_light, fieldbackground=bg_widget)
            self.style.configure('TNotebook', background=bg_dark)
            self.style.configure('TNotebook.Tab', background=bg_widget, foreground=fg_light)
            self.style.map('TNotebook.Tab', background=[('selected', bg_dark)])
            
            self.configure(bg=bg_dark)
            self.current_theme = "escuro"
            self.theme_label.config(text="Tema: Escuro")
            
            self.update_status("Tema escuro aplicado")
            logging.info("Tema escuro aplicado.")
            
        except Exception as e:
            logging.error(f"Erro ao aplicar tema escuro: {e}")

    def toggle_theme(self):
        """Alterna entre tema claro e escuro."""
        if self.current_theme == "claro":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    # --- Menu Actions ---
    
    def menu_new_client(self):
        """Abre o formulário de novo cliente."""
        self.go_to_tab(1)  # Vai para aba de clientes
        self.update_status("Vá na aba Clientes e clique em 'Novo Cliente'")

    def menu_new_order(self):
        """Abre o formulário de novo pedido."""
        self.update_status("Novo pedido: Selecione um cliente primeiro")
        messagebox.showinfo(
            "Novo Pedido",
            "Para criar um pedido:\n\n"
            "1. Vá na aba 'Clientes'\n"
            "2. Selecione um cliente\n"
            "3. Clique em 'Novo Pedido'",
            parent=self
        )

    def refresh_dashboard(self):
        """Atualiza os dados do dashboard."""
        try:
            if hasattr(self.dashboard_frame, 'load_statistics'):
                self.dashboard_frame.load_statistics()
                self.update_status("Dashboard atualizado")
        except Exception as e:
            logging.error(f"Erro ao atualizar dashboard: {e}")

    def menu_generate_report(self):
        """Vai para a tela de relatórios."""
        self.go_to_tab(3)
        self.update_status("Use os filtros e clique em 'Filtrar' para gerar relatórios")

    def menu_ia_previsao(self):
        """Menu IA: Previsão de Vendas."""
        messagebox.showinfo(
            "Previsão de Vendas",
            "Funcionalidade de IA para previsão de vendas.\n\n"
            "Em desenvolvimento...",
            parent=self
        )

    def menu_ia_clientes(self):
        """Menu IA: Análise de Clientes."""
        messagebox.showinfo(
            "Análise de Clientes",
            "Funcionalidade de IA para análise de comportamento.\n\n"
            "Em desenvolvimento...",
            parent=self
        )

    def menu_ia_recomendacoes(self):
        """Menu IA: Recomendação de Produtos."""
        messagebox.showinfo(
            "Recomendação de Produtos",
            "Funcionalidade de IA para recomendar produtos.\n\n"
            "Em desenvolvimento...",
            parent=self
        )

    def menu_ia_sobre(self):
        """Menu IA: Sobre."""
        messagebox.showinfo(
            "Sobre IA / Análises",
            "Sistema de Inteligência Artificial\n\n"
            "Recursos planejados:\n"
            "• Previsão de vendas\n"
            "• Análise comportamental\n"
            "• Sistema de recomendações\n\n"
            "Status: Em desenvolvimento",
            parent=self
        )

    def menu_help_manual(self):
        """Menu Ajuda: Manual."""
        messagebox.showinfo(
            "Manual do Usuário",
            "MANUAL DO SISTEMA\n\n"
            "Dashboard: Visão geral com estatísticas\n"
            "Clientes: Gerenciar clientes\n"
            "Produtos: Gerenciar produtos\n"
            "Relatórios: Gerar relatórios CSV/PDF\n\n"
            "Use os menus e atalhos para navegar!",
            parent=self
        )

    def menu_help_shortcuts(self):
        """Menu Ajuda: Atalhos."""
        messagebox.showinfo(
            "Atalhos de Teclado",
            "ATALHOS DISPONÍVEIS\n\n"
            "Ctrl+1 - Dashboard\n"
            "Ctrl+2 - Clientes\n"
            "Ctrl+3 - Produtos\n"
            "Ctrl+4 - Relatórios\n\n"
            "Ctrl+N - Novo Cliente\n"
            "Ctrl+P - Novo Pedido\n"
            "Ctrl+T - Alternar Tema",
            parent=self
        )

    def menu_help_about(self):
        """Menu Ajuda: Sobre."""
        messagebox.showinfo(
            "Sobre o Sistema",
            "SISTEMA DE CLIENTES E PEDIDOS\n\n"
            "Versão: 1.0.0\n\n"
            "Funcionalidades:\n"
            "✓ Gestão de Clientes\n"
            "✓ Gestão de Produtos\n"
            "✓ Registro de Pedidos\n"
            "✓ Dashboard Analítico\n"
            "✓ Relatórios (CSV/PDF)\n"
            "✓ Temas Claro/Escuro\n\n"
            "© 2025",
            parent=self
        )

    def on_closing(self):
        """Trata o fechamento da aplicação."""
        if self.has_unsaved_changes:
            result = messagebox.askyesnocancel(
                "Alterações não Salvas",
                "Existem alterações não salvas.\n\n"
                "Deseja salvar antes de sair?",
                parent=self
            )
            
            if result is True:
                messagebox.showinfo("Salvar", "Alterações salvas!", parent=self)
                self.has_unsaved_changes = False
                self.quit_application()
            elif result is False:
                self.quit_application()
        else:
            if messagebox.askyesno(
                "Confirmar Saída",
                "Deseja realmente sair do sistema?",
                parent=self
            ):
                self.quit_application()

    def quit_application(self):
        """Encerra a aplicação."""
        logging.info("Aplicação encerrada pelo usuário.")
        self.destroy()


if __name__ == "__main__":
    # Configuração de log com encoding UTF-8
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    logging.info("="*60)
    logging.info("Iniciando a aplicação...")
    logging.info("="*60)

    try:
        # Inicializa o banco de dados
        init_db()

        # Inicia a aplicação
        app = MainApplication()
        app.mainloop()

    except Exception as e:
        logging.critical(f"Erro fatal ao iniciar a aplicação: {e}")
        print(f"Erro fatal: {e}")
    finally:
        logging.info("="*60)
        logging.info("Aplicação encerrada.")
        logging.info("="*60)
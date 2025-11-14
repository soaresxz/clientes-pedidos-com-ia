import tkinter as tk
from tkinter import ttk, messagebox
from db import get_db_connection
from models import get_all_clients
import logging
from datetime import datetime
import csv
import os
import platform
import subprocess
import sys

# Importações para PDF (reportlab)
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab não está instalado. Exportação para PDF não estará disponível.")


class ReportsFrame(ttk.Frame):
    """
    Frame para gerar relatórios de pedidos com filtros e exportação.
    """

    def __init__(self, parent):
        super().__init__(parent, padding="10")
        self.parent = parent

        # Dados dos pedidos filtrados
        self.filtered_orders = []

        self.create_widgets()
        self.load_clients_for_filter()

    def create_widgets(self):
        # Título
        title_label = ttk.Label(
            self,
            text="📊 Relatórios de Pedidos",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 15))

        # --- Frame de Filtros ---
        filter_frame = ttk.LabelFrame(self, text="Filtros", padding=15)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # Grid para organizar filtros
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)

        # Data Inicial
        ttk.Label(filter_frame, text="Data Inicial:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.data_inicial_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.data_inicial_var, width=12).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W
        )
        ttk.Label(filter_frame, text="(DD/MM/AAAA)", font=("Arial", 8), foreground="gray").grid(
            row=0, column=1, padx=(90, 5), pady=5, sticky=tk.W
        )

        # Data Final
        ttk.Label(filter_frame, text="Data Final:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky=tk.W)
        self.data_final_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.data_final_var, width=12).grid(
            row=0, column=3, padx=5, pady=5, sticky=tk.W
        )
        ttk.Label(filter_frame, text="(DD/MM/AAAA)", font=("Arial", 8), foreground="gray").grid(
            row=0, column=3, padx=(90, 5), pady=5, sticky=tk.W
        )

        # Cliente (Combobox)
        ttk.Label(filter_frame, text="Cliente:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_combo = ttk.Combobox(filter_frame, state="readonly")
        self.client_combo.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=tk.EW)

        # Botões de Ação
        button_frame = ttk.Frame(filter_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=(10, 0))

        ttk.Button(button_frame, text="🔍 Filtrar", command=self.apply_filters, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Limpar Filtros", command=self.clear_filters, width=15).pack(side=tk.LEFT, padx=5)

        # --- Treeview de Resultados ---
        tree_frame = ttk.LabelFrame(self, text="Pedidos Encontrados", padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Colunas: ID, Cliente, Data, Total, Qtd Itens
        cols = ('id', 'cliente', 'data', 'total', 'itens')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=12)

        self.tree.heading('id', text='ID')
        self.tree.heading('cliente', text='Cliente')
        self.tree.heading('data', text='Data')
        self.tree.heading('total', text='Total (R$)')
        self.tree.heading('itens', text='Qtd Itens')

        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('cliente', width=250)
        self.tree.column('data', width=100, anchor=tk.CENTER)
        self.tree.column('total', width=100, anchor=tk.E)
        self.tree.column('itens', width=80, anchor=tk.CENTER)

        # Scrollbars
        ysb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        xsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)

        ysb.pack(side=tk.RIGHT, fill=tk.Y)
        xsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind duplo clique para ver detalhes
        self.tree.bind("<Double-1>", self.show_order_details)

        # --- Frame de Exportação ---
        export_frame = ttk.Frame(self)
        export_frame.pack(fill=tk.X, pady=(0, 10))

        # Label de status
        self.status_label = ttk.Label(export_frame, text="", foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Botões de Exportação
        self.export_csv_btn = ttk.Button(
            export_frame,
            text="📄 Exportar CSV",
            command=self.export_to_csv,
            state=tk.DISABLED
        )
        self.export_csv_btn.pack(side=tk.RIGHT, padx=5)

        self.export_pdf_btn = ttk.Button(
            export_frame,
            text="📑 Exportar PDF",
            command=self.export_to_pdf,
            state=tk.DISABLED if not REPORTLAB_AVAILABLE else tk.NORMAL
        )
        self.export_pdf_btn.pack(side=tk.RIGHT, padx=5)

        if not REPORTLAB_AVAILABLE:
            ttk.Label(
                export_frame,
                text="⚠️ ReportLab não instalado. Instale com: pip install reportlab",
                foreground="red",
                font=("Arial", 8)
            ).pack(side=tk.RIGHT, padx=10)

    def load_clients_for_filter(self):
        """Carrega os clientes para o combobox de filtro."""
        try:
            clients = get_all_clients()
            client_names = ["Todos os Clientes"] + [client['nome'] for client in clients]
            
            # Mapa Nome -> ID
            self.clients_map = {client['nome']: client['id'] for client in clients}
            
            self.client_combo['values'] = client_names
            self.client_combo.set("Todos os Clientes")
            
            logging.info("Clientes carregados para filtro de relatórios.")
        except Exception as e:
            logging.error(f"Erro ao carregar clientes para filtro: {e}")
            messagebox.showerror("Erro", f"Não foi possível carregar clientes:\n{e}", parent=self)

    def apply_filters(self):
        """Aplica os filtros e busca os pedidos no banco de dados."""
        try:
            # Validar e converter datas
            data_inicial = self.data_inicial_var.get().strip()
            data_final = self.data_final_var.get().strip()
            
            data_inicial_iso = None
            data_final_iso = None
            
            if data_inicial:
                data_inicial_iso = self.convert_date_to_iso(data_inicial)
            
            if data_final:
                data_final_iso = self.convert_date_to_iso(data_final)
            
            # Validar que data inicial não seja posterior à final
            if data_inicial_iso and data_final_iso and data_inicial_iso > data_final_iso:
                messagebox.showerror(
                    "Erro de Data",
                    "A data inicial não pode ser posterior à data final.",
                    parent=self
                )
                return
            
            # Pegar cliente selecionado
            cliente_nome = self.client_combo.get()
            cliente_id = None
            
            if cliente_nome != "Todos os Clientes":
                cliente_id = self.clients_map.get(cliente_nome)
            
            # Buscar pedidos no banco
            self.filtered_orders = self.fetch_orders(data_inicial_iso, data_final_iso, cliente_id)
            
            # Atualizar Treeview
            self.populate_tree(self.filtered_orders)
            
            # Atualizar status e botões
            self.status_label.config(text=f"✅ {len(self.filtered_orders)} pedido(s) encontrado(s)")
            
            if self.filtered_orders:
                self.export_csv_btn.config(state=tk.NORMAL)
                if REPORTLAB_AVAILABLE:
                    self.export_pdf_btn.config(state=tk.NORMAL)
            else:
                self.export_csv_btn.config(state=tk.DISABLED)
                self.export_pdf_btn.config(state=tk.DISABLED)
            
            logging.info(f"Filtros aplicados: {len(self.filtered_orders)} pedidos encontrados.")
            
        except ValueError as e:
            messagebox.showerror("Erro de Data", str(e), parent=self)
        except Exception as e:
            logging.error(f"Erro ao aplicar filtros: {e}")
            messagebox.showerror("Erro", f"Erro ao buscar pedidos:\n{e}", parent=self)

    def convert_date_to_iso(self, date_str):
        """Converte data DD/MM/AAAA para formato ISO AAAA-MM-DD."""
        try:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Data inválida: '{date_str}'. Use o formato DD/MM/AAAA.")

    def fetch_orders(self, data_inicial, data_final, cliente_id):
        """Busca pedidos no banco de dados com os filtros aplicados."""
        conn = get_db_connection()
        if not conn:
            raise Exception("Não foi possível conectar ao banco de dados.")
        
        cursor = conn.cursor()
        
        # Construir query dinâmica
        query = """
            SELECT 
                p.id,
                c.nome as cliente,
                p.data,
                p.total,
                COUNT(ip.id) as qtd_itens
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            LEFT JOIN itens_pedido ip ON p.id = ip.pedido_id
        """
        
        conditions = []
        params = []
        
        if data_inicial:
            conditions.append("p.data >= ?")
            params.append(data_inicial)
        
        if data_final:
            conditions.append("p.data <= ?")
            params.append(data_final)
        
        if cliente_id:
            conditions.append("p.cliente_id = ?")
            params.append(cliente_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " GROUP BY p.id ORDER BY p.data DESC, p.id DESC"
        
        cursor.execute(query, params)
        orders = cursor.fetchall()
        conn.close()
        
        return orders

    def populate_tree(self, orders):
        """Preenche o Treeview com os pedidos filtrados."""
        # Limpar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar pedidos
        for order in orders:
            # Converter data ISO para DD/MM/AAAA
            data_formatada = self.format_date_from_iso(order['data'])
            
            self.tree.insert('', tk.END, iid=order['id'], values=(
                order['id'],
                order['cliente'],
                data_formatada,
                f"{order['total']:.2f}",
                order['qtd_itens']
            ))

    def format_date_from_iso(self, date_iso):
        """Converte data ISO AAAA-MM-DD para DD/MM/AAAA."""
        try:
            dt = datetime.strptime(date_iso, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except:
            return date_iso

    def show_order_details(self, event=None):
        """Mostra os detalhes (itens) de um pedido selecionado."""
        try:
            selected_item = self.tree.selection()[0]
            order_id = selected_item
        except IndexError:
            return
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Buscar itens do pedido
            cursor.execute("""
                SELECT produto, quantidade, preco_unit, (quantidade * preco_unit) as subtotal
                FROM itens_pedido
                WHERE pedido_id = ?
                ORDER BY produto
            """, (order_id,))
            
            items = cursor.fetchall()
            conn.close()
            
            # Montar mensagem
            order_values = self.tree.item(order_id, 'values')
            message = f"📦 Pedido #{order_values[0]}\n"
            message += f"Cliente: {order_values[1]}\n"
            message += f"Data: {order_values[2]}\n"
            message += f"Total: R$ {order_values[3]}\n\n"
            message += "=" * 50 + "\n"
            message += "ITENS DO PEDIDO:\n"
            message += "=" * 50 + "\n\n"
            
            for item in items:
                message += f"• {item['produto']}\n"
                message += f"  Qtd: {item['quantidade']} x R$ {item['preco_unit']:.2f} = R$ {item['subtotal']:.2f}\n\n"
            
            messagebox.showinfo("Detalhes do Pedido", message, parent=self)
            
        except Exception as e:
            logging.error(f"Erro ao buscar detalhes do pedido: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar detalhes:\n{e}", parent=self)

    def clear_filters(self):
        """Limpa todos os filtros e o resultado."""
        self.data_inicial_var.set("")
        self.data_final_var.set("")
        self.client_combo.set("Todos os Clientes")
        
        # Limpar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.filtered_orders = []
        self.status_label.config(text="")
        self.export_csv_btn.config(state=tk.DISABLED)
        self.export_pdf_btn.config(state=tk.DISABLED)
        
        logging.info("Filtros de relatório limpos.")

    def export_to_csv(self):
        """Exporta os pedidos filtrados para arquivo CSV."""
        if not self.filtered_orders:
            messagebox.showwarning("Sem Dados", "Não há pedidos para exportar.", parent=self)
            return
        
        try:
            # Gerar nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_pedidos_{timestamp}.csv"
            
            # Escrever CSV
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # Cabeçalho
                writer.writerow(['ID Pedido', 'Cliente', 'Data', 'Total (R$)', 'Qtd Itens'])
                
                # Dados
                for order in self.filtered_orders:
                    data_formatada = self.format_date_from_iso(order['data'])
                    writer.writerow([
                        order['id'],
                        order['cliente'],
                        data_formatada,
                        f"{order['total']:.2f}",
                        order['qtd_itens']
                    ])
            
            logging.info(f"Relatório CSV exportado: {filename}")
            messagebox.showinfo(
                "Exportação Concluída",
                f"✅ Relatório exportado com sucesso!\n\nArquivo: {filename}",
                parent=self
            )
            
            # Abrir arquivo
            self.open_file(filename)
            
        except Exception as e:
            logging.error(f"Erro ao exportar CSV: {e}")
            messagebox.showerror("Erro", f"Erro ao exportar CSV:\n{e}", parent=self)

    def export_to_pdf(self):
        """Exporta os pedidos filtrados para arquivo PDF."""
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror(
                "ReportLab Não Disponível",
                "Para exportar PDF, instale o ReportLab:\npip install reportlab",
                parent=self
            )
            return
        
        if not self.filtered_orders:
            messagebox.showwarning("Sem Dados", "Não há pedidos para exportar.", parent=self)
            return
        
        try:
            # Gerar nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_pedidos_{timestamp}.pdf"
            
            # Criar documento PDF
            doc = SimpleDocTemplate(filename, pagesize=A4)
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2c3e50'),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            # Título
            title = Paragraph("📊 Relatório de Pedidos", title_style)
            elements.append(title)
            
            # Data de geração
            date_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}"
            elements.append(Paragraph(date_text, styles['Normal']))
            elements.append(Spacer(1, 0.5*cm))
            
            # Filtros aplicados
            filters_text = "Filtros aplicados: "
            if self.data_inicial_var.get():
                filters_text += f"Data Inicial: {self.data_inicial_var.get()} | "
            if self.data_final_var.get():
                filters_text += f"Data Final: {self.data_final_var.get()} | "
            if self.client_combo.get() != "Todos os Clientes":
                filters_text += f"Cliente: {self.client_combo.get()}"
            
            elements.append(Paragraph(filters_text, styles['Normal']))
            elements.append(Spacer(1, 0.5*cm))
            
            # Tabela de dados
            data = [['ID', 'Cliente', 'Data', 'Total (R$)', 'Itens']]
            
            total_geral = 0
            for order in self.filtered_orders:
                data_formatada = self.format_date_from_iso(order['data'])
                data.append([
                    str(order['id']),
                    order['cliente'],
                    data_formatada,
                    f"R$ {order['total']:.2f}",
                    str(order['qtd_itens'])
                ])
                total_geral += order['total']
            
            # Linha de total
            data.append(['', '', 'TOTAL GERAL:', f"R$ {total_geral:.2f}", ''])
            
            # Criar tabela
            table = Table(data, colWidths=[2*cm, 6*cm, 3*cm, 3*cm, 2*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e9')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 1*cm))
            
            # Rodapé
            footer = Paragraph(
                f"Total de pedidos: {len(self.filtered_orders)} | Valor total: R$ {total_geral:.2f}",
                styles['Normal']
            )
            elements.append(footer)
            
            # Construir PDF
            doc.build(elements)
            
            logging.info(f"Relatório PDF exportado: {filename}")
            messagebox.showinfo(
                "Exportação Concluída",
                f"✅ Relatório PDF gerado com sucesso!\n\nArquivo: {filename}",
                parent=self
            )
            
            # Abrir arquivo
            self.open_file(filename)
            
        except Exception as e:
            logging.error(f"Erro ao exportar PDF: {e}")
            messagebox.showerror("Erro", f"Erro ao exportar PDF:\n{e}", parent=self)

    def open_file(self, filepath):
        """Abre o arquivo gerado no programa padrão do sistema."""
        try:
            system = platform.system()
            
            if system == 'Windows':
                os.startfile(filepath)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
            
            logging.info(f"Arquivo aberto: {filepath}")
        except Exception as e:
            logging.warning(f"Não foi possível abrir o arquivo automaticamente: {e}")
            messagebox.showinfo(
                "Arquivo Salvo",
                f"O arquivo foi salvo mas não pôde ser aberto automaticamente.\n\nLocalização: {os.path.abspath(filepath)}",
                parent=self
            )
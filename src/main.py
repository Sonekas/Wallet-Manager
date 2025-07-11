import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from asset_registration import AssetRegistrationWindow
from database_manager import DatabaseManager
from yfinance_integration import YFinanceIntegration
from report_generator import ReportGenerator
from logger import log_message
from plot_manager import PlotManager
from risk_analysis import RiskAnalysis
from projection_simulation import ProjectionSimulation
from alert_manager import AlertManagerWindow
from event_calendar import EventCalendarWindow
import datetime
import threading
import time



class InvestmentCarteiraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("App de Controle e Automação de Carteira de Investimentos")

        self.db = DatabaseManager()
        self.yf_integration = YFinanceIntegration()
        self.report_gen = ReportGenerator()
        self.plot_m = PlotManager()
        self.risk_analysis = RiskAnalysis(self.db, self.yf_integration)
        self.projection_simulation = ProjectionSimulation(self.db, self.yf_integration)
        self.create_widgets()
        self.load_assets_from_db()

        # Configurar atualização em segundo plano
        self.update_interval_minutes = 5 # Atualizar a cada 5 minutos
        self.schedule_background_update()

        self.current_theme = "clam" # Tema claro como padrão
        self.apply_theme(self.current_theme)

    def create_widgets(self):
        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opções", menu=options_menu)

        theme_menu = tk.Menu(options_menu, tearoff=0)
        options_menu.add_cascade(label="Tema", menu=theme_menu)
        theme_menu.add_command(label="Tema Claro (Branco)", command=lambda: self.apply_theme("clam"))
        theme_menu.add_command(label="Tema Escuro (Preto)", command=lambda: self.apply_theme("alt"))
        
        # Adicionar separador e opção de ajuda
        options_menu.add_separator()
        options_menu.add_command(label="Ajuda", command=self.show_help)

                # Frame para os botões - Layout responsivo com tamanho fixo
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill="x", expand=False)
        
        # Lista de botões para facilitar o layout
        buttons = [
            ("Cadastrar Ativo", self.register_asset),
            ("Atualizar Cotações", self.update_quotes),
            ("Gerar Relatório", self.generate_report),
            ("Atualizar Tudo", self.update_all),
            ("Backup DB", self.backup_db),
            ("Restaurar DB", self.restore_db),
            ("Exportar Dados", self.export_data),
            ("Importar Dados", self.import_data),
            ("Análise de Risco", self.perform_risk_analysis),
            ("Comparar c/ Benchmark", self.compare_with_benchmark),
            ("Projeções/Simulações", self.perform_projection_simulation),
            ("Gerenciar Alertas", self.manage_alerts),
            ("Calendário de Eventos", self.open_event_calendar),
            ("Editar Ativo", self.edit_asset),
            ("Excluir Ativo", self.delete_asset)
        ]

        # Criar botões com tamanho fixo
        self.button_widgets = []
        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command, width=20)
            self.button_widgets.append(btn)
            
        # Armazenar referência ao frame para redimensionamento
        self.button_frame = button_frame
        
        # Layout inicial
        self._update_button_layout()
        
        # Vincular evento de redimensionamento da janela
        self.root.bind("<Configure>", self.on_window_resize)
        self._resize_timer = None

        # Frame para pesquisa e filtragem - Layout responsivo
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.pack(fill="x", expand=False)

        # Configurar grid para pesquisa
        search_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Pesquisar Ativo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.search_entry.bind("<Return>", self.apply_filter)

        btn_search = ttk.Button(search_frame, text="Filtrar", command=self.apply_filter)
        btn_search.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Tabela de exibição de ativos
        self.tree = ttk.Treeview(self.root, columns=("nome", "tipo", "quantidade", "preco_medio", "preco_atual", "valor_investido", "valor_atual", "rentabilidade"), show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.heading("nome", text="Nome do Ativo")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("quantidade", text="Quantidade")
        self.tree.heading("preco_medio", text="Preço Médio")
        self.tree.heading("preco_atual", text="Preço Atual")
        self.tree.heading("valor_investido", text="Valor Investido")
        self.tree.heading("valor_atual", text="Valor Atual")
        self.tree.heading("rentabilidade", text="Rentabilidade (%)")

        for col in ("nome", "tipo", "quantidade", "preco_medio", "preco_atual", "valor_investido", "valor_atual", "rentabilidade"):
            self.tree.column(col, anchor="center")

        self.tree.bind("<Double-1>", self.on_asset_double_click)

    def on_window_resize(self, event):
        """Reorganiza os botões conforme o tamanho da janela"""
        if hasattr(self, 'button_frame') and event.widget == self.root:
            # Aguardar um pouco para evitar muitas atualizações
            if self._resize_timer:
                self.root.after_cancel(self._resize_timer)
            self._resize_timer = self.root.after(50, self._update_button_layout)
    
    def _update_button_layout(self):
        """Atualiza o layout dos botões com tamanho fixo e quebra automática de linha, sem espaço extra"""
        if not hasattr(self, 'button_frame') or not hasattr(self, 'button_widgets'):
            return
        
        # Limpar todos os widgets do frame
        for widget in self.button_frame.winfo_children():
            widget.grid_forget()
        
        # Obter largura disponível
        available_width = self.button_frame.winfo_width() - 20
        if available_width <= 0:
            available_width = self.root.winfo_width() - 40
        
        # Tamanho fixo do botão
        button_width = 160
        button_padding = 8
        total_button_width = button_width + button_padding
        
        # Calcular quantos botões cabem por linha
        buttons_per_row = max(1, available_width // total_button_width)
        total_buttons = len(self.button_widgets)
        total_rows = (total_buttons + buttons_per_row - 1) // buttons_per_row
        
        # Limpar configurações de coluna
        for col in range(20):
            self.button_frame.grid_columnconfigure(col, weight=0)
        
        # Configurar colunas para distribuição uniforme
        for col in range(buttons_per_row):
            self.button_frame.grid_columnconfigure(col, weight=1)
        
        # Posicionar botões
        for i, button in enumerate(self.button_widgets):
            row = i // buttons_per_row
            col = i % buttons_per_row
            button.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
        
        # Configurar linhas
        for row in range(total_rows):
            self.button_frame.grid_rowconfigure(row, weight=0)

    def show_help(self):
        """Exibe a janela de ajuda com explicações de todas as funcionalidades"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Ajuda - App de Carteira de Investimentos")
        help_window.geometry("800x600")
        help_window.resizable(True, True)
        
        # Criar frame com scrollbar
        main_frame = ttk.Frame(help_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título
        title_label = ttk.Label(scrollable_frame, text="Guia de Uso - App de Carteira de Investimentos", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Seções de ajuda
        sections = [
            {
                "title": "📊 Cadastro e Gestão de Ativos",
                "items": [
                    ("Cadastrar Ativo", "Adiciona um novo ativo à sua carteira. Permite informar ticker, tipo, quantidade, preço e data da transação."),
                    ("Editar Ativo", "Modifica informações de um ativo existente. Selecione o ativo na tabela antes de usar."),
                    ("Excluir Ativo", "Remove um ativo e todas suas transações da carteira. Selecione o ativo na tabela antes de usar.")
                ]
            },
            {
                "title": "📈 Atualização de Dados",
                "items": [
                    ("Atualizar Cotações", "Busca preços atuais de todos os ativos da carteira via Yahoo Finance."),
                    ("Atualizar Tudo", "Executa atualização de cotações e gera relatórios automaticamente.")
                ]
            },
            {
                "title": "📋 Relatórios e Exportação",
                "items": [
                    ("Gerar Relatório", "Cria relatórios em Excel e PDF com resumo completo da carteira."),
                    ("Exportar Dados", "Exporta todos os dados da carteira em formato CSV ou JSON."),
                    ("Importar Dados", "Importa dados de carteira de arquivos CSV ou JSON.")
                ]
            },
            {
                "title": "💾 Backup e Restauração",
                "items": [
                    ("Backup DB", "Cria uma cópia de segurança do banco de dados com timestamp."),
                    ("Restaurar DB", "Restaura o banco de dados a partir de um arquivo de backup.")
                ]
            },
            {
                "title": "📊 Análise e Projeções",
                "items": [
                    ("Análise de Risco", "Calcula volatilidade e Beta de um ativo selecionado."),
                    ("Comparar c/ Benchmark", "Compara performance de um ativo com um benchmark (ex: Ibovespa)."),
                    ("Projeções/Simulações", "Executa simulações de Monte Carlo e projeções lineares da carteira.")
                ]
            },
            {
                "title": "🔔 Alertas e Eventos",
                "items": [
                    ("Gerenciar Alertas", "Configura alertas de preço e variação percentual para ativos."),
                    ("Calendário de Eventos", "Gerencia eventos importantes como dividendos, vencimentos e desdobramentos.")
                ]
            },
            {
                "title": "🔍 Pesquisa e Filtros",
                "items": [
                    ("Campo de Pesquisa", "Digite o nome ou tipo do ativo para filtrar a tabela. Pressione Enter para aplicar."),
                    ("Filtrar", "Aplica o filtro de pesquisa na tabela de ativos.")
                ]
            },
            {
                "title": "🎨 Personalização",
                "items": [
                    ("Tema Claro (Branco)", "Aplica tema claro com fundo branco e texto escuro."),
                    ("Tema Escuro (Preto)", "Aplica tema escuro com fundo preto e texto claro.")
                ]
            },
            {
                "title": "📊 Tipos de Ativos Suportados",
                "items": [
                    ("Ações", "Ações brasileiras e estrangeiras. Cotação automática via Yahoo Finance. Ex: PETR4, VALE3, AAPL."),
                    ("FIIs", "Fundos Imobiliários. Cotação automática via Yahoo Finance. Ex: MXRF11, HGLG11, XPML11."),
                    ("ETFs", "Fundos de Índice. Cotação automática via Yahoo Finance. Ex: BOVA11, SMAL11, IVVB11."),
                    ("Tesouro Direto", "Títulos do Tesouro Nacional. Cadastro manual (sem cotação automática). Ex: SELIC, IPCA, IGPM."),
                    ("Outros", "CDBs, LCIs, LCAs e outros ativos. Cadastro manual com controle de posições.")
                ]
            },
            {
                "title": "💡 Dicas de Uso",
                "items": [
                    ("Formato de Data", "Use DD/MM/AAAA para todas as datas (ex: 15/01/2024)."),
                    ("Tickers", "Para ações brasileiras, use o ticker sem .SA (ex: PETR4, VALE3)."),
                    ("Clique Duplo", "Clique duplo em um ativo na tabela para ver gráfico de histórico de preços."),
                    ("Layout Responsivo", "Redimensione a janela para ver os botões se reorganizarem automaticamente."),
                    ("Tesouro Direto", "Para títulos do Tesouro, insira preços manualmente quando houver atualizações.")
                ]
            }
        ]
        
        # Criar conteúdo das seções
        for section in sections:
            # Título da seção
            section_title = ttk.Label(scrollable_frame, text=section["title"], 
                                     font=("Arial", 12, "bold"))
            section_title.pack(anchor="w", pady=(20, 10))
            
            # Itens da seção
            for item_title, item_desc in section["items"]:
                item_frame = ttk.Frame(scrollable_frame)
                item_frame.pack(fill="x", pady=5, padx=20)
                
                item_title_label = ttk.Label(item_frame, text=f"• {item_title}:", 
                                           font=("Arial", 10, "bold"))
                item_title_label.pack(anchor="w")
                
                item_desc_label = ttk.Label(item_frame, text=f"  {item_desc}", 
                                          font=("Arial", 9), wraplength=700)
                item_desc_label.pack(anchor="w", padx=(20, 0))
        
        # Botão de fechar
        close_button = ttk.Button(scrollable_frame, text="Fechar", 
                                 command=help_window.destroy)
        close_button.pack(pady=20)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar tema da janela de ajuda
        if hasattr(self, 'current_theme'):
            if self.current_theme == "alt":
                help_window.configure(bg='#2d2d2d')
                style = ttk.Style()
                style.configure("TLabel", background="#2d2d2d", foreground="#ffffff")
                style.configure("TButton", background="#404040", foreground="#ffffff")

    def apply_theme(self, theme_name):
        try:
            style = ttk.Style()
            
            if theme_name == "clam":
                # Tema Claro - Fundo claro, texto escuro
                style.theme_use("clam")
                self.root.configure(bg='#f5f5f5')
                
                # Configurar todos os widgets para tema claro
                style.configure("TFrame", background="#f5f5f5")
                style.configure("TLabel", background="#f5f5f5", foreground="#000000")
                style.configure("TButton", background="#e1e1e1", foreground="#000000")
                style.configure("TEntry", fieldbackground="#ffffff", foreground="#000000")
                style.configure("TCombobox", fieldbackground="#ffffff", foreground="#000000")
                style.configure("Treeview", background="#ffffff", foreground="#000000", fieldbackground="#ffffff")
                style.configure("Treeview.Heading", background="#e1e1e1", foreground="#000000")
                
            elif theme_name == "alt":
                # Tema Escuro - Fundo escuro, texto claro
                style.theme_use("clam")
                self.root.configure(bg='#2d2d2d')
                
                # Configurar todos os widgets para tema escuro
                style.configure("TFrame", background="#2d2d2d")
                style.configure("TLabel", background="#2d2d2d", foreground="#ffffff")
                style.configure("TButton", background="#404040", foreground="#ffffff")
                style.configure("TEntry", fieldbackground="#404040", foreground="#ffffff")
                style.configure("TCombobox", fieldbackground="#404040", foreground="#ffffff")
                style.configure("Treeview", background="#404040", foreground="#ffffff", fieldbackground="#404040")
                style.configure("Treeview.Heading", background="#2d2d2d", foreground="#ffffff")
                
            else:
                style.theme_use("clam")
                self.root.configure(bg='#f5f5f5')
                style.configure("TFrame", background="#f5f5f5")
                style.configure("TLabel", background="#f5f5f5", foreground="#000000")
                style.configure("TButton", background="#e1e1e1", foreground="#000000")
                style.configure("TEntry", fieldbackground="#ffffff", foreground="#000000")
                style.configure("TCombobox", fieldbackground="#ffffff", foreground="#000000")
                style.configure("Treeview", background="#ffffff", foreground="#000000", fieldbackground="#ffffff")
                style.configure("Treeview.Heading", background="#e1e1e1", foreground="#000000")
                theme_name = "clam"
            
            self.current_theme = theme_name
            log_message(f"Tema alterado para: {theme_name}")
        except Exception as e:
            # Em caso de erro, usar tema padrão
            style = ttk.Style()
            style.theme_use("default")
            self.current_theme = "default"
            log_message(f"Erro ao aplicar tema {theme_name}, usando tema padrão: {e}")

    def register_asset(self):
        AssetRegistrationWindow(self.root, self.load_assets_from_db)

    def edit_asset(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Editar Ativo", "Selecione um ativo na tabela para editar.")
            return

        asset_name = self.tree.item(selected_item[0], "values")[0]
        asset_id = self.asset_details_map.get(asset_name)

        if asset_id:
            # Recuperar os dados completos do ativo para preencher o formulário de edição
            asset_data = self.db.get_asset_by_id(asset_id)
            if asset_data:
                # Abrir uma nova janela ou usar a mesma janela de registro para edição
                # Por simplicidade, vamos usar simpledialog para alguns campos, mas o ideal seria uma janela dedicada
                new_name = simpledialog.askstring("Editar Ativo", "Novo nome do ativo:", initialvalue=asset_data[1], parent=self.root)
                new_type = simpledialog.askstring("Editar Ativo", "Novo tipo do ativo:", initialvalue=asset_data[2], parent=self.root)

                if new_name and new_type:
                    if self.db.update_asset(asset_id, new_name, new_type):
                        messagebox.showinfo("Editar Ativo", "Ativo atualizado com sucesso!")
                        log_message(f"Ativo {asset_name} atualizado para {new_name}.")
                        self.load_assets_from_db()
                    else:
                        messagebox.showerror("Editar Ativo", "Erro ao atualizar ativo.")
                        log_message(f"Erro ao atualizar ativo {asset_name}.")
                else:
                    messagebox.showwarning("Editar Ativo", "Edição cancelada ou dados inválidos.")
            else:
                messagebox.showerror("Erro", "Não foi possível carregar os dados do ativo para edição.")
        else:
            messagebox.showerror("Erro", "Ativo não encontrado para edição.")

    def delete_asset(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Excluir Ativo", "Selecione um ativo na tabela para excluir.")
            return

        asset_name = self.tree.item(selected_item[0], "values")[0]
        asset_id = self.asset_details_map.get(asset_name)

        if asset_id:
            confirm = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o ativo {asset_name} e todas as suas transações e histórico de preços?")
            if confirm:
                if self.db.delete_asset(asset_id):
                    messagebox.showinfo("Excluir Ativo", "Ativo excluído com sucesso!")
                    log_message(f"Ativo {asset_name} excluído.")
                    self.load_assets_from_db()
                else:
                    messagebox.showerror("Excluir Ativo", "Erro ao excluir ativo.")
                    log_message(f"Erro ao excluir ativo {asset_name}.")
        else:
            messagebox.showerror("Erro", "Ativo não encontrado para exclusão.")

    def load_assets_from_db(self, filter_text=""):
        # Limpar a treeview antes de carregar os dados
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.current_carteira_data = [] # Para armazenar os dados para o relatório
        self.asset_details_map = {} # Para mapear o nome do ativo para o ID para buscar histórico
        total_invested_carteira = 0.0
        total_current_value_carteira = 0.0

        assets = self.db.get_all_assets_with_transactions()
        for asset in assets:
            asset_id, name, asset_type, total_quantity, total_invested_cost = asset
            
            # Aplicar filtro
            if filter_text and filter_text.lower() not in name.lower() and filter_text.lower() not in asset_type.lower():
                continue

            self.asset_details_map[name] = asset_id
            
            current_price = self.yf_integration.get_current_price(name + ".SA")
            if current_price is None:
                current_price = 0.0
            
            # Salvar histórico de preço
            today = datetime.date.today().strftime("%Y-%m-%d")
            self.db.add_price_history(asset_id, current_price, today)

            # Calcular preço médio de compra
            average_buy_price = total_invested_cost / total_quantity if total_quantity > 0 else 0.0

            current_value = total_quantity * current_price
            rentability = ((current_value - total_invested_cost) / total_invested_cost) * 100 if total_invested_cost != 0 else 0.0

            self.tree.insert("", "end", values=(
                name,
                asset_type,
                total_quantity,
                f"{average_buy_price:.2f}",
                f"{current_price:.2f}",
                f"{total_invested_cost:.2f}",
                f"{current_value:.2f}",
                f"{rentability:.2f}"
            ))
            self.current_carteira_data.append((name, asset_type, total_quantity, average_buy_price, current_price, total_invested_cost, current_value, rentability))

            total_invested_carteira += total_invested_cost
            total_current_value_carteira += current_value

            # Alerta visual de variação de preço (ex: > 5%)
            if abs(rentability) > 5.0:
                alert_message = f"Alerta: {name} teve variação de {rentability:.2f}%!"
                log_message(alert_message)

        self.total_invested_carteira = total_invested_carteira
        self.total_current_value_carteira = total_current_value_carteira
        self.total_rentability_carteira = ((total_current_value_carteira - total_invested_carteira) / total_invested_carteira) * 100 if total_invested_carteira != 0 else 0.0

    def apply_filter(self, event=None):
        filter_text = self.search_entry.get()
        self.load_assets_from_db(filter_text)

    def update_quotes(self):
        self.load_assets_from_db() # Recarrega os dados, o que vai buscar as cotações atualizadas
        messagebox.showinfo("Atualização", "Cotações atualizadas com sucesso!")
        log_message("Cotações atualizadas.")

    def generate_report(self):
        if not self.current_carteira_data:
            messagebox.showwarning("Gerar Relatório", "Não há ativos cadastrados para gerar o relatório.")
            log_message("Tentativa de gerar relatório sem ativos cadastrados.")
            return

        # Formatar os dados para o relatório
        formatted_data = []
        for asset in self.current_carteira_data:
            formatted_data.append((
                asset[0], asset[1], asset[2], f"{asset[3]:.2f}", f"{asset[4]:.2f}", f"{asset[5]:.2f}", f"{asset[6]:.2f}", f"{asset[7]:.2f}"
            ))

        excel_success = self.report_gen.generate_excel_report(formatted_data, "relatorio_carteira.xlsx")
        pdf_success = self.report_gen.generate_pdf_report(formatted_data, self.total_invested_carteira, self.total_current_value_carteira, self.total_rentability_carteira, "relatorio_carteira.pdf")

        if excel_success and pdf_success:
            messagebox.showinfo("Gerar Relatório", "Relatórios Excel e PDF gerados com sucesso!")
            log_message("Relatórios Excel e PDF gerados com sucesso.")
        else:
            messagebox.showerror("Gerar Relatório", "Ocorreu um erro ao gerar os relatórios.")
            log_message("Erro ao gerar relatórios.")

    def update_all(self):
        self.update_quotes()
        self.generate_report()
        messagebox.showinfo("Atualizar Tudo", "Processo de atualização e geração de relatórios concluído!")
        log_message("Processo de atualização e geração de relatórios concluído.")

    def backup_db(self):
        backup_filename = f"investment_carteira_backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.db"
        if self.db.backup_database(backup_filename):
            messagebox.showinfo("Backup", f"Backup do banco de dados criado em: {backup_filename}")
            log_message(f"Backup do banco de dados criado em: {backup_filename}")
        else:
            messagebox.showerror("Backup", "Erro ao criar backup do banco de dados.")
            log_message("Erro ao criar backup do banco de dados.")

    def restore_db(self):
        backup_filename = filedialog.askopenfilename(
            title="Selecionar Arquivo de Backup",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")])
        if backup_filename:
            if self.db.restore_database(backup_filename):
                messagebox.showinfo("Restaurar", "Banco de dados restaurado com sucesso! Reinicie o aplicativo para ver as mudanças.")
                log_message(f"Banco de dados restaurado de: {backup_filename}")
                self.load_assets_from_db()
            else:
                messagebox.showerror("Restaurar", "Erro ao restaurar o banco de dados.")
                log_message(f"Erro ao restaurar o banco de dados de: {backup_filename}")

    def export_data(self):
        # Criar janela de seleção de tipo de exportação
        export_window = tk.Toplevel(self.root)
        export_window.title("Exportar Dados")
        export_window.geometry("600x450")
        export_window.resizable(False, False)
        export_window.transient(self.root)
        export_window.grab_set()
        
        # Centralizar a janela
        export_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Frame principal
        main_frame = ttk.Frame(export_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(main_frame, text="Escolha o tipo de exportação:", font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Frame para instruções com scrollbar
        instructions_frame = ttk.Frame(main_frame)
        instructions_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Canvas e scrollbar para instruções
        canvas = tk.Canvas(instructions_frame, height=250)
        scrollbar = ttk.Scrollbar(instructions_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Instruções CSV
        csv_frame = ttk.LabelFrame(scrollable_frame, text="📄 Exportar CSV", padding="10")
        csv_frame.pack(fill="x", pady=(0, 15))
        
        csv_instructions = """
O CSV será exportado em 4 arquivos separados:

1. assets_[nome].csv - Ativos da carteira
2. transactions_[nome].csv - Transações realizadas
3. price_history_[nome].csv - Histórico de preços
4. dividends_[nome].csv - Dividendos recebidos

Formato dos dados:
- Datas: YYYY-MM-DD
- Decimais: ponto (.) como separador
- Encoding: UTF-8
"""
        ttk.Label(csv_frame, text=csv_instructions, justify="left", font=("Consolas", 9)).pack(anchor="w")
        
        # Instruções JSON
        json_frame = ttk.LabelFrame(scrollable_frame, text="📋 Exportar JSON", padding="10")
        json_frame.pack(fill="x", pady=(0, 15))
        
        json_instructions = """
O JSON será exportado em um único arquivo contendo:

{
  "assets": [...],
  "transactions": [...],
  "price_history": [...],
  "dividends": [...],
  "alerts": [...],
  "events": [...]
}

Formato dos dados:
- Datas: YYYY-MM-DD
- Encoding: UTF-8
- Indentação: 4 espaços

IMPORTAÇÃO SIMPLIFICADA:
Também aceita formato de carteira simplificado:

[
  {
    "asset_id": "PETR4",
    "current_quantity": 100,
    "average_price": 25.50
  }
]

Este formato cria automaticamente os ativos e transações.
"""
        ttk.Label(json_frame, text=json_instructions, justify="left", font=("Consolas", 9)).pack(anchor="w")
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame para botões (fora do scroll)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        
        def export_csv():
            export_window.destroy()
            self._export_csv_files()
        
        def export_json():
            export_window.destroy()
            self._export_json_files()
        
        ttk.Button(btn_frame, text="📄 Exportar CSV", command=export_csv, width=20).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame, text="📋 Exportar JSON", command=export_json, width=20).pack(side="right", padx=(10, 0))
        
        # Botão cancelar
        ttk.Button(main_frame, text="❌ Cancelar", command=export_window.destroy).pack(pady=(10, 0))

    def _export_csv_files(self):
        """Exporta dados para arquivos CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Salvar Dados como CSV")
        if filename:
            if self.db.export_data_to_csv(filename):
                messagebox.showinfo("Exportar", "Dados exportados para CSV com sucesso!")
                log_message(f"Dados exportados para CSV: {filename}")
            else:
                messagebox.showerror("Exportar", "Erro ao exportar dados para CSV.")
                log_message("Erro ao exportar dados para CSV.")

    def _export_json_files(self):
        """Exporta dados para arquivo JSON"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Salvar Dados como JSON")
        if filename:
            if self.db.export_data_to_json(filename):
                messagebox.showinfo("Exportar", "Dados exportados para JSON com sucesso!")
                log_message(f"Dados exportados para JSON: {filename}")
            else:
                messagebox.showerror("Exportar", "Erro ao exportar dados para JSON.")
                log_message("Erro ao exportar dados para JSON.")

    def import_data(self):
        # Criar janela de seleção de tipo de importação
        import_window = tk.Toplevel(self.root)
        import_window.title("Importar Dados")
        import_window.geometry("500x300")
        import_window.resizable(False, False)
        import_window.transient(self.root)
        import_window.grab_set()
        
        # Centralizar a janela
        import_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Frame principal
        main_frame = ttk.Frame(import_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="Escolha o tipo de importação:", font=("Arial", 14, "bold")).pack(pady=(0, 30))
        
        # Frame para botões principais
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=20)
        
        def import_csv():
            import_window.destroy()
            self._import_csv_files()
        
        def import_json():
            import_window.destroy()
            self._import_json_files()
        
        def show_csv_info():
            self._show_import_info("CSV")
        
        def show_json_info():
            self._show_import_info("JSON")
        
        # Botões principais
        csv_btn = ttk.Button(btn_frame, text="📄 Importar CSV", command=import_csv, width=25)
        csv_btn.pack(pady=10)
        
        json_btn = ttk.Button(btn_frame, text="📋 Importar JSON", command=import_json, width=25)
        json_btn.pack(pady=10)
        
        # Frame para botões de informação
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(info_frame, text="ℹ️ Informações CSV", command=show_csv_info, width=20).pack(side="left", padx=(0, 10))
        ttk.Button(info_frame, text="ℹ️ Informações JSON", command=show_json_info, width=20).pack(side="right", padx=(10, 0))
        
        # Botão cancelar
        ttk.Button(main_frame, text="❌ Cancelar", command=import_window.destroy).pack(pady=(20, 0))

    def _show_import_info(self, format_type):
        """Mostra informações detalhadas sobre o formato de importação"""
        info_window = tk.Toplevel(self.root)
        info_window.title(f"Informações - Importar {format_type}")
        info_window.geometry("700x600")
        info_window.resizable(True, True)
        info_window.transient(self.root)
        info_window.grab_set()
        
        # Centralizar a janela
        info_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Frame principal
        main_frame = ttk.Frame(info_window)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Título
        ttk.Label(main_frame, text=f"📋 Informações para Importar {format_type}", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Canvas e scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        if format_type == "CSV":
            # Instruções CSV
            csv_frame = ttk.LabelFrame(scrollable_frame, text="📄 Importar CSV", padding="15")
            csv_frame.pack(fill="x", pady=(0, 15))
            
            csv_instructions = """
Para importar CSV, você precisa de 4 arquivos:

1. assets.csv - Ativos:
   id,name,type
   1,PETR4,Ação
   2,MXRF11,FII
   3,VALE3,Ação

2. transactions.csv - Transações:
   id,asset_id,transaction_type,quantity,price,transaction_date
   1,1,compra,100,25.00,2023-01-15
   2,1,venda,50,26.50,2023-02-20
   3,2,compra,200,10.00,2022-11-20
   4,3,compra,150,65.30,2023-03-10

3. price_history.csv - Histórico de Preços:
   id,asset_id,price,record_date
   1,1,25.50,2023-01-15
   2,1,26.00,2023-01-16
   3,2,10.10,2022-11-20
   4,3,65.30,2023-03-10

4. dividends.csv - Dividendos:
   id,asset_id,dividend_value,payment_date
   1,1,0.50,2023-02-01
   2,2,0.10,2023-01-10
   3,3,1.20,2023-04-15

📋 FORMATO DA CARTEIRA:
- Transações: Use "compra" ou "venda" como transaction_type
- Quantidades: Números positivos (ex: 100, 50.5)
- Preços: Use ponto como separador decimal (ex: 25.50)
- Datas: Formato YYYY-MM-DD (ex: 2023-01-15)
- IDs: asset_id deve corresponder ao id do ativo

🎯 EXEMPLO DE RESULTADO:
PETR4: 50 ações (100 compradas - 50 vendidas), preço médio R$ 25,00
MXRF11: 200 cotas, preço médio R$ 10,00
VALE3: 150 ações, preço médio R$ 65,30

✅ Após importação, os ativos serão adicionados automaticamente à sua carteira!
"""
            ttk.Label(csv_frame, text=csv_instructions, justify="left", font=("Consolas", 9)).pack(anchor="w")
            
        else:  # JSON
            # Instruções JSON
            json_frame = ttk.LabelFrame(scrollable_frame, text="📋 Importar JSON", padding="15")
            json_frame.pack(fill="x", pady=(0, 15))
            
            json_instructions = """
Para importar JSON, use um arquivo com esta estrutura:

{
  "assets": [
    {"id": 1, "name": "PETR4", "type": "Ação"},
    {"id": 2, "name": "MXRF11", "type": "FII"},
    {"id": 3, "name": "VALE3", "type": "Ação"}
  ],
  "transactions": [
    {"id": 1, "asset_id": 1, "transaction_type": "compra", 
     "quantity": 100, "price": 25.00, "transaction_date": "2023-01-15"},
    {"id": 2, "asset_id": 1, "transaction_type": "venda", 
     "quantity": 50, "price": 26.50, "transaction_date": "2023-02-20"},
    {"id": 3, "asset_id": 2, "transaction_type": "compra", 
     "quantity": 200, "price": 10.00, "transaction_date": "2022-11-20"},
    {"id": 4, "asset_id": 3, "transaction_type": "compra", 
     "quantity": 150, "price": 65.30, "transaction_date": "2023-03-10"}
  ],
  "price_history": [
    {"id": 1, "asset_id": 1, "price": 25.50, "record_date": "2023-01-15"},
    {"id": 2, "asset_id": 1, "price": 26.00, "record_date": "2023-01-16"},
    {"id": 3, "asset_id": 2, "price": 10.10, "record_date": "2022-11-20"},
    {"id": 4, "asset_id": 3, "price": 65.30, "record_date": "2023-03-10"}
  ],
  "dividends": [
    {"id": 1, "asset_id": 1, "dividend_value": 0.50, "payment_date": "2023-02-01"},
    {"id": 2, "asset_id": 2, "dividend_value": 0.10, "payment_date": "2023-01-10"},
    {"id": 3, "asset_id": 3, "dividend_value": 1.20, "payment_date": "2023-04-15"}
  ]
}

📋 FORMATO DA CARTEIRA:
- Transações: Use "compra" ou "venda" como transaction_type
- Quantidades: Números positivos (ex: 100, 50.5)
- Preços: Use ponto como separador decimal (ex: 25.50)
- Datas: Formato YYYY-MM-DD (ex: 2023-01-15)
- IDs: asset_id deve corresponder ao id do ativo

🎯 EXEMPLO DE RESULTADO:
PETR4: 50 ações (100 compradas - 50 vendidas), preço médio R$ 25,00
MXRF11: 200 cotas, preço médio R$ 10,00
VALE3: 150 ações, preço médio R$ 65,30

✅ Após importação, os ativos serão adicionados automaticamente à sua carteira!
"""
            ttk.Label(json_frame, text=json_instructions, justify="left", font=("Consolas", 9)).pack(anchor="w")
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botão fechar
        ttk.Button(main_frame, text="❌ Fechar", command=info_window.destroy).pack(pady=(15, 0))

    def _import_csv_files(self):
        """Importa dados de arquivos CSV e adiciona automaticamente à carteira"""
        assets_filename = filedialog.askopenfilename(
            title="Selecionar Arquivo de Ativos CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        transactions_filename = filedialog.askopenfilename(
            title="Selecionar Arquivo de Transações CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        price_history_filename = filedialog.askopenfilename(
            title="Selecionar Arquivo de Histórico de Preços CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        dividends_filename = filedialog.askopenfilename(
            title="Selecionar Arquivo de Dividendos CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])

        if assets_filename and transactions_filename and price_history_filename and dividends_filename:
            if self.db.import_data_from_csv(assets_filename, transactions_filename, price_history_filename, dividends_filename):
                # Adicionar ativos automaticamente à carteira
                self._add_imported_assets_to_carteira()
                
                messagebox.showinfo("Importar", "Dados importados de CSV com sucesso! Ativos adicionados automaticamente à carteira.")
                log_message(f"Dados importados de CSV: {assets_filename}, {transactions_filename}, {price_history_filename}, {dividends_filename}")
                self.load_assets_from_db()
            else:
                messagebox.showerror("Importar", "Erro ao importar dados de CSV.")
                log_message("Erro ao importar dados de CSV.")
        else:
            messagebox.showwarning("Importar Dados", "Seleção de arquivos CSV cancelada ou incompleta.")

    def _import_json_files(self):
        """Importa dados de arquivos JSON e adiciona automaticamente à carteira"""
        filename = filedialog.askopenfilename(
            title="Selecionar Arquivo JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            multiple=True) # Permitir seleção de múltiplos arquivos JSON
        if filename:
            success = True
            error_details = ""
            for f in filename:
                try:
                    if not self.db.import_data_from_json(f):
                        success = False
                        error_details = f"Erro ao importar arquivo: {f}"
                        break
                except Exception as e:
                    success = False
                    error_details = f"Erro ao importar arquivo {f}: {str(e)}"
                    log_message(f"Erro detalhado na importação: {error_details}")
                    import traceback
                    traceback.print_exc()
                    break
            
            if success:
                try:
                    # Adicionar ativos automaticamente à carteira
                    self._add_imported_assets_to_carteira()
                    
                    messagebox.showinfo("Importar", "Dados importados de JSON com sucesso! Ativos adicionados automaticamente à carteira.")
                    log_message(f"Dados importados de JSON: {filename}")
                    self.load_assets_from_db()
                except Exception as e:
                    log_message(f"Erro ao processar ativos importados: {e}")
                    import traceback
                    traceback.print_exc()
                    messagebox.showerror("Importar", f"Erro ao processar ativos importados: {e}")
            else:
                messagebox.showerror("Importar", f"Erro ao importar dados de JSON.\n\nDetalhes: {error_details}")
                log_message(f"Erro ao importar dados de JSON: {error_details}")
        else:
            messagebox.showwarning("Importar Dados", "Seleção de arquivo JSON cancelada.")

    def _add_imported_assets_to_carteira(self):
        """Adiciona automaticamente os ativos importados à carteira"""
        try:
            # Obter todos os ativos com transações do banco
            assets_with_transactions = self.db.get_all_assets_with_transactions()
            
            if not assets_with_transactions:
                log_message("Nenhum ativo com transações encontrado para adicionar à carteira.")
                return
            
            added_count = 0
            for asset in assets_with_transactions:
                asset_id, asset_name, asset_type, total_quantity, total_invested = asset
                
                # Verificar se o ativo já existe na carteira atual
                asset_exists = False
                if hasattr(self, 'current_carteira_data') and self.current_carteira_data:
                    for existing_asset in self.current_carteira_data:
                        if existing_asset[0] == asset_name:
                            asset_exists = True
                            break
                
                # Se não existe, adicionar à carteira
                if not asset_exists and total_quantity > 0:
                    # Calcular preço médio
                    avg_price = total_invested / total_quantity if total_quantity > 0 else 0
                    
                    # Adicionar à carteira atual
                    if not hasattr(self, 'current_carteira_data'):
                        self.current_carteira_data = []
                    
                    self.current_carteira_data.append([
                        asset_name,           # Nome do ativo
                        asset_type,           # Tipo do ativo
                        total_quantity,       # Quantidade total
                        avg_price,            # Preço médio
                        0,                    # Preço atual (será atualizado)
                        total_invested,       # Valor investido
                        0,                    # Valor atual (será atualizado)
                        0                     # Rentabilidade (será calculada)
                    ])
                    added_count += 1
                    log_message(f"Ativo {asset_name} adicionado automaticamente à carteira (Qtd: {total_quantity}, Preço médio: R$ {avg_price:.2f})")
            
            if added_count > 0:
                log_message(f"{added_count} ativos adicionados automaticamente à carteira após importação.")
                # Atualizar a interface
                self.load_assets_from_db()
            else:
                log_message("Todos os ativos importados já existem na carteira.")
                
        except Exception as e:
            log_message(f"Erro ao adicionar ativos importados à carteira: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao adicionar ativos à carteira: {e}")

    def on_asset_double_click(self, event):
        item_id = self.tree.selection()[0]
        asset_name = self.tree.item(item_id, "values")[0]
        asset_id = self.asset_details_map.get(asset_name)

        if asset_id:
            price_history = self.db.get_price_history(asset_id)
            if price_history:
                self.plot_m.plot_price_history(asset_name, price_history)
            else:
                messagebox.showinfo("Histórico de Preços", f"Não há histórico de preços disponível para {asset_name}.")
        else:
            messagebox.showerror("Erro", "Ativo não encontrado para exibir histórico.")

    def perform_risk_analysis(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Análise de Risco", "Selecione um ativo na tabela para realizar a análise de risco.")
            return

        asset_name = self.tree.item(selected_item[0], "values")[0]
        asset_id = self.asset_details_map.get(asset_name)

        if asset_id:
            # Obter datas para a análise (pode ser configurável pelo usuário)
            end_date = datetime.date.today().strftime("%Y-%m-%d")
            start_date = (datetime.date.today() - datetime.timedelta(days=365)).strftime("%Y-%m-%d") # Último ano

            volatility = self.risk_analysis.calculate_volatility(asset_name, start_date, end_date)
            if volatility is not None:
                messagebox.showinfo("Análise de Risco", f"Volatilidade de {asset_name} (último ano): {volatility:.4f}")
                log_message(f"Volatilidade de {asset_name}: {volatility:.4f}")
            else:
                messagebox.showinfo("Análise de Risco", f"Não foi possível calcular a volatilidade para {asset_name}. Verifique se há dados históricos suficientes.")

            # Exemplo de cálculo de Beta com IBOV como benchmark
            benchmark_ticker = "^BVSP" # Ticker do Ibovespa
            beta = self.risk_analysis.calculate_beta(asset_name, benchmark_ticker, start_date, end_date)
            if beta is not None:
                messagebox.showinfo("Análise de Risco", f"Beta de {asset_name} vs {benchmark_ticker} (último ano): {beta:.4f}")
                log_message(f"Beta de {asset_name} vs {benchmark_ticker}: {beta:.4f}")
            else:
                messagebox.showinfo("Análise de Risco", f"Não foi possível calcular o Beta para {asset_name}. Verifique se há dados históricos suficientes para o ativo e o benchmark.")
        else:
            messagebox.showerror("Erro", "Ativo não encontrado para realizar análise de risco.")

    def compare_with_benchmark(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Comparar com Benchmark", "Selecione um ativo na tabela para comparar com um benchmark.")
            return

        asset_name = self.tree.item(selected_item[0], "values")[0]
        asset_id = self.asset_details_map.get(asset_name)

        if asset_id:
            benchmark_ticker = simpledialog.askstring("Comparar com Benchmark", "Digite o ticker do benchmark (ex: ^BVSP para Ibovespa):", parent=self.root)
            if benchmark_ticker:
                end_date = datetime.date.today().strftime("%Y-%m-%d")
                start_date = (datetime.date.today() - datetime.timedelta(days=365)).strftime("%Y-%m-%d") # Último ano

                asset_price_history = self.db.get_price_history(asset_id, start_date, end_date)
                benchmark_price_history = self.yf_integration.get_historical_prices(benchmark_ticker, start_date, end_date)

                if asset_price_history and benchmark_price_history:
                    self.plot_m.plot_comparison_with_benchmark(asset_name, asset_price_history, benchmark_ticker, benchmark_price_history)
                    log_message(f"Comparativo de {asset_name} com {benchmark_ticker} gerado.")
                else:
                    messagebox.showinfo("Comparar com Benchmark", f"Não foi possível obter dados históricos suficientes para {asset_name} ou {benchmark_ticker}.")
            else:
                messagebox.showwarning("Comparar com Benchmark", "Nenhum ticker de benchmark fornecido.")
        else:
            messagebox.showerror("Erro", "Ativo não encontrado para realizar comparação com benchmark.")

    def perform_projection_simulation(self):
        # Obter dados da carteira atual para a simulação
        assets_for_simulation = []
        for asset in self.current_carteira_data:
            asset_name = asset[0]
            asset_id = self.asset_details_map.get(asset_name)
            total_quantity = asset[2]
            if asset_id:
                assets_for_simulation.append((asset_id, asset_name, total_quantity))

        if not assets_for_simulation:
            messagebox.showwarning("Projeções e Simulações", "Não há ativos na carteira para realizar projeções ou simulações.", parent=self.root)
            return

        initial_carteira_value = self.total_current_value_carteira
        if initial_carteira_value == 0:
            messagebox.showwarning("Projeções e Simulações", "O valor atual da carteira é zero. Não é possível realizar projeções ou simulações.", parent=self.root)
            return

        # Perguntar ao usuário qual tipo de projeção/simulação deseja
        choice = simpledialog.askstring("Projeções e Simulações", "Escolha o tipo: Monte Carlo (MC) ou Linear (L)?", parent=self.root)

        if choice and choice.upper() == "MC":
            num_simulations = simpledialog.askinteger("Monte Carlo", "Número de simulações (ex: 1000):", parent=self.root, minvalue=100, maxvalue=5000)
            num_days = simpledialog.askinteger("Monte Carlo", "Número de dias futuros (ex: 252 para 1 ano):", parent=self.root, minvalue=30, maxvalue=1000)

            if num_simulations and num_days:
                simulated_values = self.projection_simulation.monte_carlo_simulation(initial_carteira_value, assets_for_simulation, num_simulations, num_days, gui_parent=self.root)
                if simulated_values is not None:
                    self.projection_simulation.plot_monte_carlo_results(simulated_values, gui_parent=self.root)
                    log_message(f"Simulação de Monte Carlo realizada com {num_simulations} simulações e {num_days} dias.")
                else:
                    messagebox.showerror("Monte Carlo", "Não foi possível realizar a simulação de Monte Carlo. Verifique os dados.", parent=self.root)
            else:
                messagebox.showwarning("Monte Carlo", "Parâmetros de simulação inválidos ou cancelados.", parent=self.root)

        elif choice and choice.upper() == "L":
            annual_return_rate = simpledialog.askfloat("Projeção Linear", "Taxa de retorno anual esperada (ex: 0.10 para 10%):", parent=self.root, minvalue=0.0, maxvalue=1.0)
            num_years = simpledialog.askinteger("Projeção Linear", "Número de anos futuros (ex: 5):", parent=self.root, minvalue=1, maxvalue=30)

            if annual_return_rate is not None and num_years is not None:
                projected_values = self.projection_simulation.linear_projection(initial_carteira_value, annual_return_rate, num_years, gui_parent=self.root)
                if projected_values is not None:
                    self.projection_simulation.plot_linear_projection(projected_values, num_years, gui_parent=self.root)
                    log_message(f"Projeção Linear realizada para {num_years} anos com taxa de {annual_return_rate*100:.2f}%")
                else:
                    messagebox.showerror("Projeção Linear", "Não foi possível realizar a projeção linear. Verifique os dados.", parent=self.root)
            else:
                messagebox.showwarning("Projeção Linear", "Parâmetros de projeção inválidos ou cancelados.", parent=self.root)
        else:
            messagebox.showwarning("Projeções e Simulações", "Tipo de projeção/simulação inválido ou cancelado.", parent=self.root)

    def manage_alerts(self):
        AlertManagerWindow(self.root, self.db, self.yf_integration, self.load_assets_from_db)

    def open_event_calendar(self):
        EventCalendarWindow(self.root, self.db)

    def schedule_background_update(self):
        # Inicia a thread de atualização em segundo plano
        self.background_update_thread = threading.Thread(target=self._background_update_task, daemon=True)
        self.background_update_thread.start()

    def _background_update_task(self):
        while True:
            try:
                time.sleep(self.update_interval_minutes * 60) # Espera o tempo configurado
                log_message("Iniciando atualização em segundo plano...")
                self._check_and_update_data()
                self._check_alerts()
                log_message("Atualização em segundo plano concluída.")
            except Exception as e:
                log_message(f"Erro na thread de background: {e}")
                time.sleep(60)  # Espera 1 minuto antes de tentar novamente

    def _check_and_update_data(self):
        # Esta função será chamada pela thread de segundo plano
        # Ela deve atualizar os dados e a UI de forma segura
        try:
            self.root.after(0, self.load_assets_from_db) # Agenda a atualização da UI na thread principal
        except Exception as e:
            log_message(f"Erro ao atualizar dados em background: {e}")

    def _check_alerts(self):
        # Esta função será chamada pela thread de segundo plano
        # Verifica os alertas e notifica o usuário se necessário
        try:
            active_alerts = self.db.get_active_alerts()
            for alert in active_alerts:
                alert_id, asset_name, alert_type, target_value, percentage_change = alert
                current_price = self.yf_integration.get_current_price(asset_name + ".SA")

                if current_price is None:
                    log_message(f"Não foi possível obter preço atual para {asset_name} para verificar alerta.")
                    continue

                if alert_type == "price_target":
                    if current_price >= target_value:
                        alert_message = f"ALERTA DE PREÇO: {asset_name} atingiu ou superou o preço alvo de R$ {target_value:.2f}! Preço atual: R$ {current_price:.2f}"
                        self.root.after(0, lambda msg=alert_message: messagebox.showinfo("Alerta de Preço", msg))
                        log_message(alert_message)
                        self.db.deactivate_alert(alert_id) # Desativa o alerta após ser acionado
                elif alert_type == "percentage_change":
                    # Precisa do preço anterior para calcular a variação percentual
                    # Por simplicidade, vamos usar o preço atual e o preço médio de compra como base para um alerta de variação inicial
                    # Em uma implementação mais robusta, seria necessário armazenar o preço de referência para o alerta
                    assets = self.db.get_all_assets_with_transactions()
                    asset_info = next((a for a in assets if a[1] == asset_name), None)
                    if asset_info:
                        total_quantity = asset_info[3]
                        total_invested_cost = asset_info[4]
                        average_buy_price = total_invested_cost / total_quantity if total_quantity > 0 else 0.0

                        if average_buy_price > 0:
                            current_percentage_change = ((current_price - average_buy_price) / average_buy_price) * 100
                            if abs(current_percentage_change) >= percentage_change:
                                alert_message = f"ALERTA DE VARIAÇÃO: {asset_name} teve uma variação de {current_percentage_change:.2f}% (alvo: {percentage_change:.2f}%)! Preço atual: R$ {current_price:.2f}"
                                self.root.after(0, lambda msg=alert_message: messagebox.showinfo("Alerta de Variação", msg))
                                log_message(alert_message)
                                self.db.deactivate_alert(alert_id) # Desativa o alerta após ser acionado
        except Exception as e:
            log_message(f"Erro ao verificar alertas: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = InvestmentCarteiraApp(root)
    root.mainloop()





import tkinter as tk
from tkinter import ttk, messagebox
from database_manager import DatabaseManager
from datetime import datetime
from yfinance_integration import YFinanceIntegration

class AssetRegistrationWindow(tk.Toplevel):
    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.title("Cadastrar Novo Ativo")
        self.geometry("550x450")
        self.resizable(True, True)
        self.on_save_callback = on_save_callback
        self.db = DatabaseManager() # Instanciar o DatabaseManager
        self.yf_integration = YFinanceIntegration() # Instanciar o YFinanceIntegration

        self.create_widgets()

    def create_widgets(self):
        # Frame principal com padding
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Configurar grid do frame principal
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="📝 Cadastrar Novo Ativo", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")
        
        # Nome do Ativo
        ttk.Label(main_frame, text="Nome do Ativo (Ticker):").grid(row=1, column=0, padx=(0, 10), pady=8, sticky="w")
        self.name_entry = ttk.Entry(main_frame, width=20)
        self.name_entry.grid(row=1, column=1, padx=(0, 10), pady=8, sticky="ew")

        # Frame para botão de cotação
        price_btn_frame = ttk.Frame(main_frame)
        price_btn_frame.grid(row=1, column=2, padx=(0, 0), pady=8, sticky="ew")
        price_btn_frame.grid_columnconfigure(0, weight=1)
        
        # Botão para buscar cotação automática
        btn_auto_price = ttk.Button(price_btn_frame, text="🔍 Cotação", command=self.get_auto_price)
        btn_auto_price.grid(row=0, column=0, sticky="ew")

        # Tipo
        ttk.Label(main_frame, text="Tipo:").grid(row=2, column=0, padx=(0, 10), pady=8, sticky="w")
        self.type_combobox = ttk.Combobox(main_frame, values=["Ação", "FII", "Tesouro", "ETF", "Outro"], width=15)
        self.type_combobox.grid(row=2, column=1, padx=(0, 10), pady=8, sticky="ew")
        self.type_combobox.set("Ação") # Valor padrão
        
        # Dica sobre tipos de ativos
        tip_label = ttk.Label(main_frame, text="💡 Ações, FIIs e ETFs têm cotação automática", 
                             font=("Arial", 8), foreground="gray")
        tip_label.grid(row=2, column=2, padx=(0, 0), pady=8, sticky="w")

        # Quantidade
        ttk.Label(main_frame, text="Quantidade:").grid(row=3, column=0, padx=(0, 10), pady=8, sticky="w")
        self.quantity_entry = ttk.Entry(main_frame, width=15)
        self.quantity_entry.grid(row=3, column=1, columnspan=2, padx=(0, 0), pady=8, sticky="ew")

        # Preço da Transação
        ttk.Label(main_frame, text="Preço da Transação:").grid(row=4, column=0, padx=(0, 10), pady=8, sticky="w")
        self.price_entry = ttk.Entry(main_frame, width=15)
        self.price_entry.grid(row=4, column=1, columnspan=2, padx=(0, 0), pady=8, sticky="ew")

        # Data da Transação
        ttk.Label(main_frame, text="Data da Transação:").grid(row=5, column=0, padx=(0, 10), pady=8, sticky="w")
        self.date_entry = ttk.Entry(main_frame, width=15)
        self.date_entry.grid(row=5, column=1, padx=(0, 10), pady=8, sticky="ew")
        self.date_entry.insert(0, "DD/MM/AAAA")
        self.date_entry.bind("<FocusIn>", self.on_date_focus_in)
        self.date_entry.bind("<FocusOut>", self.on_date_focus_out)
        
        # Frame para botão de data
        date_btn_frame = ttk.Frame(main_frame)
        date_btn_frame.grid(row=5, column=2, padx=(0, 0), pady=8, sticky="ew")
        date_btn_frame.grid_columnconfigure(0, weight=1)
        
        # Botão para preencher data atual
        btn_today = ttk.Button(date_btn_frame, text="📅 Hoje", command=self.fill_today_date)
        btn_today.grid(row=0, column=0, sticky="ew")

        # Tipo de Transação (Compra/Venda)
        ttk.Label(main_frame, text="Tipo de Transação:").grid(row=6, column=0, padx=(0, 10), pady=8, sticky="w")
        self.transaction_type_combobox = ttk.Combobox(main_frame, values=["compra", "venda"], width=15)
        self.transaction_type_combobox.grid(row=6, column=1, columnspan=2, padx=(0, 0), pady=8, sticky="ew")
        self.transaction_type_combobox.set("compra") # Valor padrão

        # Espaçador para empurrar botões para baixo
        spacer = ttk.Frame(main_frame)
        spacer.grid(row=7, column=0, columnspan=3, pady=20)
        spacer.grid_rowconfigure(0, weight=1)

        # Frame para botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=8, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        
        # Configurar grid do frame de botões
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)
        
        btn_save = ttk.Button(btn_frame, text="💾 Salvar", command=self.save_asset_and_transaction)
        btn_save.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        
        btn_cancel = ttk.Button(btn_frame, text="❌ Cancelar", command=self.destroy)
        btn_cancel.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        btn_clear = ttk.Button(btn_frame, text="🗑️ Limpar", command=self.clear_fields)
        btn_clear.grid(row=0, column=2, padx=(5, 0), pady=5, sticky="ew")

    def get_auto_price(self):
        """Busca a cotação atual do ativo automaticamente"""
        ticker = self.name_entry.get().strip().upper()
        
        if not ticker:
            messagebox.showwarning("Aviso", "Digite o nome/ticker do ativo primeiro!", parent=self)
            return
        
        # Verificar se é um tipo de ativo que tem cotação automática
        asset_type = self.type_combobox.get()
        if asset_type in ["Tesouro", "Outro"]:
            messagebox.showinfo("Informação", 
                              f"Ativos do tipo '{asset_type}' não têm cotação automática.\n"
                              "Digite o preço manualmente.", parent=self)
            return
        
        try:
            # Adicionar .SA para ativos brasileiros
            if asset_type in ["Ação", "FII", "ETF"]:
                ticker_with_suffix = f"{ticker}.SA"
            else:
                ticker_with_suffix = ticker
            
            # Buscar cotação atual
            current_price = self.yf_integration.get_current_price(ticker_with_suffix)
            
            if current_price and current_price > 0:
                # Preencher o campo de preço
                self.price_entry.delete(0, tk.END)
                self.price_entry.insert(0, f"{current_price:.2f}")
                
                # Preencher a data atual se estiver vazia
                if not self.date_entry.get():
                    today = datetime.now().strftime("%d/%m/%Y")
                    self.date_entry.insert(0, today)
                
                messagebox.showinfo("Sucesso", 
                                  f"Cotação atual de {ticker}: R$ {current_price:.2f}\n"
                                  "Preço preenchido automaticamente!", parent=self)
            else:
                messagebox.showwarning("Aviso", 
                                     f"Não foi possível obter a cotação de {ticker}.\n"
                                     "Verifique se o ticker está correto ou digite o preço manualmente.", parent=self)
                
        except Exception as e:
            messagebox.showerror("Erro", 
                               f"Erro ao buscar cotação: {str(e)}\n"
                               "Digite o preço manualmente.", parent=self)

    def fill_today_date(self):
        """Preenche a data atual no campo de data"""
        today = datetime.now().strftime("%d/%m/%Y")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, today)
        # Remover o placeholder temporariamente
        self.date_entry.unbind("<FocusIn>")
        self.date_entry.unbind("<FocusOut>")

    def clear_fields(self):
        """Limpa todos os campos do formulário"""
        self.name_entry.delete(0, tk.END)
        self.type_combobox.set("Ação")
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, "DD/MM/AAAA")
        self.transaction_type_combobox.set("compra")

    def on_date_focus_in(self, event):
        """Quando o campo de data recebe foco, limpa o placeholder"""
        if self.date_entry.get() == "DD/MM/AAAA":
            self.date_entry.delete(0, tk.END)

    def on_date_focus_out(self, event):
        """Quando o campo de data perde foco, mostra placeholder se vazio"""
        if not self.date_entry.get():
            self.date_entry.insert(0, "DD/MM/AAAA")

    def save_asset_and_transaction(self):
        name = self.name_entry.get().upper() # Ticker em maiúsculas
        asset_type = self.type_combobox.get()
        quantity = self.quantity_entry.get()
        price = self.price_entry.get()
        date = self.date_entry.get()
        transaction_type = self.transaction_type_combobox.get()

        if not all([name, asset_type, quantity, price, date, transaction_type]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!", parent=self)
            return

        try:
            quantity = float(quantity)
            price = float(price)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e Preço devem ser números válidos.", parent=self)
            return

        # Validar e converter data do formato brasileiro para o formato do banco
        try:
            # Converter de DD/MM/AAAA para AAAA-MM-DD
            date_obj = datetime.strptime(date, "%d/%m/%Y")
            date_db = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Data deve estar no formato DD/MM/AAAA (ex: 15/01/2024).", parent=self)
            return

        # Verificar se o ativo já existe
        asset = self.db.get_asset_by_name(name)
        asset_id = None

        if asset:
            asset_id = asset[0] # ID do ativo existente
        else:
            # Adicionar novo ativo se não existir
            asset_id = self.db.add_asset(name, asset_type)
            if not asset_id:
                messagebox.showerror("Erro", "Não foi possível adicionar o ativo.", parent=self)
                return

        # Adicionar a transação
        transaction_id = self.db.add_transaction(asset_id, transaction_type, quantity, price, date_db)

        if transaction_id:
            messagebox.showinfo("Sucesso", "Ativo e transação cadastrados com sucesso!", parent=self)
            self.on_save_callback() # Chamar callback para atualizar a Treeview principal
            self.destroy()
        else:
            messagebox.showerror("Erro", "Não foi possível registrar a transação.", parent=self)




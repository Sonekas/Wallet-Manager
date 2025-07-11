import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime

class EventCalendarWindow(tk.Toplevel):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.title("Calendário de Eventos")
        self.db = db_manager

        self.create_widgets()
        self.load_events()

    def create_widgets(self):
        # Frame para adicionar novo evento
        add_frame = ttk.LabelFrame(self, text="Adicionar Novo Evento", padding="10")
        add_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(add_frame, text="Data (DD/MM/AAAA):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.event_date_entry = ttk.Entry(add_frame)
        self.event_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(add_frame, text="Tipo de Evento:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.event_type_var = tk.StringVar()
        self.event_type_combobox = ttk.Combobox(add_frame, textvariable=self.event_type_var, values=["Dividendo", "Desdobramento", "Vencimento", "Outro"])
        self.event_type_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(add_frame, text="Descrição:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.description_entry = ttk.Entry(add_frame)
        self.description_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(add_frame, text="Ativo (Opcional):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.asset_name_entry = ttk.Entry(add_frame)
        self.asset_name_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.add_event_button = ttk.Button(add_frame, text="Adicionar Evento", command=self.add_new_event)
        self.add_event_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Frame para listar eventos existentes
        list_frame = ttk.LabelFrame(self, text="Eventos Futuros", padding="10")
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.events_tree = ttk.Treeview(list_frame, columns=("data", "tipo", "descricao", "ativo"), show="headings")
        self.events_tree.pack(fill="both", expand=True)

        self.events_tree.heading("data", text="Data")
        self.events_tree.heading("tipo", text="Tipo")
        self.events_tree.heading("descricao", text="Descrição")
        self.events_tree.heading("ativo", text="Ativo")

        self.events_tree.column("data", width=100, anchor="center")
        self.events_tree.column("tipo", width=100, anchor="center")
        self.events_tree.column("descricao", width=200, anchor="w")
        self.events_tree.column("ativo", width=100, anchor="center")

    def add_new_event(self):
        event_date_str = self.event_date_entry.get().strip()
        event_type = self.event_type_var.get()
        description = self.description_entry.get().strip()
        asset_name = self.asset_name_entry.get().strip()

        if not event_date_str or not event_type or not description:
            messagebox.showwarning("Erro", "Por favor, preencha todos os campos obrigatórios (Data, Tipo, Descrição).")
            return

        try:
            # Converter de DD/MM/AAAA para AAAA-MM-DD
            date_obj = datetime.datetime.strptime(event_date_str, "%d/%m/%Y")
            event_date_db = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA (ex: 15/01/2024).")
            return

        asset_id = None
        if asset_name:
            asset = self.db.get_asset_by_name(asset_name)
            if not asset:
                messagebox.showerror("Erro", f"Ativo \'{asset_name}\' não encontrado no banco de dados.")
                return
            asset_id = asset[0]

        self.db.add_event(event_date_db, event_type, description, asset_id)
        messagebox.showinfo("Sucesso", "Evento adicionado com sucesso!")
        self.event_date_entry.delete(0, tk.END)
        self.event_type_combobox.set("")
        self.description_entry.delete(0, tk.END)
        self.asset_name_entry.delete(0, tk.END)
        self.load_events()

    def load_events(self):
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        today = datetime.date.today().strftime("%Y-%m-%d")
        events = self.db.get_events(start_date=today) # Carrega eventos a partir de hoje
        for event in events:
            event_id, event_date, event_type, description, asset_name = event
            # Converter data para formato brasileiro
            try:
                date_obj = datetime.datetime.strptime(event_date, "%Y-%m-%d")
                event_date_br = date_obj.strftime("%d/%m/%Y")
            except:
                event_date_br = event_date
            self.events_tree.insert("", "end", values=(event_date_br, event_type, description, asset_name if asset_name else "N/A"))



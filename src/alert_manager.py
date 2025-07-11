import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class AlertManagerWindow(tk.Toplevel):
    def __init__(self, parent, db_manager, yf_integration, refresh_callback):
        super().__init__(parent)
        self.title("Gerenciar Alertas")
        self.db = db_manager
        self.yf_integration = yf_integration
        self.refresh_callback = refresh_callback

        self.create_widgets()
        self.load_alerts()

    def create_widgets(self):
        # Frame para adicionar novo alerta
        add_frame = ttk.LabelFrame(self, text="Adicionar Novo Alerta", padding="10")
        add_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(add_frame, text="Ativo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.asset_name_entry = ttk.Entry(add_frame)
        self.asset_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(add_frame, text="Tipo de Alerta:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.alert_type_var = tk.StringVar()
        self.alert_type_combobox = ttk.Combobox(add_frame, textvariable=self.alert_type_var, values=["Preço Alvo", "Variação Percentual"])
        self.alert_type_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.alert_type_combobox.bind("<<ComboboxSelected>>", self.on_alert_type_selected)

        ttk.Label(add_frame, text="Valor Alvo / Percentual:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.target_value_entry = ttk.Entry(add_frame)
        self.target_value_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.add_alert_button = ttk.Button(add_frame, text="Adicionar Alerta", command=self.add_new_alert)
        self.add_alert_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Frame para listar alertas existentes
        list_frame = ttk.LabelFrame(self, text="Alertas Ativos", padding="10")
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.alerts_tree = ttk.Treeview(list_frame, columns=("id", "ativo", "tipo", "valor", "status"), show="headings")
        self.alerts_tree.pack(fill="both", expand=True)

        self.alerts_tree.heading("id", text="ID")
        self.alerts_tree.heading("ativo", text="Ativo")
        self.alerts_tree.heading("tipo", text="Tipo")
        self.alerts_tree.heading("valor", text="Valor/Percentual")
        self.alerts_tree.heading("status", text="Status")

        self.alerts_tree.column("id", width=50, anchor="center")
        self.alerts_tree.column("ativo", width=100, anchor="center")
        self.alerts_tree.column("tipo", width=120, anchor="center")
        self.alerts_tree.column("valor", width=120, anchor="center")
        self.alerts_tree.column("status", width=80, anchor="center")

        self.deactivate_alert_button = ttk.Button(list_frame, text="Desativar Alerta Selecionado", command=self.deactivate_selected_alert)
        self.deactivate_alert_button.pack(pady=10)

    def on_alert_type_selected(self, event):
        selected_type = self.alert_type_var.get()
        if selected_type == "Preço Alvo":
            self.target_value_entry.config(state="normal")
            self.target_value_entry.delete(0, tk.END)
            self.target_value_entry.insert(0, "Preço Alvo")
        elif selected_type == "Variação Percentual":
            self.target_value_entry.config(state="normal")
            self.target_value_entry.delete(0, tk.END)
            self.target_value_entry.insert(0, "Percentual (ex: 5 para 5%)")

    def add_new_alert(self):
        asset_name = self.asset_name_entry.get().strip()
        alert_type = self.alert_type_var.get()
        target_value_str = self.target_value_entry.get().strip()

        if not asset_name or not alert_type or not target_value_str:
            messagebox.showwarning("Erro", "Por favor, preencha todos os campos.")
            return

        asset = self.db.get_asset_by_name(asset_name)
        if not asset:
            messagebox.showerror("Erro", f"Ativo \'{asset_name}\' não encontrado no banco de dados.")
            return
        asset_id = asset[0]

        try:
            value = float(target_value_str)
        except ValueError:
            messagebox.showerror("Erro", "Valor alvo/percentual inválido. Deve ser um número.")
            return

        if alert_type == "Preço Alvo":
            self.db.add_alert(asset_id, "price_target", target_value=value)
        elif alert_type == "Variação Percentual":
            self.db.add_alert(asset_id, "percentage_change", percentage_change=value)
        
        messagebox.showinfo("Sucesso", "Alerta adicionado com sucesso!")
        self.asset_name_entry.delete(0, tk.END)
        self.target_value_entry.delete(0, tk.END)
        self.alert_type_combobox.set("")
        self.load_alerts()
        self.refresh_callback() # Atualiza a tela principal para verificar novos alertas

    def load_alerts(self):
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)
        
        alerts = self.db.get_active_alerts()
        for alert in alerts:
            # alert: (id, asset_name, alert_type, target_value, percentage_change)
            alert_id = alert[0]
            asset_name = alert[1]
            alert_type = alert[2]
            target_value = alert[3]
            percentage_change = alert[4]

            display_value = ""
            if alert_type == "price_target":
                display_value = f"R$ {target_value:.2f}"
                alert_type_display = "Preço Alvo"
            elif alert_type == "percentage_change":
                display_value = f"{percentage_change:.2f}%"
                alert_type_display = "Variação Percentual"
            
            self.alerts_tree.insert("", "end", values=(alert_id, asset_name, alert_type_display, display_value, "Ativo"))

    def deactivate_selected_alert(self):
        selected_item = self.alerts_tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Por favor, selecione um alerta para desativar.")
            return
        
        alert_id = self.alerts_tree.item(selected_item[0], "values")[0]
        
        if messagebox.askyesno("Confirmar Desativação", f"Tem certeza que deseja desativar o alerta ID {alert_id}? "):
            if self.db.deactivate_alert(alert_id):
                messagebox.showinfo("Sucesso", "Alerta desativado com sucesso!")
                self.load_alerts()
                self.refresh_callback()
            else:
                messagebox.showerror("Erro", "Erro ao desativar o alerta.")



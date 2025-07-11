import sqlite3
import datetime
import pandas as pd
import json
import threading

class DatabaseManager:
    def __init__(self, db_name="investment_carteira.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.lock = threading.Lock()  # Lock para thread-safety
        self._local = threading.local()  # Para conexões thread-local
        self.connect()
        self.create_tables()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def get_thread_connection(self):
        """Obtém uma conexão específica para a thread atual"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(self.db_name)
            self._local.cursor = self._local.connection.cursor()
        return self._local.connection, self._local.cursor

    def create_tables(self):
        if self.conn:
            try:
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS assets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        type TEXT NOT NULL
                    )
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        asset_id INTEGER NOT NULL,
                        transaction_type TEXT NOT NULL, -- 'compra' ou 'venda'
                        quantity REAL NOT NULL,
                        price REAL NOT NULL,
                        transaction_date TEXT NOT NULL,
                        FOREIGN KEY (asset_id) REFERENCES assets(id)
                    )
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS price_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        asset_id INTEGER NOT NULL,
                        price REAL NOT NULL,
                        record_date TEXT NOT NULL,
                        FOREIGN KEY (asset_id) REFERENCES assets(id),
                        UNIQUE(asset_id, record_date)
                    )
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dividends (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        asset_id INTEGER NOT NULL,
                        dividend_value REAL NOT NULL,
                        payment_date TEXT NOT NULL,
                        FOREIGN KEY (asset_id) REFERENCES assets(id)
                    )
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        asset_id INTEGER NOT NULL,
                        alert_type TEXT NOT NULL, -- 'price_target', 'percentage_change'
                        target_value REAL,
                        percentage_change REAL,
                        is_active INTEGER DEFAULT 1, -- 1 for active, 0 for inactive
                        FOREIGN KEY (asset_id) REFERENCES assets(id)
                    )
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_date TEXT NOT NULL,
                        event_type TEXT NOT NULL, -- 'dividendo', 'desdobramento', 'vencimento'
                        description TEXT NOT NULL,
                        asset_id INTEGER,
                        FOREIGN KEY (asset_id) REFERENCES assets(id)
                    )
                """)
                self.conn.commit()
            except sqlite3.Error as e:
                print(f"Erro ao criar tabelas: {e}")

    def add_asset(self, name, asset_type):
        with self.lock:
            if self.conn:
                try:
                    self.cursor.execute("INSERT INTO assets (name, type) VALUES (?, ?)",
                                        (name, asset_type))
                    self.conn.commit()
                    return self.cursor.lastrowid
                except sqlite3.Error as e:
                    print(f"Erro ao adicionar ativo: {e}")
            return None

    def add_transaction(self, asset_id, transaction_type, quantity, price, transaction_date):
        with self.lock:
            if self.conn:
                try:
                    self.cursor.execute("INSERT INTO transactions (asset_id, transaction_type, quantity, price, transaction_date) VALUES (?, ?, ?, ?, ?)",
                                        (asset_id, transaction_type, quantity, price, transaction_date))
                    self.conn.commit()
                    return self.cursor.lastrowid
                except sqlite3.Error as e:
                    print(f"Erro ao adicionar transação: {e}")
            return None

    def add_price_history(self, asset_id, price, record_date):
        try:
            conn, cursor = self.get_thread_connection()
            cursor.execute("INSERT OR IGNORE INTO price_history (asset_id, price, record_date) VALUES (?, ?, ?)",
                            (asset_id, price, record_date))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar histórico de preço: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao adicionar histórico de preço: {e}")
            return None

    def add_dividend(self, asset_id, dividend_value, payment_date):
        if self.conn:
            try:
                self.cursor.execute("INSERT INTO dividends (asset_id, dividend_value, payment_date) VALUES (?, ?, ?)",
                                    (asset_id, dividend_value, payment_date))
                self.conn.commit()
                return self.cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar dividendo: {e}")
        return None

    def add_event(self, event_date, event_type, description, asset_id=None):
        if self.conn:
            try:
                self.cursor.execute("INSERT INTO events (event_date, event_type, description, asset_id) VALUES (?, ?, ?, ?)",
                                    (event_date, event_type, description, asset_id))
                self.conn.commit()
                return self.cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar evento: {e}")
        return None

    def add_alert(self, asset_id, alert_type, target_value=None, percentage_change=None):
        if self.conn:
            try:
                self.cursor.execute("INSERT INTO alerts (asset_id, alert_type, target_value, percentage_change) VALUES (?, ?, ?, ?)",
                                    (asset_id, alert_type, target_value, percentage_change))
                self.conn.commit()
                return self.cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar alerta: {e}")
        return None

    def get_events(self, start_date=None, end_date=None):
        if self.conn:
            try:
                query = "SELECT e.id, e.event_date, e.event_type, e.description, a.name FROM events e LEFT JOIN assets a ON e.asset_id = a.id"
                params = []
                if start_date and end_date:
                    query += " WHERE e.event_date BETWEEN ? AND ?"
                    params.append(start_date)
                    params.append(end_date)
                query += " ORDER BY e.event_date ASC"
                self.cursor.execute(query, tuple(params))
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao buscar eventos: {e}")
        return []

    def get_active_alerts(self):
        try:
            conn, cursor = self.get_thread_connection()
            cursor.execute("SELECT al.id, a.name, al.alert_type, al.target_value, al.percentage_change FROM alerts al JOIN assets a ON al.asset_id = a.id WHERE al.is_active = 1")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar alertas ativos: {e}")
            return []
        except Exception as e:
            print(f"Erro inesperado ao buscar alertas ativos: {e}")
            return []

    def deactivate_alert(self, alert_id):
        try:
            conn, cursor = self.get_thread_connection()
            cursor.execute("UPDATE alerts SET is_active = 0 WHERE id = ?", (alert_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao desativar alerta: {e}")
            return False
        except Exception as e:
            print(f"Erro inesperado ao desativar alerta: {e}")
            return False

    def get_all_assets_with_transactions(self):
        try:
            conn, cursor = self.get_thread_connection()
            cursor.execute("""
                SELECT
                    a.id, a.name, a.type,
                    SUM(CASE WHEN t.transaction_type = 'compra' THEN t.quantity ELSE -t.quantity END) as total_quantity,
                    SUM(CASE WHEN t.transaction_type = 'compra' THEN t.quantity * t.price ELSE 0 END) as total_invested
                FROM assets a
                LEFT JOIN transactions t ON a.id = t.asset_id
                GROUP BY a.id, a.name, a.type
                HAVING total_quantity > 0 OR total_invested > 0
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar ativos com transações: {e}")
            return []
        except Exception as e:
            print(f"Erro inesperado ao buscar ativos com transações: {e}")
            return []

    def get_asset_transactions(self, asset_id):
        if self.conn:
            try:
                self.cursor.execute("SELECT * FROM transactions WHERE asset_id = ? ORDER BY transaction_date ASC", (asset_id,))
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao buscar transações do ativo: {e}")
        return []

    def get_price_history(self, asset_id, start_date=None, end_date=None):
        if self.conn:
            try:
                query = "SELECT record_date, price FROM price_history WHERE asset_id = ?"
                params = [asset_id]
                if start_date:
                    query += " AND record_date >= ?"
                    params.append(start_date)
                if end_date:
                    query += " AND record_date <= ?"
                    params.append(end_date)
                query += " ORDER BY record_date ASC"
                self.cursor.execute(query, tuple(params))
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao buscar histórico de preços: {e}")
        return []

    def get_all_price_history(self):
        if self.conn:
            try:
                self.cursor.execute("""
                    SELECT
                        a.name, ph.record_date, ph.price
                    FROM price_history ph
                    JOIN assets a ON ph.asset_id = a.id
                    ORDER BY a.name, ph.record_date
                """)
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao buscar histórico de preços de todos os ativos: {e}")
        return []

    def get_asset_dividends(self, asset_id):
        if self.conn:
            try:
                self.cursor.execute("SELECT * FROM dividends WHERE asset_id = ? ORDER BY payment_date ASC", (asset_id,))
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao buscar dividendos do ativo: {e}")
        return []

    def close(self):
        if self.conn:
            self.conn.close()
        
        # Fechar conexões thread-local
        if hasattr(self._local, 'connection'):
            try:
                self._local.connection.close()
            except:
                pass

    def backup_database(self, backup_path):
        if self.conn:
            try:
                backup_conn = sqlite3.connect(backup_path)
                with backup_conn:
                    self.conn.backup(backup_conn)
                backup_conn.close()
                print(f"Backup do banco de dados criado em: {backup_path}")
                return True
            except sqlite3.Error as e:
                print(f"Erro ao criar backup do banco de dados: {e}")
                return False
        return False

    def restore_database(self, backup_path):
        if self.conn:
            self.close() # Fechar a conexão atual antes de restaurar
            try:
                # Renomear o banco de dados atual para um backup temporário
                import os
                if os.path.exists(self.db_name):
                    os.rename(self.db_name, self.db_name + ".bak")
                
                # Copiar o backup para o nome do banco de dados original
                import shutil
                shutil.copy(backup_path, self.db_name)
                
                self.connect() # Reconectar ao banco de dados restaurado
                print(f"Banco de dados restaurado de: {backup_path}")
                return True
            except Exception as e:
                print(f"Erro ao restaurar banco de dados: {e}")
                # Tentar reverter se a restauração falhar
                if os.path.exists(self.db_name + ".bak"):
                    os.rename(self.db_name + ".bak", self.db_name)
                self.connect()
                return False
        return False

    def get_asset_by_name(self, name):
        if self.conn:
            try:
                self.cursor.execute("SELECT id, name, type FROM assets WHERE name = ?", (name,))
                return self.cursor.fetchone()
            except sqlite3.Error as e:
                print(f"Erro ao buscar ativo por nome: {e}")
        return None

    def get_asset_by_id(self, asset_id):
        if self.conn:
            try:
                self.cursor.execute("SELECT id, name, type FROM assets WHERE id = ?", (asset_id,))
                return self.cursor.fetchone()
            except sqlite3.Error as e:
                print(f"Erro ao buscar ativo por ID: {e}")
        return None

    def export_data_to_csv(self, filename="export_data.csv"):
        if self.conn:
            try:
                # Exportar ativos
                assets_df = pd.read_sql_query("SELECT * FROM assets", self.conn)
                assets_df.to_csv(f"assets_{filename}", index=False)

                # Exportar transações
                transactions_df = pd.read_sql_query("SELECT * FROM transactions", self.conn)
                transactions_df.to_csv(f"transactions_{filename}", index=False)

                # Exportar histórico de preços
                price_history_df = pd.read_sql_query("SELECT * FROM price_history", self.conn)
                price_history_df.to_csv(f"price_history_{filename}", index=False)

                # Exportar dividendos
                dividends_df = pd.read_sql_query("SELECT * FROM dividends", self.conn)
                dividends_df.to_csv(f"dividends_{filename}", index=False)

                # Exportar alertas
                alerts_df = pd.read_sql_query("SELECT * FROM alerts", self.conn)
                alerts_df.to_csv(f"alerts_{filename}", index=False)

                # Exportar eventos
                events_df = pd.read_sql_query("SELECT * FROM events", self.conn)
                events_df.to_csv(f"events_{filename}", index=False)

                print(f"Dados exportados para CSV com sucesso: assets_{filename}, transactions_{filename}, price_history_{filename}, dividends_{filename}, alerts_{filename}, events_{filename}")
                return True
            except Exception as e:
                print(f"Erro ao exportar dados para CSV: {e}")
                return False
        return False

    def import_data_from_csv(self, assets_filename="assets_export_data.csv", transactions_filename="transactions_export_data.csv", price_history_filename="price_history_export_data.csv", dividends_filename="dividends_export_data.csv", alerts_filename="alerts_export_data.csv", events_filename="events_export_data.csv"):
        if self.conn:
            try:
                # Importar ativos
                assets_df = pd.read_csv(assets_filename)
                assets_df.to_sql("assets", self.conn, if_exists="append", index=False)

                # Importar transações
                transactions_df = pd.read_csv(transactions_filename)
                transactions_df.to_sql("transactions", self.conn, if_exists="append", index=False)

                # Importar histórico de preços
                price_history_df = pd.read_csv(price_history_filename)
                price_history_df.to_sql("price_history", self.conn, if_exists="append", index=False)

                # Importar dividendos
                dividends_df = pd.read_csv(dividends_filename)
                dividends_df.to_sql("dividends", self.conn, if_exists="append", index=False)

                # Importar alertas
                alerts_df = pd.read_csv(alerts_filename)
                alerts_df.to_sql("alerts", self.conn, if_exists="append", index=False)

                # Importar eventos
                events_df = pd.read_csv(events_filename)
                events_df.to_sql("events", self.conn, if_exists="append", index=False)

                print("Dados importados de CSV com sucesso.")
                return True
            except Exception as e:
                print(f"Erro ao importar dados de CSV: {e}")
                return False
        return False

    def export_data_to_json(self, filename="export_data.json"):
        if self.conn:
            try:
                data = {
                    "assets": [],
                    "transactions": [],
                    "price_history": [],
                    "dividends": [],
                    "alerts": [],
                    "events": []
                }

                self.cursor.execute("SELECT * FROM assets")
                assets_cols = [description[0] for description in self.cursor.description]
                for row in self.cursor.fetchall():
                    data["assets"].append(dict(zip(assets_cols, row)))

                self.cursor.execute("SELECT * FROM transactions")
                transactions_cols = [description[0] for description in self.cursor.description]
                for row in self.cursor.fetchall():
                    data["transactions"].append(dict(zip(transactions_cols, row)))

                self.cursor.execute("SELECT * FROM price_history")
                price_history_cols = [description[0] for description in self.cursor.description]
                for row in self.cursor.fetchall():
                    data["price_history"].append(dict(zip(price_history_cols, row)))

                self.cursor.execute("SELECT * FROM dividends")
                dividends_cols = [description[0] for description in self.cursor.description]
                for row in self.cursor.fetchall():
                    data["dividends"].append(dict(zip(dividends_cols, row)))

                self.cursor.execute("SELECT * FROM alerts")
                alerts_cols = [description[0] for description in self.cursor.description]
                for row in self.cursor.fetchall():
                    data["alerts"].append(dict(zip(alerts_cols, row)))

                self.cursor.execute("SELECT * FROM events")
                events_cols = [description[0] for description in self.cursor.description]
                for row in self.cursor.fetchall():
                    data["events"].append(dict(zip(events_cols, row)))

                with open(filename, "w") as f:
                    json.dump(data, f, indent=4)

                print(f"Dados exportados para JSON com sucesso: {filename}")
                return True
            except Exception as e:
                print(f"Erro ao exportar dados para JSON: {e}")
                return False
        return False

    def import_data_from_json(self, filename="export_data.json"):
        if self.conn:
            try:
                with open(filename, "r") as f:
                    data = json.load(f)

                # Verificar se é o formato de carteira simplificado
                if isinstance(data, list) and len(data) > 0 and "asset_id" in data[0]:
                    return self._import_carteira_format(data)
                
                # Formato completo (assets, transactions, etc.)
                if isinstance(data, dict) and "assets" in data:
                    return self._import_full_format(data)
                
                print("Formato de JSON não reconhecido.")
                return False
                
            except Exception as e:
                print(f"Erro ao importar dados de JSON: {e}")
                return False
        return False

    def _import_carteira_format(self, carteira_data):
        """Importa formato simplificado de carteira"""
        try:
            import datetime
            
            for item in carteira_data:
                asset_id = item["asset_id"]
                current_quantity = item["current_quantity"]
                average_price = item["average_price"]
                
                # Verificar se o ativo já existe
                existing_asset = self.get_asset_by_name(asset_id)
                if not existing_asset:
                    # Criar ativo se não existir (assumir tipo "Ação" por padrão)
                    asset_db_id = self.add_asset(asset_id, "Ação")
                else:
                    asset_db_id = existing_asset[0]
                
                if asset_db_id and current_quantity > 0:
                    # Adicionar transação de compra para representar a posição atual
                    today = datetime.datetime.now().strftime("%Y-%m-%d")
                    self.add_transaction(asset_db_id, "compra", current_quantity, average_price, today)
                    
                    # Adicionar preço atual ao histórico
                    self.add_price_history(asset_db_id, average_price, today)
            
            print("Dados de carteira importados com sucesso.")
            return True
            
        except Exception as e:
            print(f"Erro ao importar formato de carteira: {e}")
            return False

    def _import_full_format(self, data):
        """Importa formato completo de dados"""
        try:
            # Importar ativos
            for asset in data["assets"]:
                self.add_asset(asset["name"], asset["type"])

            # Importar transações
            for transaction in data["transactions"]:
                # Usar asset_id diretamente do JSON exportado
                asset_id = transaction["asset_id"]
                self.add_transaction(asset_id, transaction["transaction_type"], transaction["quantity"], transaction["price"], transaction["transaction_date"])

            # Importar histórico de preços
            for price_entry in data["price_history"]:
                # Usar asset_id diretamente do JSON exportado
                asset_id = price_entry["asset_id"]
                self.add_price_history(asset_id, price_entry["price"], price_entry["record_date"])
            
            # Importar dividendos
            for dividend_entry in data["dividends"]:
                # Usar asset_id diretamente do JSON exportado
                asset_id = dividend_entry["asset_id"]
                self.add_dividend(asset_id, dividend_entry["dividend_value"], dividend_entry["payment_date"])

            # Importar alertas
            for alert_entry in data["alerts"]:
                # Usar asset_id diretamente do JSON exportado
                asset_id = alert_entry["asset_id"]
                self.add_alert(asset_id, alert_entry["alert_type"], alert_entry["target_value"], alert_entry["percentage_change"])

            # Importar eventos
            for event_entry in data["events"]:
                asset_id = event_entry["asset_id"]
                self.add_event(event_entry["event_date"], event_entry["event_type"], event_entry["description"], asset_id)

            print("Dados completos importados de JSON com sucesso.")
            return True
            
        except Exception as e:
            print(f"Erro ao importar formato completo: {e}")
            return False

    def delete_asset(self, asset_id):
        if self.conn:
            try:
                # Excluir transações, histórico de preços, dividendos, alertas e eventos relacionados ao ativo
                self.cursor.execute("DELETE FROM transactions WHERE asset_id = ?", (asset_id,))
                self.cursor.execute("DELETE FROM price_history WHERE asset_id = ?", (asset_id,))
                self.cursor.execute("DELETE FROM dividends WHERE asset_id = ?", (asset_id,))
                self.cursor.execute("DELETE FROM alerts WHERE asset_id = ?", (asset_id,))
                self.cursor.execute("DELETE FROM events WHERE asset_id = ?", (asset_id,))
                # Excluir o ativo
                self.cursor.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
                self.conn.commit()
                return True
            except Exception as e:
                print(f'Erro ao excluir ativo: {e}')
        return False


if __name__ == "__main__":
    db = DatabaseManager("test_carteira.db")

    # Adicionar um ativo de exemplo
    asset_id_petr4 = db.add_asset("PETR4", "Ação")
    if asset_id_petr4:
        db.add_transaction(asset_id_petr4, "compra", 100, 25.00, "2023-01-15")
        db.add_price_history(asset_id_petr4, 25.50, "2023-01-15")
        db.add_price_history(asset_id_petr4, 26.00, "2023-01-16")
        db.add_dividend(asset_id_petr4, 0.50, "2023-02-01")
        db.add_alert(asset_id_petr4, "price_target", target_value=27.00)
        db.add_event("2023-02-10", "dividendo", "Pagamento de dividendos PETR4", asset_id_petr4)

    asset_id_mxrf11 = db.add_asset("MXRF11", "FII")
    if asset_id_mxrf11:
        db.add_transaction(asset_id_mxrf11, "compra", 200, 10.00, "2022-11-20")
        db.add_price_history(asset_id_mxrf11, 10.10, "2022-11-20")
        db.add_price_history(asset_id_mxrf11, 10.20, "2022-11-21")
        db.add_dividend(asset_id_mxrf11, 0.10, "2023-01-10")
        db.add_alert(asset_id_mxrf11, "percentage_change", percentage_change=5.0)
        db.add_event("2023-01-15", "vencimento", "Vencimento de opções MXRF11", asset_id_mxrf11)

    # Buscar todos os ativos com transações
    assets_with_transactions = db.get_all_assets_with_transactions()
    print("Ativos no banco de dados com transações:")
    for asset in assets_with_transactions:
        print(asset)

    # Buscar transações de um ativo
    if asset_id_petr4:
        petr4_transactions = db.get_asset_transactions(asset_id_petr4)
        print(f"Transações de PETR4: {petr4_transactions}")

    # Buscar histórico de preços de um ativo
    if asset_id_petr4:
        petr4_price_history = db.get_price_history(asset_id_petr4)
        print(f"Histórico de preços de PETR4: {petr4_price_history}")

    # Buscar dividendos de um ativo
    if asset_id_petr4:
        petr4_dividends = db.get_asset_dividends(asset_id_petr4)
        print(f"Dividendos de PETR4: {petr4_dividends}")

    # Buscar alertas ativos
    active_alerts = db.get_active_alerts()
    print(f"Alertas Ativos: {active_alerts}")

    # Buscar eventos
    events = db.get_events()
    print(f"Eventos: {events}")

    # Testar backup e restauração
    db.backup_database("test_carteira_backup.db")
    # db.restore_database("test_carteira_backup.db")

    # Testar exportação/importação
    db.export_data_to_csv("my_carteira_export.csv")
    db.export_data_to_json("my_carteira_export.json")

    db.close()



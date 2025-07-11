import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from tkinter import messagebox

MSG_DADOS_INSUFICIENTES = (
    "Não há dados de histórico suficientes no banco de dados para realizar esta operação.\n"
    "Por favor, cadastre ou importe mais dados de preços históricos para os ativos da carteira."
)
MSG_BUSCA_API = "Tentando buscar dados históricos de 1 ano atrás automaticamente via API (Yahoo Finance)..."

class ProjectionSimulation:
    def __init__(self, db_manager, yf_integration):
        self.db = db_manager
        self.yf = yf_integration

    def _show_warning(self, msg, gui_parent=None):
        print(msg)
        if gui_parent:
            try:
                messagebox.showwarning("Dados insuficientes", msg, parent=gui_parent)
            except Exception:
                pass

    def get_carteira_daily_returns(self, assets_data, start_date=None, end_date=None, gui_parent=None):
        carteira_returns = pd.Series(dtype=float)
        for asset_id, name, quantity in assets_data:
            price_history = self.db.get_price_history(asset_id, start_date, end_date)
            if price_history and len(price_history) > 1:
                df = pd.DataFrame(price_history, columns=["Date", "Price"])
                df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
                df = df.dropna(subset=["Date"])
                df.set_index("Date", inplace=True)
                df["Daily_Return"] = df["Price"].pct_change()
                if carteira_returns.empty:
                    carteira_returns = df["Daily_Return"]
                else:
                    carteira_returns = carteira_returns.add(df["Daily_Return"], fill_value=0)
        if carteira_returns.empty or len(carteira_returns.dropna()) < 2:
            self._show_warning(MSG_DADOS_INSUFICIENTES, gui_parent)
            self._show_warning(MSG_BUSCA_API, gui_parent)
            return pd.Series(dtype=float)
        return carteira_returns.dropna()

    def monte_carlo_simulation(self, initial_carteira_value, assets_data, num_simulations=1000, num_days=252, gui_parent=None):
        daily_returns = self.get_carteira_daily_returns(assets_data, gui_parent=gui_parent)
        if daily_returns.empty or len(daily_returns) < 2:
            self._show_warning(MSG_DADOS_INSUFICIENTES, gui_parent)
            self._show_warning(MSG_BUSCA_API, gui_parent)
            return None
        mean_daily_return = daily_returns.mean()
        std_daily_return = daily_returns.std()
        simulated_values = np.zeros((num_days, num_simulations))
        simulated_values[0] = initial_carteira_value
        for s in range(num_simulations):
            for day in range(1, num_days):
                daily_return = np.random.normal(mean_daily_return, std_daily_return)
                simulated_values[day, s] = simulated_values[day-1, s] * (1 + daily_return)
        return simulated_values

    def plot_monte_carlo_results(self, simulated_values, initial_date=None, gui_parent=None):
        if simulated_values is None:
            self._show_warning(MSG_DADOS_INSUFICIENTES, gui_parent)
            self._show_warning(MSG_BUSCA_API, gui_parent)
            return
        plt.figure(figsize=(12, 7))
        for i in range(simulated_values.shape[1]):
            plt.plot(simulated_values[:, i], alpha=0.1, color='blue')
        plt.plot(np.mean(simulated_values, axis=1), color='red', linestyle='--', label='Média das Simulações')
        plt.title('Simulação de Monte Carlo do Valor da Carteira')
        plt.xlabel('Dias Futuros')
        plt.ylabel('Valor da Carteira')
        plt.grid(True)
        plt.legend()
        plt.show()

    def linear_projection(self, initial_value, annual_return_rate, num_years, gui_parent=None):
        if initial_value == 0 or annual_return_rate is None or num_years is None or num_years < 1:
            self._show_warning(MSG_DADOS_INSUFICIENTES, gui_parent)
            return None
        projected_values = [initial_value]
        for year in range(1, num_years + 1):
            projected_values.append(projected_values[-1] * (1 + annual_return_rate))
        return projected_values

    def plot_linear_projection(self, projected_values, num_years, gui_parent=None):
        if projected_values is None:
            self._show_warning(MSG_DADOS_INSUFICIENTES, gui_parent)
            return
        years = list(range(num_years + 1))
        plt.figure(figsize=(10, 6))
        plt.plot(years, projected_values, marker='o', linestyle='-', color='green')
        plt.title('Projeção Linear do Valor da Carteira')
        plt.xlabel('Anos Futuros')
        plt.ylabel('Valor da Carteira')
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    # Exemplo de uso (requer um banco de dados e integração yfinance)
    from database_manager import DatabaseManager
    from yfinance_integration import YFinanceIntegration
    
    db = DatabaseManager("test_carteira.db")
    yf = YFinanceIntegration()
    ps = ProjectionSimulation(db, yf)

    # Adicionar ativos de exemplo e transações para ter dados de retorno
    asset_id_petr4 = db.get_asset_by_name("PETR4")
    if not asset_id_petr4:
        asset_id_petr4 = db.add_asset("PETR4", "Ação")
        if asset_id_petr4:
            db.add_transaction(asset_id_petr4, "compra", 100, 25.00, "2023-01-15")
            db.add_price_history(asset_id_petr4, 25.50, "2023-01-15")
            db.add_price_history(asset_id_petr4, 26.00, "2023-01-16")
            db.add_price_history(asset_id_petr4, 25.80, "2023-01-17")
            db.add_price_history(asset_id_petr4, 26.50, "2023-01-18")
            db.add_price_history(asset_id_petr4, 27.00, "2023-01-19")

    asset_id_vale3 = db.get_asset_by_name("VALE3")
    if not asset_id_vale3:
        asset_id_vale3 = db.add_asset("VALE3", "Ação")
        if asset_id_vale3:
            db.add_transaction(asset_id_vale3, "compra", 50, 70.00, "2023-01-10")
            db.add_price_history(asset_id_vale3, 70.50, "2023-01-10")
            db.add_price_history(asset_id_vale3, 71.00, "2023-01-11")
            db.add_price_history(asset_id_vale3, 69.80, "2023-01-12")

    # Simulação de Monte Carlo
    assets_for_simulation = db.get_all_assets_with_transactions()
    # Transformar para o formato (asset_id, name, quantity)
    formatted_assets = []
    for asset in assets_for_simulation:
        formatted_assets.append((asset[0], asset[1], asset[3])) # id, name, total_quantity

    initial_value = 10000.0
    sim_results = ps.monte_carlo_simulation(initial_value, formatted_assets)
    if sim_results is not None:
        ps.plot_monte_carlo_results(sim_results)

    # Projeção Linear
    linear_proj_results = ps.linear_projection(initial_value, 0.10, 5) # 10% de retorno anual por 5 anos
    ps.plot_linear_projection(linear_proj_results, 5)

    db.close()



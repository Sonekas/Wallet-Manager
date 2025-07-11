import pandas as pd
import numpy as np
import datetime
from tkinter import messagebox

MSG_DADOS_INSUFICIENTES = (
    "Não há dados de histórico suficientes no banco de dados para realizar esta operação.\n"
    "Por favor, cadastre ou importe mais dados de preços históricos para os ativos da carteira."
)
MSG_BUSCA_API = "Tentando buscar dados históricos de 1 ano atrás automaticamente via API (Yahoo Finance)..."

class RiskAnalysis:
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

    def calculate_daily_returns(self, asset_name, start_date=None, end_date=None, gui_parent=None):
        asset = self.db.get_asset_by_name(asset_name)
        if not asset:
            self._show_warning(MSG_DADOS_INSUFICIENTES, gui_parent)
            return None
        asset_id = asset[0]

        price_history = self.db.get_price_history(asset_id, start_date, end_date)
        if not price_history or len(price_history) < 2:
            self._show_warning(MSG_DADOS_INSUFICIENTES, gui_parent)
            self._show_warning(MSG_BUSCA_API, gui_parent)
            if not end_date:
                end_date_obj = datetime.date.today()
                end_date = end_date_obj.strftime("%Y-%m-%d")
            else:
                end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            start_date_obj = end_date_obj - datetime.timedelta(days=365)
            start_date = start_date_obj.strftime("%Y-%m-%d")
            yf_data = self.yf.get_historical_prices(asset_name + ".SA", start_date, end_date)
            if yf_data and len(yf_data) >= 2:
                print(f"✅ Dados do Yahoo Finance obtidos para {asset_name}: {len(yf_data)} registros")
                for date, price in yf_data:
                    self.db.add_price_history(asset_id, price, date)
                df = pd.DataFrame(yf_data, columns=["Date", "Price"])
                df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
                df = df.dropna(subset=["Date"])
                df.set_index("Date", inplace=True)
                df["Daily_Return"] = df["Price"].pct_change()
                return df["Daily_Return"].dropna()
            else:
                self._show_warning(MSG_DADOS_INSUFICIENTES, gui_parent)
                return None
        df = pd.DataFrame(price_history, columns=["Date", "Price"])
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Date"])
        df.set_index("Date", inplace=True)
        df["Daily_Return"] = df["Price"].pct_change()
        return df["Daily_Return"].dropna()

    def calculate_volatility(self, asset_name, start_date=None, end_date=None, gui_parent=None):
        daily_returns = self.calculate_daily_returns(asset_name, start_date, end_date, gui_parent)
        if daily_returns is None or daily_returns.empty or len(daily_returns) < 2:
            self._show_warning(MSG_DADOS_INSUFICIENTES, gui_parent)
            return 0.0
        volatility = daily_returns.std() * np.sqrt(252)
        print(f"📊 Volatilidade de {asset_name}: {volatility:.4f} ({len(daily_returns)} dias de dados)")
        return volatility

    def calculate_beta(self, asset_name, benchmark_ticker, start_date=None, end_date=None, gui_parent=None):
        asset_returns = self.calculate_daily_returns(asset_name, start_date, end_date, gui_parent)
        if asset_returns is None or asset_returns.empty or len(asset_returns) < 2:
            self._show_warning(MSG_DADOS_INSUFICIENTES, gui_parent)
            return 0.0
        benchmark_data = self.yf.get_historical_prices(benchmark_ticker, start_date, end_date)
        if not benchmark_data or len(benchmark_data) < 2:
            self._show_warning(MSG_DADOS_INSUFICIENTES, gui_parent)
            self._show_warning(MSG_BUSCA_API, gui_parent)
            return 0.0
        benchmark_df = pd.DataFrame(benchmark_data, columns=["Date", "Price"])
        benchmark_df["Date"] = pd.to_datetime(benchmark_df["Date"], dayfirst=True, errors="coerce")
        benchmark_df = benchmark_df.dropna(subset=["Date"])
        benchmark_df.set_index("Date", inplace=True)
        benchmark_df["Daily_Return"] = benchmark_df["Price"].pct_change()
        benchmark_daily_returns = benchmark_df["Daily_Return"].dropna()
        combined_returns = pd.concat([asset_returns, benchmark_daily_returns], axis=1).dropna()
        combined_returns.columns = ["Asset", "Benchmark"]
        if combined_returns.empty or len(combined_returns) < 2:
            self._show_warning(MSG_DADOS_INSUFICIENTES, gui_parent)
            return 0.0
        covariance = combined_returns["Asset"].cov(combined_returns["Benchmark"])
        benchmark_variance = combined_returns["Benchmark"].var()
        if benchmark_variance == 0:
            self._show_warning(MSG_DADOS_INSUFICIENTES, gui_parent)
            return 0.0
        beta = covariance / benchmark_variance
        print(f"📊 Beta de {asset_name} vs {benchmark_ticker}: {beta:.4f} ({len(combined_returns)} dias de dados)")
        return beta

if __name__ == "__main__":
    # Exemplo de uso (requer um banco de dados e integração yfinance)
    from database_manager import DatabaseManager
    from yfinance_integration import YFinanceIntegration
    
    db = DatabaseManager("test_carteira.db")
    yf = YFinanceIntegration()
    ra = RiskAnalysis(db, yf)

    # Adicionar um ativo de exemplo (se não existir)
    asset_id_petr4 = db.get_asset_by_name("PETR4")
    if not asset_id_petr4:
        asset_id_petr4 = db.add_asset("PETR4", "Ação")
        if asset_id_petr4:
            db.add_transaction(asset_id_petr4, "compra", 100, 25.00, "2023-01-15")
            # Adicionar alguns dados de histórico de preço para PETR4
            db.add_price_history(asset_id_petr4, 25.50, "2023-01-15")
            db.add_price_history(asset_id_petr4, 26.00, "2023-01-16")
            db.add_price_history(asset_id_petr4, 25.80, "2023-01-17")
            db.add_price_history(asset_id_petr4, 26.50, "2023-01-18")
            db.add_price_history(asset_id_petr4, 27.00, "2023-01-19")

    # Calcular volatilidade
    volatility = ra.calculate_volatility("PETR4", start_date="2023-01-01", end_date="2023-01-31")
    print(f"Volatilidade de PETR4: {volatility:.4f}")

    # Calcular Beta (usando IBOV como benchmark)
    beta = ra.calculate_beta("PETR4", "^BVSP", start_date="2023-01-01", end_date="2023-01-31")
    print(f"Beta de PETR4 vs IBOV: {beta:.4f}")

    db.close()



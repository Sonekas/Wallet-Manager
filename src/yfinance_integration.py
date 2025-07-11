import yfinance as yf
import pandas as pd

class YFinanceIntegration:
    def __init__(self):
        pass

    def get_current_price(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if not hist.empty:
                return hist["Close"].iloc[-1]
            else:
                print(f"Não foi possível obter dados para {ticker}")
                return None
        except Exception as e:
            print(f"Erro ao consultar {ticker} no yfinance: {e}")
            return None

    def get_historical_prices(self, ticker, start_date=None, end_date=None):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            if not hist.empty:
                # Retorna uma lista de tuplas (data, preço de fechamento)
                return list(zip(hist.index.strftime("%d/%m/%Y"), hist["Close"].tolist()))
            else:
                print(f"Não foi possível obter dados históricos para {ticker}")
                return None
        except Exception as e:
            print(f"Erro ao consultar histórico de {ticker} no yfinance: {e}")
            return None

if __name__ == "__main__":
    yf_integration = YFinanceIntegration()
    # Exemplo de uso
    price_petr4 = yf_integration.get_current_price("PETR4.SA") # Para ações brasileiras, geralmente usa .SA
    if price_petr4:
        print(f"Preço atual de PETR4.SA: {price_petr4:.2f}")

    price_aapl = yf_integration.get_current_price("AAPL")
    if price_aapl:
        print(f"Preço atual de AAPL: {price_aapl:.2f}")

    price_invalid = yf_integration.get_current_price("INVALIDTICKER")
    if price_invalid:
        print(f"Preço atual de INVALIDTICKER: {price_invalid:.2f}")

    # Teste de histórico de preços
    historical_petr4 = yf_integration.get_historical_prices("PETR4.SA", start_date="2023-01-01", end_date="2023-01-31")
    if historical_petr4:
        print(f"Histórico de PETR4.SA (primeiros 5): {historical_petr4[:5]}")

    historical_ibov = yf_integration.get_historical_prices("^BVSP", start_date="2023-01-01", end_date="2023-01-31")
    if historical_ibov:
        print(f"Histórico de ^BVSP (primeiros 5): {historical_ibov[:5]}")



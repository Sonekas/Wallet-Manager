import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import pandas as pd
from collections import OrderedDict

class PlotManager:
    def __init__(self):
        pass

    def plot_price_history(self, asset_name, price_history_data):
        # Parsing robusto das datas
        parsed = []
        for row in price_history_data:
            date_str = row[0]
            price = row[1]
            try:
                date = datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue
            parsed.append((date, price))

        if not parsed:
            print(f"Não há dados de histórico de preços válidos para {asset_name}.")
            return

        # Ordenar por data
        parsed.sort(key=lambda x: x[0])

        # Remover datas duplicadas (mantendo o último preço do dia)
        date_price_dict = OrderedDict()
        for date, price in parsed:
            date_price_dict[date] = price
        dates = list(date_price_dict.keys())
        prices = list(date_price_dict.values())

        plt.figure(figsize=(10, 6))
        plt.plot(dates, prices, marker=".", linestyle="-", color="blue")
        plt.title(f"Evolução de Preço - {asset_name}")
        plt.xlabel("Data")
        plt.ylabel("Preço")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_comparison_with_benchmark(self, asset_name, asset_price_history, benchmark_ticker, benchmark_price_history):
        if not asset_price_history or not benchmark_price_history:
            print("Dados insuficientes para plotar a comparação.")
            return

        # Converter para DataFrame para facilitar o manuseio
        df_asset = pd.DataFrame(asset_price_history, columns=["Date", "Price"])
        df_asset["Date"] = pd.to_datetime(df_asset["Date"])
        df_asset.set_index("Date", inplace=True)
        df_asset.rename(columns={"Price": asset_name}, inplace=True)

        df_benchmark = pd.DataFrame(benchmark_price_history, columns=["Date", "Price"])
        df_benchmark["Date"] = pd.to_datetime(df_benchmark["Date"])
        df_benchmark.set_index("Date", inplace=True)
        df_benchmark.rename(columns={"Price": benchmark_ticker}, inplace=True)

        # Combinar os DataFrames e normalizar para o ponto de partida (primeiro dia)
        combined_df = pd.concat([df_asset, df_benchmark], axis=1).dropna()
        if combined_df.empty:
            print("Não há datas em comum para a comparação.")
            return

        # Normalizar os preços para 100 no primeiro dia para comparar a performance
        normalized_df = (combined_df / combined_df.iloc[0]) * 100

        plt.figure(figsize=(12, 7))
        plt.plot(normalized_df.index, normalized_df[asset_name], label=asset_name, color='blue')
        plt.plot(normalized_df.index, normalized_df[benchmark_ticker], label=benchmark_ticker, color='red', linestyle='--')
        plt.title(f"Comparativo de Performance: {asset_name} vs {benchmark_ticker}")
        plt.xlabel("Data")
        plt.ylabel("Performance Relativa (Base 100)")
        plt.legend()
        plt.grid(True)

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%Y"))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Exemplo de uso
    plot_m = PlotManager()
    sample_price_history_asset = [
        ("01/01/2023", 100.00),
        ("02/01/2023", 101.50),
        ("03/01/2023", 102.20),
        ("04/01/2023", 103.00),
        ("05/01/2023", 102.80),
    ]
    sample_price_history_benchmark = [
        ("01/01/2023", 5000.00),
        ("02/01/2023", 5050.00),
        ("03/01/2023", 5010.00),
        ("04/01/2023", 5080.00),
        ("05/01/2023", 5070.00),
    ]
    plot_m.plot_comparison_with_benchmark("ATIVO_X", sample_price_history_asset, "BENCHMARK_Y", sample_price_history_benchmark)



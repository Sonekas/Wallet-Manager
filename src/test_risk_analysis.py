#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from yfinance_integration import YFinanceIntegration
from risk_analysis import RiskAnalysis
import datetime

def test_risk_analysis():
    """Testa a análise de risco para identificar problemas"""
    
    # Inicializar componentes
    db = DatabaseManager("investment_carteira.db")
    yf = YFinanceIntegration()
    ra = RiskAnalysis(db, yf)
    
    print("=== TESTE DE ANÁLISE DE RISCO ===\n")
    
    # 1. Verificar ativos no banco
    print("1. Verificando ativos no banco de dados:")
    assets = db.get_all_assets_with_transactions()
    if not assets:
        print("   ❌ Nenhum ativo encontrado no banco de dados!")
        return
    
    for asset in assets:
        asset_id, asset_name, asset_type, total_quantity, total_invested = asset
        print(f"   ✅ {asset_name} ({asset_type}) - Qtd: {total_quantity}, Investido: R$ {total_invested:.2f}")
    
    # 2. Verificar histórico de preços para cada ativo
    print("\n2. Verificando histórico de preços:")
    for asset in assets:
        asset_id, asset_name, asset_type, total_quantity, total_invested = asset
        print(f"\n   📊 {asset_name}:")
        
        # Buscar histórico de preços
        price_history = db.get_price_history(asset_id)
        if not price_history:
            print(f"      ❌ Nenhum histórico de preços encontrado!")
            
            # Tentar buscar dados do Yahoo Finance
            print(f"      🔍 Buscando dados do Yahoo Finance...")
            try:
                # Buscar dados dos últimos 30 dias
                end_date = datetime.date.today()
                start_date = end_date - datetime.timedelta(days=30)
                
                yf_data = yf.get_historical_prices(asset_name + ".SA", 
                                                  start_date.strftime("%Y-%m-%d"), 
                                                  end_date.strftime("%Y-%m-%d"))
                
                if yf_data:
                    print(f"      ✅ Dados do Yahoo Finance encontrados: {len(yf_data)} registros")
                    
                    # Adicionar dados ao banco
                    for date, price in yf_data:
                        db.add_price_history(asset_id, price, date)
                        print(f"         Adicionado: {date} - R$ {price:.2f}")
                    
                    # Recalcular volatilidade
                    volatility = ra.calculate_volatility(asset_name, 
                                                       start_date.strftime("%Y-%m-%d"), 
                                                       end_date.strftime("%Y-%m-%d"))
                    print(f"      📈 Volatilidade calculada: {volatility:.4f}")
                else:
                    print(f"      ❌ Não foi possível obter dados do Yahoo Finance")
            except Exception as e:
                print(f"      ❌ Erro ao buscar dados: {e}")
        else:
            print(f"      ✅ Histórico encontrado: {len(price_history)} registros")
            
            # Mostrar alguns registros
            for i, (date, price) in enumerate(price_history[:5]):
                print(f"         {date}: R$ {price:.2f}")
            if len(price_history) > 5:
                print(f"         ... e mais {len(price_history) - 5} registros")
            
            # Calcular volatilidade
            volatility = ra.calculate_volatility(asset_name)
            print(f"      📈 Volatilidade: {volatility:.4f}")
            
            # Calcular Beta vs IBOV
            beta = ra.calculate_beta(asset_name, "^BVSP")
            print(f"      📊 Beta vs IBOV: {beta:.4f}")
    
    # 3. Teste específico com PETR4
    print("\n3. Teste específico com PETR4:")
    petr4_asset = db.get_asset_by_name("PETR4")
    if petr4_asset:
        asset_id = petr4_asset[0]
        print(f"   ✅ PETR4 encontrado (ID: {asset_id})")
        
        # Verificar dados de retornos diários
        daily_returns = ra.calculate_daily_returns("PETR4")
        if daily_returns is not None and not daily_returns.empty:
            print(f"   📊 Retornos diários: {len(daily_returns)} registros")
            print(f"      Média: {daily_returns.mean():.6f}")
            print(f"      Desvio padrão: {daily_returns.std():.6f}")
            print(f"      Mínimo: {daily_returns.min():.6f}")
            print(f"      Máximo: {daily_returns.max():.6f}")
            
            # Volatilidade anualizada
            volatility = ra.calculate_volatility("PETR4")
            print(f"   📈 Volatilidade anualizada: {volatility:.4f}")
        else:
            print(f"   ❌ Não foi possível calcular retornos diários")
    else:
        print(f"   ❌ PETR4 não encontrado no banco")
    
    db.close()
    print("\n=== FIM DO TESTE ===")

if __name__ == "__main__":
    test_risk_analysis() 
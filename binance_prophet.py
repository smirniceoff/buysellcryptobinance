import pandas as pd
import numpy as np
from binance.client import Client
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
from ta.trend import SMAIndicator, EMAIndicator
from prophet import Prophet
import time

# Configurações da API da Binance
api_key = "SUA_API_KEY"
api_secret = "SEU_API_SECRET"
client = Client(api_key, api_secret)

def get_binance_data(symbol, interval, lookback):
    """Obtém os dados históricos de velas da Binance."""
    klines = client.get_klines(symbol=symbol, interval=interval, limit=lookback)
    data = pd.DataFrame(klines, columns=["time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore"])
    data = data[["time", "open", "high", "low", "close", "volume"]]
    data["time"] = pd.to_datetime(data["time"], unit="ms")
    data.set_index("time", inplace=True)
    data = data.astype(float)
    return data

def calculate_indicators(data):
    """Calcula RSI, MACD, Médias Móveis e Bandas de Bollinger."""
    data["rsi"] = RSIIndicator(data["close"], window=14).rsi()
    macd = MACD(data["close"], window_slow=26, window_fast=12, window_sign=9)
    data["macd"] = macd.macd()
    data["macd_signal"] = macd.macd_signal()
    bollinger = BollingerBands(data["close"], window=20, window_dev=2)
    data["bollinger_high"] = bollinger.bollinger_hband()
    data["bollinger_low"] = bollinger.bollinger_lband()
    data["sma_50"] = SMAIndicator(data["close"], window=50).sma_indicator()
    data["ema_20"] = EMAIndicator(data["close"], window=20).ema_indicator()
    return data

def predict_future_prices(data):
    """Usa Prophet para prever preços futuros."""
    prophet_data = data.reset_index()[["time", "close"]].rename(columns={"time": "ds", "close": "y"})
    model = Prophet()
    model.fit(prophet_data)
    future = model.make_future_dataframe(periods=10, freq='min')
    forecast = model.predict(future)
    return forecast

def analyze_and_trade(data):
    """Analisa indicadores e decide compra/venda."""
    latest = data.iloc[-1]
    decision = "Hold"

    # Regras básicas de compra/venda
    if latest["rsi"] < 30 and latest["close"] < latest["bollinger_low"]:
        decision = "Buy"
    elif latest["rsi"] > 70 and latest["close"] > latest["bollinger_high"]:
        decision = "Sell"

    # MACD cruzando sinal
    if latest["macd"] > latest["macd_signal"] and decision != "Sell":
        decision = "Buy"
    elif latest["macd"] < latest["macd_signal"] and decision != "Buy":
        decision = "Sell"

    return decision

def main():
    symbol = "BTCUSDT"
    interval = Client.KLINE_INTERVAL_1MINUTE
    lookback = 500

    while True:
        try:
            print("Obtendo dados...")
            data = get_binance_data(symbol, interval, lookback)
            data = calculate_indicators(data)

            print("Prevendo preços futuros...")
            forecast = predict_future_prices(data)

            print("Analisando e decidindo...")
            decision = analyze_and_trade(data)

            print(f"Decisão: {decision}")
            
            # Simula ação de compra/venda (ou substitua por integração real de trade)
            if decision == "Buy":
                print("Sinal de Compra detectado!")
            elif decision == "Sell":
                print("Sinal de Venda detectado!")

            # Pausa antes da próxima análise
            time.sleep(60)
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
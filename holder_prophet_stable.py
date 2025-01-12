import pandas as pd
import numpy as np
from binance.client import Client
import ta
from prophet import Prophet

# Substitua pelas suas chaves de API
api_key = 'SUA_CHAVE_API'
api_secret = 'SUA_CHAVE_SECRETA'

# Inicializa o cliente da Binance
client = Client(api_key, api_secret)

# Função para obter dados históricos de preço
def get_historical_data(symbol, interval='1h', lookback=100):
    """Obtém dados históricos de preço da Binance"""
    data = client.get_historical_klines(symbol, interval, f"{lookback} hours ago UTC")
    df = pd.DataFrame(data, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 'Number of Trades', 'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'])
    df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
    df.set_index('Open Time', inplace=True)
    df = df.astype(float)
    return df

# Função para calcular indicadores de análise técnica
def calculate_indicators(df):
    """Calcula indicadores técnicos como SMA, EMA, RSI, MACD e Bollinger Bands"""
    # Médias móveis
    df['SMA_20'] = df['Close'].rolling(window=20).mean()  # Média Móvel Simples de 20 períodos
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()  # Média Móvel Exponencial de 20 períodos
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()  # Média Móvel Exponencial de 50 períodos
    
    # RSI (Índice de Força Relativa)
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

    # MACD (Moving Average Convergence Divergence)
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
    df['BB_bbm'] = bb.bollinger_mavg()  # Média móvel da banda de Bollinger
    df['BB_bbh'] = bb.bollinger_hband()  # Banda superior
    df['BB_bbl'] = bb.bollinger_lband()  # Banda inferior

    return df

# Função para prever a tendência com Prophet

def forecast_trend(df):
    """Previsão de tendência usando Prophet"""
    
    # Criação do DataFrame para Prophet com as colunas ds (data) e y (valor de fechamento)
    df_prophet = df[['Close']].reset_index()  # Use a coluna 'Close' para a previsão
    df_prophet.rename(columns={'Open Time': 'ds', 'Close': 'y'}, inplace=True)
    
    # Verifica se o DataFrame está correto
    #print(df_prophet.head())
    
    # Instanciando o modelo Prophet
    model = Prophet()
    
    # Ajustar o modelo aos dados históricos
    model.fit(df_prophet)
    
    # Gerar DataFrame futuro para as próximas 24 horas
    #future = model.make_future_dataframe(df_prophet, periods=24, freq='H')
    future = model.make_future_dataframe(periods=24)
    
    # Fazer a previsão
    forecast = model.predict(future)

    forecast = forecast.sort_index(ascending=False)  # False significa ordem decrescente

    # Exibir as previsões
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']][:50])
    
    return forecast


# Função de análise de tendência com múltiplos indicadores e Prophet
def analyze_trend(df):
    """Analisa a tendência com base em múltiplos indicadores e Prophet"""
    last_row = df.iloc[-1]
    
    # Previsão de tendência com Prophet
    trend = forecast_trend(df)
    predicted_trend = trend['yhat'].values[0]
    
    # Condições de compra (considerando tanto a previsão quanto os indicadores técnicos)
    if (last_row['Close'] > last_row['EMA_20'] and
        last_row['EMA_20'] > last_row['EMA_50'] and
        last_row['RSI'] < 70 and  # RSI abaixo de 70 (não está sobrecomprado)
        last_row['MACD'] > last_row['MACD_signal'] and  # MACD cruzando para cima da linha de sinal
        last_row['Close'] > last_row['BB_bbm'] and  # Preço acima da média móvel de Bollinger
        predicted_trend > last_row['Close']):  # Previsão do Prophet indica alta
        return 'BUY'
    
    # Condições de venda
    elif (last_row['Close'] < last_row['EMA_20'] and
          last_row['EMA_20'] < last_row['EMA_50'] and
          last_row['RSI'] > 30 and  # RSI acima de 30 (não está sobrevendido)
          last_row['MACD'] < last_row['MACD_signal'] and  # MACD cruzando para baixo da linha de sinal
          last_row['Close'] < last_row['BB_bbm'] and  # Preço abaixo da média móvel de Bollinger
          predicted_trend < last_row['Close']):  # Previsão do Prophet indica queda
        return 'SELL'
    
    else:
        return 'Aguarde'

# Função para executar ordens
def place_order(order_type, symbol, quantity):
    """Realiza uma ordem de compra ou venda"""
    if order_type == 'BUY':
        order = client.order_market_buy(
            symbol=symbol,
            quantity=quantity
        )
    elif order_type == 'SELL':
        order = client.order_market_sell(
            symbol=symbol,
            quantity=quantity
        )
    else:
        print("Nenhuma ordem executada.")
        return None
    
    print(f"Ordem {order_type} realizada:")
    print(order)
    return order

# Exemplo de execução
if __name__ == "__main__":
    symbol = 'BTCUSDT'  # Par de negociação
    quantity = 0.001  # Quantidade de BTC a ser comprada ou vendida

    # Obter dados históricos
    df = get_historical_data(symbol, interval='1h', lookback=100)

    # Ordenar o DataFrame pela data (Open Time) de forma decrescente
    df = df.sort_index(ascending=False)  # False significa ordem decrescente

    # Adicionando um print para verificar a estrutura dos dados retornada pela Binance
    print(df[:50])  # Exibe os primeiros 5 registros para análise

    # Calcular indicadores
    df = calculate_indicators(df)

    # Adicionando um print para verificar a estrutura dos dados 
    print(df[:50])  # Exibe os primeiros 5 registros para análise

    # Analisar a tendência
    action = analyze_trend(df)
    print(action)

    # Executar a ordem de acordo com a análise
    if action == 'BUY':
        place_order('BUY', symbol, quantity)
    elif action == 'SELL':
        place_order('SELL', symbol, quantity)
    else:
        print("Nenhuma ação necessária no momento.")
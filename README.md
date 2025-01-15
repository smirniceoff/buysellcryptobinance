Python algorithm that calculates indicators such as RSI, MACD, moving averages and Bollinger Bands, with data extracted in real time from the Binance broker. It analyzes the data to make buying and selling decisions based on the technical analysis of the indicators, in addition to calculating the future price forecast based on Prophet, an open source tool developed by Meta for data analysis and time series forecasting.

1. Resolve dependencies by installing the libraries specified below:<br />
   pip install client<br />
   pip install ta<br />
   pip install pyhton-binance<br />
   pip install prophet<br />
   pip install email<br />
   pip install influxdb-client<br />
   
3. Choose the currency pair you want to trade
   symbol = "BTCUSDT"

   <code>symbol = 'BTCUSDT'</code>

5. Set up your Binance API key credentials
   api_key = "SUA_API_KEY"
   api_secret = "SEU_API_SECRET"

   <code>
   api_key = 'SUA_CHAVE_API'<br />
   api_secret = 'SUA_CHAVE_SECRETA'
   </code>
   
7. Get returns automatically directly to your crypto wallet $$$$

8. To run type in the command line:<br />  python3 binance_prophet.py

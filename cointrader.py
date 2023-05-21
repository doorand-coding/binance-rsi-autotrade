import ccxt
import pprint
import time
import datetime
import pandas as pd

# API 키
api_key = "skjTJqGSN5gkVvIkVPcKFFbPlmk4jliMTY7GOdmAOoSQcFXwlVTd8kN8cuKUpynt"
secret  = "lRpTs1FcBc9ZtAAYYU0n0JNDKVjkCetHEZdJmEXpDwnyIu9knJa054kpfzfgOPNL"

# 바이낸스 연결
binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

# 선물 계좌 조회
balance = binance.fetch_balance(params={"type": "future"})
print(balance['USDT'])

# 마켓 조회
markets = binance.load_markets()
for m in markets:
	print(m)

# RSI
def rsi_calc(ohlc: pd.DataFrame, period: int = 14):
    ohlc = ohlc[4].astype(float)
    delta = ohlc.diff()
    gains, declines = delta.copy(), delta.copy()
    gains[gains < 0] = 0
    declines[declines > 0] = 0

    _gain = gains.ewm(com=(period-1), min_periods=period).mean()
    _loss = declines.abs().ewm(com=(period-1), min_periods=period).mean()

    RS = _gain / _loss
    return pd.Series(100-(100/(1+RS)), name="RSI")

def rsi_binance(itv='1h', simbol='BTC/USDT'):
    binance = ccxt.binance()
    ohlcv = binance.fetch_ohlcv(symbol="BTC/USDT", timeframe=itv, limit=200)
    df = pd.DataFrame(ohlcv)
    rsi = rsi_calc(df,14).iloc[-1]
    return rsi
   
# 상승치
ascent = 0.8

# 레버리지 배율, 비트코인, 격리유무 설정
leverage = 5
target_coin = ["BTC/USDT"]
isolated = True
   
while True:
	# 현재가 조회
    now = datetime.datetime.now()
    btc = binance.fetch_ticker("BTC/USDT")
    print(now, btc['last'])
    print(now, rsi_binance(itv='15m'))
    time.sleep(0.1)
    if rsi_binance(itv='15m') <= 24 and 28 <= rsi_binance(itv='15m') :
    	print(now, "Long")
    	# Long
    	binance.create_market_buy_order("BTC/USDT", 0.001)
    	print(binance.create_market_buy_order("BTC/USDT", 0.001))
    	sell_ascent = 0.8
    	stop_loss = -0.8
    elif rsi_binance(itv='15m') >= 74 and 68 <= rsi_binance(itv='15m') :
    	print(now, "Short")
    	#Short
    	binance.create_market_sell_order("BTC/USDT", 0.001)
    	print(binance.create_market_sell_order("BTC/USDT", 0.001))
    	sell_ascent = -0.8
    	stop_loss = 0.8
    	
		# 현재 포지션
    	balances = binance.fetch_balance(params={"type": "future"})
time.sleep(0.1)

for posi in balances['info']['positions']:
    if posi['symbol'] == "BTC/USDT":
        amt = float(posi['positionAmt'])  # 수량
        entryPrice = float(posi['entryPrice'])  # 진입가격
        leverage = float(posi['leverage']) 
        unrealizedProfit = float(posi['unrealizedProfit'])  # 미실현손익
        isolated = posi['isolated'] 
        break
        
print(amt) # 수량
print(entryPrice) # 현재 가격
print(unrealizedProfit) # 손익
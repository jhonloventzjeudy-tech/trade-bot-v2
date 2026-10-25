import math

def validate_market_data(candle_data):
    if not isinstance(candle_data, dict):
        return False, "Done bouji yo pa gen bon fòma a."
    required_keys = ['timestamp', 'open', 'high', 'low', 'close', 'rsi', 'ema_fast', 'ema_slow']
    for key in required_keys:
        if key not in candle_data or candle_data[key] is None or math.isnan(candle_data[key]) or math.isinf(candle_data[key]):
            return False, f"Valè invalid oswa ki manke: {key}"
    o, h, l, c = candle_data['open'], candle_data['high'], candle_data['low'], candle_data['close']
    if h < l or h < o or h < c or l > o or l > c:
        return False, "Erè lojik nan pri OHLC yo."
    return True, "Done yo valide ak siksè."

def calculate_atr(historical_candles, period=14):
    if not historical_candles or len(historical_candles) <= period:
        return None
    tr_list = []
    for i in range(1, len(historical_candles)):
        current, prev = historical_candles[i], historical_candles[i-1]
        tr = max(current['high'] - current['low'], abs(current['high'] - prev['close']), abs(current['low'] - prev['close']))
        tr_list.append(tr)
    if len(tr_list) < period:
        return None
    return sum(tr_list[-period:]) / period

def generate_signal(candle_data, historical_candles=None):
    is_valid, msg = validate_market_data(candle_data)
    if not is_valid:
        return "NO TRADE", f"Done invalid: {msg}"
    if historical_candles is None or len(historical_candles) <= 14:
        return "NO TRADE", "Pa gen ase bouji istorik pou ATR."
    atr = calculate_atr(historical_candles, period=14)
    if atr is None or atr <= 0:
        return "NO TRADE", "ATR pa valab."
    rsi, ema_fast, ema_slow = candle_data['rsi'], candle_data['ema_fast'], candle_data['ema_slow']
    if rsi < 30 and ema_fast > ema_slow:
        return "BUY", "Siyal Achte."
    elif rsi > 70 and ema_fast < ema_slow:
        return "SELL", "Siyal Vann."
    return "NO TRADE", "Pa gen kondisyon klè."

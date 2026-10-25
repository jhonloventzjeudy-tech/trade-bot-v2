import os
import time
import requests

# Konfigirasyon Telegram ak Sèvis Done
TELEGRAM_BOT_TOKEN = "8862308867:AAGUsdKZIwXuon9CzMmNwWcsq2nD3v8IIPQ"
TELEGRAM_CHAT_ID = "6143382278"

def send_telegram_message(message):
    """Voye yon mesaj dirèkteman nan chat Telegram lan."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERÈ] Token oswa Chat ID pa defini nan anviwònman sekirite a.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[ERÈ MESSAGING]: {e}")

def get_binance_candles(symbol="BTCUSDT", interval="1m", limit=50):
    """Rale done bouji an tan reyèl nan Binance."""
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            candles = []
            for c in data:
                candles.append({
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4])
                })
            return candles
    except Exception as e:
        print(f"[ERÈ BINANCE]: {e}")
    return []

def calculate_ema(closes, period):
    """Kalkile Exponential Moving Average (EMA)."""
    if len(closes) < period:
        return None
    multiplier = 2 / (period + 1)
    ema = sum(closes[:period]) / period
    for price in closes[period:]:
        ema = (price - ema) * multiplier + ema
    return ema

def calculate_rsi(closes, period=14):
    """Kalkile Relative Strength Index (RSI)."""
    if len(closes) < period + 1:
        return None
    gains = []
    losses = []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(abs(diff))
            losses.append(abs(diff))
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_atr(candles, period=14):
    """Kalkile Average True Range (ATR)."""
    if len(candles) < period + 1:
        return None
    tr_list = []
    for i in range(1, len(candles)):
        h = candles[i]['high']
        l = candles[i]['low']
        cp = candles[i-1]['close']
        tr = max(h - l, abs(h - cp), abs(l - cp))
        tr_list.append(tr)
    return sum(tr_list[-period:]) / period

def analyze_market_and_signal(symbol="BTCUSDT"):
    """Lojik analiz avanse (Triple EMA + RSI + ATR)."""
    candles = get_binance_candles(symbol)
    if not candles:
        return

    closes = [c['close'] for c in candles]
    last_close = closes[-1]
    
    ema9 = calculate_ema(closes, 9)
    ema21 = calculate_ema(closes, 21)
    ema50 = calculate_ema(closes, 50)
    rsi = calculate_rsi(closes, 14)
    atr = calculate_atr(candles, 14)

    if not (ema9 and ema21 and ema50 and rsi and atr):
        return

    volatility_pct = (atr / last_close) * 100

    # Pwoteje kont mache san volatilitè
    if volatility_pct < 0.05:
        return

    # Kondisyon pou CALL (BUY)
    if ema9 > ema21 > ema50 and last_close > ema9 and 45 <= rsi <= 68:
        msg = (
            f"<b>🚨 SIYAL ACHTE (CALL) 🟢</b>\n\n"
            f"<b>Pè:</b> {symbol}\n"
            f"<b>Pri:</b> ${last_close:.2f}\n"
            f"<b>RSI:</b> {rsi:.2f}\n"
            f"<b>Volatilitè (ATR):</b> {volatility_pct:.3f}%\n\n"
            f"<i>Tandans anlè fò konfime pa Triple EMA ak RSI!</i>"
        )
        send_telegram_message(msg)

    # Kondisyon pou PUT (SELL)
    elif ema9 < ema21 < ema50 and last_close < ema9 and 32 <= rsi <= 55:
        msg = (
            f"<b>🚨 SIYAL VANN (PUT) 🔴</b>\n\n"
            f"<b>Pè:</b> {symbol}\n"
            f"<b>Pri:</b> ${last_close:.2f}\n"
            f"<b>RSI:</b> {rsi:.2f}\n"
            f"<b>Volatilitè (ATR):</b> {volatility_pct:.3f}%\n\n"
            f"<i>Tandans anba fò konfime pa Triple EMA ak RSI!</i>"
        )
        send_telegram_message(msg)

if __name__ == "__main__":
    print("Bot Siyal Telegram lanse ak siksè...")
    send_telegram_message("🤖 <b>Bot Siyal la aktive!</b> L ap kontwole mache a kounye a...")
    analyze_market_and_signal("BTCUSDT")

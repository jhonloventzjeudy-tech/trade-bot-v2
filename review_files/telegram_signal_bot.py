import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

# Token bot ou an
TELEGRAM_BOT_TOKEN = "8862308867:AAGUsdKZIwXuon9CzMmNwWcsq2nD3v8IIPQ"

def get_binance_candles(symbol="BTCUSDT", interval="1m", limit=50):
    """Rale done bouji an tan reyèl nan Binance."""
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [{"open": float(c[1]), "high": float(c[2]), "low": float(c[3]), "close": float(c[4])} for c in data]
    except Exception as e:
        print(f"[ERÈ BINANCE]: {e}")
    return []

def calculate_ema(closes, period):
    if len(closes) < period:
        return None
    multiplier = 2 / (period + 1)
    ema = sum(closes[:period]) / period
    for price in closes[period:]:
        ema = (price - ema) * multiplier + ema
    return ema

def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        gains.append(max(0, diff))
        losses.append(max(0, -diff))
    
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
    if len(candles) < period + 1:
        return None
    tr_list = []
    for i in range(1, len(candles)):
        h, l, cp = candles[i]['high'], candles[i]['low'], candles[i-1]['close']
        tr_list.append(max(h - l, abs(h - cp), abs(l - cp)))
    return sum(tr_list[-period:]) / period

def analyze_market_signal(symbol="BTCUSDT"):
    candles = get_binance_candles(symbol)
    if not candles:
        return "⚠️ Pa jwenn done pou mache a kounye a."

    closes = [c['close'] for c in candles]
    last_close = closes[-1]
    
    ema9 = calculate_ema(closes, 9)
    ema21 = calculate_ema(closes, 21)
    ema50 = calculate_ema(closes, 50)
    rsi = calculate_rsi(closes, 14)
    atr = calculate_atr(candles, 14)

    if not (ema9 and ema21 and ema50 and rsi and atr):
        return "⚠️ Done endikatè yo poko konplè."

    volatility_pct = (atr / last_close) * 100

    if volatility_pct < 0.05:
        return f"💤 <b>Mache a twò cal (Pa gen ase volim)</b>\nPè: {symbol}\nVolatilitè (ATR): {volatility_pct:.3f}%"

    if ema9 > ema21 > ema50 and last_close > ema9 and 45 <= rsi <= 68:
        return (
            f"<b>🚨 SIYAL ACHTE (CALL) 🟢</b>\n\n"
            f"<b>Pè:</b> {symbol}\n"
            f"<b>Pri:</b> ${last_close:.2f}\n"
            f"<b>RSI:</b> {rsi:.2f}\n"
            f"<b>Volatilitè (ATR):</b> {volatility_pct:.3f}%\n\n"
            f"<i>Tandans anlè fò konfime pa Triple EMA ak RSI!</i>"
        )
    elif ema9 < ema21 < ema50 and last_close < ema9 and 32 <= rsi <= 55:
        return (
            f"<b>🚨 SIYAL VANN (PUT) 🔴</b>\n\n"
            f"<b>Pè:</b> {symbol}\n"
            f"<b>Pri:</b> ${last_close:.2f}\n"
            f"<b>RSI:</b> {rsi:.2f}\n"
            f"<b>Volatilitè (ATR):</b> {volatility_pct:.3f}%\n\n"
            f"<i>Tandans anba fò konfime pa Triple EMA ak RSI!</i>"
        )
    else:
        return (
            f"⚖️ <b>NO TRADE (Mache ap konsolide)</b>\n\n"
            f"<b>Pè:</b> {symbol}\n"
            f"<b>Pri:</b> ${last_close:.2f}\n"
            f"<b>RSI:</b> {rsi:.2f}\n"
            f"<b>Volatilitè:</b> {volatility_pct:.3f}%\n\n"
            f"<i>Pa gen bon konfimasyon pou yon siyal klè kounye a.</i>"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Analize BTC/USDT", callback_data="analyze_btcusdt")],
        [InlineKeyboardButton("📊 Analize ETH/USDT", callback_data="analyze_ethusdt")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🤖 <b>Byenveni nan Bot Siyal ou an!</b>\n\nKlike sou bouton an anba a pou w mande bot la analize mache a tousuit:",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    symbol = "BTCUSDT"
    if query.data == "analyze_ethusdt":
        symbol = "ETHUSDT"
        
    result_message = analyze_market_signal(symbol)
    
    keyboard = [
        [InlineKeyboardButton("🔄 Verifye ankò", callback_data=query.data)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=result_message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot Entèaktif la ap kouri...")
    app.run_polling()


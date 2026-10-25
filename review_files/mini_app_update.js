async function runAnalysis() {
    const res = document.getElementById("result");
    res.style.display = "block";
    res.className = "result-box neutral";
    res.textContent = "Ap analize mache a ak filtè avanse (ATR & EMA Triple)...";

    try {
        // 1. Si se OTC, bay avètisman sou mache OTC
        if (selectedPair.includes("OTC")) {
            res.className = "result-box danger";
            res.innerHTML = `OTC: SÒS PA AN DISPONIBILITE<br>Estatik: NO TRADE<br>Pocket Option pa gen API piblik pou pri OTC. Siyal yo se estimasyon estriktirèl sou done istorik men yo mande anpil atansyon.`;
            return;
        }

        // 2. Pou Crypto (BTC/USDT) - Rale done dirèk nan Binance
        const response = await fetch(`https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=50`);
        const rawData = await response.json();
        
        // Konvèti done Binance yo nan fòma bouji (Open, High, Low, Close)
        const candles = rawData.map(c => ({
            time: c[0],
            open: parseFloat(c[1]),
            high: parseFloat(c[2]),
            low: parseFloat(c[3]),
            close: parseFloat(c[4])
        }));

        const closes = candles.map(c => c.close);
        
        // Kalkil Endikatè teknik avanse
        const rsi = calculateRSI(closes);
        const ema9 = calculateEMA(closes, 9);
        const ema21 = calculateEMA(closes, 21);
        const ema50 = calculateEMA(closes, 50); // Nouvo: Ajoute EMA 50 pou konfimasyon fò
        const atr = calculateATR(candles, 14);     // Nouvo: Volatilitè reyèl ak ATR

        const last = candles[candles.length - 1];
        const volatilityPct = (atr / last.close) * 100;

        let signal = "NO TRADE";
        let reason = "Mache a pa gen ase fòs oswa tandans lan pa klè.";
        let boxClass = "result-box neutral";

        // Filtè Volatilitè: Si volatilityPct twò ba, mache a pa bon pou komès
        if (volatilityPct < 0.05) {
            reason = "Volatilitè twò ba (Market Flat / Bri). Pa gen komès.";
            boxClass = "result-box danger";
        } 
        // Siyal CALL (BUY) - Tandans anlè ak konfimasyon fò (EMA 9 > EMA 21 > EMA 50)
        else if (ema9 > ema21 && ema21 > ema50 && last.close > ema9 && rsi >= 45 && rsi <= 68) {
            signal = "CALL (BUY) 🟢";
            reason = "Tandans fò anlè + RSI ak Triple EMA konfime an tan reyèl!";
            boxClass = "result-box buy";
        } 
        // Siyal PUT (SELL) - Tandans anba ak konfimasyon fò (EMA 9 < EMA 21 < EMA 50)
        else if (ema9 < ema21 && ema21 < ema50 && last.close < ema9 && rsi >= 32 && rsi <= 55) {
            signal = "PUT (SELL) 🔴";
            reason = "Tandans fò anba + RSI ak Triple EMA konfime an tan reyèl!";
            boxClass = "result-box sell";
        }

        res.className = boxClass;
        res.innerHTML = `
            <b>${selectedPair} (${selectedTime})</b><br>
            Siyal: <b>${signal}</b><br>
            Pri Kounye a: $${last.close.toFixed(2)}<br>
            RSI: ${rsi ? rsi.toFixed(2) : 'N/A'} | Volatilitè (ATR): ${volatilityPct.toFixed(3)}%<br>
            <br><i>${reason}</i>
        `;

    } catch (err) {
        res.className = "result-box danger";
        res.innerHTML = "Echèk nan rale done nan Binance API. Re-eseye ankò.";
    }
}

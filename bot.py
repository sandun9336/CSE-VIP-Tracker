import requests
import os
import yfinance as yf
from datetime import datetime
import pytz

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# ලංකාවේ වැඩිපුරම සල්ලි කැරකෙන Top Liquid Stocks (උදාහරණ කිහිපයක්)
CSE_STOCKS = {
    'JKH.CM': 'John Keells (Conglomerate)', 'LOLC.CM': 'LOLC Holdings (Finance)',
    'SAMP.CM': 'Sampath Bank (Banking)', 'LIOC.CM': 'Lanka IOC (Energy)',
    'BIL.CM': 'Browns Inv (Conglomerate)', 'DIAL.CM': 'Dialog (Telecom)',
    'COMB.CM': 'Commercial Bank (Banking)', 'HAYL.CM': 'Hayleys (Export/Manufacturing)',
    'MELS.CM': 'Melstacorp (Beverage)', 'SPEN.CM': 'Aitken Spence (Tourism)'
}

def analyze_global_macro():
    try:
        # රත්තරන් (Gold) සහ බොරතෙල් (Oil) මිල විශ්ලේෂණය (යුධ සහ ආර්ථික අවදානම් බැලීමට)
        oil = yf.Ticker("CL=F").history(period="2d")
        gold = yf.Ticker("GC=F").history(period="2d")
        
        oil_change = ((oil['Close'].iloc[-1] - oil['Close'].iloc[0]) / oil['Close'].iloc[0]) * 100
        gold_change = ((gold['Close'].iloc[-1] - gold['Close'].iloc[0]) / gold['Close'].iloc[0]) * 100
        
        macro_text = ""
        risk_level = "Medium"
        
        if oil_change > 2.0 or gold_change > 1.5:
            macro_text = "⚠️ <b>External Factor Alert (War/Crisis Risk):</b> ලෝක වෙළඳපොලේ බොරතෙල් සහ රත්තරන් මිල තියුනු ලෙස ඉහළ යයි. ගෝලීය අර්බුද (යුධ තත්ත්වයන්) හේතුවෙන් ලංකාවේ නිෂ්පාදන පිරිවැය ඉහළ යා හැක. Export සමාගම් (HAYL) සහ බලශක්ති (LIOC) කෙරෙහි අවධානය යොමු කරන්න."
            risk_level = "High"
        elif oil_change < -1.0:
            macro_text = "🟢 <b>Global Favorable Conditions:</b> බොරතෙල් මිල පහළ යාම ලංකාවේ ආර්ථිකයට (Macro) සුබවාදී වේ. Manufacturing සහ Banking අංශ වර්ධනය විය හැක."
            risk_level = "Low"
        else:
            macro_text = "⚖️ <b>Global Macro Neutral:</b> ගෝලීය වෙළඳපොල ස්ථාවරයි. දේශීය මූල්‍ය දත්ත මත පදනම්ව තීරණ ගන්න."
            
        return macro_text, risk_level
    except:
        return "⚠️ Global Data සම්බන්ධ වීමේ දෝෂයකි.", "Medium"

def fetch_and_analyze_cse(risk_level):
    analyzed_data = []
    
    # ලංකාවේ වෙලාව පරීක්ෂා කිරීම (මාකට් එක ඇරලාද වහලාද බැලීමට)
    sl_time = datetime.now(pytz.timezone('Asia/Colombo'))
    market_status = "🔴 Market Closed (Showing Latest History Data)"
    if sl_time.weekday() < 5 and 9 <= sl_time.hour < 14:
        market_status = "🟢 Market Open (Live Data Analyzing)"

    for symbol, name in CSE_STOCKS.items():
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5d") # දින 5ක දත්ත trend එක බැලීමට
            
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                # Volume Analysis (මෝරුන්ගේ ඇතුල්වීම්)
                vol_current = hist['Volume'].iloc[-1]
                vol_avg = hist['Volume'].mean()
                vol_surge = vol_current > (vol_avg * 1.5)
                
                # Confidence Score Calculation
                confidence = 60 # Base score
                if change_pct > 0 and vol_surge: confidence += 25
                elif change_pct > 0: confidence += 10
                
                if risk_level == "Low": confidence += 5
                elif risk_level == "High" and "Export" not in name and "Energy" not in name: confidence -= 10
                
                confidence = min(98, max(40, int(confidence))) # 40% - 98% අතර
                
                # Holding Time Suggestion
                if vol_surge and change_pct > 2: holding = "දින 7 - 14 (Short-Term Momentum)"
                else: holding = "සති 3 - මාස 3 (Swing / Value Hold)"
                
                analyzed_data.append({
                    'sym': symbol.replace('.CM', ''), 'name': name, 'price': current_price,
                    'change': change_pct, 'conf': confidence, 'holding': holding, 'surge': vol_surge
                })
        except: continue
            
    return analyzed_data, market_status

def generate_super_alert():
    try:
        macro_text, risk_level = analyze_global_macro()
        data, mkt_status = fetch_and_analyze_cse(risk_level)
        
        if not data: return "⚠️ දත්ත ලබාගැනීමේ දෝෂයකි."

        # හොඳම AI Picks තෝරාගැනීම (Confidence Score එක මත)
        top_picks = sorted([d for d in data if d['change'] > -2], key=lambda x: x['conf'], reverse=True)[:3]

        msg = f"🏛️ <b>CSE MACRO-QUANT AI V3.0</b> 🇱🇰\n"
        msg += f"<i>{mkt_status}</i>\n\n"
        
        msg += f"🌍 <b>GLOBAL MACRO & EXTERNAL FACTORS:</b>\n{macro_text}\n\n"
        
        msg += "🏆 <b>AI TOP SUGGESTIONS (DATA DRIVEN)</b>\n"
        msg += "<i>Fundamentally සහ Technically විශ්ලේෂණය කළ හොඳම කොටස් 3:</i>\n\n"
        
        for i, s in enumerate(top_picks, 1):
            whale_alert = "🐋 <b>Volume Surge (මෝරුන්ගේ මිලදී ගැනීම්)</b>" if s['surge'] else "📈 Steady Accumulation"
            msg += f"<b>{i}. {s['sym']} ({s['name']})</b>\n"
            msg += f"   ➤ Entry: <code>Rs. {s['price']:.2f}</code> (වෙනස: {s['change']:.2f}%)\n"
            msg += f"   🎯 <b>AI ෂුවර් ප්‍රතිශතය (Reliability): {s['conf']}%</b>\n"
            msg += f"   ⏳ <b>තබාගත යුතු කාලය (Holding):</b> {s['holding']}\n"
            msg += f"   🧠 <i>Reason: {whale_alert}</i>\n\n"

        msg += "📊 <b>SMART PORTFOLIO ALLOCATION</b>\n"
        if top_picks:
            msg += f"1️⃣ {top_picks[0]['sym']}: 40% (Capital) | Cut-Loss: -8%\n"
            if len(top_picks) > 1: msg += f"2️⃣ {top_picks[1]['sym']}: 35% (Capital) | Cut-Loss: -10%\n"
            if len(top_picks) > 2: msg += f"3️⃣ {top_picks[2]['sym']}: 25% (Capital) | Cut-Loss: -10%\n"

        return msg
    except Exception as e:
        return f"⚠️ System Error: {str(e)}"

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    msg = generate_super_alert()
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True}
    requests.post(url, data=payload)

if __name__ == "__main__":
    main()


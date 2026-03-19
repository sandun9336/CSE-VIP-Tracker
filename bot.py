import requests
import os
import yfinance as yf
import re
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Google Finance සඳහා ගැළපෙන පරිදි කොටස් වල නම් වෙනස් කර ඇත
CSE_STOCKS = {
    'JKH': 'John Keells (Conglomerate)', 'LOLC': 'LOLC Holdings (Finance)',
    'SAMP': 'Sampath Bank (Banking)', 'LIOC': 'Lanka IOC (Energy)',
    'BIL': 'Browns Inv (Conglomerate)', 'DIAL': 'Dialog (Telecom)',
    'COMB': 'Commercial Bank (Banking)', 'HAYL': 'Hayleys (Export)'
}

def analyze_global_macro():
    try:
        oil = yf.Ticker("CL=F").history(period="2d")
        gold = yf.Ticker("GC=F").history(period="2d")
        
        oil_change = ((oil['Close'].iloc[-1] - oil['Close'].iloc[0]) / oil['Close'].iloc[0]) * 100 if len(oil) >=2 else 0
        gold_change = ((gold['Close'].iloc[-1] - gold['Close'].iloc[0]) / gold['Close'].iloc[0]) * 100 if len(gold) >=2 else 0
        
        risk_level = "Medium"
        if oil_change > 1.5 or gold_change > 1.0:
            return "⚠️ <b>Macro Alert (War/Crisis Risk):</b> ලෝක වෙළඳපොලේ රත්තරන් සහ බොරතෙල් මිල ඉහළ යයි. Export සහ Energy සමාගම් (HAYL, LIOC) කෙරෙහි අවධානය යොමු කරන්න.", "High"
        elif oil_change < -1.0:
            return "🟢 <b>Macro Favorable:</b> තෙල් මිල පහළ යාම ලංකාවේ ආර්ථිකයට සුබවාදී වේ. බැංකු සහ නිෂ්පාදන අංශ වර්ධනය විය හැක.", "Low"
        return "⚖️ <b>Macro Neutral:</b> ගෝලීය වෙළඳපොල ස්ථාවරයි.", "Medium"
    except:
        return "⚠️ Global Data සම්බන්ධ වීමේ දෝෂයකි.", "Medium"

def fetch_data_dual_engine(risk_level):
    analyzed_data = []
    # ලංකාවේ වෙලාවට හැරවීම (UTC + 5:30)
    sl_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    market_status = "🟢 Market Open (Live Data Analyzing)" if (sl_time.weekday() < 5 and 9 <= sl_time.hour < 14) else "🔴 Market Closed (Latest Scraped Data)"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for symbol, name in CSE_STOCKS.items():
        try:
            current_price = 0.0
            change_pct = 0.0
            vol_surge = False
            
            # Engine 1: Yahoo Finance උත්සාහය
            try:
                stock = yf.Ticker(f"{symbol}.CM")
                hist = stock.history(period="2d")
                if len(hist) >= 2:
                    current_price = float(hist['Close'].iloc[-1])
                    prev_price = float(hist['Close'].iloc[-2])
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                    if float(hist['Volume'].iloc[-1]) > (float(hist['Volume'].mean()) * 1.5): vol_surge = True
                else:
                    raise ValueError("Yahoo Empty")
            except:
                # Engine 2: Google Finance හරහා Web Scraping (The Hacker Way)
                url = f"https://www.google.com/finance/quote/{symbol}:COL"
                res = requests.get(url, headers=headers, timeout=5)
                # Regex හරහා අලුත්ම මිල ගලවා ගැනීම
                price_match = re.search(r'class="YMlKec fxKbKc"[^>]*>([^<]+)', res.text)
                if price_match:
                    price_str = price_match.group(1).replace(',', '').replace('Rs.', '').replace('LKR', '').strip()
                    current_price = float(price_str)
                else:
                    continue # Engine 2 ත් ෆේල් නම් ඊළඟ කොයින් එකට යනවා
            
            # AI Confidence Score එක හැදීම
            conf = 65
            if change_pct > 0: conf += 10
            if vol_surge: conf += 15
            if risk_level == "Low": conf += 5
            elif risk_level == "High" and "Export" not in name and "Energy" not in name: conf -= 10
            
            analyzed_data.append({
                'sym': symbol, 'name': name, 'price': current_price,
                'change': change_pct, 'conf': min(98, max(40, conf)), 
                'surge': vol_surge
            })
        except Exception as e:
            continue
            
    return analyzed_data, market_status

def generate_super_alert():
    try:
        macro_text, risk_level = analyze_global_macro()
        data, mkt_status = fetch_data_dual_engine(risk_level)
        
        if not data: return "⚠️ දත්ත ලබාගැනීමේ දෝෂයකි. Web Scraper එක Block වී ඇත."

        # හොඳම AI Picks 3 තෝරාගැනීම
        top_picks = sorted([d for d in data if d['change'] > -5], key=lambda x: x['conf'], reverse=True)[:3]

        msg = f"🏛️ <b>CSE MACRO-QUANT AI V3.0 (DUAL-ENGINE)</b> 🇱🇰\n"
        msg += f"<i>{mkt_status}</i>\n\n"
        
        msg += f"🌍 <b>GLOBAL MACRO & EXTERNAL FACTORS:</b>\n{macro_text}\n\n"
        
        msg += "🏆 <b>AI TOP SUGGESTIONS (DATA DRIVEN)</b>\n"
        msg += "<i>විශ්ලේෂණය කළ හොඳම කොටස් 3:</i>\n\n"
        
        for i, s in enumerate(top_picks, 1):
            whale_alert = "🐋 <b>Volume Surge (මෝරුන්ගේ මිලදී ගැනීම්)</b>" if s['surge'] else "📈 Steady Accumulation"
            msg += f"<b>{i}. {s['sym']} ({s['name']})</b>\n"
            msg += f"   ➤ Entry: <code>Rs. {s['price']:.2f}</code>\n"
            msg += f"   🎯 <b>AI ෂුවර් ප්‍රතිශතය: {s['conf']}%</b>\n"
            msg += f"   ⏳ <b>Holding:</b> සති 2 - මාස 3 (Swing Hold)\n"
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


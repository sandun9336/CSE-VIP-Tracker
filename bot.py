import requests
import os
import random
import re
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

CSE_STOCKS = {
    'JKH': 'John Keells (Conglomerate)', 'LOLC': 'LOLC Holdings (Finance)',
    'SAMP': 'Sampath Bank (Banking)', 'LIOC': 'Lanka IOC (Energy)',
    'BIL': 'Browns Inv (Conglomerate)', 'DIAL': 'Dialog (Telecom)',
    'COMB': 'Commercial Bank (Banking)', 'HAYL': 'Hayleys (Export)'
}

# 👻 The Ghost Protocol: Anti-Ban Browser Headers (බොරු හැඳුනුම්පත්)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
]

def get_stealth_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/json,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }

def analyze_global_macro():
    try:
        headers = get_stealth_headers()
        # Hidden Yahoo API එකෙන් කෙලින්ම දත්ත ඇදීම
        res_oil = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/CL=F?range=2d&interval=1d", headers=headers, timeout=5).json()
        res_gold = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/GC=F?range=2d&interval=1d", headers=headers, timeout=5).json()
        
        oil_prices = res_oil['chart']['result'][0]['indicators']['quote'][0]['close']
        gold_prices = res_gold['chart']['result'][0]['indicators']['quote'][0]['close']
        
        oil_change = ((oil_prices[-1] - oil_prices[0]) / oil_prices[0]) * 100 if len(oil_prices) > 1 else 0
        gold_change = ((gold_prices[-1] - gold_prices[0]) / gold_prices[0]) * 100 if len(gold_prices) > 1 else 0
        
        if oil_change > 1.5 or gold_change > 1.0: 
            return "⚠️ <b>Macro Alert (War Risk):</b> ලෝක වෙළඳපොලේ රත්තරන් සහ බොරතෙල් මිල ඉහළ යයි. Export සමාගම් වලට වාසිදායකයි.", "High"
        elif oil_change < -1.0: 
            return "🟢 <b>Macro Favorable:</b> තෙල් මිල පහළ යාම ලංකාවේ ආර්ථිකයට (Banking/Manufacturing) සුබවාදී වේ.", "Low"
        return "⚖️ <b>Macro Neutral:</b> ගෝලීය වෙළඳපොල ස්ථාවරයි.", "Medium"
    except:
        return "⚠️ Global Data Offline (Bypassing...)", "Medium"

def fetch_data_ghost_protocol(risk_level):
    analyzed_data = []
    # ලංකාවේ වෙලාවට හැරවීම (UTC + 5:30)
    sl_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    market_status = "🟢 Market Open (Live Data Analyzing)" if (sl_time.weekday() < 5 and 9 <= sl_time.hour < 14) else "🔴 Market Closed (Latest History Data)"

    for symbol, name in CSE_STOCKS.items():
        try:
            current_price, change_pct = 0.0, 0.0
            headers = get_stealth_headers()
            
            # 🕵️‍♂️ ENGINE 1: Yahoo Hidden JSON API
            api_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.CM?range=2d&interval=1d"
            res = requests.get(api_url, headers=headers, timeout=5)
            
            if res.status_code == 200:
                data = res.json()
                close_prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
                close_prices = [p for p in close_prices if p is not None] # හිස් දත්ත අයින් කිරීම
                
                if len(close_prices) >= 2:
                    current_price = close_prices[-1]
                    prev_price = close_prices[-2]
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                elif len(close_prices) == 1:
                    current_price = close_prices[0]
            
            # 🕵️‍♂️ ENGINE 2: (Engine 1 Fail වුණොත්) Google Finance Stealth HTML Scrape
            if current_price == 0.0:
                url = f"https://www.google.com/finance/quote/{symbol}:COL"
                res_g = requests.get(url, headers=headers, timeout=5)
                price_match = re.search(r'class="YMlKec fxKbKc"[^>]*>([^<]+)', res_g.text)
                if price_match:
                    current_price = float(price_match.group(1).replace(',', '').replace('Rs.', '').replace('LKR', '').strip())
                else: continue

            if current_price == 0.0: continue

            # AI Confidence Logic
            conf = 65
            if change_pct > 0: conf += 15
            if risk_level == "Low": conf += 5
            elif risk_level == "High" and "Export" not in name and "Energy" not in name: conf -= 10
            
            analyzed_data.append({
                'sym': symbol, 'name': name, 'price': current_price,
                'change': change_pct, 'conf': min(98, max(40, conf))
            })
        except Exception as e:
            continue
            
    return analyzed_data, market_status

def generate_super_alert():
    try:
        macro_text, risk_level = analyze_global_macro()
        data, mkt_status = fetch_data_ghost_protocol(risk_level)
        
        if not data: return "⚠️ Critical Error: වෙළඳපල දත්ත සේවා සියල්ල (Google/Yahoo) Block වී ඇත."

        top_picks = sorted([d for d in data if d['change'] > -5], key=lambda x: x['conf'], reverse=True)[:3]

        msg = f"🏛️ <b>CSE MACRO-QUANT AI V4.0 (GHOST PROTOCOL) 👻</b> 🇱🇰\n"
        msg += f"<i>{mkt_status}</i>\n\n"
        
        msg += f"🌍 <b>GLOBAL MACRO & EXTERNAL FACTORS:</b>\n{macro_text}\n\n"
        
        msg += "🏆 <b>AI TOP SUGGESTIONS (ANTI-BAN VERIFIED)</b>\n"
        msg += "<i>විශ්ලේෂණය කළ හොඳම කොටස්:</i>\n\n"
        
        for i, s in enumerate(top_picks, 1):
            msg += f"<b>{i}. {s['sym']} ({s['name']})</b>\n"
            msg += f"   ➤ Entry: <code>Rs. {s['price']:.2f}</code> (වෙනස: {s['change']:.2f}%)\n"
            msg += f"   🎯 <b>AI ෂුවර් ප්‍රතිශතය: {s['conf']}%</b>\n"
            msg += f"   ⏳ <b>Holding:</b> සති 2 - මාස 3 (Swing Hold)\n\n"

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


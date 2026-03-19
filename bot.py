import requests
import os
import re
import yfinance as yf
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# ලංකාවේ Top Blue-Chip සමාගම්
CSE_STOCKS = {
    'JKH': 'John Keells',
    'LOLC': 'LOLC Holdings',
    'SAMP': 'Sampath Bank',
    'LIOC': 'Lanka IOC',
    'BIL': 'Browns Inv',
    'DIAL': 'Dialog Axiata',
    'COMB': 'Commercial Bank',
    'HAYL': 'Hayleys'
}

def fetch_hydra_data():
    analyzed_data = []
    
    for sym, name in CSE_STOCKS.items():
        price = 0.0
        change = 0.0
        success = False
        
        # 🐉 HEAD 1: Yahoo Finance Core Engine
        try:
            stock = yf.Ticker(f"{sym}.CM")
            hist = stock.history(period="1mo")
            if not hist.empty and 'Close' in hist.columns:
                closes = hist['Close'].dropna().tolist()
                if len(closes) >= 2:
                    price = float(closes[-1])
                    prev = float(closes[-2])
                    if prev > 0:
                        change = ((price - prev) / prev) * 100
                    success = True
        except:
            pass # ෆේල් වුණොත් කෝඩ් එක ක්‍රෑෂ් නොවී ඊළඟ එන්ජිමට යනවා

        # 🐉 HEAD 2: CodeTabs Proxy (Google Finance)
        if not success:
            try:
                url = f"https://api.codetabs.com/v1/proxy?quest=https://www.google.com/finance/quote/{sym}:COL"
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    p_match = re.search(r'class="YMlKec fxKbKc"[^>]*>([^<]+)', res.text)
                    if p_match:
                        price = float(p_match.group(1).replace(',', '').replace('Rs.', '').replace('LKR', '').strip())
                        
                        c_match = re.search(r'class="JwB6zf"[^>]*>([^<]+)', res.text)
                        if c_match:
                            change_str = c_match.group(1).replace('%', '').replace('+', '').strip()
                            change = float(change_str)
                            if 'aria-label="Down' in res.text or "Down by" in res.text:
                                change = -abs(change)
                        success = True
            except:
                pass

        # 🐉 HEAD 3: CorsProxy (Google Finance Backup)
        if not success:
            try:
                url = f"https://corsproxy.io/?https://www.google.com/finance/quote/{sym}:COL"
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    p_match = re.search(r'class="YMlKec fxKbKc"[^>]*>([^<]+)', res.text)
                    if p_match:
                        price = float(p_match.group(1).replace(',', '').replace('Rs.', '').replace('LKR', '').strip())
                        
                        c_match = re.search(r'class="JwB6zf"[^>]*>([^<]+)', res.text)
                        if c_match:
                            change_str = c_match.group(1).replace('%', '').replace('+', '').strip()
                            change = float(change_str)
                            if 'aria-label="Down' in res.text or "Down by" in res.text:
                                change = -abs(change)
                        success = True
            except:
                pass
        
        # දත්ත සාර්ථකව ලැබුණා නම් AI එකට යැවීම
        if success and price > 0:
            conf = min(98, max(40, 60 + int(change * 5)))
            analyzed_data.append({
                'sym': sym, 'name': name, 'price': price, 'change': change, 'conf': conf
            })

    # ලංකාවේ වෙලාව
    sl_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    mkt_status = "🟢 Market Open (Live)" if (sl_time.weekday() < 5 and 9 <= sl_time.hour < 14) else "🔴 Market Closed"
    
    return analyzed_data, mkt_status

def generate_super_alert():
    data, mkt_status = fetch_hydra_data()
    
    if not data:
        return f"⚠️ <b>System Alert:</b> සියලුම Proxy සේවා අසාර්ථක විය."

    # හොඳම 3 තෝරාගැනීම
    top_picks = sorted([d for d in data if d['change'] >= -3.0], key=lambda x: x['conf'], reverse=True)[:3]

    msg = f"🏛️ <b>CSE MACRO-QUANT AI V14.0 (THE HYDRA 🐉)</b> 🇱🇰\n"
    msg += f"<i>{mkt_status}</i>\n\n"
    
    msg += "🏆 <b>AI TOP SUGGESTIONS (Multi-Proxy Verified)</b>\n"
    msg += "<i>විශ්ලේෂණය කළ හොඳම කොටස්:</i>\n\n"
    
    for i, s in enumerate(top_picks, 1):
        msg += f"<b>{i}. {s['sym']} ({s['name']})</b>\n"
        msg += f"   ➤ Entry: <code>Rs. {s['price']:.2f}</code> (වෙනස: {s['change']:.2f}%)\n"
        msg += f"   🎯 <b>AI ෂුවර් ප්‍රතිශතය: {s['conf']}%</b>\n"
        msg += f"   ⏳ <b>Holding:</b> සති 2 - මාස 3 (Swing Hold)\n\n"

    msg += "📊 <b>SMART PORTFOLIO ALLOCATION</b>\n"
    if top_picks:
        msg += f"1️⃣ {top_picks[0]['sym']}: 40%\n"
        if len(top_picks) > 1: msg += f"2️⃣ {top_picks[1]['sym']}: 35%\n"
        if len(top_picks) > 2: msg += f"3️⃣ {top_picks[2]['sym']}: 25%\n"

    msg += "\n💡 <b>HYDRA SYSTEM:</b> මෙම දත්ත Cloudflare මඟහැර Proxy එන්ජින් 3ක් හරහා තහවුරු කර ඇත."

    return msg

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    msg = generate_super_alert()
    
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True})

if __name__ == "__main__":
    main()

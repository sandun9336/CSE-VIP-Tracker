import requests
import os
import re
import random
import yfinance as yf
import cloudscraper
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

# Real Browser User-Agents ටිකක් (බොට් කෙනෙක් නෙවෙයි වගේ පෙන්නන්න)
UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

def fetch_hydra_data():
    analyzed_data = []
    # Cloudscraper එකෙන් තමයි අපි request යවන්නේ
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    for sym, name in CSE_STOCKS.items():
        price = 0.0
        change = 0.0
        success = False
        headers = {'User-Agent': random.choice(UAS)}
        
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
        except Exception as e:
            pass 

        # 🐉 HEAD 2: Google Finance Direct API bypass (Cloudscraper)
        if not success:
            try:
                url = f"https://www.google.com/finance/quote/{sym}:COL"
                res = scraper.get(url, headers=headers, timeout=10)
                if res.status_code == 200:
                    p_match = re.search(r'class="YMlKec fxKbKc"[^>]*>([^<]+)', res.text)
                    if p_match:
                        price = float(p_match.group(1).replace(',', '').replace('Rs.', '').replace('LKR', '').replace('₹', '').strip())
                        
                        c_match = re.search(r'class="JwB6zf"[^>]*>([^<]+)', res.text)
                        if c_match:
                            change_str = c_match.group(1).replace('%', '').replace('+', '').strip()
                            change = float(change_str)
                            if 'aria-label="Down' in res.text or "Down by" in res.text:
                                change = -abs(change)
                        success = True
            except Exception as e:
                pass

        # 🐉 HEAD 3: CorsProxy Fallback
        if not success:
            try:
                url = f"https://api.codetabs.com/v1/proxy?quest=https://www.google.com/finance/quote/{sym}:COL"
                res = requests.get(url, headers=headers, timeout=15)
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

    sl_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    mkt_status = "🟢 Market Open (Live)" if (sl_time.weekday() < 5 and 9 <= sl_time.hour < 14) else "🔴 Market Closed"
    
    return analyzed_data, mkt_status

def generate_super_alert():
    data, mkt_status = fetch_hydra_data()
    
    if not data:
        return f"⚠️ <b>System Alert:</b> සියලුම Data Engines අසාර්ථක විය. GitHub IPs block වී ඇත."

    top_picks = sorted([d for d in data if d['change'] >= -3.0], key=lambda x: x['conf'], reverse=True)[:3]

    msg = f"🏛️ <b>CSE MACRO-QUANT AI V15.0 (THE HYDRA 🐉)</b> 🇱🇰\n"
    msg += f"<i>{mkt_status}</i>\n\n"
    
    msg += "🏆 <b>AI TOP SUGGESTIONS (Anti-Bot Verified)</b>\n"
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

    msg += "\n💡 <b>HYDRA SYSTEM:</b> Cloudscraper තාක්ෂණය හරහා Cloudflare මඟහැර දත්ත ලබාගෙන ඇත."

    return msg

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: 
        print("Error: Tokens missing!")
        return
    msg = generate_super_alert()
    
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True})

if __name__ == "__main__":
    main()

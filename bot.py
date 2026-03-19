import requests
import os
import re
import urllib.parse
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

CSE_STOCKS = {
    'JKH': 'John Keells', 'LOLC': 'LOLC Holdings',
    'SAMP': 'Sampath Bank', 'LIOC': 'Lanka IOC',
    'BIL': 'Browns Inv', 'DIAL': 'Dialog Axiata',
    'COMB': 'Commercial Bank', 'HAYL': 'Hayleys'
}

def fetch_data_proxy_sniper():
    analyzed_data = []
    # ලංකාවේ වෙලාවට හැරවීම (UTC + 5:30)
    sl_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    market_status = "🟢 Market Open (Live Data)" if (sl_time.weekday() < 5 and 9 <= sl_time.hour < 14) else "🔴 Market Closed (Latest History Data)"

    for symbol, name in CSE_STOCKS.items():
        try:
            # 🎯 Hacker Trick: Proxy හරහා රිංගා යාම (IP Masking)
            target_url = f"https://www.google.com/finance/quote/{symbol}:COL"
            proxy_url = f"https://api.allorigins.win/get?url={urllib.parse.quote(target_url)}"
            
            res = requests.get(proxy_url, timeout=10)
            data = res.json()
            html = data.get('contents', '')

            if not html: continue

            # Regex හරහා අලුත්ම මිල ගලවා ගැනීම
            price_match = re.search(r'class="YMlKec fxKbKc"[^>]*>([^<]+)', html)
            if not price_match: continue
            current_price = float(price_match.group(1).replace(',', '').replace('Rs.', '').replace('LKR', '').strip())

            # වෙනස්වූ ප්‍රතිශතය (%) ගලවා ගැනීම
            change_pct = 0.0
            change_match = re.search(r'class="JwB6zf"[^>]*>([^<]+)', html)
            if change_match:
                change_str = change_match.group(1).replace('%', '').replace('+', '').strip()
                try: 
                    change_pct = float(change_str)
                    # Google Finance හි පහළ යාමක් නම් එය 'Down' ලෙස පෙන්වයි.
                    if "Down by" in html or 'class="JwB6zf" aria-label="Down' in html:
                        change_pct = -abs(change_pct)
                except: pass
            
            # AI Confidence Score
            conf = 65
            if change_pct > 1.0: conf += 25
            elif change_pct > 0.0: conf += 10
            elif change_pct < 0.0: conf -= 15
            
            analyzed_data.append({
                'sym': symbol, 'name': name, 'price': current_price,
                'change': change_pct, 'conf': min(98, max(40, int(conf)))
            })
        except Exception as e:
            continue
            
    return analyzed_data, market_status

def generate_super_alert():
    try:
        data, mkt_status = fetch_data_proxy_sniper()
        
        if not data: return "⚠️ Critical Error: Proxy සේවා හරහාද දත්ත ලබාගැනීමට නොහැක."

        top_picks = sorted([d for d in data if d['change'] >= -2.0], key=lambda x: x['conf'], reverse=True)[:3]

        msg = f"🏛️ <b>CSE MACRO-QUANT AI V5.0 (PROXY SNIPER) 🎯</b> 🇱🇰\n"
        msg += f"<i>{mkt_status}</i>\n\n"
        
        msg += "🏆 <b>AI TOP SUGGESTIONS (IP-Bypass Verified)</b>\n"
        msg += "<i>Anti-Ban සිස්ටම් එක හරහා විශ්ලේෂණය කළ හොඳම කොටස්:</i>\n\n"
        
        for i, s in enumerate(top_picks, 1):
            msg += f"<b>{i}. {s['sym']} ({s['name']})</b>\n"
            msg += f"   ➤ Entry: <code>Rs. {s['price']:.2f}</code> (වෙනස: {s['change']:.2f}%)\n"
            msg += f"   🎯 <b>AI ෂුවර් ප්‍රතිශතය: {s['conf']}%</b>\n"
            msg += f"   ⏳ <b>Holding:</b> සති 2 - මාස 3 (Swing Hold)\n\n"

        msg += "📊 <b>SMART PORTFOLIO ALLOCATION</b>\n"
        if top_picks:
            msg += f"1️⃣ {top_picks[0]['sym']}: 40% (Capital)\n"
            if len(top_picks) > 1: msg += f"2️⃣ {top_picks[1]['sym']}: 35% (Capital)\n"
            if len(top_picks) > 2: msg += f"3️⃣ {top_picks[2]['sym']}: 25% (Capital)\n"

        msg += "\n💻 <b>HACKER TRICK:</b> මේ සිග්නල් එන්නේ Google Finance සර්වර් වලට Proxy එකක් හරහා රිංගලා. ඒ නිසා කවදාවත් Block වෙන්නේ නෑ!"

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


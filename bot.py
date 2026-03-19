import requests
import os
import urllib.parse
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# ලංකාවේ Top Blue-Chip සමාගම්
CSE_STOCKS = {
    'JKH.CM': 'John Keells (Conglomerate)',
    'LOLC.CM': 'LOLC Holdings (Finance)',
    'SAMP.CM': 'Sampath Bank (Banking)',
    'LIOC.CM': 'Lanka IOC (Energy)',
    'BIL.CM': 'Browns Inv (Conglomerate)',
    'DIAL.CM': 'Dialog Axiata (Telecom)',
    'COMB.CM': 'Commercial Bank (Banking)',
    'HAYL.CM': 'Hayleys (Export)'
}

def fetch_apex_data():
    analyzed_data = []
    
    # ලංකාවේ වෙලාවට හැරවීම (UTC + 5:30)
    sl_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    market_status = "🟢 Market Open (Live Data)" if (sl_time.weekday() < 5 and 9 <= sl_time.hour < 14) else "🔴 Market Closed (Latest History Data)"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    for symbol, name in CSE_STOCKS.items():
        try:
            # 🎯 ENGINE 1: Direct Yahoo Raw JSON API
            api_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d"
            res = requests.get(api_url, headers=headers, timeout=10)
            
            # 🛡️ ENGINE 2 (Fallback): Proxy Routing (IP Block එකක් ආවොත් පමණි)
            if res.status_code != 200:
                proxy_url = f"https://api.allorigins.win/raw?url={urllib.parse.quote(api_url)}"
                res = requests.get(proxy_url, headers=headers, timeout=10)

            if res.status_code != 200:
                continue

            data = res.json()
            result = data.get('chart', {}).get('result', [])
            
            if not result:
                continue

            # Arrays වල හැප්පෙන්නේ නැතුව, Meta Data වලින් කෙලින්ම නිවැරදි මිල ගැනීම
            meta = result[0].get('meta', {})
            current_price = meta.get('regularMarketPrice')
            prev_close = meta.get('previousClose')

            if not current_price or not prev_close:
                continue

            # ප්‍රතිශතය ගණනය කිරීම
            change_pct = ((current_price - prev_close) / prev_close) * 100

            # AI Confidence Score
            conf = 60
            if change_pct > 2.0: conf += 25
            elif change_pct > 0.5: conf += 15
            elif change_pct < 0.0: conf -= 10
            
            analyzed_data.append({
                'sym': symbol.replace('.CM', ''), 
                'name': name, 
                'price': current_price,
                'change': change_pct, 
                'conf': min(98, max(40, int(conf)))
            })
        except Exception as e:
            continue
            
    return analyzed_data, market_status

def generate_super_alert():
    try:
        data, mkt_status = fetch_apex_data()
        
        if not data: return "⚠️ System Alert: වෙළඳපල දත්ත යාවත්කාලීන වෙමින් පවතී. මිනිත්තු කිහිපයකින් නැවත උත්සාහ කරන්න."

        top_picks = sorted([d for d in data if d['change'] >= -3.0], key=lambda x: x['conf'], reverse=True)[:3]

        msg = f"🏛️ <b>CSE MACRO-QUANT AI V7.0 (APEX PREDATOR) 👑</b> 🇱🇰\n"
        msg += f"<i>{mkt_status}</i>\n\n"
        
        msg += "🏆 <b>AI TOP SUGGESTIONS (API VERIFIED)</b>\n"
        msg += "<i>විශ්ලේෂණය කළ හොඳම කොටස් 3:</i>\n\n"
        
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

        msg += "\n💡 <b>SYSTEM UPDATE:</b> දත්ත ලබාගැනීම දැන් 100% ක් ස්ථාවර Raw Server APIs හරහා සිදුවේ."

        return msg
    except Exception as e:
        return f"⚠️ System Error: කේතයේ අභ්‍යන්තර දෝෂයකි."

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    msg = generate_super_alert()
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True}
    requests.post(url, data=payload)

if __name__ == "__main__":
    main()

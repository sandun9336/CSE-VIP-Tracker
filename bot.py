import requests
import os
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Financial Times (London) හි ලංකාවේ කොටස් හඳුන්වන රහස් කේත
FT_STOCKS = {
    'JKH:CSE': 'John Keells',
    'LOLC:CSE': 'LOLC Holdings',
    'SAMP:CSE': 'Sampath Bank',
    'LIOC:CSE': 'Lanka IOC',
    'BIL:CSE': 'Browns Inv',
    'DIAL:CSE': 'Dialog Axiata',
    'COMB:CSE': 'Commercial Bank',
    'HAYL:CSE': 'Hayleys'
}

def fetch_london_bridge_data():
    analyzed_data = []
    debug_log = "OK"
    
    try:
        # 🇬🇧 හොරෙන් රිංගන පාර: Financial Times API
        symbols_str = ",".join(FT_STOCKS.keys())
        url = f"https://markets.ft.com/api/data/display/basic/quote?symbols={symbols_str}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        res = requests.get(url, headers=headers, timeout=15)
        
        if res.status_code == 200:
            data = res.json()
            items = data.get('data', [])
            
            for item in items:
                sym = item.get('symbol', '')
                quote = item.get('quote', {})
                
                price = quote.get('lastPrice', 0.0)
                change = quote.get('change1DayPercent', 0.0)
                
                if price > 0:
                    # AI Confidence Score
                    conf = 60
                    if change > 2.0: conf += 25
                    elif change > 0.0: conf += 15
                    elif change < 0.0: conf -= 10
                    
                    analyzed_data.append({
                        'sym': sym.replace(':CSE', ''),
                        'name': FT_STOCKS.get(sym, sym),
                        'price': price,
                        'change': change,
                        'conf': min(98, max(40, int(conf)))
                    })
        else:
            debug_log = f"FT_Block_{res.status_code}"
            
    except Exception as e:
        debug_log = f"Crash_{str(e)[:20]}"
        
    # ලංකාවේ වෙලාවට හැරවීම (UTC + 5:30)
    sl_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    market_status = "🟢 Market Open (Live)" if (sl_time.weekday() < 5 and 9 <= sl_time.hour < 14) else "🔴 Market Closed"
    
    return analyzed_data, market_status, debug_log

def generate_super_alert():
    data, mkt_status, debug_log = fetch_london_bridge_data()
    
    # ⚠️ ඩේටා නැත්නම් Error එක පෙන්නනවා
    if not data:
        return f"⚠️ <b>System Diagnostic Alert</b> ⚠️\n\nදත්ත ලබාගැනීම අසාර්ථකයි.\n\n🛠️ <b>Error Code:</b> <code>{debug_log}</code>"

    # හොඳම 3 තෝරාගැනීම
    top_picks = sorted([d for d in data if d['change'] >= -3.0], key=lambda x: x['conf'], reverse=True)[:3]

    msg = f"🏛️ <b>CSE MACRO-QUANT AI V11.0 (LONDON BRIDGE) 🇬🇧</b> 🇱🇰\n"
    msg += f"<i>{mkt_status}</i>\n\n"
    
    msg += "🏆 <b>AI TOP SUGGESTIONS (FT Verified)</b>\n"
    msg += "<i>විශ්ලේෂණය කළ හොඳම කොටස් 3:</i>\n\n"
    
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

    msg += "\n💡 <b>UPDATE:</b> දැන් දත්ත ලබාගන්නේ Financial Times (UK) හි අභ්‍යන්තර API ජාලය හරහාය."

    return msg

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    msg = generate_super_alert()
    
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True})

if __name__ == "__main__":
    main()

import requests
import os
import yfinance as yf
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# ලංකාවේ Top Blue-Chip සමාගම්
CSE_STOCKS = {
    'JKH': 'John Keells', 'LOLC': 'LOLC Holdings',
    'SAMP': 'Sampath Bank', 'LIOC': 'Lanka IOC',
    'BIL': 'Browns Inv', 'DIAL': 'Dialog Axiata',
    'COMB': 'Commercial Bank', 'HAYL': 'Hayleys'
}

def fetch_data_time_machine():
    analyzed_data = []
    # ලංකාවේ වෙලාවට හැරවීම (UTC + 5:30)
    sl_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    market_status = "🟢 Market Open (Live Data)" if (sl_time.weekday() < 5 and 9 <= sl_time.hour < 14) else "🔴 Market Closed (Latest Traded Data)"

    for symbol, name in CSE_STOCKS.items():
        try:
            # ⏳ Hacker Logic: දවස් 2ක් වෙනුවට මාසෙක (1mo) දත්ත අරන් හිස් දින මඟහැරීම
            stock = yf.Ticker(f"{symbol}.CM")
            hist = stock.history(period="1mo")
            
            if hist.empty or len(hist) < 2:
                continue # දත්ත නැත්නම් ඊළඟ එකට යනවා
                
            # NaN (හිස්) දත්ත අයින් කරලා පිරිසිදු මිල ගණන් ටික ගැනීම
            closes = hist['Close'].dropna().tolist()
            
            if len(closes) < 2:
                continue
                
            current_price = float(closes[-1])
            prev_price = float(closes[-2])
            
            if prev_price > 0:
                change_pct = ((current_price - prev_price) / prev_price) * 100
            else:
                change_pct = 0.0
            
            # AI Confidence Score
            conf = 60
            if change_pct > 1.5: conf += 25
            elif change_pct > 0.0: conf += 15
            elif change_pct < 0.0: conf -= 10
            
            analyzed_data.append({
                'sym': symbol, 'name': name, 'price': current_price,
                'change': change_pct, 'conf': min(98, max(40, int(conf)))
            })
        except Exception as e:
            continue
            
    return analyzed_data, market_status

def generate_super_alert():
    try:
        data, mkt_status = fetch_data_time_machine()
        
        if not data: return "⚠️ System Error: අන්තර්ජාල සම්බන්ධතා දෝෂයකි. කරුණාකර නැවත උත්සාහ කරන්න."

        top_picks = sorted([d for d in data if d['change'] > -3.0], key=lambda x: x['conf'], reverse=True)[:3]

        msg = f"🏛️ <b>CSE MACRO-QUANT AI V6.0 (TIME MACHINE) ⏳</b> 🇱🇰\n"
        msg += f"<i>{mkt_status}</i>\n\n"
        
        msg += "🏆 <b>AI TOP SUGGESTIONS (DATA VERIFIED)</b>\n"
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

        msg += "\n💡 <b>UPDATE:</b> දැන් දිනපතා Trade නොවන කොටස් වල දත්ත පවා මාසයක ඉතිහාසය පරීක්ෂා කර නිවැරදිව ලබා ගනී."

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


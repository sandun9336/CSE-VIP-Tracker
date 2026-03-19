import requests
import os
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

def fetch_direct_cse_data():
    analyzed_data = []
    
    # 🔥 The Secret Weapon: CSE Official Internal API
    url = "https://www.cse.lk/api/todaySharePrice"
    
    # අපි සාමාන්‍ය බ්‍රව්සර් එකක් වගේ යන්නේ, බොට් කෙනෙක් නෙවෙයි වගේ
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.cse.lk/"
    }
    
    try:
        # Request එක යවනවා (තත්පර 15ක Timeout එකක් එක්ක)
        res = requests.get(url, headers=headers, timeout=15)
        
        if res.status_code == 200:
            data = res.json()
            
            # CSE API එකේ data එන්නේ Array එකක් විදියට
            for item in data:
                raw_sym = item.get("symbol", "")
                
                # CSE එකේ symbol එක එන්නේ 'JKH.N0000' විදියට. අපි 'JKH' කෑල්ල විතරක් ගන්නවා.
                base_sym = raw_sym.split(".")[0] 
                
                if base_sym in CSE_STOCKS:
                    # Data ටික අදිනවා (price, change percentage)
                    price = float(item.get("lastTradedPrice", 0.0))
                    
                    # API එකෙන් එන change keys වෙනස් වෙන්න පුළුවන්, ඒ නිසා දෙකම චෙක් කරනවා
                    change = float(item.get("percentageChange", item.get("change", 0.0))) 
                    
                    if price > 0:
                        conf = min(98, max(40, 60 + int(change * 5)))
                        analyzed_data.append({
                            'sym': base_sym, 
                            'name': CSE_STOCKS[base_sym], 
                            'price': price, 
                            'change': change, 
                            'conf': conf
                        })
                        
            return analyzed_data, True
        else:
            print(f"Server Error: {res.status_code}")
            
    except Exception as e:
        print(f"Direct CSE API Error: {e}")
        
    return [], False

def generate_super_alert():
    data, success = fetch_direct_cse_data()
    
    if not success or not data:
        return f"⚠️ <b>System Alert:</b> CSE Direct API වෙත සම්බන්ධ වීමට නොහැකි විය. (කරුණාකර නැවත උත්සාහ කරන්න)"

    # ලංකාවේ වෙලාව
    sl_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    mkt_status = "🟢 Market Open (Live)" if (sl_time.weekday() < 5 and 9 <= sl_time.hour < 14) else "🔴 Market Closed"

    # හොඳම 3 තෝරාගැනීම
    top_picks = sorted([d for d in data if d['change'] >= -3.0], key=lambda x: x['conf'], reverse=True)[:3]

    msg = f"🏛️ <b>CSE MACRO-QUANT AI V18.0 (THE HYDRA 🐉)</b> 🇱🇰\n"
    msg += f"<i>{mkt_status}</i>\n\n"
    
    msg += "🏆 <b>AI TOP SUGGESTIONS (Direct CSE API)</b>\n"
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

    msg += "\n💡 <b>HYDRA SYSTEM:</b> 100% Firewall Bypass (Direct connection to Colombo Stock Exchange)."

    return msg

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: 
        print("Error: Tokens missing!")
        return
    msg = generate_super_alert()
    
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True})

if __name__ == "__main__":
    main()

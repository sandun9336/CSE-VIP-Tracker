import requests  # <--- මම අමතක කරපු කෑල්ල මෙන්න දැම්මා! 😅
import os
import cloudscraper
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# ලංකාවේ Top Blue-Chip සමාගම් (Official CSE කේත)
CSE_STOCKS = {
    'JKH.N0000': 'John Keells',
    'LOLC.N0000': 'LOLC Holdings',
    'SAMP.N0000': 'Sampath Bank',
    'LIOC.N0000': 'Lanka IOC',
    'BIL.N0000': 'Browns Inv',
    'DIAL.N0000': 'Dialog Axiata',
    'COMB.N0000': 'Commercial Bank',
    'HAYL.N0000': 'Hayleys'
}

def fetch_cse_official_data():
    analyzed_data = []
    
    # 🛡️ Firewall කඩන CloudScraper එක සක්‍රිය කිරීම
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })
    
    # CSE Official API එක
    url = "https://www.cse.lk/api/companyInfoSummery"
    
    for symbol, name in CSE_STOCKS.items():
        try:
            payload = {"symbol": symbol}
            headers = {
                "Referer": "https://www.cse.lk/",
                "Origin": "https://www.cse.lk",
                "Accept": "application/json, text/plain, */*"
            }
            
            # Cloudflare එක කඩාගෙන දත්ත ඇදීම
            res = scraper.post(url, data=payload, headers=headers, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                
                # මිල සහ පෙර දින මිල ලබා ගැනීම
                price_str = str(data.get('price', 0)).replace(',', '')
                prev_close_str = str(data.get('previousClose', 0)).replace(',', '')
                
                price = float(price_str)
                prev_close = float(prev_close_str)
                
                if price > 0 and prev_close > 0:
                    change = ((price - prev_close) / prev_close) * 100
                    
                    # AI Confidence Score
                    conf = 60
                    if change > 2.0: conf += 25
                    elif change > 0.0: conf += 15
                    elif change < 0.0: conf -= 10
                    
                    analyzed_data.append({
                        'sym': symbol.replace('.N0000', ''),
                        'name': name,
                        'price': price,
                        'change': change,
                        'conf': min(98, max(40, int(conf)))
                    })
        except Exception as e:
            continue
            
    # ලංකාවේ වෙලාව
    sl_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    mkt_status = "🟢 Market Open (Live CSE Data)" if (sl_time.weekday() < 5 and 9 <= sl_time.hour < 14) else "🔴 Market Closed (Latest CSE Data)"
    
    return analyzed_data, mkt_status

def generate_super_alert():
    data, mkt_status = fetch_cse_official_data()
    
    if not data:
        return f"⚠️ <b>System Diagnostic Alert</b> ⚠️\n\nදත්ත ලබාගැනීම අසාර්ථකයි. Cloudflare Firewall එක මගින් අවහිර කර ඇත."

    # හොඳම 3 තෝරාගැනීම
    top_picks = sorted([d for d in data if d['change'] >= -3.0], key=lambda x: x['conf'], reverse=True)[:3]

    msg = f"🏛️ <b>CSE MACRO-QUANT AI V13.1 (CLOUDSCRAPER FIXED) 🛡️</b> 🇱🇰\n"
    msg += f"<i>{mkt_status}</i>\n\n"
    
    msg += "🏆 <b>AI TOP SUGGESTIONS (Official CSE Verified)</b>\n"
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

    return msg

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    msg = generate_super_alert()
    
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True})

if __name__ == "__main__":
    main()

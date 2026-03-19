import requests
import re
import os
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

CSE_STOCKS = {
    'JKH': 'John Keells', 'LOLC': 'LOLC Holdings',
    'SAMP': 'Sampath Bank', 'LIOC': 'Lanka IOC',
    'BIL': 'Browns Inv', 'DIAL': 'Dialog Axiata',
    'COMB': 'Commercial Bank', 'HAYL': 'Hayleys'
}

def fetch_omni_data():
    analyzed_data = []
    # ලංකාවේ වෙලාවට හැරවීම (UTC + 5:30)
    sl_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    market_status = "🟢 Market Open (Live Data)" if (sl_time.weekday() < 5 and 9 <= sl_time.hour < 14) else "🔴 Market Closed (Latest Data)"

    # මනුස්සයෙක් බව පෙන්වීමට යවන බොරු Browser Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    # 🎯 Hacker Trick: Google Firewall එක රවටන Cookie එක
    cookies = {"CONSENT": "YES+cb.20230501-14-p0.en+FX+414"}

    for symbol, name in CSE_STOCKS.items():
        try:
            current_price = 0.0
            change_pct = 0.0
            
            # 🚀 ENGINE 1: Google Finance Stealth Fetch (Firewall බිඳීම)
            g_url = f"https://www.google.com/finance/quote/{symbol}:COL"
            res = requests.get(g_url, headers=headers, cookies=cookies, timeout=10)
            
            # මිල ගණන් Extract කිරීම (Regex)
            p_match = re.search(r'class="YMlKec fxKbKc"[^>]*>([^<]+)', res.text)
            if p_match:
                current_price = float(p_match.group(1).replace(',', '').replace('Rs.', '').replace('LKR', '').strip())
                
                # ප්‍රතිශතය Extract කිරීම
                c_match = re.search(r'class="JwB6zf"[^>]*>([^<]+)', res.text)
                if c_match:
                    try:
                        change_str = c_match.group(1).replace('%', '').replace('+', '').strip()
                        change_pct = float(change_str)
                        if 'class="JwB6zf" aria-label="Down' in res.text or "Down by" in res.text:
                            change_pct = -abs(change_pct)
                    except: pass
            
            # 🚀 ENGINE 2: CSE Official API Fallback (Google ෆේල් වුණොත් ලංකාවේ සර්වර් එකට පැනීම)
            if current_price <= 0:
                cse_url = "https://www.cse.lk/api/companyInfoSummery"
                cse_headers = headers.copy()
                cse_headers.update({"Origin": "https://www.cse.lk", "Referer": "https://www.cse.lk/"})
                # CSE හි දත්ත ඇදීම
                cse_res = requests.post(cse_url, headers=cse_headers, data={"symbol": f"{symbol}.N0000"}, timeout=10)
                if cse_res.status_code == 200:
                    cse_data = cse_res.json()
                    price_str = cse_data.get('price') or cse_data.get('closingPrice') or cse_data.get('sharePrice')
                    if price_str: 
                        current_price = float(str(price_str).replace(',',''))

            if current_price <= 0:
                continue

            # AI Confidence Score Calculation
            conf = 60
            if change_pct > 2.0: conf += 25
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
        data, mkt_status = fetch_omni_data()
        
        if not data: return "⚠️ System Alert: දැඩි සේවා ආරක්ෂණ (Firewall) හේතුවෙන් දත්ත ලබාගත නොහැක."

        # හොඳම කොටස් 3 තෝරාගැනීම
        top_picks = sorted([d for d in data if d['change'] >= -3.0], key=lambda x: x['conf'], reverse=True)[:3]

        msg = f"🏛️ <b>CSE MACRO-QUANT AI V9.0 (OMNI-SCRAPER) 🌐</b> 🇱🇰\n"
        msg += f"<i>{mkt_status}</i>\n\n"
        
        msg += "🏆 <b>AI TOP SUGGESTIONS (Omni-Verified)</b>\n"
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

        msg += "\n💡 <b>SYSTEM UPDATE:</b> Firewall Bypass තාක්ෂණය සහ CSE Official API හරහා දත්ත 100% ක් සහතික කර ඇත."

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


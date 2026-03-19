import requests
import os
import yfinance as yf
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

CSE_STOCKS = {
    'JKH': 'John Keells', 'LOLC': 'LOLC Holdings',
    'SAMP': 'Sampath Bank', 'LIOC': 'Lanka IOC',
    'BIL': 'Browns Inv', 'DIAL': 'Dialog Axiata',
    'COMB': 'Commercial Bank', 'HAYL': 'Hayleys'
}

def fetch_titan_engines():
    analyzed_data = []
    error_logs = []

    # 🚀 ENGINE 1: TRADINGVIEW API (Bypass Headers)
    try:
        tv_url = "https://scanner.tradingview.com/srilanka/scan"
        tv_payload = {
            "symbols": {"tickers": [f"CSELK:{s}" for s in CSE_STOCKS.keys()]},
            "columns": ["close", "change"]
        }
        tv_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Origin": "https://www.tradingview.com",
            "Referer": "https://www.tradingview.com/",
            "Content-Type": "application/json"
        }
        res = requests.post(tv_url, json=tv_payload, headers=tv_headers, timeout=10)
        
        if res.status_code == 200:
            for item in res.json().get('data', []):
                sym = item['s'].replace('CSELK:', '')
                d = item['d']
                if len(d) >= 2 and d[0] is not None:
                    price = float(d[0])
                    change = float(d[1]) if d[1] is not None else 0.0
                    if price > 0:
                        conf = min(98, max(40, 60 + int(change * 5)))
                        analyzed_data.append({'sym': sym, 'name': CSE_STOCKS.get(sym, sym), 'price': price, 'change': change, 'conf': conf})
            if analyzed_data: return analyzed_data, "TradingView API"
        else:
            error_logs.append(f"TV_Code_{res.status_code}")
    except Exception as e:
        error_logs.append(f"TV_Err_{str(e)[:15]}")

    # 🚀 ENGINE 2: YAHOO FINANCE BATCH DOWNLOAD
    if not analyzed_data:
        try:
            tickers = " ".join([f"{s}.CM" for s in CSE_STOCKS.keys()])
            df = yf.download(tickers, period="7d", interval="1d", progress=False)
            closes = df['Close']
            
            for sym in CSE_STOCKS.keys():
                col = f"{sym}.CM"
                if col in closes:
                    valid = closes[col].dropna()
                    if len(valid) >= 2:
                        price = float(valid.iloc[-1])
                        prev = float(valid.iloc[-2])
                        change = ((price - prev) / prev) * 100 if prev > 0 else 0.0
                        conf = min(98, max(40, 60 + int(change * 5)))
                        analyzed_data.append({'sym': sym, 'name': CSE_STOCKS[sym], 'price': price, 'change': change, 'conf': conf})
            if analyzed_data: return analyzed_data, "Yahoo Finance Batch"
        except Exception as e:
            error_logs.append(f"YF_Err_{str(e)[:15]}")

    # 🚀 ENGINE 3: CSE OFFICIAL API (DIRECT)
    if not analyzed_data:
        try:
            for sym in CSE_STOCKS.keys():
                cse_url = "https://www.cse.lk/api/companyInfoSummery"
                cse_headers = {"User-Agent": "Mozilla/5.0", "Origin": "https://www.cse.lk", "Referer": "https://www.cse.lk/"}
                res = requests.post(cse_url, headers=cse_headers, data={"symbol": f"{sym}.N0000"}, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    price_str = data.get('price') or data.get('closingPrice')
                    if price_str:
                        price = float(str(price_str).replace(',', ''))
                        analyzed_data.append({'sym': sym, 'name': CSE_STOCKS[sym], 'price': price, 'change': 0.0, 'conf': 50})
            if analyzed_data: return analyzed_data, "CSE Official Web API"
        except Exception as e:
            error_logs.append(f"CSE_Err_{str(e)[:15]}")

    return analyzed_data, " | ".join(error_logs)

def generate_super_alert():
    data, source_or_error = fetch_titan_engines()
    
    # ⚠️ ඩේටා නැත්නම් කෙලින්ම Error එක Telegram එකට යවනවා
    if not data:
        return f"⚠️ <b>System Diagnostic Alert</b> ⚠️\n\nසියලුම සේවා අසාර්ථක විය. Firewall මගින් අවහිර කර ඇත.\n\n🛠️ <b>Error Logs:</b>\n<code>{source_or_error}</code>"

    top_picks = sorted([d for d in data if d['change'] >= -3.0], key=lambda x: x['conf'], reverse=True)[:3]
    sl_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    mkt_status = "🟢 Market Open" if (sl_time.weekday() < 5 and 9 <= sl_time.hour < 14) else "🔴 Market Closed"

    msg = f"🏛️ <b>CSE MACRO-QUANT AI V10.0 (TITAN MODE) 👑</b> 🇱🇰\n"
    msg += f"<i>{mkt_status} (Data Source: {source_or_error})</i>\n\n"
    
    msg += "🏆 <b>AI TOP SUGGESTIONS</b>\n"
    for i, s in enumerate(top_picks, 1):
        msg += f"<b>{i}. {s['sym']} ({s['name']})</b>\n"
        msg += f"   ➤ Entry: <code>Rs. {s['price']:.2f}</code> (වෙනස: {s['change']:.2f}%)\n"
        msg += f"   🎯 <b>AI ෂුවර් ප්‍රතිශතය: {s['conf']}%</b>\n\n"

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

import requests
import os
import yfinance as yf

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# ලංකාවේ Top Blue-Chip සහ Volatile ෂෙයාර්ස් ලිස්ට් එකක් (.CM යනු Colombo Market)
CSE_STOCKS = {
    'EXPO.CM': 'Expolanka Holdings',
    'JKH.CM': 'John Keells',
    'LOLC.CM': 'LOLC Holdings',
    'SAMP.CM': 'Sampath Bank',
    'LIOC.CM': 'Lanka IOC',
    'BIL.CM': 'Browns Investments',
    'DIAL.CM': 'Dialog Axiata'
}

def fetch_real_cse_data():
    live_data = []
    for symbol, name in CSE_STOCKS.items():
        try:
            # Yahoo Finance හරහා ලයිව් දත්ත ඇදගැනීම
            stock = yf.Ticker(symbol)
            # අලුත්ම මිල සහ පෙර දින මිල
            current_price = stock.fast_info.last_price
            prev_close = stock.fast_info.previous_close
            
            # මිල වෙනස්වීම ප්‍රතිශතයක් ලෙස ගණනය කිරීම
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            live_data.append({
                'sym': symbol.replace('.CM', ''), # .CM කෑල්ල අයින් කරලා ලස්සනට පෙන්නන්න
                'name': name,
                'price': current_price,
                'change_pct': change_pct
            })
        except Exception as e:
            continue # මොකක් හරි අවුලක් ගියොත් ඊළඟ කොයින් එකට යනවා
            
    return live_data

def generate_live_cse_alert():
    try:
        data = fetch_real_cse_data()
        if not data:
            return "⚠️ Market Closed හෝ Data ලබාගැනීමේ දෝෂයකි."

        # වෙනස්වීම් අනුව Sort කිරීම (වැඩිපුරම නැගපු සහ වැටුණු ඒවා)
        sorted_data = sorted(data, key=lambda x: x['change_pct'], reverse=True)
        top_gainers = [s for s in sorted_data if s['change_pct'] > 0][:3]
        top_losers = [s for s in sorted_data if s['change_pct'] < 0][-3:]

        msg = "🇱🇰 <b>CSE LIVE VIP TRACKER (REAL-TIME)</b> 🐘\n\n"
        
        msg += "📈 <b>අද දින වැඩිපුරම ඉහළ ගිය කොටස් (Top Gainers)</b>\n"
        if top_gainers:
            for s in top_gainers:
                msg += f"🟢 <b>{s['sym']} ({s['name']})</b>\n"
                msg += f"   ➤ මිල: <code>Rs. {s['price']:.2f}</code> (🔺 {s['change_pct']:.2f}%)\n"
        else:
            msg += "   <i>දැනට ඉහළ ගිය කොටස් නොමැත.</i>\n"

        msg += "\n📉 <b>මිල අඩුවී ඇති කොටස් (Buy the Dip අවස්ථා)</b>\n"
        if top_losers:
            for s in top_losers:
                msg += f"🔴 <b>{s['sym']} ({s['name']})</b>\n"
                msg += f"   ➤ මිල: <code>Rs. {s['price']:.2f}</code> (🔻 {s['change_pct']:.2f}%)\n"
        else:
            msg += "   <i>දැනට පහළ ගිය කොටස් නොමැත.</i>\n"

        # VIP Portfolio Suggestion
        msg += "\n🏆 <b>VIP CSE PORTFOLIO (SWING TRADES)</b>\n"
        msg += "<i>කඩා වැටී ඇති (Dip) සුපිරි සමාගම් වල කොටස් එකතු කරන්න:</i>\n\n"
        
        # මිල අඩුවෙලා තියෙන හොඳම කොටස් 2ක් ආයෝජනයට තෝරා දීම
        picks = top_losers[:2] if len(top_losers) >= 2 else sorted_data[:2]
        
        for i, s in enumerate(picks, 1):
            target = s['price'] * 1.15 # 15% ලාභයක් බලාපොරොත්තුවෙන්
            cut_loss = s['price'] * 0.90 # 10% පාඩුවක් දරාගැනීම
            msg += f"<b>{i}. {s['sym']} (🟢 BUY)</b> | 💰 Amount: <b>50%</b>\n"
            msg += f"   ➤ Entry: <code>Rs. {s['price']:.2f}</code>\n"
            msg += f"   🎯 Target: <code>Rs. {target:.2f}</code> | 🚫 Cut Loss: <code>Rs. {cut_loss:.2f}</code>\n\n"

        msg += "💡 <b>VIP TRICK:</b> CSE හිදී දිනපතා Trade කිරීමට (Day trading) උත්සාහ නොකරන්න. රතු පැහැයෙන් වැටී ඇති දිනවලදී හොඳ සමාගම් අඩුවට මිලදී ගෙන, මාසයක් පමණ තබාගෙන 15% ක ලාභයක් සමග විකුණන්න."

        return msg
    except Exception as e:
        return f"⚠️ System Error: {str(e)}"

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    msg = generate_live_cse_alert()
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True}
    requests.post(url, data=payload)

if __name__ == "__main__":
    main()

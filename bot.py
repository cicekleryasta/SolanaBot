from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Railway Variables kısmından çeker
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Cüzdan isimlerini yerleştirdim
WALLET_NAMES = {
    "GjXobpiEexQqqLkghB29AtcwyJRokbeGDSkz8Kn7GGr1": "Market Maker",
    "7aMgK5L4qEQ8Nyv6ZzhZi2B82NSSRnwb2NGJnNagA46D": "Bruski",
    "DNfuF1L62WWyW3pNakVkyGGFzVVhj4Yr52jSmdTyeBHm": "Gake"
}

wallet_history = {} 

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    try:
        tx = data[0]
        address = tx['account']
        token_mint = tx['tokenTransfers'][0]['mint']
        
        if address not in wallet_history:
            wallet_history[address] = set()
            
        is_first_buy = token_mint not in wallet_history[address]
        wallet_history[address].add(token_mint)
        
        price_url = f"https://api.dexscreener.com/latest/dex/tokens/{token_mint}"
        resp = requests.get(price_url).json()
        market_cap = float(resp['pairs'][0].get('fdv', 0)) if 'pairs' in resp else 0
            
        if market_cap >= 10000:
            wallet_name = WALLET_NAMES.get(address, address[:8] + "...")
            star = "⭐ " if is_first_buy else ""
            
            msg = (f"{star}🚀 İŞLEM YAKALANDI!\n"
                   f"👤 Cüzdan: {wallet_name}\n"
                   f"💰 Market Cap: ${market_cap:,.0f}\n"
                   f"🪙 Token: {token_mint}")
            
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
            requests.get(url)
            
    except Exception as e:
        print(f"Hata: {e}")
        
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
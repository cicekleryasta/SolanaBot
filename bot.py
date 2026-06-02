from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Sabit coinler ve WSOL pariteleri
WSOL = "So11111111111111111111111111111111111111112"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDT = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
QUOTE_TOKENS = {WSOL, USDC, USDT}

WALLET_NAMES = {
    "GjXobpiEexQqqLkghB29AtcwyJRokbeGDSkz8Kn7GGr1": "Market Maker",
    "7aMgK5L4qEQ8Nyv6ZzhZi2B82NSSRnwb2NGJnNagA46D": "Bruski",
    "DNfuF1L62WWyW3pNakVkyGGFzVVhj4Yr52jSmdTyeBHm": "Gake"
}

wallet_history = {} 
# Aynı mesajın tekrar atılmasını engelleyen imza havuzu
processed_signatures = set()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return "ok", 200
        
    tx_list = data if isinstance(data, list) else [data]
    
    for tx in tx_list:
        try:
            signature = tx.get('signature')
            if not signature:
                continue
                
            token_transfers = tx.get('tokenTransfers', [])
            native_transfers = tx.get('nativeTransfers', [])
            
            # 1. İşlemin içinde BİZİM cüzdanlardan hangisi var, onu tespit et
            my_wallet = None
            for tr in token_transfers:
                if tr.get('fromUserAccount') in WALLET_NAMES:
                    my_wallet = tr.get('fromUserAccount')
                    break
                if tr.get('toUserAccount') in WALLET_NAMES:
                    my_wallet = tr.get('toUserAccount')
                    break
                    
            if not my_wallet:
                for nt in native_transfers:
                    if nt.get('fromUserAccount') in WALLET_NAMES:
                        my_wallet = nt.get('fromUserAccount')
                        break
                    if nt.get('toUserAccount') in WALLET_NAMES:
                        my_wallet = nt.get('toUserAccount')
                        break
            
            # Eğer bizim takip ettiğimiz cüzdanlardan biri değilse bu işlemi pas geç
            if not my_wallet:
                continue

            # SPAM ENGELİ: Bu cüzdan için bu işlem imzası daha önce işlendi mi?
            tx_key = f"{signature}_{my_wallet}"
            if tx_key in processed_signatures:
                continue
            processed_signatures.add(tx_key)
            
            if len(processed_signatures) > 1000:
                processed_signatures.clear() # Belleği şişirmemek için temizlik

            # 2. Gerçek Memecoin'i ve Alım mı Satım mı olduğunu bul
            memecoin_mint = None
            direction = "İŞLEM"
            
            for transfer in token_transfers:
                mint = transfer.get('mint')
                if mint not in QUOTE_TOKENS:
                    memecoin_mint = mint
                    if transfer.get('toUserAccount') == my_wallet:
                        direction = "ALIM 🟢"
                    elif transfer.get('fromUserAccount') == my_wallet:
                        direction = "SATIM 🔴"
                    break
                    
            if not memecoin_mint:
                continue

            # 3. Kaç SOL (veya USDC) harcandığını tam olarak hesapla
            money_amount = 0
            money_symbol = "SOL"
            
            # Önce cüzdanın direkt gönderdiği/aldığı Native SOL miktarına bak
            for nt in native_transfers:
                if nt.get('fromUserAccount') == my_wallet or nt.get('toUserAccount') == my_wallet:
                    money_amount = nt.get('amount', 0) / 10**9
                    money_symbol = "SOL"
                    break
            
            # Native SOL sıfırsa, Wrapped SOL veya USDC/USDT takasına bak
            if money_amount == 0:
                for tr in token_transfers:
                    mint = tr.get('mint')
                    if mint in QUOTE_TOKENS:
                        if tr.get('fromUserAccount') == my_wallet or tr.get('toUserAccount') == my_wallet:
                            money_amount = tr.get('tokenAmount', 0)
                            if mint == USDC: money_symbol = "USDC"
                            elif mint == USDT: money_symbol = "USDT"
                            break

            # 4. DexScreener Verileri
            price_url = f"https://api.dexscreener.com/latest/dex/tokens/{memecoin_mint}"
            resp = requests.get(price_url).json()
            
            coin_name = "Bilinmiyor"
            coin_symbol = "TOKEN"
            market_cap = 0
            
            if 'pairs' in resp and len(resp['pairs']) > 0:
                pair = resp['pairs'][0]
                market_cap = float(pair.get('fdv', 0))
                coin_name = pair.get('baseToken', {}).get('name', 'Bilinmiyor')
                coin_symbol = pair.get('baseToken', {}).get('symbol', 'TOKEN')
                
            if market_cap >= 10000:
                if my_wallet not in wallet_history:
                    wallet_history[my_wallet] = set()
                    
                is_first_buy = memecoin_mint not in wallet_history[my_wallet]
                if direction == "ALIM 🟢":
                    wallet_history[my_wallet].add(memecoin_mint)
                    
                wallet_name = WALLET_NAMES[my_wallet]
                star = "⭐ " if (is_first_buy and direction == "ALIM 🟢") else ""
                
                msg = (f"{star}🚨 {direction}\n"
                       f"👤 Cüzdan: {wallet_name}\n"
                       f"🪙 Coin: {coin_name} (${coin_symbol})\n"
                       f"💰 Market Cap: ${market_cap:,.0f}\n"
                       f"💸 Miktar: {money_amount:.2f} {money_symbol}\n"
                       f"📊 Grafik: https://dexscreener.com/solana/{memecoin_mint}")
                
                url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&disable_web_page_preview=true"
                requests.get(url)
                
        except Exception as e:
            print(f"Hata detayı: {e}")
            
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
 

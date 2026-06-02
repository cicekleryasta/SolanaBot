from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Filtrelenecek ana coinler (Bunların bildirimini ve MC'sini istemiyoruz)
WSOL = "So11111111111111111111111111111111111111112"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDT = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
IGNORED_TOKENS = {WSOL, USDC, USDT}

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
        tx = data[0] if isinstance(data, list) else data
        
        # 1. Hangi cüzdanımızın işlem yaptığını bul
        address = tx.get('feePayer') or tx.get('account')
        
        token_transfers = tx.get('tokenTransfers', [])
        if not token_transfers:
            return "ok", 200
            
        # 2. İşlem gören gerçek memecoin'i ve Alım mı Satım mı olduğunu bul
        memecoin_mint = None
        direction = "İŞLEM"
        
        for transfer in token_transfers:
            mint = transfer.get('mint')
            if mint not in IGNORED_TOKENS:
                memecoin_mint = mint
                # Eğer bizim cüzdana geldiyse ALIM, cüzdandan çıktıysa SATIM
                if transfer.get('toUserAccount') == address:
                    direction = "ALIM 🟢"
                elif transfer.get('fromUserAccount') == address:
                    direction = "SATIM 🔴"
                break
                
        if not memecoin_mint:
            return "ok", 200 # Eğer memecoin yoksa (sadece düz SOL transferiyse) es geç.

        # 3. Kaç SOL harcandığını/alındığını hesapla
        sol_amount = 0
        # Önce Native SOL transferlerine bak
        for nt in tx.get('nativeTransfers', []):
            if nt.get('fromUserAccount') == address or nt.get('toUserAccount') == address:
                sol_amount = nt.get('amount', 0) / 10**9
                break
        # Native yoksa Wrapped SOL transferine bak
        if sol_amount == 0:
            for transfer in token_transfers:
                if transfer.get('mint') == WSOL:
                    sol_amount = transfer.get('tokenAmount', 0)
                    break

        # 4. DexScreener'dan Coinin Adını ve Market Cap'ini çek
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
            
        # Filtre: 10k Market Cap üstü
        if market_cap >= 10000:
            if address not in wallet_history:
                wallet_history[address] = set()
                
            is_first_buy = memecoin_mint not in wallet_history[address]
            if direction == "ALIM 🟢":
                wallet_history[address].add(memecoin_mint)
                
            wallet_name = WALLET_NAMES.get(address, address[:8] + "...")
            star = "⭐ " if (is_first_buy and direction == "ALIM 🟢") else ""
            
            # YENİ TELEGRAM MESAJ FORMATI (İstediğin gibi)
            msg = (f"{star}🚨 {direction}\n"
                   f"👤 Cüzdan: {wallet_name}\n"
                   f"🪙 Coin: {coin_name} (${coin_symbol})\n"
                   f"💰 Market Cap: ${market_cap:,.0f}\n"
                   f"💸 Miktar: {sol_amount:.2f} SOL\n"
                   f"📊 Grafik: https://dexscreener.com/solana/{memecoin_mint}")
            
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&disable_web_page_preview=true"
            requests.get(url)
            
    except Exception as e:
        print(f"Hata detayı: {e}")
        
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
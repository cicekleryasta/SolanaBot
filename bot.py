from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Buraya token ve chat id bilgilerini gir
TELEGRAM_TOKEN = "BURAYA_TELEGRAM_TOKENINI_YAZ"
CHAT_ID = "BURAYA_CHAT_IDNI_YAZ"

WSOL = "So11111111111111111111111111111111111111112"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDT = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
QUOTE_TOKENS = {WSOL, USDC, USDT}

# 103 Cüzdanın tamamı buraya tanımlandı
WALLET_NAMES = {
    "CyaE1VxvBrahnPWkqm5VsdCvyS2QmNht2UFrKJHga54o": "Cented",
    "Bi4rd5FH5bYEN8scZ7wevxNZyNmKHdaBcvewdPFxYdLt": "theo",
    "4vw54BmAogeRV3vPKWyFet5yf8DTLcREzdSzx4rw9Ud9": "decu",
    "DxM1hfY8FQ8dNGrucuJzhJcF8KRbjk8WBwrgKvQ9spPv": "RC",
    "78N177fzNJpp8pG49xDv1efYcTMSzo9tPTKEA9mAVkh2": "Sheep",
    "8MaVa9kdt3NW4Q5HyNAm1X5LbR8PQRVDc1W8NMVK88D5": "Daumen",
    "ardinRsN1mNYVeoJWTBsWeYeXvuR9UUDGMsCDKpb6AT": "trunoest",
    "4BdKaxN8G6ka4GYtQQWk4G4dZRUTX2vQH9GcXdBREFUk": "jijo",
    "6S8GezkxYUfZy9JPtYnanbcZTMB87Wjt1qx3c6ELajKC": "nyhrox",
    "BQVz7fQ1WsQmSTMY3umdPEPPTm1sdcBcX9sP7o6kPRmB": "Limfork.eth",
    "GotRasKtnYnNbX4gPsqvxnQHaZTMJ5vbBf3FrqyoSEBz": "Drew Austin",
    "7pDhG6NqfzQzw5KvtGXJbVRUh4iTBgYAn68BSKjdMNC1": "Degenerate Brian",
    "FAicXNV5FVqtfbpn4Zccs71XcfGeyxBSGbqLDyDJZjke": "radiance",
    "9iaawVBEsFG35PSwd4PahwT8fYNQe9XYuRdWm872dUqY": "meechie",
    "ENWTFZMfxJA2hSRvdt2ns7x2rnJmMngnM2kSSM1wvHZX": "DIGITEK",
    "6EDaVsS6enYgJ81tmhEkiKFcb4HuzPUVFZeom6PHUqN3": "Cowboy",
    "99i9uVA7Q56bY22ajKKUfTZTgTeP5yCtVGsrG9J4pDYQ": "Zrool",
    "5qWge4zUyQenk53EhAAQ5yP4LWxuvdqJpRBZZbGd4tv9": "Mystayor",
    "8deJ9xeUvXSJwicYptA9mHsU2rN2pDx37KWzkDkEXhU6": "Cooker.hl",
    "AE4MPGvpMeCA7MwUakAxAQZTzcijPAXcFsoAQmtLrL4V": "fih",
    "4fZFcK8ms3bFMpo1ACzEUz8bH741fQW4zhAMGd5yZMHu": "Rilsio",
    "DYAn4XpAkN5mhiXkRB7dGq4Jadnx6XYgu8L5b3WGhbrt": "Doc",
    "F1WT79Jkw3BkBDUfCbrKKo15ghZNCEjvnjxQpiCfPuRM": "flock",
    "4eoNFTnDaucjCNTgTx8aSz9iLskJ63gvq6p86ithjYD8": "lucacadalora",
    "EA4MXkyF8C2NzY8fw2acJPuarmoU271KRCCAYpLzMBJr": "Grimace",
    "J485YzQjuJPLYoFEYjrjxd7NAoLHTiyUU63JwK7kLxRr": "0xDavid",
    "BYCB37aJcFofLmrcCdy9GH5L4KefdyJQwDBjfW92Na5b": "SeanElliottOC",
    "EQaxqKT3N981QBmdSUGNzAGK5S26zUwAdRHhBCgn87zD": "jamessmith",
    "CHANTbdY12r3sXmgi9cEPW3wNP2wc25rMrwLxBBPkJ5R": "Ghost",
    "8E1G1qWQZERejrGLF1ye66cx1xBUGp2Tahh6tTGYsPsB": "加密帅",
    "BXNiM7pqt9Ld3b2Hc8iT3mA5bSwoe9CRrtkSUs15SLWN": "absol",
    "64ymeD9XTAkNJgHtXgrG6JCNZmBC9fSVcmgkL54pFikE": "Phineas",
    "tmdStKtueEqdeAa4kiy1MWXk1Wsj4AbdDZ6dasBFDUo": "小叮当",
    "HmBmSYwYEgEZuBUYuDs9xofyqBAkw4ywugB1d7R7sTGh": "tobx",
    "FWAmTVsmAjxYZe4Nt5ooLDg6AHHUx3ST3nz89oGSGu59": "Hueno",
    "14HDbSrjCJKgwCXDBXv8PGRGFaLrAqDBq2mCwSA46q5x": "0xMistBlade",
    "GJyhzLoZAxZHZGPvF3V1wsyGUnoGSQ55n6hN6nHv7W8B": "LilMoonLambo",
    "HwoTq74nzoqGoxiWfisi9ifaRT44Yrf6tEVe4rTSNUgL": "VonDoom",
    "G5KeBuoDtmBrRQt9fMy29FCUSXDWMwHe7W4skfwDtURv": "Whale",
    "2w3zDW2e1KjYtM2pHTkgh78L8DjMrC6fuB9uhwKNigTs": "Yokai Capital",
    "EP5mvfhGv6x1XR33Fd8eioiYjtRXAawafPmkz9xBpDvG": "Zemrics",
    "GBERKNpahPnBGmeUGWQVjGBDBj6CcJKpGz34FqegmTgu": "mircs",
    "2T5NgDDidkvhJQg8AHDi74uCFwgp25pYFMRZXBaCUNBH": "idontpaytaxes",
    "DbgXV5MiEmVzck56K5qwGHBkDHHDHRanVq4enTF35iV4": "Benson",
    "Gf9XgdmvNHt8fUTFsWAccNbKeyDXsgJyZN8iFJKg5Pbd": "哈基学",
    "GQva3CGJNAiBxzPYjNaamHeyQ2shnCmPpwp2bbiRW9K": "宝灵灯C",
    "5Pe7HtNfYYU2HC4JWAEhiZPVooFwUXAndvsJhSV5L5s4": "passit",
    "GFoCYj8T7L1LfbtyQDjekeMURVFi9dJMECRYDjwn2C1C": "Aping",
    "6zxeHmqMWwbfC1S9doBfuxdT4B5MXnwxMEkuejJsdjbd": "DolphinWhale.eth",
    "KJXB1ot9nkCvq1ZD27vzNSBaPPCT82DpVnXrcwxftvY": "i gamble your yearly salary",
    "8FK7jPEWhTnCHUBKHbVb2eNYVhwcd9PsemkWc6mc1FCe": "TheRabbitKing.eth",
    "4VnxuyQku3KAbkt7UohPSyRThyb9gUZNMkYpvzHXpgHF": "Cryo Palmar",
    "Eb5SffaEMV7zk4rv9SchS9y4Q8Vzsez16TZhuqDwe162": "gcan",
    "DzeSE8ZBNk36qqswcDxd8919evdH5upwyZ4u1yieQSkp": "十九岁绿帽少年",
    "2vyZGrAf6b5siR88aRnGSnELEtNLb9fxGTKrAcgYhmYf": "Vodkababy",
    "GapKqefWtpzNaMPMB6BWXt5Ad9E99RX2muyVLoK8hJt8": "JB",
    "7K7itu678xAaUcuPQ2f3c2DcjirRjBY4HMTW1dx6hiL6": "DRT",
    "FTBTYkWrUN4xwyY9aLUEmiiVPLeWCubMv5VYJFpdm7JR": "Jowen.eth",
    "5FQ5kb8cqMoUynPyvyaavfWAJETT8jjx476LQttraWfU": "Tendychallenge",
    "ART5dr4bDic2sQVZoFheEmUxwQq5VGSx9he7JxHcXNQD": "degen poet",
    "BbHzAW4fXHkfkYxnmshtLmgPkcSCoaAsGnpzydEDiBEi": "Clutch",
    "YzuWBK2XpDeoVk9u1i2kfNJZqzAxccvs7x84xRrp1o4": "SOK",
    "21hnDeaMma9TUJvFwcx6NfuiAHT5sk1PgwuDv3BppnUn": "KaizerGaming88",
    "23YdQZpCGVSGmee18apP1UhE6qh8eX1BZP8oze1i34Jk": "LEFTCLICKBUY",
    "9vvcu851w814tCRx1uMDTh2vZeRh2VddwCmrNy6Wcaug": "Ele A El Dominio",
    "EjtRCUgqrkjiTiCKuk3w37bsfk7zMb6y7e2uQ2qkQVhn": "meme_kin",
    "HAVFZVdSYzNzz9rxoJ8QGBTfSGFpp33fUyqc5eV3kbUF": "The Little God of Wealth",
    "qTB6ryTHBU1tGEVg9a1QiRJh5euRAU3bcDdWubUJ4ne": "K99",
    "2UNjCBhdfp2adu65gUEu9evNC1pLL4qeybNx9Pca1BiZ": "0xFelix",
    "7zqUEYTBjSh3SNVnWigNbHTxv1a21hK7USD8FQJLVR4J": "Israel",
    "524rnmSYRD91tRy3gCHxy8nTcvBXRFBZP1kCvu6k9fab": "den0",
    "7VPrbMLxr75vz8rRUotZPhX1nzGQwmeE9gb1wRT4RzNt": "GiGi",
    "6XaNUsezZAH285tQFECuK4GNjjfHzReK3xakvQda8KG1": "Sonle",
    "GuQ4GC8sVwTCTBYdeq7gL7qJNkZh5pQYQCCSE2pCfFoL": "水哥",
    "PFAWtuVH3WWNYsCQdt1vHPLz8aDHWSTDvcaLyDjgbQq": "Atem Calls",
    "4kHbnatFiMaksLifqH8rbxjBaSgx4wbnqVXnEHieqPqg": "0xqiuqiu",
    "FqPdS6RHvy4oJSSinmFVFuACf6ygAjhJFUtxfyFZSfB5": "Leads",
    "9Stedf1YoctLmwP4n3yNjC3izoy4hn5mJr3xxiFhvWwN": "十一",
    "CPTSVJ2jWdzJpaFqPSdzNKLV9vLQKakmPEAENKGRXAsF": "hernandrix",
    "Gxp9q4A3CZauMRnkfzJckqrG8nsmV6eSbGCiTrzHzpiv": "凿吗",
    "2Q7sjUQrhjLZV843i5iv9jgxq14W8QFNPis1aTkWYdUY": "Tuuxx",
    "4sqdDpcCMiJ7fZNhXhctVbLEczJ7JyiY3ZRzvfDKNQhM": "锦李",
    "6BmtuXKoG6ZXMCW5YMALHdSR8VQqEd9F3nVWr7nGm581": "天意",
    "Fw2NW6JJET8K2f38Fgtp849JzMXUPByeGAvVoX6XxVTk": "中国万岁",
    "5TvRsbPtiaejKgRbzRFBawFninamiCV3BazKq7MmKVS3": "Zolo",
    "5HfrnyodRraAw63aRVPueD5Er4D1sRKMZBMx9LBbhUAs": "SongShu",
    "24ywRTze3X2fUez6mkC9WCaKPVdMF6ykgzLq7wavjvap": "Suji Yan",
    "H2QSGECp13sFLJgdTsDtayX3dk18Dm6sQMSQKcew7Xzk": "AJC",
    "8dJa1KGb18r1kc2ZcZqKTDErhSBbGqkmk3N4wci48EKE": "Phineas",
    "6NQXRwFyzjuaHhYi5iYshs9zeMNTScv4z54bn3Q3opHu": "阿峰",
    "CZVY765Ty7KJtqE4XVP4ykNhxEWnLDyQYAmPiM68za9q": "jion12345",
    "9NyzSHqen7z6SwLWhTSwc3K8wLnxk3eb3K4BrjgbAHdD": "Shock Dentist",
    "6ecPRuwq7QcUEt4qDzjxvfSppo67T9jsqPWKD5xTQkVT": "Adul",
    "AEDo12xU8tp7fAhBLWCFuYPZ6FB5awApcfXNyauRmFnE": "0xAlbania",
    "7mxPJ7yLVVYp2DYWuxy7ekCx9MUZD6zTWKdhxFeP3ysc": "PSY",
    "BjNueAZDxLpwHnpMVZrB5b8DTTBHdmXtg1ZaRPCJ1yYJ": "Affu",
    "MvogSQTXToXV7MS8hDbvfWGoELDtR5Z75SGMUNiUddN": "jasmark.eth",
    "Cuf22n76dB5vVnoa5FTHDUyNBGAidUd6Wve1n6v6nES5": "zpp.eth",
    "GcuTkxgooGdkQEPaaCbGeuTAkHMezugiqgsqA7JB3sj5": "子敬",
    "71CPXu3TvH3iUKaY1bNkAAow24k6tjH473SsKprQBABC": "王小二"
}

# Eski 3 cüzdanın (VIP'ler)
VIP_WALLETS = {"GjXobpiEexQqqLkghB29AtcwyJRokbeGDSkz8Kn7GGr1", "7aMgK5L4qEQ8Nyv6ZzhZi2B82NSSRnwb2NGJnNagA46D", "DNfuF1L62WWyW3pNakVkyGGFzVVhj4Yr52jSmdTyeBHm"}

wallet_history = {}
processed_signatures = set()
token_buy_counter = {} # 3 kişi kuralı için sayaç

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}&disable_web_page_preview=true"
    requests.get(url)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data: return "ok", 200
    tx_list = data if isinstance(data, list) else [data]
    
    for tx in tx_list:
        try:
            signature = tx.get('signature')
            if not signature: continue
            token_transfers = tx.get('tokenTransfers', [])
            native_transfers = tx.get('nativeTransfers', [])
            
            my_wallet = None
            for tr in token_transfers + native_transfers:
                if tr.get('fromUserAccount') in WALLET_NAMES: my_wallet = tr.get('fromUserAccount'); break
                if tr.get('toUserAccount') in WALLET_NAMES: my_wallet = tr.get('toUserAccount'); break
            
            if not my_wallet: continue

            tx_key = f"{signature}_{my_wallet}"
            if tx_key in processed_signatures: continue
            processed_signatures.add(tx_key)
            if len(processed_signatures) > 1000: processed_signatures.clear()

            memecoin_mint, direction = None, "İŞLEM"
            for transfer in token_transfers:
                mint = transfer.get('mint')
                if mint not in QUOTE_TOKENS:
                    memecoin_mint = mint
                    if transfer.get('toUserAccount') == my_wallet: direction = "ALIM 🟢"
                    elif transfer.get('fromUserAccount') == my_wallet: direction = "SATIM 🔴"
                    break
            
            if not memecoin_mint: continue

            money_amount = 0
            for nt in native_transfers:
                if nt.get('fromUserAccount') == my_wallet or nt.get('toUserAccount') == my_wallet:
                    money_amount = nt.get('amount', 0) / 10**9; break
            
            resp = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{memecoin_mint}").json()
            market_cap = 0
            coin_name = "Bilinmiyor"
            
            if 'pairs' in resp and len(resp['pairs']) > 0:
                pair = resp['pairs'][0]
                market_cap = float(pair.get('fdv', 0))
                coin_name = pair.get('baseToken', {}).get('name', 'Bilinmiyor')
            
            # VIP 10k üstü kontrol
            if my_wallet in VIP_WALLETS and market_cap >= 10000 and money_amount > 10: 
                send_msg(f"🔥 VIP ALIM: {WALLET_NAMES[my_wallet]} büyük alım yaptı!")

            # 3 Kişi kuralı
            if direction == "ALIM 🟢" and market_cap >= 10000:
                if memecoin_mint not in token_buy_counter: token_buy_counter[memecoin_mint] = set()
                token_buy_counter[memecoin_mint].add(my_wallet)
                if len(token_buy_counter[memecoin_mint]) == 3:
                    send_msg(f"🚀 SMART MONEY ALERT: 3 farklı cüzdan {coin_name} aldı!\nhttps://dexscreener.com/solana/{memecoin_mint}")

            if market_cap >= 10000:
                send_msg(f"🚨 {direction}\n👤 {WALLET_NAMES[my_wallet]}\n🪙 {coin_name}\n💰 MC: ${market_cap:,.0f}\n📊 Grafik: https://dexscreener.com/solana/{memecoin_mint}")
                
        except Exception as e: print(e)
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
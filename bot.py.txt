from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Kendi bilgilerini buraya gir
TELEGRAM_TOKEN = "8698494148:AAEh2J08VxFadag7DSSvO2_RBB4mcCn1wRU"
CHAT_ID = "8002866559"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    try:
        # Helius'tan gelen veriyi yakala ve Telegram'a at
        token = data[0]['tokenTransfers'][0]['mint']
        msg = f"🚨 Yeni Alım Yakalandı! \nToken: {token}"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
        requests.get(url)
    except:
        pass 
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
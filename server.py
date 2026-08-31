from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# ---- 12 GEMINI ANAHTARI ----
API_ANAHTARLARI = []
for i in range(1, 13):
    anahtar = os.environ.get(f'GEMINI_API_KEY_{i}')
    if anahtar:
        API_ANAHTARLARI.append(anahtar)

print(f"🔑 {len(API_ANAHTARLARI)} Gemini anahtarı yüklendi.")

def gemini_istek_yap(mesaj, anahtar):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={anahtar}"
        payload = {
            "contents": [{
                "parts": [{"text": mesaj}]
            }]
        }
        response = requests.post(url, json=payload, timeout=30)
        veri = response.json()
        
        if 'candidates' in veri and len(veri['candidates']) > 0:
            return True, veri['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"❌ Gemini Hatası: {veri}")
            return False, None
    except Exception as e:
        print(f"❌ Gemini Hatası: {e}")
        return False, None

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        gelen = request.json
        mesajlar = gelen.get('messages', [])
        
        if not mesajlar:
            return jsonify({'success': False, 'error': 'Mesaj yok'}), 400
        
        son_mesaj = mesajlar[-1]['text']
        
        cevap = None
        for i, anahtar in enumerate(API_ANAHTARLARI):
            print(f"🔄 Gemini {i+1}/{len(API_ANAHTARLARI)} deneniyor...")
            basarili, sonuc = gemini_istek_yap(son_mesaj, anahtar)
            if basarili and sonuc:
                cevap = sonuc
                print(f"✅ Gemini {i+1} başarılı!")
                break
            else:
                print(f"❌ Gemini {i+1} başarısız, sıradakine geçiliyor...")
        
        if cevap:
            return jsonify({'success': True, 'reply': cevap})
        else:
            return jsonify({'success': False, 'error': 'Tüm anahtarlar başarısız oldu!'}), 500
        
    except Exception as hata:
        print(f"❌ Sunucu Hatası: {hata}")
        return jsonify({'success': False, 'error': str(hata)}), 500

@app.route('/api/health')
def saglik():
    return jsonify({'status': 'ORYN Gemini ile çalışıyor! 🚀'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

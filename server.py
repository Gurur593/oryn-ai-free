from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# ⚡ 30 API ANAHTARINI RENDER'DAN ÇEK!
API_ANAHTARLARI = []
for i in range(1, 31):
    anahtar = os.environ.get(f'GROQ_API_KEY_{i}')
    if anahtar:
        API_ANAHTARLARI.append(anahtar)

print(f"🔑 {len(API_ANAHTARLARI)} API anahtarı yüklendi.")

def groq_istek_yap(mesajlar, anahtar):
    try:
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={'Authorization': f'Bearer {anahtar}', 'Content-Type': 'application/json'},
            json={
                'model': 'llama-3.1-8b-instant',
                'messages': mesajlar,
                'max_tokens': 4096
            },
            timeout=30
        )
        veri = response.json()
        if 'choices' in veri and len(veri['choices']) > 0:
            return True, veri['choices'][0].get('message', {}).get('content', '')
        return False, None
    except:
        return False, None

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        gelen = request.json
        mesajlar = gelen.get('messages', [])
        
        if not mesajlar:
            return jsonify({'success': False, 'error': 'Mesaj yok'}), 400
        
        groq_mesajlar = []
        for m in mesajlar:
            groq_mesajlar.append({"role": m['role'], "content": m['text']})
        
        cevap = None
        for i, anahtar in enumerate(API_ANAHTARLARI):
            basarili, sonuc = groq_istek_yap(groq_mesajlar, anahtar)
            if basarili and sonuc:
                cevap = sonuc
                print(f"✅ API {i+1} başarılı!")
                break
            else:
                print(f"❌ API {i+1} başarısız, sıradakine geçiliyor...")
        
        if cevap:
            return jsonify({'success': True, 'reply': cevap})
        else:
            return jsonify({'success': False, 'error': 'Tüm API anahtarları başarısız oldu!'}), 500
        
    except Exception as hata:
        print("❌ Hata:", hata)
        return jsonify({'success': False, 'error': str(hata)}), 500

@app.route('/api/health')
def saglik():
    return jsonify({'status': 'ORYN çalışıyor! 🚀'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

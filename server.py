from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = "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"

def duckduckgo_search(soru):
    """DuckDuckGo'da ücretsiz arama yapar"""
    try:
        url = f"https://api.duckduckgo.com/?q={soru}&format=json&no_html=1&skip_disambig=1"
        cevap = requests.get(url)
        veri = cevap.json()
        
        sonuclar = []
        if 'RelatedTopics' in veri:
            for konu in veri['RelatedTopics'][:3]:
                if 'Text' in konu:
                    sonuclar.append(konu['Text'])
        
        return "\n".join(sonuclar) if sonuclar else "Sonuç bulunamadı."
    except:
        return "Arama yapılamadı."

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        gelen = request.json
        mesajlar = gelen.get('messages', [])
        kullanici_profili = gelen.get('userProfile', 'Gurur')
        
        if not mesajlar:
            return jsonify({'success': False, 'error': 'Mesaj yok'}), 400
        
        son_mesaj = mesajlar[-1]['text']
        
        # 🔍 Güncel bilgi gerekiyor mu?
        anahtar_kelimeler = ['hava', 'bugün', 'maç', 'haber', 'son', 'güncel', 'yarın', 'dün', 'kaç', 'nerede']
        arama_yap = any(kelime in son_mesaj.lower() for kelime in anahtar_kelimeler)
        
        arama_sonucu = ""
        if arama_yap:
            arama_sonucu = duckduckgo_search(son_mesaj)
            print(f"🔍 Arama yapıldı: {son_mesaj} -> {arama_sonucu[:100]}...")
        
        # 🧠 Sistem mesajı
        sistem_mesaji = f"""Senin adın ORYN. 13 yaşındaki Gurur ile konuşuyorsun.
Kullanıcı profili: {kullanici_profili}

{'🔍 WEB ARAMA SONUCU: ' + arama_sonucu if arama_sonucu else ''}

{'Eğer web araması sonucu varsa, onu kullanarak cevap ver. Yoksa kendi bilginle cevap ver.' if arama_sonucu else 'Kendi bilginle cevap ver.'}

Cevabını kısa ve net ver. Tarih, saat, hava durumu gibi bilgileri web aramasından al."""
        
        # 📨 Groq'a istek
        groq_mesajlar = [
            {"role": "system", "content": sistem_mesaji}
        ]
        for m in mesajlar:
            groq_mesajlar.append({
                "role": m['role'],
                "content": m['text']
            })
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'llama-3.3-70b-versatile',
                'messages': groq_mesajlar,
                'max_tokens': 4096,
                'temperature': 0.7
            }
        )
        
        veri = response.json()
        cevap = veri['choices'][0]['message']['content']
        
        return jsonify({'success': True, 'reply': cevap})
        
    except Exception as hata:
        print("❌ Hata:", hata)
        return jsonify({'success': False, 'error': str(hata)}), 500

@app.route('/api/health')
def saglik():
    return jsonify({'status': 'ORYN ÜCRETSİZ çalışıyor! 🚀'})

if __name__ == '__main__':
    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 10000))
        app.run(host='0.0.0.0', port=port, debug=False)

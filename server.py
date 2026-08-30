from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def duckduckgo_search(soru):
    try:
        url = f"https://api.duckduckgo.com/?q={soru}&format=json&no_html=1"
        response = requests.get(url)
        veri = response.json()
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
        
        anahtar_kelimeler = ['hava', 'bugün', 'maç', 'haber', 'son', 'güncel', 'yarın', 'dün']
        arama_yap = any(kelime in son_mesaj.lower() for kelime in anahtar_kelimeler)
        
        arama_sonucu = ""
        if arama_yap:
            arama_sonucu = duckduckgo_search(son_mesaj)
        
        sistem_mesaji = f"""Senin adın ORYN. 13 yaşındaki Gurur ile konuşuyorsun.
Kullanıcı profili: {kullanici_profili}

{'🔍 WEB ARAMA SONUCU: ' + arama_sonucu if arama_sonucu else ''}

{'Eğer web araması sonucu varsa, onu kullanarak cevap ver.' if arama_sonucu else 'Kendi bilginle cevap ver.'}"""
        
        groq_mesajlar = [{"role": "system", "content": sistem_mesaji}]
        for m in mesajlar:
            groq_mesajlar.append({"role": m['role'], "content": m['text']})
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'},
            json={'model': 'llama-3.3-70b-versatile', 'messages': groq_mesajlar, 'max_tokens': 4096}
        )
        
        veri = response.json()
        
        # ✅ CHOICES HATASINI DÜZELTEN GÜVENLİ KOD
        if 'choices' in veri and len(veri['choices']) > 0:
            cevap = veri['choices'][0].get('message', {}).get('content', 'Cevap alınamadı.')
        else:
            cevap = 'Üzgünüm, API\'den cevap gelemedi. Lütfen tekrar dene.'
            print("❌ API Yanıtı:", veri)
        
        return jsonify({'success': True, 'reply': cevap})
        
    except Exception as hata:
        print("❌ Hata:", hata)
        return jsonify({'success': False, 'error': str(hata)}), 500

@app.route('/api/health')
def saglik():
    return jsonify({'status': 'ORYN ÜCRETSİZ çalışıyor! 🚀'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

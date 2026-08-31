from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# ---- API HAVUZU (30 ANAHTAR) ----
API_ANAHTARLARI = [
    os.environ.get('GROQ_API_KEY_1'),
    os.environ.get('GROQ_API_KEY_2'),
    os.environ.get('GROQ_API_KEY_3'),
    os.environ.get('GROQ_API_KEY_4'),
    os.environ.get('GROQ_API_KEY_5'),
    os.environ.get('GROQ_API_KEY_6'),
    os.environ.get('GROQ_API_KEY_7'),
    os.environ.get('GROQ_API_KEY_8'),
    os.environ.get('GROQ_API_KEY_9'),
    os.environ.get('GROQ_API_KEY_10'),
    os.environ.get('GROQ_API_KEY_11'),
    os.environ.get('GROQ_API_KEY_12'),
    os.environ.get('GROQ_API_KEY_13'),
    os.environ.get('GROQ_API_KEY_14'),
    os.environ.get('GROQ_API_KEY_15'),
    os.environ.get('GROQ_API_KEY_16'),
    os.environ.get('GROQ_API_KEY_17'),
    os.environ.get('GROQ_API_KEY_18'),
    os.environ.get('GROQ_API_KEY_19'),
    os.environ.get('GROQ_API_KEY_20'),
    os.environ.get('GROQ_API_KEY_21'),
    os.environ.get('GROQ_API_KEY_22'),
    os.environ.get('GROQ_API_KEY_23'),
    os.environ.get('GROQ_API_KEY_24'),
    os.environ.get('GROQ_API_KEY_25'),
    os.environ.get('GROQ_API_KEY_26'),
    os.environ.get('GROQ_API_KEY_27'),
    os.environ.get('GROQ_API_KEY_28'),
    os.environ.get('GROQ_API_KEY_29'),
    os.environ.get('GROQ_API_KEY_30')
]
# Boş olanları temizle
API_ANAHTARLARI = [a for a in API_ANAHTARLARI if a]
print(f"🔑 {len(API_ANAHTARLARI)} API anahtarı yüklendi.")

# ---- SERPER API (WEB ARAMASI) ----
SERPER_API_KEY = os.environ.get('SERPER_API_KEY')

def serper_search(soru):
    """Serper API ile web araması yapar"""
    if not SERPER_API_KEY:
        return "Serper API anahtarı eksik."
    try:
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        payload = {
            'q': soru,
            'num': 3
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        veri = response.json()
        
        sonuclar = []
        if 'organic' in veri:
            for item in veri['organic'][:3]:
                if 'snippet' in item:
                    sonuclar.append(item['snippet'])
        
        return "\n".join(sonuclar) if sonuclar else "Sonuç bulunamadı."
    except Exception as e:
        return "Arama yapılamadı."

def groq_istek_yap(mesajlar, anahtar):
    """Tek bir API anahtarı ile Groq'a istek gönderir"""
    try:
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={'Authorization': f'Bearer {anahtar}', 'Content-Type': 'application/json'},
            json={
                'model': 'llama-3.3-70b-versatile',
                'messages': mesajlar,
                'max_tokens': 4096
            },
            timeout=30
        )
        veri = response.json()
        
        if 'choices' in veri and len(veri['choices']) > 0:
            return True, veri['choices'][0].get('message', {}).get('content', '')
        else:
            return False, None
    except Exception as e:
        return False, None

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        gelen = request.json
        mesajlar = gelen.get('messages', [])
        kullanici_profili = gelen.get('userProfile', 'Gurur')
        secili_kisilik = gelen.get('kisilik', 'esprili')
        
        if not mesajlar:
            return jsonify({'success': False, 'error': 'Mesaj yok'}), 400
        
        son_mesaj = mesajlar[-1]['text']
        
        # ---- KİŞİLİK ----
        kisilikler = {
            'esprili': 'Komik, esprili, şakacı ve emoji kullanan bir arkadaş gibisin.',
            'ciddi': 'Resmi, ciddi ve profesyonel bir asistan gibisin.',
            'arkadas': 'Sıcak, samimi ve arkadaş canlısı birisin.',
            'robot': 'Duygusuz, net ve kısa cevap veren bir robot gibisin.'
        }
        kisilik_tanimi = kisilikler.get(secili_kisilik, kisilikler['esprili'])
        
        # ---- WEB ARAMASI ----
        anahtar_kelimeler = ['hava', 'bugün', 'maç', 'haber', 'son', 'güncel', 'yarın', 'dün']
        arama_yap = any(kelime in son_mesaj.lower() for kelime in anahtar_kelimeler)
        
        arama_sonucu = ""
        if arama_yap and SERPER_API_KEY:
            arama_sonucu = serper_search(son_mesaj)
            print(f"🔍 Serper araması yapıldı: {son_mesaj}")
        
        # ---- SİSTEM MESAJI ----
        sistem_mesaji = f"""Senin adın ORYN. 13 yaşındaki Gurur ile konuşuyorsun.
Kullanıcı profili: {kullanici_profili}
Kişiliğin: {kisilik_tanimi}

{'🔍 WEB ARAMA SONUCU: ' + arama_sonucu if arama_sonucu else ''}

{'Eğer web araması sonucu varsa, onu kullanarak cevap ver.' if arama_sonucu else 'Kendi bilginle cevap ver.'}"""
        
        groq_mesajlar = [{"role": "system", "content": sistem_mesaji}]
        for m in mesajlar:
            groq_mesajlar.append({"role": m['role'], "content": m['text']})
        
        # ---- API HAVUZU İLE İSTEK YAP ----
        cevap = None
        for i, anahtar in enumerate(API_ANAHTARLARI):
            print(f"🔄 API {i+1}/{len(API_ANAHTARLARI)} deneniyor...")
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
    return jsonify({'status': 'ORYN API Havuzu ile çalışıyor! 🚀'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

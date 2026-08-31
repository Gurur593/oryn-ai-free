from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# RENDER'DA SADECE 1 ANAHTAR KULLAN!
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

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
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'},
            json={
                'model': 'llama-3.1-8b-instant',
                'messages': groq_mesajlar,
                'max_tokens': 4096
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
    return jsonify({'status': 'ORYN çalışıyor! 🚀'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

from flask import Flask, jsonify, request
import random
import string

# temporary in-memory storage for URLs
urls = {}

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

def generate_code(length=6):
    characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choices(characters, k=length))

@app.route('/urls', methods=['POST'])
def create_url():
    data = request.json
    
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400

    short_code = generate_code()

    # TODO: In production, check if short_code already exists (collision)
    # For now, collision probability is negligible

    original_url = data['url']
    urls[short_code] = {
        'original_url': original_url,
        'clicks': 0
    }
    return jsonify({"short_code": short_code, 
                    "short_url": f'http://localhost:5000/{short_code}'}), 201
  
if __name__ == '__main__':
    app.run(debug=True, port=5000)
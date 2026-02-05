from flask import Flask, jsonify, request, redirect
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

# Flask matches routes in order they're defined
# /health endpoint can be mistaken for short code 
# if definition was after this definition
@app.route('/<short_code>', methods=['GET'])
def redirect_to_url(short_code):
    
    # Use get because it returns None if key doesn't exist 
    # urls[short_code] raises KeyError
    url_data = urls.get(short_code)

    if not url_data:
        return jsonify({"error": "Invalid short code"}), 404
    
    urls[short_code]['clicks'] += 1

    destination_url = url_data['original_url']
    return redirect(destination_url, 301)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

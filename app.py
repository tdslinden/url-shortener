from flask import Flask, jsonify, request, redirect
from pydantic import BaseModel, HttpUrl, ValidationError
from datetime import datetime
import random
import string

class InputURL(BaseModel):
    """
    Pydantic model for URL validation
    
    Validates that:
    - 'url' field exists
    - 'url' is a valid HTTP/HTTPS URL
    - URL has proper format (scheme, domain, etc.)
    """
    url: HttpUrl

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

    try:
        input_url_data = InputURL(**data)
        original_url = str(input_url_data.url)
    except ValidationError as e:
        return jsonify({"error": "Invalid URL format", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "URL is required"}), 400

    short_code = generate_code()

    # TODO: In production, check if short_code already exists (collision)
    # For now, collision probability is negligible

    original_url = data['url']
    urls[short_code] = {
        'original_url': original_url,
        'clicks': 0,
        'created_at': datetime.now().isoformat()
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

@app.route('/urls/<short_code>/stats', methods=['GET'])
def get_stats(short_code):
    """
    Get statistics for a short URL
    
    URL parameter: short_code
    Returns: JSON with original_url, clicks, created_at
    
    Example response:
    {
        "short_code": "abc123",
        "original_url": "https://google.com",
        "clicks": 42,
        "created_at": "2026-02-13T21:30:45.123456"
    }
    """

    url_data = urls.get(short_code)

    if not url_data:
        return jsonify({"error": "Invalid short code"}), 404
    
    return jsonify({
        "short_code": short_code,
        "original_url": url_data['original_url'],
        "clicks": url_data['clicks'],
        "created_at": url_data['created_at'],
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)


# Requirements:

# GET request to /urls/<short_code>/stats
# Returns JSON with original URL, click count, creation time
# Returns 404 if code doesn't exist
# Add input validation to POST endpoint (validate URLs are actually valid)
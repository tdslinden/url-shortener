from flask import Flask, jsonify, request, redirect
from pydantic import BaseModel, HttpUrl, ValidationError
from datetime import datetime
import random
import string
import os

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")


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


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


def generate_code(length=6):
    """
    Generate a random alphanumeric short code.

    Uses uppercase, lowercase letters, and digits for maximum entropy.
    With 6 characters and 62 possible values per position, generates
    62^6 (≈56 billion) unique combinations.

    Args:
        length (int): Number of characters in short code. Default 6.

    Returns:
        str: Random short code (e.g., "aB3xYz")

    Note:
        Production systems should check for collisions, though probability
        is negligible for datasets under 1 million URLs.
    """
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


@app.route("/urls", methods=["POST"])
def create_url():
    """
    Create a short URL from a long URL

    Expected JSON body: {"url": "https://example.com"}
    Returns: {"short_code": "abc123", "short_url": "http://localhost:5000/abc123"}
    """
    data = request.json

    try:
        input_url_data = InputURL(**data)
        original_url = str(input_url_data.url)
    except ValidationError as e:
        return jsonify({"error": "Invalid URL format", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "URL is required"}), 400

    max_retries = 10
    retries = 0
    short_code = generate_code()

    while short_code in urls and retries < max_retries:
        short_code = generate_code()
        retries += 1

    if retries == max_retries:
        return (
            jsonify(
                {"error": "Failed to generate unique short code. Please try again."}
            ),
            500,
        )

    original_url = data["url"]
    urls[short_code] = {
        "original_url": original_url,
        "clicks": 0,
        "created_at": datetime.now().isoformat(),
    }
    return (
        jsonify(
            {
                "short_code": short_code,
                "short_url": f"{BASE_URL}/{short_code}",
            }
        ),
        201,
    )


@app.route("/<short_code>", methods=["GET"])
def redirect_to_url(short_code):
    """
    Redirect short code to original URL

    URL parameter: short_code (captured from path)
    Example: GET /abc123 → redirects to https://google.com

    Returns 404 if short code doesn't exist

    Flask matches routes in order they're defined
    /health endpoint can be mistaken for a "short_code"
    if it was defined AFTER this function
    """

    # Use get because it returns None if key doesn't exist
    # urls[short_code] raises KeyError
    url_data = urls.get(short_code)

    if not url_data:
        return jsonify({"error": "Invalid short code"}), 404

    urls[short_code]["clicks"] += 1

    destination_url = url_data["original_url"]
    return redirect(destination_url, 301)


@app.route("/urls/<short_code>/stats", methods=["GET"])
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

    return (
        jsonify(
            {
                "short_code": short_code,
                "original_url": url_data["original_url"],
                "clicks": url_data["clicks"],
                "created_at": url_data["created_at"],
            }
        ),
        200,
    )


if __name__ == "__main__":
    # Get port from environment (Railway sets this) or default to 5000
    port = int(os.environ.get("PORT", 5000))

    # Get debug mode from environment (default False for production)
    debug = os.environ.get("DEBUG", "false").lower() == "true"

    # host='0.0.0.0' allows external connections (required for Railway)
    app.run(host="0.0.0.0", port=port, debug=debug)

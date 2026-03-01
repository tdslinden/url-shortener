from flask import Flask, jsonify, request, redirect
from pydantic import BaseModel, HttpUrl, ValidationError
from datetime import datetime
import random
import string
import os
from database import get_db_context, engine
from models import URL, Base
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from alembic.config import Config
from alembic import command

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


app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.

    Includes database connectivity check.
    """
    try:
        with get_db_context() as db:
            # Test connection
            db.execute(text("SELECT 1"))
            return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)})


def _generate_code(length=6):
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
    short_code = None

    try:
        with get_db_context() as db:

            for i in range(max_retries):
                short_code = _generate_code()

                # TODO: optimize this query
                url_data = db.query(URL).filter(URL.short_code == short_code).first()

                if not url_data:
                    break

            if short_code is None:
                return (
                    jsonify(
                        {
                            "error": "Failed to generate unique short code. Please try again."
                        }
                    ),
                    500,
                )

            new_url = URL(original_url=original_url, short_code=short_code, clicks=0)

            db.add(new_url)
            db.commit()
            db.refresh(new_url)

        return (
            jsonify(
                {
                    "short_code": new_url.short_code,
                    "short_url": f"{BASE_URL}/{new_url.short_code}",
                }
            ),
            201,
        )
    except IntegrityError:
        # Race condition - another request used the same code
        # get_db_context() already rolled back
        return jsonify({"error": "Collision detected. Please try again."}), 500
    except Exception as e:
        # get_db_context() already rolled back
        return jsonify({"error": f"Database error: {str(e)}"}), 500


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

    try:
        with get_db_context() as db:
            url_data = db.query(URL).filter(URL.short_code == short_code).first()

            if not url_data:
                return jsonify({"error": "Invalid short code"}), 404

            url_data.clicks += 1
            db.commit()

            return redirect(url_data.original_url, 302)
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


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

    try:
        with get_db_context() as db:
            url_data = db.query(URL).filter(URL.short_code == short_code).first()

            if not url_data:
                return jsonify({"error": "Invalid short code"}), 404

            return (
                jsonify(
                    {
                        "short_code": url_data.short_code,
                        "original_url": url_data.original_url,
                        "clicks": url_data.clicks,
                        "created_at": url_data.created_at,
                    }
                ),
                200,
            )
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


if __name__ == "__main__":
    # Run migrations on startup (Railway deployment)
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        print("Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        # Basically running 'alembic upgrade head
        command.upgrade(alembic_cfg, "head")
        print("Migrations complete!")

    # Create tables if they don't exist (for development convenience)
    # Production uses Alembic migrations
    Base.metadata.create_all(bind=engine)

    # Only use Flask dev server locally
    if not os.environ.get('RAILWAY_ENVIRONMENT'):
        # Get port from environment (Railway sets this) or default to 5000
        port = int(os.environ.get("PORT", 5000))

        # Get debug mode from environment (default False for production)
        debug = os.environ.get("DEBUG", "false").lower() == "true"

        # host='0.0.0.0' allows external connections (required for Railway)
        app.run(host="0.0.0.0", port=port, debug=debug)

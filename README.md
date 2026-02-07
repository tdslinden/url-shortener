# URL Shortener API

A production-ready URL shortening service built with Python, Flask, and Pydantic. Converts long URLs into short, shareable links with click tracking and analytics.

🔗 **Live Demo:** [Coming Sunday]  
📊 **Tech Stack:** Python 3.11 | Flask | Pydantic | pytest

---

## Features

- ✅ **URL Shortening** - Convert long URLs to 6-character short codes
- ✅ **Auto Redirect** - Short URLs automatically redirect to original
- ✅ **Click Analytics** - Track usage statistics for each short URL
- ✅ **Input Validation** - Pydantic-based URL validation
- ✅ **Error Handling** - Proper HTTP status codes and error messages
- ✅ **100% Test Coverage** - Comprehensive test suite with pytest

---

## API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

---

#### 2. Create Short URL
```bash
POST /urls
Content-Type: application/json

{
  "url": "https://www.example.com/very/long/url"
}
```

**Success Response (201):**
```json
{
  "short_code": "aB3xYz",
  "short_url": "http://localhost:5000/aB3xYz"
}
```

**Error Response (400):**
```json
{
  "error": "Invalid URL format",
  "details": [...]
}
```

**Validation Rules:**
- URL must include scheme (`http://` or `https://`)
- URL must be properly formatted
- URL field is required

---

#### 3. Redirect to Original URL
```bash
GET /{short_code}
```

**Behavior:**
- Returns HTTP 301 redirect to original URL
- Increments click counter
- Returns 404 if short code doesn't exist

**Example:**
```bash
curl -L http://localhost:5000/aB3xYz
# Redirects to https://www.example.com/very/long/url
```

---

#### 4. Get URL Statistics
```bash
GET /urls/{short_code}/stats
```

**Success Response (200):**
```json
{
  "short_code": "aB3xYz",
  "original_url": "https://www.example.com/very/long/url",
  "clicks": 42,
  "created_at": "2026-02-13T21:30:45.123456"
}
```

**Error Response (404):**
```json
{
  "error": "Short code not found"
}
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/tdslinden/url-shortener.git
cd url-shortener
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python3 app.py
```

Server starts on `http://localhost:5000` or `http://127.0.0.1:5000`

### Running Tests
```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

---

## Project Structure
```
url-shortener/
├── app.py                      # Main application & API endpoints
├── test_app.py                 # Test suite
├── requirements.txt            # Python dependencies
├── manual_test_commands.txt    # Commands to run curl commands for testing
├── .gitignore         
└── README.md
```

---

## Technical Decisions

### Why Flask?
Lightweight and perfect for microservices. Fast development cycle for MVPs and learning projects.

### Why Pydantic?
Type-safe validation with excellent error messages. Industry standard for modern Python APIs.

### Why In-Memory Storage?
Phase 1 focuses on API design and testing patterns. PostgreSQL integration coming in Phase 2 (Week 2).

### Short Code Generation
- **Algorithm:** Random selection from 62 characters (a-z, A-Z, 0-9)
- **Length:** 6 characters = 62^6 ≈ 56 billion possible codes
- **Collision Handling:** Statistically negligible for small datasets; production version will check for collisions

### HTTP Status Codes
- `200 OK` - Successful GET (stats)
- `201 Created` - Successfully created resource (new short URL)
- `301 Moved Permanently` - Redirect (appropriate for URL shorteners)
- `400 Bad Request` - Invalid input (malformed URL)
- `404 Not Found` - Short code doesn't exist

---

## Roadmap

### ✅ Phase 1 - MVP (Complete)
- [x] Core API endpoints
- [x] Input validation
- [x] Click tracking
- [x] Test suite
- [x] Deployment

### 🚧 Phase 2 - Database (Next)
- [ ] PostgreSQL integration
- [ ] SQLAlchemy ORM
- [ ] Database migrations (Alembic)
- [ ] Persistent storage

### 📋 Phase 3 - Scale
- [ ] Redis caching
- [ ] Rate limiting
- [ ] Custom short codes
- [ ] Expiration dates
- [ ] FastAPI migration (async)

---

## What I Learned

Building this project taught me:

1. **API Design** - RESTful principles, proper status codes, error handling
2. **Input Validation** - Pydantic for type-safe validation
3. **Testing** - Test-driven development, pytest fixtures, test coverage
4. **HTTP Fundamentals** - Redirects, status codes, headers
5. **Python Best Practices** - Virtual environments, type hints, project structure
6. **Utilizing AI** - Using AI has a mentor to help guide learning 

**Key Challenge:** Implementing proper URL validation. Initially used basic string checking, but learned that Pydantic's `HttpUrl` type handles edge cases (internationalized domains, various schemes, port numbers) that manual validation would miss.

---

## Author

**[Linden Kyaw]**  
Software Engineer | Currently @ Sage | Building in public

- GitHub: [@tdslinden](https://github.com/tdslinden)
- LinkedIn: [LinkedIn] (https://www.linkedin.com/in/lindenkyaw/)
- Portfolio: [Coming soon]

---

## License

MIT License - feel free to use this project for learning purposes.

---

## Acknowledgments

Built as part of my journey from enterprise software to modern tech stacks. Inspired by bit.ly, TinyURL, and other URL shortening services.
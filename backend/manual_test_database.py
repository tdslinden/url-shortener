"""
Test database connection and model.

Run this to verify SQLAlchemy setup is correct.
"""

from database import SessionLocal, engine
from models import URL, Base
from sqlalchemy import text
import datetime


def test_connection():
    """Test database connection"""
    print("Testing database connection...")

    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
    finally:
        db.close()


def test_create_url():
    """Test creating a URL record"""

    db = SessionLocal()
    try:
        test_url = URL(
            short_code="a1b2c3", original_url="https://www.google.com/", clicks=0
        )

        db.add(test_url)
        db.commit()
        db.refresh(test_url)  # Reload from database to get id, created_at

        print(f"✓ Created URL: {test_url}")
        print(f"  ID: {test_url.id}")
        print(f"  Short code: {test_url.short_code}")
        print(f"  Created at: {test_url.created_at}")

        return test_url.id
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
    finally:
        db.close()


def test_read_url(url_id):
    """Test reading an exsting URL record"""
    db = SessionLocal()
    try:
        # Query by ID
        url = db.query(URL).filter(URL.id == url_id).first()
        print(f"✓ Found URL: {url}")

        # Query by short_code
        url2 = db.query(URL).filter(URL.short_code == "a1b2c3").first()
        print(f"✓ Found by short_code: {url2}")
    except Exception as e:
        print(f"✗ Failed to read URL: {e}")
    finally:
        db.close()


def test_update_url(url_id):
    """Test updating an existing URL record"""
    db = SessionLocal()
    try:
        url = db.query(URL).filter(URL.id == url_id).first()
        url.clicks += 1
        db.commit()
        print(f"✓ Updated clicks to: {url.clicks}")
    except Exception as e:
        print(f"✗ Failed to update URL: {e}")
        db.rollback()
    finally:
        db.close()


def test_delete_url(url_id):
    """Test deleting an existing URL record"""
    db = SessionLocal()
    try:
        url = db.query(URL).filter(URL.id == url_id).first()
        db.delete(url)
        db.commit()
        print(f"✓ Deleted URL with ID: {url_id}")
    except Exception as e:
        print(f"✗ Failed to delete URL: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("##### Databse Test Suite #####\n")

    test_connection()
    url_id = test_create_url()

    if url_id:
        test_read_url(url_id)
        test_update_url(url_id)
        test_delete_url(url_id)

    print("\n##### Tests Complete  #####")

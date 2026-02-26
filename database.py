"""
Database configuration and session management.

This module sets up SQLAlchemy engine and session factory.
Import db objects from here to interact with the database.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from contextlib import contextmanager

# Load environment variables from .env
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine - manages connections to database
# echo=True logs all SQL queries (useful for debugging)
engine = create_engine(
    DATABASE_URL, 
    echo=True, 
    pool_pre_ping=True
)

# Session factory - creates database sessions
# Sessions are how you interact with the database
SessionLocal = sessionmaker(
    autocommit=False,  # Manual transaction control
    autoflush=False,  # Manual flush control
    bind=engine,
)

# Base class for all models
# All database models will inherit from this
Base = declarative_base()


@contextmanager
def get_db_context():
    """
    Context manager for database sessions.
    
    Automatically handles commit, rollback, and cleanup.
    
    Usage in Flask endpoints:
        with get_db_context() as db:
            url = URL(short_code="abc", original_url="https://...")
            db.add(url)
            db.commit()
            db.refresh(url)
    
    On exception: automatically rolls back
    On completion: automatically closes session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

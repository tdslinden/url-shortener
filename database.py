"""
Database configuration and session management.

This module sets up SQLAlchemy engine and session factory.
Import db objects from here to interact with the database.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine - manages connections to database
# echo=True logs all SQL queries (useful for debugging)
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# Session factory - creates database sessions
# Sessions are how you interact with the database
SessionLocal = sessionmaker(
    autocommit=False,  # Manual transaction control
    autoflush=False,  # Manual flush control
    bind=engine,
)

# Base class for all models
# All your database models will inherit from this
Base = declarative_base()


def get_db():
    """
    Get a database session.

    Usage:
        db = get_db()
        try:
            # Use db here
            db.add(url_object)
            db.commit()
        finally:
            db.close()

    Or use as context manager (better):
        with get_db() as db:
            db.add(url_object)
            db.commit()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

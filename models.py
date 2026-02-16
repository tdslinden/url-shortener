from sqlalchemy import String, Index, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from datetime import datetime


class URL(Base):
    """
    URL shortener table.

    Stores mapping between short codes and original URLs,
    plus metadata like click count and creation timestamp.
    """

    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column(String(6), unique=True, index=True)
    original_url: Mapped[str] = mapped_column(String)
    clicks: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<URL(short_code='{self.short_code}', clicks={self.clicks})>"


# Create composite index for common queries
# Example: finding URLs by creation date range
Index("idx_created_at", URL.created_at)

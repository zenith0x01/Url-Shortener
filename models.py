from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from database import Base

# This class = one table in your database called "urls"
class URL(Base):
    __tablename__ = "urls"

    # Each variable below = one column in the table

    id           = Column(Integer, primary_key=True, index=True)  # auto-increments
    original_url = Column(String, nullable=False)                 # the long URL
    short_code   = Column(String, unique=True, index=True)        # e.g. "abc123"
    created_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<URL short_code={self.short_code} original={self.original_url}>"
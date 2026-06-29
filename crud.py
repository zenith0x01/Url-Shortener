import string
import random
from sqlalchemy.orm import Session
from models import URL

# ── Helper ─────────────────────────────────────────────────────────────────────

def generate_short_code(length: int = 6) -> str:
    """Generates a random 6-character code like 'aB3xYz'"""
    chars = string.ascii_letters + string.digits   # a-z + A-Z + 0-9
    return "".join(random.choices(chars, k=length))


# ── Database operations ────────────────────────────────────────────────────────

def get_url_by_short_code(db: Session, short_code: str) -> URL | None:
    """Look up a URL row by its short code. Returns None if not found."""
    return db.query(URL).filter(URL.short_code == short_code).first()


def get_url_by_original(db: Session, original_url: str) -> URL | None:
    """Check if this long URL was already shortened before."""
    return db.query(URL).filter(URL.original_url == original_url).first()


def create_short_url(db: Session, original_url: str, custom_alias: str | None = None) -> URL:
    """
    Creates a new short URL record in the database.
    Uses custom_alias if provided, otherwise generates a random code.
    """
    # Use custom alias or generate one
    short_code = custom_alias or generate_short_code()

    new_url = URL(
        original_url=original_url,
        short_code=short_code
    )

    db.add(new_url)     # stage the new record
    db.commit()         # save to database
    db.refresh(new_url) # reload from DB to get generated fields (id, created_at)

    return new_url
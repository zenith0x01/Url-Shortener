from pydantic import BaseModel, HttpUrl
from datetime import datetime

# ── Request shape ──────────────────────────────────────────────────────────────
# This is what the CLIENT sends to your API

class URLRequest(BaseModel):
    url: HttpUrl                        # Pydantic rejects anything that isn't a valid URL
    custom_alias: str | None = None     # optional — user can pick their own short code


# ── Response shape ─────────────────────────────────────────────────────────────
# This is what YOUR API sends back to the client

class URLResponse(BaseModel):
    short_code:   str
    short_url:    str
    original_url: str
    created_at:   datetime

    # This lets Pydantic read a SQLAlchemy model object directly
    # without this, you'd have to manually convert it to a dict
    model_config = {"from_attributes": True}
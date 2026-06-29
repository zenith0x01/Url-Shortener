from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from fastapi.responses import RedirectResponse, FileResponse  # ← add FileResponse here
from fastapi.staticfiles import StaticFiles

from database import engine, get_db, Base
from models import URL
from schemas import URLRequest, URLResponse
import crud

# Create all tables in the database on startup (if they don't exist yet)
Base.metadata.create_all(bind=engine)



app = FastAPI(title="URL Shortener", version="1.0.0")

@app.get("/app")
def serve_frontend():
    return FileResponse("index.html")



# ── CORS ───────────────────────────────────────────────────────────────────────
# Without this, your browser will BLOCK requests from your frontend to this API
# because they run on different ports (e.g. :3000 vs :8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # In production: replace with your frontend's domain
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_URL = "http://localhost:8000"  # change this when you deploy


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    """Health check — just to confirm the API is running."""
    return {"message": "URL Shortener API is running"}


@app.post("/shorten", response_model=URLResponse)
def shorten_url(payload: URLRequest, db: Session = Depends(get_db)):
    """
    Takes a long URL and returns a short one.

    - Pydantic validates the incoming JSON automatically via URLRequest
    - Depends(get_db) injects the database session
    - response_model=URLResponse filters what gets sent back
    """
    original_url = str(payload.url)

    # If a custom alias is given, make sure it's not already taken
    if payload.custom_alias:
        existing = crud.get_url_by_short_code(db, payload.custom_alias)
        if existing:
            raise HTTPException(status_code=400, detail="That alias is already taken")

    # If this URL was already shortened before, return the existing one
    existing = crud.get_url_by_original(db, original_url)
    if existing:
        return URLResponse(
            short_code=existing.short_code,
            short_url=f"{BASE_URL}/{existing.short_code}",
            original_url=existing.original_url,
            created_at=existing.created_at
        )

    # Create the new short URL in the database
    new_url = crud.create_short_url(
        db=db,
        original_url=original_url,
        custom_alias=payload.custom_alias
    )

    return URLResponse(
        short_code=new_url.short_code,
        short_url=f"{BASE_URL}/{new_url.short_code}",
        original_url=new_url.original_url,
        created_at=new_url.created_at
    )


@app.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    """
    When someone visits /abc123, look it up and redirect to the original URL.
    302 = temporary redirect (safe to change later, unlike 301 which browsers cache)
    """
    db_url = crud.get_url_by_short_code(db, short_code)

    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=db_url.original_url, status_code=302)
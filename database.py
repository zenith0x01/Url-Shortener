from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# This is the database file that will be created in your project folder
# SQLite is perfect for local development — no setup needed
import os

load_dotenv()  # reads .env file

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)  # no connect_args needed

# SessionLocal is a factory — every time you call it, you get a new DB session
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,   # we manually commit changes
    autoflush=False     # we manually flush changes
)

# Base class that all our models (tables) will inherit from
class Base(DeclarativeBase):
    pass

# Dependency used in FastAPI routes
# It opens a session, gives it to the route, then closes it when done
def get_db():
    db = SessionLocal()
    try:
        yield db        # hands the session to your route function
    finally:
        db.close()      # always closes, even if an error occurs
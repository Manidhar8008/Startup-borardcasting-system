import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use SQLite for local development, gracefully switchable to PostgreSQL via env var.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jan_ai_saas.db")

# SQLite specific connect args (not needed for Postgres)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

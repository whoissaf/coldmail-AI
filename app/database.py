import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Baca dari .env, fallback ke SQLite lokal jika DATABASE_URL tidak ada (untuk dev offline)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./coldgenius.db")

# Konfigurasi khusus untuk SQLite agar thread-safe
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

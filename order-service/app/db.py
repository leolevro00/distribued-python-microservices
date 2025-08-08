from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}"


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Crea le tabelle (una volta sola)
def init_db():
    Base.metadata.create_all(bind=engine)

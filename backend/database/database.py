import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()
DB_USER     = os.environ.get("POSTGRES_USER", "salesgenie")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "salesgenie_dev")
DB_NAME     = os.environ.get("POSTGRES_DB", "salesgenie")
DB_HOST     = os.environ.get("POSTGRES_HOST", "localhost") 
DB_PORT     = int(os.environ.get("DB_PORT", "5432"))         

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    echo=os.environ.get("SQL_ECHO") == "1",
    connect_args={
        "application_name": "salesgenie-api",
        "options": "-c timezone=UTC",
    },
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore",)

settings = Settings()

class Base(DeclarativeBase):
    pass

engine = create_engine(settings.DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

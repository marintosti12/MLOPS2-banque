import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DATABASE_URL = os.environ["DATABASE_URL"]  
engine = create_engine(DATABASE_URL, future=True)

UPSERT = text("""
    INSERT INTO ml_models (id, name, description, created_at, is_active)
    VALUES (:id, :name, :description, :created_at, :is_active)
    ON CONFLICT (name) DO UPDATE
      SET description = EXCLUDED.description,
          is_active  = EXCLUDED.is_active
""")

def seed_ml_models(session: Session):
    rows = [
        {"id": "5b1c7b3a-0000-4000-8000-000000000001", "name": "baseline",   "description": "Baseline model", "is_active": True},
        {"id": "5b1c7b3a-0000-4000-8000-000000000002", "name": "best_model", "description": "Best model",        "is_active": False},
    ]
    now = datetime.now(timezone.utc)
    for r in rows:
        session.execute(UPSERT, {**r, "created_at": now})

def main():
    with Session(engine) as s:
        seed_ml_models(s)
        s.commit()

if __name__ == "__main__":
    main()

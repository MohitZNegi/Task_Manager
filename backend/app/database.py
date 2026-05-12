from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
)

# SessionLocal is a factory — calling SessionLocal() creates a new DB session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent all ORM models inherit from.
# It holds the metadata (table definitions) SQLAlchemy uses to create/query tables.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency. Yields a DB session per request, then closes it.
    The try/finally guarantees the session closes even if the route raises.

    Used as: db: Session = Depends(get_db)
    FastAPI calls this, injects the session, and cleans up after the response.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
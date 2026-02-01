from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from .config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import models here if you want to use Base.metadata.create_all(bind=engine)
    # For now, we use the schema.sql script
    pass

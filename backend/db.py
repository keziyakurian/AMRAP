from sqlalchemy import create_engine
from .config import config

# Single DB connection point
engine = create_engine(config.DB_URL)

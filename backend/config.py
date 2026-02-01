import os

class Config:
    # Database Configuration
    # Update these with your actual database credentials
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "mr_db")
    
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'sample_data')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
    
    # SOW Analysis Settings
    SOW_MODEL_NAME = 'all-MiniLM-L6-v2'  # Lightweight efficient transformer model

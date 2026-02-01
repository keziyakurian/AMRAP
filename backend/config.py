import os

# Central config for DB, paths, model params

class Config:
    # Database Configuration
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "mr_db")
    
    DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_PATH = os.path.join(BASE_DIR, 'sample_data')
    CHART_PATH = os.path.join(BASE_DIR, 'charts')
    OUTPUT_PATH = os.path.join(BASE_DIR, 'deliverables')
    
    # NLP / AI Settings
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    SIMILARITY_THRESHOLD = 0.65

# Ensure directories exist
os.makedirs(Config.DATA_PATH, exist_ok=True)
os.makedirs(Config.CHART_PATH, exist_ok=True)
os.makedirs(Config.OUTPUT_PATH, exist_ok=True)

config = Config()

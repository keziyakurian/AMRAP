import pyreadstat
import pandas as pd
from backend.db import engine

def load_spss(file_path):
    print(f"Loading SPSS file: {file_path}")
    df, meta = pyreadstat.read_sav(file_path)
    
    # Ingest to 'responses' table
    # Using 'replace' for MVP to clear old run data, or 'append' for production persistence
    print(f"Writing {len(df)} rows to database...")
    df.to_sql("responses", engine, if_exists="replace", index=False)
    print("Ingestion complete.")
    
    return df

import pandas as pd
import pyreadstat
import os
from sqlalchemy import text
from .database import engine

def load_spss_to_db(file_path: str, study_name: str):
    """
    Reads an SPSS file and ingests it into the database.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    print(f"Reading SPSS file: {file_path}...")
    df, meta = pyreadstat.read_sav(file_path)
    
    # Add metadata columns
    # df['study_name'] = study_name
    
    # In a real scenario, you probably want to normalize this.
    # For this MVP, let's assume we maintain the DataFrame structure 
    # but maybe upsert basic study info first.
    
    with engine.connect() as conn:
        # Check if study exists
        result = conn.execute(text("SELECT id FROM studies WHERE study_name = :name"), {"name": study_name})
        study_id = result.scalar()
        
        if not study_id:
            print(f"Creating new study: {study_name}")
            result = conn.execute(
                text("INSERT INTO studies (study_name) VALUES (:name) RETURNING id"),
                {"name": study_name}
            )
            study_id = result.scalar()
            conn.commit()
    
    print(f"Ingesting {len(df)} rows for study {study_name} (ID: {study_id})...")
    
    # Store Raw Data
    # For simplicity in this demo, we'll write the dataframe to a table named after the study
    # OR map it to the 'raw_responses' EAV table.
    # To keep it essentially 'pandas-ready', dumping to a dedicated table is often easier for Analytics.
    
    table_name = "responses"
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    
    print(f"Data successfully saved to table '{table_name}'.")
    return study_id, table_name

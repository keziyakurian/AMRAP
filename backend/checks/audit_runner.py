import pandas as pd
import os
from backend.db import engine
from backend.config import config
from .rule_checks import run_rule_checks
from .nlp_relevance import score_relevance

def run_audit(df):
    print("Running Automated Data Audit...")
    audit_rows = []

    # 1. Run Rule Checks
    print("- Executing Rule-Based Checks...")
    audit_rows.extend(run_rule_checks(df))

    # 2. Run NLP Relevance Checks
    print("- Executing NLP SOW Relevance Checks...")
    sow_path = os.path.join(config.DATA_PATH, "sow.txt")
    if os.path.exists(sow_path):
        with open(sow_path, "r") as f:
            sow_text = f.read()
            
        metric_labels = df.columns.tolist()
        relevance = score_relevance(sow_text, metric_labels)
        
        for r in relevance:
            # We log these as specific checks
            audit_rows.append({
                "variable": r["metric"],
                "check": "SOW Relevance",
                "status": "Yes" if r["relevant"] else "No",
                "comments": f"Similarity Score: {round(r['similarity'], 2)}"
            })
    else:
        print(f"Warning: sow.txt not found at {sow_path}. Skipping NLP checks.")

    # 3. Save to Database
    print("- Saving Audit Results to Database...")
    audit_df = pd.DataFrame(audit_rows)
    
    # Map to schema columns: check_category, check_item, status, details
    # We rename to match our schema.sql or update schema.sql to match this?
    # User's Plan code used "data_checks" table.
    # Schema.sql has: check_category, check_item, status, details
    # Audit rows have: variable, check, status, comments
    
    db_ready_df = audit_df.rename(columns={
        "variable": "check_category", # Broad mapping
        "check": "check_item",
        "comments": "details"
    })
    
    # Add study_id (default 1 for MVP)
    db_ready_df['study_id'] = 1 
    
    db_ready_df.to_sql("data_checks", engine, if_exists="append", index=False)
    print("Audit Complete.")

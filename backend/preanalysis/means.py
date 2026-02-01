import pandas as pd
from backend.db import engine

def compute_means():
    print("Computing Means (Step 3)...")
    
    # For MVP, we assume the 'responses' table is flat: Respondent x Metrics
    # So we compute mean of metric columns grouped by Brand (if Brand column exists)
    # If no Brand column, we compute Total Means.
    
    # 1. Read Data
    df = pd.read_sql("SELECT * FROM responses", engine)
    
    # Identify numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Identify Grouping Column (Brand)
    group_cols = [c for c in df.columns if 'brand' in c.lower()]
    
    if group_cols:
        group_col = group_cols[0]
        print(f"Grouping by {group_col}")
        # Group and Mean
        means_df = df.groupby(group_col)[numeric_cols].mean().reset_index()
        
        # Melt to ID-Variable-Value format for DB storage if needed, 
        # But user plan suggested: SELECT study_id, brand_id, metric_id, AVG...
        # We'll save the result in a flexible way corresponding to 'preanalysis_results'
        
        # We need to reshape to fit: study_id, brand_id, metric_id, mean_score
        # For this MVP refactor, we'll store the PIVOTED means (easier for next steps) 
        # or stick to the relational schema.
        # User Code Plan: df.to_sql("preanalysis_results", ...)
        # Let's save the summary table directly.
        
        means_df['study_id'] = 1
        means_df.to_sql("preanalysis_results", engine, if_exists="replace", index=False)
        
    else:
        print("No Brand column found. Computing Total Means.")
        means = df[numeric_cols].mean().to_frame().T
        means['study_id'] = 1
        means.to_sql("preanalysis_results", engine, if_exists="replace", index=False)
        
    print("Pre-analysis means saved.")

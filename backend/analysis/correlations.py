import pandas as pd
from backend.db import engine

def compute_correlations():
    print("Computing Correlations (Step 4)...")
    
    # Load Pre-analysis results
    # Ideally correlation is run on RAW data (Respondent Level) for Metric-to-Metric correlation?
    # OR Mean Level (Brand-to-Brand correlation)?
    # User Plan says: "pivot = df.pivot... corr = pivot.corr()" from preanalysis_results.
    # This implies correlation of patterns across BRANDS.
    
    try:
        df = pd.read_sql("SELECT * FROM preanalysis_results", engine)
    except:
        print("Preanalysis results not found.")
        return

    # Determine Pivot Index
    # We look for the brand column
    cols = df.columns
    brand_col = next((c for c in cols if 'brand' in c.lower()), None)
    
    if not brand_col:
        print("Cannot compute correlation without Brand variance (only 1 row?).")
        return

    # Pivot: Index=Brand, Columns=Metrics (all numeric except IDs)
    non_metric_cols = ['study_id', brand_col, 'index']
    metric_cols = [c for c in df.columns if c not in non_metric_cols]
    
    # If the table is already wide (Brand x Metric1 x Metric2...), we just set index
    df_pivot = df.set_index(brand_col)[metric_cols]
    
    # Compute Corr
    corr_matrix = df_pivot.corr()
    
    # Save
    # We'll save the matrix (Metrics x Metrics)
    # The DB table 'correlations' in schema is Long format (Metric A, Metric B, Val).
    # But user plan says: corr.to_sql("correlations"). Pandas to_sql dumps the matrix.
    # We will dump the matrix as requested.
    
    corr_matrix.to_sql("correlations", engine, if_exists="replace")
    print("Correlations saved.")

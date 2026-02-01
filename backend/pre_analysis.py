import pandas as pd
from sqlalchemy import func
from .database import SessionLocal
from .models import Response, PreAnalysisResult, Metric

def compute_brand_means(study_id: int):
    """
    Computes mean scores for all numeric columns in 'responses'.
    Stores results in preanalysis_results table.
    """
    print(f"Computing means for study {study_id}...")
    
    # 1. Load Data
    # We read from the 'responses' table which ingestion created
    query = f"SELECT * FROM responses"
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        print(f"Error reading responses: {e}")
        return

    db = SessionLocal()
    
    # 2. Compute Means for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    means = df[numeric_cols].mean()
    
    print(f"Computed means for {len(means)} metrics.")
    
    # 3. Save to DB
    # We map Column Name -> Metric Name
    # We assume a default Brand ID 1 for MVP (Total)
    
    for col, mean_val in means.items():
        # Get or Create Metric
        metric = db.query(Metric).filter_by(metric_label=col).first()
        if not metric:
            metric = Metric(metric_label=col, category="Auto-Detected")
            db.add(metric)
            db.commit()
            
        # Insert Result
        res = PreAnalysisResult(
            study_id=study_id,
            brand_id=1, # Default Brand
            metric_id=metric.id,
            mean_score=float(mean_val),
            base_size=len(df)
        )
        db.add(res)
    
    db.commit()
    db.close()

def get_preanalysis_df(study_id: int):
    """Returns the pre-analysis data as a Pivot Table."""
    db = SessionLocal()
    query = db.query(PreAnalysisResult).filter(PreAnalysisResult.study_id == study_id)
    df = pd.read_sql(query.statement, db.bind)
    db.close()
    
    if df.empty:
        return pd.DataFrame()

    # Flatten for correlation: Rows=Brands(or 1), Cols=Metrics, Values=Mean
    # Since we only have Brand=1, correlation across brands impossible?
    # Actually, for Correlation we need respondent level data usually OR correlation across brands.
    # The user asked: "Compute Pearson correlations between metrics/endorsements."
    # Usually this is correlation of *metrics* across *brands* (e.g. Image A vs Image B).
    # If we only have 1 brand, we can't do this.
    # So we need to pivot: Index=Brand, Col=Metric.
    
    pivot_df = df.pivot(index='brand_id', columns='metric_id', values='mean_score')
    return pivot_df

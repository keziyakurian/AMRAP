import pandas as pd
from sqlalchemy import func
from .database import SessionLocal
from .models import Response, PreAnalysisResult, Metric

def compute_brand_means(study_id: int):
    """
    Computes mean scores for all brands and metrics in a study.
    Store results in preanalysis_results table.
    """
    db = SessionLocal()
    
    # SQL Aggregation
    # SELECT brand_id, metric_id, AVG(value), COUNT(*)
    # FROM responses WHERE study_id = X
    # GROUP BY brand_id, metric_id
    
    results = db.query(
        Response.brand_id,
        Response.metric_id,
        func.avg(Response.value).label('mean_score'),
        func.count(Response.id).label('base_size')
    ).filter(
        Response.study_id == study_id
    ).group_by(
        Response.brand_id,
        Response.metric_id
    ).all()
    
    print(f"Computed means for {len(results)} brand-metric pairs.")
    
    # Save to DB
    for row in results:
        # Check if exists to update or insert
        # Simplified: just adding new for now
        res = PreAnalysisResult(
            study_id=study_id,
            brand_id=row.brand_id,
            metric_id=row.metric_id,
            mean_score=row.mean_score,
            base_size=row.base_size
        )
        db.add(res)
    
    db.commit()
    db.close()

def get_preanalysis_df(study_id: int):
    """Returns the pre-analysis data as a Pandas DataFrame (Pivot Table)."""
    db = SessionLocal()
    query = db.query(PreAnalysisResult).filter(PreAnalysisResult.study_id == study_id)
    df = pd.read_sql(query.statement, db.bind)
    db.close()
    
    # Pivot: Index=Brand, Columns=Metric, Values=Mean
    # We need to join with Brand and Metric names for readability, 
    # but for raw calculation ID is fine.
    
    pivot_df = df.pivot(index='brand_id', columns='metric_id', values='mean_score')
    return pivot_df

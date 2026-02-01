import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from .models import Correlation, Metric
from .config import config
import os

# Ensure charts directory exists
os.makedirs(config.CHARTS_DIR, exist_ok=True)

def run_correlation_analysis(study_id: int):
    """
    Computes Pearson correlation matrix from pre-analysis results.
    Saves heatmap and stores values in DB.
    """
    print("Running Correlation Analysis...")
    
    # 1. Fetch Data
    # relying on pre_analysis module or direct query
    from .pre_analysis import get_preanalysis_df
    df_pivot = get_preanalysis_df(study_id)
    
    if df_pivot.empty:
        print("No data for correlation analysis.")
        return

    # 2. Compute Correlation
    corr_matrix = df_pivot.corr(method='pearson')
    
    # 3. Save Heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Brand Metric Correlations")
    heatmap_path = os.path.join(config.CHARTS_DIR, f"correlation_heatmap_{study_id}.png")
    plt.savefig(heatmap_path)
    plt.close()
    print(f"Saved correlation heatmap to {heatmap_path}")
    
    # 4. Save to Database
    db = SessionLocal()
    # Clear old correlations for this study
    db.query(Correlation).filter(Correlation.study_id == study_id).delete()
    
    # Iterate and save
    # Metric IDs are columns and index
    for metric_a in corr_matrix.index:
        for metric_b in corr_matrix.columns:
            val = corr_matrix.loc[metric_a, metric_b]
            # Avoid self-correlation if desired, but keeping 1.0 is fine
            corr_entry = Correlation(
                study_id=study_id,
                metric_a_id=int(metric_a),
                metric_b_id=int(metric_b),
                correlation_coefficient=val
            )
            db.add(corr_entry)
            
    db.commit()
    db.close()
    
    return corr_matrix

def run_factor_analysis(study_id: int, n_components=3):
    """
    Runs Factor Analysis (PCA or FA) to group metrics.
    """
    from sklearn.decomposition import FactorAnalysis
    from .pre_analysis import get_preanalysis_df
    
    print("Running Factor Analysis...")
    df_pivot = get_preanalysis_df(study_id)
    
    if df_pivot.empty:
        return
        
    fa = FactorAnalysis(n_components=n_components, random_state=42)
    # Fill NAs if any with 0 or mean
    df_clean = df_pivot.fillna(0)
    
    fa.fit(df_clean)
    
    # Loadings: rows=components, cols=metrics
    loadings = pd.DataFrame(
        fa.components_,
        columns=df_clean.columns,
        index=[f'Factor_{i+1}' for i in range(n_components)]
    )
    
    print("Factor Loadings:")
    print(loadings.T)
    # Logic to save factors to DB would go here
    
    return loadings

from sklearn.decomposition import FactorAnalysis
import pandas as pd
from backend.db import engine

def run_factor_analysis():
    print("Running Factor Analysis (Step 5)...")
    
    try:
        df = pd.read_sql("SELECT * FROM preanalysis_results", engine)
    except:
        return

    # Pivot setup similar to correlations
    cols = df.columns
    brand_col = next((c for c in cols if 'brand' in c.lower()), None)
    
    if not brand_col:
        print("Need brand variance for FA.")
        return

    non_metric_cols = ['study_id', brand_col, 'index']
    metric_cols = [c for c in df.columns if c not in non_metric_cols]
    df_pivot = df.set_index(brand_col)[metric_cols].dropna()

    if df_pivot.empty:
        print("Not enough data for FA.")
        return

    # Factor Analysis
    n_comps = min(5, len(df_pivot.columns), len(df_pivot))
    fa = FactorAnalysis(n_components=n_comps)
    fa.fit(df_pivot)

    loadings = pd.DataFrame(
        fa.components_,
        columns=df_pivot.columns,
        index=[f'Factor_{i+1}' for i in range(n_comps)]
    )

    print("Factor Loadings (Top):")
    print(loadings.iloc[:, :5])
    
    loadings.to_sql("factors", engine, if_exists="replace")
    print("Factors saved.")

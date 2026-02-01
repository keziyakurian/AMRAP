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
    Runs Factor Analysis (PCA or FA) to group metrics and generates BIP Map.
    """
    from sklearn.decomposition import FactorAnalysis, PCA
    from .pre_analysis import get_preanalysis_df
    
    print("Running Factor Analysis & Visualization...")
    df_pivot = get_preanalysis_df(study_id)
    
    if df_pivot.empty:
        print("Error: No data available for Factor Analysis.")
        return
        
    # Data Cleaning: Fill NA
    df_clean = df_pivot.fillna(0)
    
    # 1. Factor Analysis (for Hierarchy / Groupings)
    fa = FactorAnalysis(n_components=n_components, random_state=42)
    fa.fit(df_clean)
    
    loadings = pd.DataFrame(
        fa.components_,
        columns=df_clean.columns,
        index=[f'Factor_{i+1}' for i in range(n_components)]
    )
    
    print("\nFactor Loadings (Metrics to Factors):")
    print(loadings.T)
    
    # Save Loadings to CSV (or DB)
    loadings_path = os.path.join(config.OUTPUT_DIR, f"factor_loadings_{study_id}.csv")
    loadings.T.to_csv(loadings_path)
    print(f"Saved Factor Loadings to {loadings_path}")

    # 2. BIP Map (Brand Interaction / Positioning)
    # Using PCA for 2D visualization of Brands vs Metrics
    # Biplot: Brands are points, Metrics are vectors (loadings)
    
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(df_clean) # Shape: (n_brands, 2)
    
    # Coordinates of Brands
    brand_coords = pd.DataFrame(pca_result, columns=['Dim1', 'Dim2'], index=df_clean.index)
    
    # Coordinates of Metrics (Loadings * Scalar for scaling)
    # Allows plotting vectors on same chart
    metric_coords = pd.DataFrame(pca.components_.T, columns=['Dim1', 'Dim2'], index=df_clean.columns)
    
    # Plotting
    plt.figure(figsize=(12, 10))
    
    # Plot Metrics (Vectors)
    for metric in metric_coords.index:
        x = metric_coords.loc[metric, 'Dim1']
        y = metric_coords.loc[metric, 'Dim2']
        plt.arrow(0, 0, x, y, color='red', alpha=0.5, head_width=0.05)
        plt.text(x*1.1, y*1.1, str(metric), color='darkred', fontsize=9)
        
    # Plot Brands (Points)
    for brand_id in brand_coords.index:
        x = brand_coords.loc[brand_id, 'Dim1']
        y = brand_coords.loc[brand_id, 'Dim2']
        plt.scatter(x, y, color='blue', s=100)
        plt.text(x+0.05, y+0.05, f"Brand {brand_id}", color='blue', fontsize=12, fontweight='bold')
        
    plt.xlabel(f"Dimension 1 ({pca.explained_variance_ratio_[0]:.1%})")
    plt.ylabel(f"Dimension 2 ({pca.explained_variance_ratio_[1]:.1%})")
    plt.title("BIP Map (Brand Positioning)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.axhline(0, color='black', linewidth=1)
    plt.axvline(0, color='black', linewidth=1)
    
    bip_path = os.path.join(config.CHARTS_DIR, f"bip_map_{study_id}.png")
    plt.savefig(bip_path)
    plt.close()
    print(f"Saved BIP Map to {bip_path}")
    
    return loadings, brand_coords

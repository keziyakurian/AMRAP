import subprocess
import os
import pandas as pd
from .config import config

def run_r_path_model(data_csv_path: str, output_csv_path: str):
    """
    Executes the R script for Path Analysis.
    
    Args:
        data_csv_path: Input data for R.
        output_csv_path: Where R should save the coefficients.
    """
    r_script = config.R_SCRIPT_PATH
    
    if not os.path.exists(r_script):
        print(f"Error: R script not found at {r_script}")
        return
        
    cmd = ["Rscript", r_script, data_csv_path, output_csv_path]
    
    print(f"Running R model: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("R Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("R Execution Failed!")
        print(e.stderr)
        raise e

def process_modelling_step(study_id: int):
    """
    Prepares data, runs R model, and processes results.
    """
    # 1. Export Data for R
    # We might need respondent-level data for SEM, or correlation matrix
    # Assuming respondent level for this example
    from .ingestion import SessionLocal, Response
    
    db = SessionLocal()
    # Simplified export: fetching all responses for study
    # Ideally should be pivoted (Respondents x Metrics)
    # ignoring for brevity, assuming 'data.csv' exists or logic is implemented
    
    data_path = os.path.join(config.SAMPLE_DATA_DIR, "model_input.csv")
    output_path = os.path.join(config.OUTPUT_DIR, "model_results.csv")
    
    # perform export logic here... 
    # df.to_csv(data_path)
    
    # 2. Run R
    # run_r_path_model(data_path, output_path)
    
    # 3. Ingest Results
    if os.path.exists(output_path):
        results = pd.read_csv(output_path)
        print("Model Results Loaded:")
        print(results.head())
        # Filter weak paths (< 0.1)
        strong_paths = results[results['est'].abs() > 0.1]
        print(f"Retained {len(strong_paths)} strong paths.")
        
    db.close()

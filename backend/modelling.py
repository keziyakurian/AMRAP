import subprocess
import os
import pandas as pd
from .config import config
from .database import engine

def run_r_path_model(study_id: int):
    """
    Exports data to CSV, triggers R script, and reads back results.
    """
    print("Step 7: Preparing data for R Path Analysis...")
    
    # 1. Export Data to CSV
    query = "SELECT * FROM responses WHERE study_id = :sid"
    df = pd.read_sql(query, engine, params={"sid": study_id})
    
    if df.empty:
        print("No data for Path Analysis.")
        return

    # Select only numeric
    df_numeric = df.select_dtypes(include=['number'])
    
    input_csv = os.path.join(config.OUTPUT_DIR, f"r_input_{study_id}.csv")
    output_csv = os.path.join(config.OUTPUT_DIR, f"r_output_paths_{study_id}.csv")
    
    df_numeric.to_csv(input_csv, index=False)
    print(f"Data exported to {input_csv}")
    
    # 2. Run R Script
    r_script_path = os.path.join(config.BASE_DIR, 'r_models', 'path_model.R')
    
    # Verify R installation
    try:
        subprocess.run(["Rscript", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("ERROR: 'Rscript' not found. Please ensure R is installed and in PATH.")
        return

    print("Executing R script...")
    cmd = ["Rscript", r_script_path, input_csv, output_csv]
    
    process = subprocess.run(cmd, capture_output=True, text=True)
    
    if process.returncode != 0:
        print("R Script Failed:")
        print(process.stderr)
        return
    else:
        print("R Script Success.")
        print(process.stdout)
        
    # 3. Read Results
    if os.path.exists(output_csv):
        paths_df = pd.read_csv(output_csv)
        print("Model Paths (Top 5):")
        print(paths_df.head())
        
        # Save to DB (Optional)
        # paths_df.to_sql('model_paths', engine, if_exists='append')
    else:
        print("Output file not found.")


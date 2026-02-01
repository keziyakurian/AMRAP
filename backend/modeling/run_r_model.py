import subprocess
import os
from backend.config import config

def run_r():
    print("Running R Path Model (Step 6)...")
    script_path = os.path.join(config.BASE_DIR, "r_models", "path_model.R")
    
    # We assume the R script knows where to pull data (or we pass it)
    # User Plan: subprocess.run(["Rscript", "r_models/path_model.R"])
    
    if os.path.exists(script_path):
        subprocess.run(["Rscript", script_path])
        print("R Model Execution triggered.")
    else:
        print(f"R Script not found at {script_path}")

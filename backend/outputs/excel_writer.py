from openpyxl import Workbook, load_workbook
import pandas as pd
from backend.db import engine
from backend.config import config
import os

def write_excel():
    print("Generating Excel Deliverable (Step 9)...")
    
    output_file = os.path.join(config.OUTPUT_PATH, "output.xlsx")
    
    # We can use pandas ExcelWriter for multiple sheets easily
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # 1. Data Checks
        try:
            checks = pd.read_sql("SELECT * FROM data_checks", engine)
            checks.to_excel(writer, sheet_name="Data Checks", index=False)
        except:
            pass
            
        # 2. Means
        try:
            means = pd.read_sql("SELECT * FROM preanalysis_results", engine)
            means.to_excel(writer, sheet_name="Pre-Analysis", index=False)
        except:
            pass
            
        # 3. Correlations
        try:
            corrs = pd.read_sql("SELECT * FROM correlations", engine)
            corrs.to_excel(writer, sheet_name="Correlations")
        except:
            pass

    print(f"Excel saved to {output_file}")

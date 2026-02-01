import sys
import os
from database import init_db
from ingestion import ingest_spss
from checks import DataValidator
from pre_analysis import compute_brand_means
from analytics import run_correlation_analysis, run_factor_analysis
from outputs import generate_excel_report, generate_ppt_presentation
# from modelling import process_modelling_step # Uncomment when R is ready

def main():
    print("Initializing AMRAP System...")
    init_db()
    
    # 1. Pipeline Definition
    # Ideally, arguments would come from CLI or API
    file_path = "sample_data/demo.sav"
    study_name = "Project_Alpha"
    wave_no = 1
    
    # Dummy data creation for testing if file doesn't exist
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found. Using mock Data Check flow.")
        # Create a mock dataframe for testing checks
        import pandas as pd
        mock_df = pd.DataFrame({
            'respondent_id': range(1, 301),
            'week': [1] * 100 + [2] * 100 + [3] * 100,
            'brand_name': ['BrandA', 'BrandB', 'BrandC'] * 100,
            'value': [4, 5, 3] * 100
        })
        mock_meta = type('Meta', (), {'column_names_to_labels': {'week': 'Week No', 'brand_name': 'Brand Name'}, 'variable_value_labels': {}})()
        
        # SOW Requirements from User
        sow_reqs = [
            "Time frame – Week No.",
            "Variable Labels – Familiarity",
            "Base Sizes",
            "All Brands Present"
        ]
        
        validator = DataValidator(mock_df, mock_meta, sow_reqs)
        validator.run_all_checks()
        print("Data Validation Complete. See DB or Logs.")
        
        # Continue to reporting steps with mock data not possible without DB ingestion
        # So we return here for the demo
        return

    # Real Flow
    # Step 1: Ingestion
    ingest_spss(file_path, study_name, wave_no)
    
    # Step 2: Checks (Requires loading df again or passing it)
    # In a real app, ingestion returns the df
    # Assuming ingest_spss saves to DB and we load from there, OR we make ingest return DF.
    
    # Step 3: Pre-Analysis
    # study_id = get_study_id(study_name)
    # compute_brand_means(study_id)
    
    # Step 4: Analytics
    # run_correlation_analysis(study_id)
    
    # Step 9: Outputs
    # generate_excel_report(study_id)
    # generate_ppt_presentation(study_id)
    
    print("Pipeline Execution Finished.")

if __name__ == "__main__":
    main()

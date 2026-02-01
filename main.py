import argparse
from backend.ingestion.spss_loader import load_spss
from backend.checks.audit_runner import run_audit
from backend.preanalysis.means import compute_means
from backend.analysis.correlations import compute_correlations
from backend.analysis.factors import run_factor_analysis
from backend.modeling.run_r_model import run_r
from backend.outputs.excel_writer import write_excel
from backend.outputs.ppt_writer import write_ppt

def run_pipeline(step=None, file_path=None):
    # Step 1: Ingestion
    if step == 1 or step is None:
        if file_path:
            df = load_spss(file_path)
            # If running full pipeline, we pass df to next step?
            # Or reliance on DB state.
            # For "run all", ideally we execute sequentially.
            if step is None:
                run_audit(df)
        else:
            print("File path required for Step 1.")
            return

    # Step 2: Checks
    if step == 2:
        # We need to load DF from DB or re-ingest?
        # For simplicity, let's assume Ingestion populated DB.
        # But audit_runner expects DF to check structure/columns.
        from backend.db import engine
        import pandas as pd
        df = pd.read_sql("SELECT * FROM responses", engine)
        run_audit(df)

    # Step 3: Means
    if step == 3 or step is None:
        compute_means()

    # Step 4: Correlations
    if step == 4 or step is None:
        compute_correlations()

    # Step 5: Factors
    if step == 5 or step is None:
        run_factor_analysis()

    # Step 6: R Model
    # if step == 6 or step is None:
    #    run_r()

    # Step 9: Outputs
    if step == 9:
        write_excel()
        write_ppt()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", type=int, help="Step to run")
    parser.add_argument("--file", type=str, help="Path to SPSS file")
    args = parser.parse_args()
    
    run_pipeline(step=args.step, file_path=args.file)

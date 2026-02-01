import argparse
from backend.ingestion import load_spss_to_db
from backend.data_checks import DataChecker
from backend.database import init_db

def main():
    parser = argparse.ArgumentParser(description="AMRAP: Automated Market Research Analytics Pipeline")
    parser.add_argument('--step', type=int, choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], help="Step to run")
    parser.add_argument('--file', type=str, help="Path to input file (for Step 1)")
    parser.add_argument('--study_name', type=str, default="Test_Study", help="Name of the study")
    
    args = parser.parse_args()

    # Step 0: Setup (implicitly handled by imports usually, but explicit here)
    if args.step == 0:
        print("Initializing Database...")
        init_db()
        print("Database initialized.")

    # Step 1: Ingestion
    elif args.step == 1:
        if not args.file:
            print("Error: --file is required for Step 1")
            return
        study_id, table_name = load_spss_to_db(args.file, args.study_name)
        print(f"Step 1 Complete. Study ID: {study_id}, raw data in {table_name}")

    # Step 2: Checks
    elif args.step == 2:
        # For demo purposes, we connect to the most recent study or generic table
        # We assume table name format 'raw_data_{id}' or pass it explicitly.
        # Here we just hardcode/find one for the demo logic.
        print("Running Data Checks...")
        
        # Example: Let's assume we are checking the last inserted study
        # In prod: fetch from DB or args.
        table_name = "raw_data_1" # Placeholder
        
        try:
            checker = DataChecker(study_id=1, table_name=table_name)
            
            # Define SOW requirements (Simulated input from SOW document)
            sow_requirements = [
                "Unaided Brand Awareness",
                "Tom of Mind Awareness",
                "Brand Consideration",
                "Purchase Intent",
                "Demographics: Age and Gender",
                "Net Promoter Score"
            ]
            
            checker.run_all_checks(sow_requirements)
            print("Step 2 Complete. Checks logged to DB.")
        except Exception as e:
            print(f"Error running checks: {e}")
            print("Tip: Ensure you ran Step 1 first to populate the DB.")

    else:
        print("Step not yet implemented or invalid step.")

if __name__ == "__main__":
    main()

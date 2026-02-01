import pandas as pd
import numpy as np
from sqlalchemy import text
from sentence_transformers import SentenceTransformer, util
from .database import engine

class DataChecker:
    def __init__(self, study_id, table_name):
        self.study_id = study_id
        self.table_name = table_name
        self.df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        self.results = []
        
        # Initialize NLP model for SOW matching
        # We load this lazily or once per class
        print("Loading NLP model for SOW validation...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2') 

    def log_result(self, variable, check, status, comments):
        self.results.append({
            "study_id": self.study_id,
            "check_category": variable,  # Mapping to 'Variable / Sub-Pointer'
            "check_item": check,         # Mapping to 'What is the data / check'
            "status": status,            # 'Yes' (Pass), 'No' (Fail), 'NA'
            "details": comments
        })

    def save_results(self):
        """Saves the check results to the database."""
        if not self.results:
            return
        
        results_df = pd.DataFrame(self.results)
        # Map to schema columns: check_category, check_item, status, details
        # We do this for the 'data_checks' table
        results_df.to_sql('data_checks', engine, if_exists='append', index=False)
        print("Check results saved to database.")

    def run_all_checks(self, sow_requirements=None):
        """
        Runs the full suite of checks defined in the requirements.
        sow_requirements: List of strings (sentences) describing required variables/metrics.
        """
        print("Running Time Frame Checks...")
        self.check_time_frame()
        
        print("Running Label Checks...")
        self.check_labels()
        
        print("Running Structural Checks...")
        self.check_structure()
        
        if sow_requirements:
            print("Running SOW Alignment Checks (AI-Powered)...")
            self.check_sow_alignment(sow_requirements)
            
        self.save_results()

    # --- specific checks based on user table ---

    def check_time_frame(self):
        # 1. Week No. - Ensure at least one year of data
        # Assuming variable is 'Week' or 'Date'
        # We try to auto-detect time variable
        time_cols = [c for c in self.df.columns if 'week' in c.lower() or 'date' in c.lower()]
        if time_cols:
            col = time_cols[0]
            unique_weeks = self.df[col].nunique()
            # Heuristic: 52 weeks in a year
            status = "Yes" if unique_weeks >= 48 else "No"  # Allow some buffer
            comment = f"Found {unique_weeks} weeks."
            self.log_result("Time frame – Week No.", "Ensure 1 year data", status, comment)
        else:
            self.log_result("Time frame – Week No.", "Ensure 1 year data", "No", "Week variable not found.")

        # 3. Month
        month_cols = [c for c in self.df.columns if 'month' in c.lower()]
        if month_cols:
             self.log_result("Time frame – Month", "correct monthly mapping", "Yes", "Month variable present.")
        else:
             self.log_result("Time frame – Month", "correct monthly mapping", "No", "Month variable missing.")

        # 4. Year
        year_cols = [c for c in self.df.columns if 'year' in c.lower()]
        if year_cols:
             self.log_result("Time frame – Year", "correctly coded", "Yes", "Year variable present.")
        else:
             self.log_result("Time frame – Year", "correctly coded", "No", "Year variable missing.")


    def check_labels(self):
        # Variable Labels – Familiarity
        # Heuristic: check if column headers or mapped labels seem like English
        # Python pyreadstat usually gives us the labels in metadata, but here we check the DF columns
        # or we assume column *names* are keys and we need to check coverage.
        
        # Check for non-ascii characters which might indicate encoding issues or non-English
        try:
            non_ascii = [c for c in self.df.columns if not c.isascii()]
            if not non_ascii:
                self.log_result("Variable Labels – Familiarity", "Labels in English", "Yes", "All headers ASCII.")
            else:
                self.log_result("Variable Labels – Familiarity", "Labels in English", "Warning", f"Non-ASCII chars found: {non_ascii[:3]}")
        except:
             self.log_result("Variable Labels – Familiarity", "Labels in English", "No", "Error checking labels.")

    def check_structure(self):
        # Stack vs Unstack
        # Check if data is long or wide. 
        # Long usually has a 'Background' or 'Brand' column repeating for same respondent?
        # Or simplistic check: ratio of rows to unique respondent IDs.
        
        id_cols = [c for c in self.df.columns if 'id' in c.lower() or 'resp' in c.lower()]
        if id_cols:
            resp_id = id_cols[0]
            n_rows = len(self.df)
            n_unique = self.df[resp_id].nunique()
            
            if n_rows > n_unique:
                details = f"Rows ({n_rows}) > Unique IDs ({n_unique}). Likely Stacked."
                self.log_result("Stack vs Unstack", "Check if stacked", "Yes", details)
            else:
                details = "Rows == Unique IDs. Likely Unstacked."
                # User asked to convert if unstacked. We just flag here.
                self.log_result("Stack vs Unstack", "Check if stacked", "Warning", details)
        
        # Respondent IDs Unique per brand?
        # If stacked, we group by Brand and ID and count
        brand_cols = [c for c in self.df.columns if 'brand' in c.lower()]
        if brand_cols and id_cols:
            brand_col = brand_cols[0]
            resp_id = id_cols[0]
            dupes = self.df.duplicated(subset=[resp_id, brand_col]).sum()
            if dupes == 0:
                self.log_result("Respondent IDs", "Unique per brand", "Yes", "No duplicates found.")
            else:
                self.log_result("Respondent IDs", "Unique per brand", "No", f"Found {dupes} duplicates.")

        # Base Sizes
        # Check counts per brand
        if brand_cols:
            brand_col = brand_cols[0]
            counts = self.df[brand_col].value_counts()
            low_base = counts[counts < 30].count() # Strict check
            if low_base == 0:
                self.log_result("Base Sizes", "Check base sizes >= 30", "Yes", f"Min base: {counts.min()}")
            else:
                self.log_result("Base Sizes", "Check base sizes >= 30", "Warning", f"Found groups with low base: {counts[counts<30].index.tolist()}")

    def check_sow_alignment(self, requirements_text):
        """
        Uses Semantic Search to check if required variables from SOW exist in the dataset.
        """
        # 1. Embed the dataset column names (and labels if available)
        column_names = list(self.df.columns)
        col_embeddings = self.model.encode(column_names, convert_to_tensor=True)
        
        # 2. Embed the requirements
        req_embeddings = self.model.encode(requirements_text, convert_to_tensor=True)
        
        # 3. Compute Similarity
        # For each requirement, find the best matching column
        cosine_scores = util.cos_sim(req_embeddings, col_embeddings)
        
        for i, req in enumerate(requirements_text):
            best_score = cosine_scores[i].max()
            best_col_idx = cosine_scores[i].argmax()
            best_match_col = column_names[best_col_idx]
            
            threshold = 0.5 # Confidence threshold
            
            status = "Yes" if best_score > threshold else "No"
            # Truncate req for cleanliness
            req_short = (req[:50] + '..') if len(req) > 50 else req
            
            self.log_result(
                "SOW Check", 
                req_short, 
                status, 
                f"Best match: '{best_match_col}' (Score: {best_score:.2f})"
            )

if __name__ == "__main__":
    # Test Run
    # In a real run, this is called by main.py
    print("This module is intended to be imported.")

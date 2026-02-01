import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import DataCheck
from sentence_transformers import SentenceTransformer, util
from .config import config

class DataValidator:
    def __init__(self, df: pd.DataFrame, meta, sow_requirements: list):
        """
        Args:
            df: The dataframe from SPSS.
            meta: Metadata from pyreadstat.
            sow_requirements: List of strings describing required metrics from SOW.
        """
        self.df = df
        self.meta = meta
        self.sow_requirements = sow_requirements
        self.db = SessionLocal()
        # Load NLP model
        print("Loading NLP model...")
        self.model = SentenceTransformer(config.SENTENCE_MODEL_NAME)
        self.check_results = []

    def log_result(self, category, item, status, details):
        """Logs a check result to the database and internal list."""
        check = DataCheck(
            check_category=category,
            check_item=item,
            status=status,
            details=details
        )
        self.db.add(check)
        self.check_results.append({
            "Category": category, 
            "Item": item, 
            "Status": status, 
            "Details": details
        })

    def save_results(self):
        self.db.commit()
        self.db.close()

    # --- 1. NLP-Based SOW Validation ---
    def check_sow_coverage_nlp(self):
        """
        Uses NLP to check if SOW requirements exist in the Variable Labels.
        """
        print("Running NLP SOW Match...")
        variable_labels = list(self.meta.column_names_to_labels.values())
        
        # Encode both lists
        sow_embeddings = self.model.encode(self.sow_requirements, convert_to_tensor=True)
        var_embeddings = self.model.encode(variable_labels, convert_to_tensor=True)
        
        # Compute cosine similarity
        cosine_scores = util.cos_sim(sow_embeddings, var_embeddings)
        
        # For each SOW requirement, find the best match
        for i, req in enumerate(self.sow_requirements):
            best_match_idx = np.argmax(cosine_scores[i])
            score = cosine_scores[i][best_match_idx].item()
            best_match_label = variable_labels[best_match_idx]
            
            if score > 0.8: # Threshold for "Good Match"
                self.log_result("SOW Coverage", req, "Pass", f"Matched with: '{best_match_label}' (Score: {score:.2f})")
            elif score > 0.6:
                self.log_result("SOW Coverage", req, "Warning", f"Potential match: '{best_match_label}' (Score: {score:.2f})")
            else:
                self.log_result("SOW Coverage", req, "Fail", "No matching variable found in dataset.")

    # --- 2. Specific Audit Checks (User Requirements) ---
    
    def check_time_frame(self):
        """Checks Week, Month, Year validity."""
        # 1. Week No.
        if 'week' in self.df.columns.str.lower():
            weeks = self.df.select_dtypes(include=np.number).filter(regex='(?i)week').iloc[:,0]
            unique_weeks = weeks.nunique()
            min_w, max_w = weeks.min(), weeks.max()
            self.log_result("Time Frame", "Week No.", "Info", f"Weeks present: {min_w}-{max_w} (Count: {unique_weeks})")
            if unique_weeks < 4: # Arbitrary rule for "at least a month"
                self.log_result("Time Frame", "Week No.", "Warning", "Less than 4 weeks of data found.")
        else:
            self.log_result("Time Frame", "Week No.", "Fail", "Week variable not found.")

        # 2. Month/Year
        # Assuming typical column names, this would need specific mapping logic
        pass 

    def check_variable_labels(self):
        """Checks if labels look like valid English (simple heuristic)."""
        labels = self.meta.column_names_to_labels.values()
        non_ascii = [l for l in labels if not l.isascii()]
        if len(non_ascii) > 0:
            self.log_result("Labels", "English Only", "Warning", f"Found {len(non_ascii)} labels with non-ascii characters.")
        else:
            self.log_result("Labels", "English Only", "Pass", "All labels are ASCII.")

    def check_base_sizes(self):
        """
        Check base sizes as per SOW (main >= 300, filters >= 200).
        """
        total_respondents = len(self.df)
        if total_respondents >= 300:
            self.log_result("Base Sizes", "Main Sample", "Pass", f"N={total_respondents}")
        else:
            self.log_result("Base Sizes", "Main Sample", "Fail", f"N={total_respondents} (Target: 300)")

        # Filter subgroup checks would go here loop over key groups
    
    def check_duplicates(self, id_column='respondent_id'):
        if id_column in self.df.columns:
            dupes = self.df.duplicated(subset=[id_column]).sum()
            if dupes == 0:
                self.log_result("Data Quality", "Respondent IDs", "Pass", "Unique.")
            else:
                self.log_result("Data Quality", "Respondent IDs", "Fail", f"Found {dupes} duplicates.")
        else:
            self.log_result("Data Quality", "Respondent IDs", "Skip", "ID column not found.")

    def check_all_brands_present(self, expected_brands: list):
        """
        Check if all required brands are present in the brand column.
        """
        # Assuming a 'brand_id' or 'brand_name' column exists in stacked data
        if 'brand_name' in self.df.columns:
            actual_brands = set(self.df['brand_name'].unique())
            missing = set(expected_brands) - actual_brands
            if not missing:
                self.log_result("All Brands Present", "Brand Check", "Pass", f"Found all: {actual_brands}")
            else:
                self.log_result("All Brands Present", "Brand Check", "Fail", f"Missing brands: {missing}")
    
    def run_all_checks(self):
        self.check_time_frame()
        self.check_variable_labels()
        self.check_base_sizes()
        self.check_duplicates()
        self.check_sow_coverage_nlp()
        self.save_results()
        return pd.DataFrame(self.check_results)

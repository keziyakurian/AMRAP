# AMRAP Data Checks Manual

## Overview
Step 2 of the pipeline automates the data quality assurance process. It moves away from manual Excel checks to automated Script-based validation.

## Automated Checks Implemented
The Python module `backend/data_checks.py` implements the following:

1. **Time Frame Validation**: Checks for presence of Week/Month/Year and data duration (1 year requirement).
2. **Label Integrity**: Checks for non-ASCII characters in variable labels.
3. **Structure Analysis**: Detects if data is Stacked or Unstacked based on ID/Row ratios.
4. **Duplicate Detection**: Verifies unique Respondent IDs within Brands.
5. **Base Size Validation**: Flags brands with N < 30.

## AI-Powered SOW Validation
We use the `sentence-transformers` library to validate if the dataset contains variables required by the Statement of Work (SOW).

**How it works:**
1. User provides a list of required strings (e.g., "Unaided Awareness").
2. The system converts these strings into vector embeddings.
3. The system converts all Dataset Column Headers into vector embeddings.
4. It calculates the Cosine Similarity between them.
5. If a match > 0.5 is found, it marks it as "Present".

## Running the Checks
```bash
python main.py --step 2
```

## Reviewing Results
Results are stored in the `data_checks` table in your PostgreSQL database.
Query them using:
```sql
SELECT * FROM data_checks WHERE study_id = 1;
```

import pandas as pd

def run_rule_checks(df):
    results = []

    # 1. Missing Values Check
    missing = df.isnull().sum().to_dict()
    for var, count in missing.items():
        if count > 0:
            results.append({
                "variable": var,
                "check": "Missing Values",
                "status": "Fail",
                "comments": f"{count} missing values found."
            })
        # Else pass? User table showed "Yes" for checks performed.
        # We can log passes too for completeness (like "Did you check? Yes")
        else:
             results.append({
                "variable": var,
                "check": "Missing Values",
                "status": "Pass",
                "comments": "No missing values."
            })

    # 2. Duplicate Respondent IDs
    # Heuristic: Look for column named 'respondent_id', 'resp_id', or 'id'
    id_cols = [c for c in df.columns if 'id' in c.lower() and 'study' not in c.lower()]
    if id_cols:
        resp_id_col = id_cols[0] 
        dup = df[resp_id_col].duplicated().sum()
        status = "Fail" if dup > 0 else "Pass"
        results.append({
            "variable": resp_id_col,
            "check": "Duplicate IDs",
            "status": status,
            "comments": f"{dup} duplicates found"
        })
    
    # 3. Base Sizes (User Requirement: main >= 300, filters >= 200)
    # Simple check on total rows for now
    total_base = len(df)
    status = "Pass" if total_base >= 300 else "Warning"
    results.append({
        "variable": "Total Sample",
        "check": "Base Sizes",
        "status": status,
        "comments": f"Total N={total_base}"
    })

    return results

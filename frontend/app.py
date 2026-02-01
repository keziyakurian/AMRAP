import streamlit as st
import pandas as pd
import os
import sys

# Add root to path so we can import backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ingestion.spss_loader import load_spss
from backend.checks.audit_runner import run_audit
from backend.db import engine
from backend.config import config

st.set_page_config(page_title="AMRAP Ingestion Audit", layout="wide")

st.title("🚀 AMRAP: Automated Ingestion & Audit")

col1, col2 = st.columns(2)

with col1:
    st.header("Step 1: Upload Data")
    uploaded_file = st.file_uploader("Upload SPSS File (.sav)", type=["sav"])
    
    sow_text = st.text_area("Paste Statement of Work (SOW) Requirements", height=200, 
                            placeholder="Paste the KPIs and Objectives from the SOW here...")

    run_btn = st.button("Run Ingestion & Audit", type="primary")

if run_btn and uploaded_file:
    with st.spinner("Ingesting Data..."):
        # Save temp file
        temp_path = os.path.join(config.DATA_PATH, "temp_upload.sav")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # Run Backend Ingestion
        df = load_spss(temp_path)
        st.success(f"Ingested {len(df)} rows and {len(df.columns)} columns.")

    with st.spinner("Running AI Audit..."):
        # Save SOW for backend to pick up (or pass directly if we refactor)
        # Backend currently reads from 'sample_data/sow.txt', let's overwrite it for this session
        sow_path = os.path.join(config.DATA_PATH, "sow.txt")
        with open(sow_path, "w") as f:
            f.write(sow_text if sow_text else "")
            
        # Run Backend Audit
        run_audit(df)
        st.success("Audit Complete!")
        
        # Display Results
        with col2:
            st.header("Step 2: Audit Results")
            
            # Fetch from DB
            results_df = pd.read_sql("SELECT * FROM data_checks", engine)
            
            # 1. Summary Metrics
            fails = len(results_df[results_df['status'] == 'Fail'])
            warnings = len(results_df[results_df['status'] == 'Warning'])
            passes = len(results_df[results_df['status'] == 'Pass']) # or 'Yes'
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Failed Checks", fails, delta=-fails, delta_color="inverse")
            m2.metric("Warnings", warnings, delta=-warnings, delta_color="inverse")
            m3.metric("Passed", passes)
            
            # 2. Detailed Table
            st.subheader("Detailed Findings")
            
            def color_status(val):
                if val == 'Fail' or val == 'No':
                    return 'background-color: #ffcccc'
                elif val == 'Warning':
                    return 'background-color: #ffffcc'
                else:
                    return 'background-color: #ccffcc'
            
            st.dataframe(results_df.style.applymap(color_status, subset=['status']), use_container_width=True)
            
            # 3. SOW Match Visualization
            st.subheader("SOW Relevance Analysis")
            sow_checks = results_df[results_df['check_item'] == 'SOW Relevance']
            if not sow_checks.empty:
                # Extract score from comments "Similarity Score: 0.85"
                # This is a bit hacky, normally we'd store score in a column.
                # For visualization, let's just show the status distribution
                st.bar_chart(sow_checks['status'].value_counts())
                
                with st.expander("View Unmatched Metrics"):
                    st.write(sow_checks[sow_checks['status'] == 'No'][['check_category', 'details']])

elif run_btn and not uploaded_file:
    st.error("Please upload an SPSS file first.")

st.markdown("---")
st.caption("Powered by AMRAP Backend | PostgreSQL | SentenceTransformers")

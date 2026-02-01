# AMRAP — Automated Market Research Analytics Pipeline

## 🎯 Project Objective

AMRAP automates the entire Kantar-style market research workflow — from SPSS ingestion to AI-driven data validation, pre-analysis, modelling, and client-ready outputs (Excel & PPT).

### What AMRAP replaces
- Manual human work such as:
    - Reading SOW documents
    - Deciding which KPIs / imagery matter
    - Excel data checks
    - Manual SPSS → Excel → R → PPT handoffs

### What AMRAP introduces
- Centralized database-driven workflow
- NLP-based KPI relevance detection
- Automated data audits
- Fully reproducible analytics pipeline

## 🧱 High-Level Architecture

```
SPSS (.sav)
   ↓
Python Ingestion (pyreadstat)
   ↓
PostgreSQL (raw + derived tables)
   ↓
Automated Data Checks (rule + NLP based)
   ↓
Pre-Analysis (means, bases)
   ↓
Correlation / Factors
   ↓
R Path Modelling
   ↓
Validation
   ↓
Excel + PPT Outputs
```

## 📁 Folder Structure

```
AMRAP/
├── backend/
│   ├── config.py             # Central config
│   ├── db.py                 # DB Connection
│   ├── main.py               # Pipeline Orchestrator
│   ├── ingestion/            # SPSS Loader
│   ├── checks/               # AI & Rule-based Audits
│   ├── preanalysis/          # Means & Aggregations
│   ├── analysis/             # Correlations & Factor Analysis
│   ├── modeling/             # R Integration
│   └── outputs/              # Excel/PPT Writers
├── r_models/
│   └── path_model.R          # R Script for SEM
├── sql/
│   └── schema.sql            # Database Schema
├── sample_data/              # Inputs (.sav, .txt)
├── charts/                   # Generated Visualizations
└── deliverables/             # Final Reports
```

## 🚀 How to Run

### 1. Requirements
- Python 3.9+
- PostgreSQL
- R (for Modeling step)

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Setup
Ensure your DB credentials are set in `backend/config.py` (or via Env Vars).
Initialize the database tables using `sql/schema.sql`.

### 3. Execution
The `main.py` script handles all steps of the pipeline.

**Step 1: Ingestion**
Load your SPSS file into the database.
```bash
python main.py --step 1 --file sample_data/demo.sav
```

**Step 2: Automated Audit (AI + Rules)**
Runs data quality checks and checks SOW relevance using NLP.
*Note: Requires `sample_data/sow.txt` to be present.*
```bash
python main.py --step 2
```

**Run Full Pipeline**
(You can sequence these or run specific steps)
```bash
python main.py --step 3  # Means
python main.py --step 4  # Correlations
python main.py --step 5  # Factor Analysis / BIP
python main.py --step 9  # Generate Deliverables
```

## 🧠 AI Intelligence Layer
AMRAP uses `sentence-transformers` to read your **Statement of Work (SOW)** and automatically determine which metrics in your dataset are relevant, replacing manual descriptive checks.

# AMRAP: Automated Market Research Analytics Pipeline

## Overview
AMRAP automates the end-to-end market research workflow, replacing manual Excel/SPSS processes with a Python-based pipeline. It handles data ingestion, automated quality checks (using NLP), statistical analysis, and report generation.

## Features
- **SPSS Ingestion**: Reads `.sav` files directly.
- **Automated Data Checks**: Validates time frames, labels, base sizes, and SOW coverage using `sentence-transformers`.
- **Pre-Analysis**: Computes brand means and aggregations.
- **Advanced Analytics**: Pearson correlations, Factor Analysis.
- **Reporting**: Auto-generates Excel data dumps and PowerPoint decks.
- **R Integration**: Wrapper for Path Analysis (SEM).

## Setup

1. **Prerequisites**
   - Python 3.9+
   - PostgreSQL
   - R (for modelling)

2. **Installation**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database**
   - Ensure PostgreSQL is running.
   - Update `backend/config.py` with credentials.
   - The app will auto-create tables on first run.

4. **Running the Pipeline**
   ```bash
   cd backend
   python main.py
   ```

## Directory Structure
- `backend/`: Core Python code.
- `r_models/`: R scripts for SEM.
- `sql/`: Schema definitions.
- `outputs/`: Generated Excel/PPT files.
- `sample_data/`: Place `.sav` files here.

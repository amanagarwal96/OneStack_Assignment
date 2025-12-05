# Dynamic PDF Data Extraction System

## [cite_start]Approach & Assumptions [cite: 7, 8]
This project implements a system to extract unstructured tabular data from PDFs (e.g., Balance Sheets), convert it to JSON, and store it in a relational database with a **dynamic schema**.

### 1. Architecture
* **Language:** Python 3.9+
* **Framework:** FastAPI (High performance, auto-documentation).
* **PDF Processing:** `pdfplumber` was chosen over `pypdf` because it offers superior table extraction logic, essential for financial documents with grid layouts.
* **Database:** SQLite (via SQLAlchemy).
* **Dynamic Logic:** The system uses SQLAlchemy Core to inspect the JSON keys from the PDF. If the database lacks a column for a specific key, it performs an `ALTER TABLE` operation on the fly before insertion.

### 2. Assumptions
* The PDF contains tables with detectable borders or distinct structural layouts.
* The first row of the table implies the column headers.
* "Particulars" and numeric values are the primary targets for extraction.

### 3. Setup Instructions
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the server:
    ```bash
    uvicorn app.main:app --reload
    ```
3.  Open Browser: Go to `http://127.0.0.1:8000/docs` to test the upload API via the Swagger UI.

### 4. Features Implemented
* **[POST] /upload-pdf:** Accepts PDF, extracts tables, auto-updates DB schema, inserts data.
* **[GET] /get-data:** Retrieves stored data for analysis.